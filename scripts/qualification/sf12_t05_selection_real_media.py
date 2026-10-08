"""SF12-T05 owned-fixture selection with subtitles and narration, real Windows FFmpeg."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

from ai_ngerti_geopolitik.application.commands import (
    CommandBatch,
    SetNarrationTrackCommand,
    SetSubtitleTrackCommand,
)
from ai_ngerti_geopolitik.application.export_request import (
    ExportFrameRange,
    ExportRequest,
    ExportScope,
)
from ai_ngerti_geopolitik.application.vertical_slice import VerticalSliceSession
from ai_ngerti_geopolitik.domain import (
    FrameTime,
    NarrationTrack,
    SubtitleCue,
    SubtitleTrack,
)
from ai_ngerti_geopolitik.infrastructure.export_capability_probe import detect_export_toolchain
from ai_ngerti_geopolitik.infrastructure.export_output_inspector import LocalExportOutputInspector
from ai_ngerti_geopolitik.infrastructure.ffmpeg_slice import FfmpegSliceMediaEngine, FfprobeMediaProbe
from ai_ngerti_geopolitik.infrastructure.media_integrity import LocalMediaIntegrityInspector
from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def process(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, text=True, capture_output=True, check=True, shell=False)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", required=True, type=Path)
    parser.add_argument("--evidence", required=True, type=Path)
    args = parser.parse_args()
    source = args.fixture.resolve(strict=True)
    evidence = args.evidence.resolve()
    evidence.mkdir(parents=True, exist_ok=True)
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise AssertionError("FFmpeg not installed")
    narration = evidence.parent / "generated_narration.wav"
    process(
        [
            ffmpeg,
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=440:sample_rate=48000",
            "-t",
            "4",
            "-c:a",
            "pcm_s16le",
            str(narration),
        ]
    )
    probe = FfprobeMediaProbe()
    engine = FfmpegSliceMediaEngine(probe)
    session = VerticalSliceSession.create(probe, JsonProjectRepository(), engine)
    video_id = session.import_media(source)
    clip_id = session.add_to_timeline(video_id)
    session.trim_right(clip_id, 120)
    session.split_clip(clip_id, 60)
    narration_id = session.import_media(narration)
    assert session.state.timeline_end_frame == 120

    subtitles = SubtitleTrack(
        source_ref="owned-fixture-manual",
        cues=(
            SubtitleCue(
                "S001", 1, FrameTime(30, 30), FrameTime(90, 30), "ACROSS SCENE BOUNDARY"
            ),
            SubtitleCue("S002", 2, FrameTime(90, 30), FrameTime(120, 30), "FINAL SECTION"),
        ),
    )
    narration_track = NarrationTrack(
        "N001", narration_id, FrameTime(15, 30), gain_percent=100
    )
    session.bus.execute(
        CommandBatch(
            batch_id="SF12-T05-FIXTURE",
            label="Add synthetic narration and subtitle",
            actor="manual",
            expected_revision=session.state.revision,
            commands=(
                SetSubtitleTrackCommand(subtitles),
                SetNarrationTrackCommand(narration_track),
            ),
        )
    )
    session.state.validate()
    original = session.state.semantic_json(include_revision=True)
    digests = {"source": sha(source), "narration": sha(narration)}
    tools = detect_export_toolchain()
    assert tools.baseline_detected
    inspector = LocalMediaIntegrityInspector(probe)
    target = LocalExportOutputInspector()

    def create_request(name: str, scope: ExportScope, bounds: tuple[int, int] | None):
        return ExportRequest.for_project(
            session.state,
            request_id=name,
            session_id="T05-WINDOWS",
            output_path=evidence / (name + ".mp4"),
            scope=scope,
            selection=ExportFrameRange(*bounds) if bounds is not None else None,
        )

    full_request = create_request("full_reference", ExportScope.FULL, None)
    full = engine.export_h264_baseline(
        session.state,
        full_request,
        session_id="T05-WINDOWS",
        media_inspector=inspector,
        target_inspector=target,
        toolchain=tools,
    )
    assert full.duration_frames == 120

    results: list[dict[str, object]] = []
    for name, (start, end) in [
        ("beginning", (0, 30)),
        ("scene_boundary", (45, 75)),
        ("ending", (90, 120)),
    ]:
        selection = create_request(name, ExportScope.SELECTION, (start, end))
        rendered = engine.export_h264_selection(
            session.state,
            selection,
            session_id="T05-WINDOWS",
            media_inspector=inspector,
            target_inspector=target,
            toolchain=tools,
        )
        raw = probe.raw_probe(rendered.output_path)
        video = next(s for s in raw["streams"] if s.get("codec_type") == "video")
        audio = next(s for s in raw["streams"] if s.get("codec_type") == "audio")
        assert video["codec_name"] == "h264"
        assert audio["codec_name"] == "aac"
        assert video["avg_frame_rate"] == "30/1"
        assert (int(video["width"]), int(video["height"])) == (1920, 1080)
        assert int(video["nb_frames"]) == end - start
        assert abs(float(raw["format"]["duration"]) - (end - start) / 30) < 0.05
        # Compare independently decoded 30-frame video against the matching
        # global timeline interval. A large timestamp/subtitle displacement
        # will collapse the PSNR; this also verifies inherited cue timing.
        compare = process(
            [
                ffmpeg,
                "-hide_banner",
                "-ss",
                f"{start / 30:.6f}",
                "-i",
                str(full.output_path),
                "-i",
                str(rendered.output_path),
                "-filter_complex",
                "[0:v][1:v]psnr",
                "-frames:v",
                str(end - start),
                "-f",
                "null",
                "-",
            ]
        )
        values = re.findall(r"average:([0-9.]+)", compare.stderr)
        assert values, "independent PSNR metric absent"
        psnr = float(values[-1])
        assert psnr > 33, f"timeline video/subtitle misalignment: {psnr}"
        results.append(
            {
                "range": [start, end],
                "selection_frames": int(video["nb_frames"]),
                "duration": raw["format"]["duration"],
                "psnr_with_full_project": round(psnr, 2),
                "sha256": sha(rendered.output_path),
            }
        )
    assert session.state.semantic_json(include_revision=True) == original
    assert sha(source) == digests["source"] and sha(narration) == digests["narration"]
    report = {
        "status": "PASS",
        "git_sha": os.environ.get("GITHUB_SHA", "unknown"),
        "source_owned": True,
        "full_project_frames": full.duration_frames,
        "subtitle_cues": [(30, 90), (90, 120)],
        "narration_start_frame": 15,
        "selection_results": results,
        "source_hashes_unchanged": digests,
        "ui_render": "DISABLED_T08_T09",
        "architecture": "T05 two-pass qualification; external FFmpeg only",
    }
    (evidence / "selection_qualification.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
