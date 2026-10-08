"""Real T07 owned Windows fixture: subtitle on/off, narration, sharpen and CRF."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import struct
import subprocess
from dataclasses import replace
from pathlib import Path

from ai_ngerti_geopolitik.application.commands import (
    CommandBatch,
    SetNarrationTrackCommand,
    SetSubtitleTrackCommand,
)
from ai_ngerti_geopolitik.application.export_request import ExportRequest
from ai_ngerti_geopolitik.application.export_style_policy import T07_STYLE_CANDIDATES
from ai_ngerti_geopolitik.application.vertical_slice import VerticalSliceSession
from ai_ngerti_geopolitik.domain import FrameTime, NarrationTrack, SubtitleCue, SubtitleTrack
from ai_ngerti_geopolitik.infrastructure.export_capability_probe import detect_export_toolchain
from ai_ngerti_geopolitik.infrastructure.export_output_inspector import LocalExportOutputInspector
from ai_ngerti_geopolitik.infrastructure.ffmpeg_export_style import FfmpegStyleQualificationExporter
from ai_ngerti_geopolitik.infrastructure.ffmpeg_slice import FfmpegSliceMediaEngine, FfprobeMediaProbe
from ai_ngerti_geopolitik.infrastructure.media_integrity import LocalMediaIntegrityInspector
from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def execute(argv: list[str]) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(argv, capture_output=True, check=True, shell=False)


def gray_frame(ffmpeg: str, path: Path, at: str) -> bytes:
    data = execute(
        [
            ffmpeg, "-hide_banner", "-loglevel", "error", "-ss", at, "-i", str(path),
            "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "gray", "-"
        ]
    ).stdout
    assert len(data) == 1920 * 1080
    return data


def pcm_audio(ffmpeg: str, path: Path) -> tuple[int, ...]:
    raw = execute(
        [
            ffmpeg, "-hide_banner", "-loglevel", "error", "-i", str(path),
            "-map", "0:a:0", "-ac", "1", "-ar", "48000",
            "-f", "s16le", "-acodec", "pcm_s16le", "-"
        ]
    ).stdout
    assert len(raw) >= 48000 * 2
    return struct.unpack("<" + "h" * (len(raw) // 2), raw)


def mean_difference(a: tuple[int, ...], b: tuple[int, ...], start: int, end: int) -> float:
    samples = min(len(a), len(b))
    lo = min(start, samples)
    hi = min(end, samples)
    assert hi > lo
    return sum(abs(a[i] - b[i]) for i in range(lo, hi)) / (hi - lo)


def mean_pixel_difference(a: bytes, b: bytes) -> float:
    assert len(a) == len(b)
    return sum(abs(x - y) for x, y in zip(a, b, strict=True)) / len(a)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    fixture = args.fixture.resolve(strict=True)
    evidence = args.evidence.resolve()
    evidence.mkdir(parents=True, exist_ok=True)
    ffmpeg = shutil.which("ffmpeg")
    assert ffmpeg is not None
    narration = evidence.parent / "narration_440hz.wav"
    execute(
        [
            ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
            "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000",
            "-t", "2", "-c:a", "pcm_s16le", str(narration)
        ]
    )
    probe = FfprobeMediaProbe()
    engine = FfmpegSliceMediaEngine(probe)
    exporter = FfmpegStyleQualificationExporter(engine)
    session = VerticalSliceSession.create(probe, JsonProjectRepository(), engine)
    media = session.import_media(fixture)
    clip = session.add_to_timeline(media)
    session.trim_right(clip, 180)
    assert session.state.timeline_end_frame == 60
    narration_id = session.import_media(narration)
    subtitle = SubtitleTrack(
        source_ref="owned-t07",
        cues=(SubtitleCue("S001", 1, FrameTime(15, 30), FrameTime(55, 30), "CHECK T07 SUBTITLE"),),
    )
    narration_track = NarrationTrack("N001", narration_id, FrameTime(15, 30), gain_percent=130)
    session.bus.execute(
        CommandBatch(
            batch_id="T07-MEDIA-FIXTURE",
            label="Synthetic narration/subtitle",
            actor="manual",
            expected_revision=session.state.revision,
            commands=(
                SetSubtitleTrackCommand(subtitle),
                SetNarrationTrackCommand(narration_track),
            ),
        )
    )
    session.state.validate()
    original_state = session.state.semantic_json(include_revision=True)
    input_hashes = {"video": sha(fixture), "narration": sha(narration)}
    tools = detect_export_toolchain()
    assert tools.baseline_detected
    media_inspector = LocalMediaIntegrityInspector(probe)
    target_inspector = LocalExportOutputInspector()

    files: list[Path] = []
    records: list[dict[str, object]] = []
    for index, style in enumerate(T07_STYLE_CANDIDATES):
        target = evidence / f"style_{index}.mp4"
        request = ExportRequest.for_project(
            session.state,
            session_id="T07-WIN",
            request_id=f"style-{index}",
            output_path=target,
            quality=style.quality,
            sharpen=style.sharpen,
            subtitles=style.subtitles,
        )
        result = exporter.export(
            session.state,
            request,
            session_id="T07-WIN",
            media_inspector=media_inspector,
            target_inspector=target_inspector,
            toolchain=tools,
        )
        raw = probe.raw_probe(target)
        videos = [v for v in raw["streams"] if v.get("codec_type") == "video"]
        audios = [v for v in raw["streams"] if v.get("codec_type") == "audio"]
        assert len(videos) == 1 and len(audios) == 1
        assert videos[0]["codec_name"] == "h264"
        assert audios[0]["codec_name"] == "aac"
        assert (int(videos[0]["width"]), int(videos[0]["height"])) == (1920, 1080)
        assert videos[0]["avg_frame_rate"] == "30/1"
        assert int(videos[0]["nb_frames"]) == 60
        assert abs(float(raw["format"]["duration"]) - 2.0) < 0.06
        assert result.duration_frames == 60
        files.append(target)
        records.append({
            "style": index,
            "quality": style.quality.value,
            "sharpen": style.sharpen.value,
            "subtitles": style.subtitles.value,
            "preset": style.preset,
            "crf": style.crf,
            "video_filter": style.video_filter,
            "size_bytes": target.stat().st_size,
            "sha256": sha(target),
        })

    # Text is active at frame 30. Gray-frame differences verify on/off;
    # no pixel equality expected after separate lossy re-encodes.
    on = gray_frame(ffmpeg, files[0], "1.000")
    off = gray_frame(ffmpeg, files[1], "1.000")
    light = gray_frame(ffmpeg, files[4], "1.000")
    crisp = gray_frame(ffmpeg, files[5], "1.000")
    off_difference = mean_pixel_difference(on, off)
    light_difference = mean_pixel_difference(on, light)
    crisp_difference = mean_pixel_difference(on, crisp)
    assert off_difference > 0.15, "subtitle burn-in/off was visually identical"
    assert light_difference > 0.05, "light sharpen had no measurable pixel change"
    assert crisp_difference > 0.05, "crisp sharpen had no measurable pixel change"
    assert sha(files[0]) != sha(files[2]) and sha(files[2]) != sha(files[3])

    # Independent narration reference, same synthetic state minus narration.
    # It is written only in the runner's private evidence directory.
    no_narration = evidence / "no_narration_control.mp4"
    derived = replace(session.state, narration=None)
    engine.export(derived, no_narration)
    audio_with = pcm_audio(ffmpeg, files[0])
    audio_without = pcm_audio(ffmpeg, no_narration)
    early = mean_difference(audio_with, audio_without, 4800, 14400)
    late = mean_difference(audio_with, audio_without, 48000, 72000)
    assert late > early * 2 + 15, "narration not measurably mixed after frame 15"
    assert session.state.semantic_json(include_revision=True) == original_state
    assert input_hashes == {"video": sha(fixture), "narration": sha(narration)}
    report = {
        "status": "PASS",
        "git_sha": os.environ.get("GITHUB_SHA", "unknown"),
        "fixture_frames": 60,
        "subtitle_cue_frames": [15, 55],
        "narration_start_frame": 15,
        "variants": records,
        "gray_mean_difference_subtitles": round(off_difference, 4),
        "gray_mean_difference_sharpen_light": round(light_difference, 4),
        "gray_mean_difference_sharpen_crisp": round(crisp_difference, 4),
        "audio_mean_difference_pre_narration": round(early, 4),
        "audio_mean_difference_during_narration": round(late, 4),
        "owned_inputs_unchanged": input_hashes,
        "gui_render": "DISABLED_T08_T09",
        "toolchain": "external FFmpeg/FFprobe only; not portable bundle",
    }
    (evidence / "t07_style_evidence.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
