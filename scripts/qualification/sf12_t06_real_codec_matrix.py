"""Actual Windows qualification of four codec/profile cells on owned footage."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

from ai_ngerti_geopolitik.application.export_profiles import T06_CANDIDATE_PROFILES
from ai_ngerti_geopolitik.application.export_request import ExportRequest
from ai_ngerti_geopolitik.application.vertical_slice import VerticalSliceSession
from ai_ngerti_geopolitik.infrastructure.export_capability_probe import detect_export_toolchain
from ai_ngerti_geopolitik.infrastructure.export_output_inspector import LocalExportOutputInspector
from ai_ngerti_geopolitik.infrastructure.ffmpeg_export_profiles import FfmpegMatrixQualificationExporter
from ai_ngerti_geopolitik.infrastructure.ffmpeg_slice import FfmpegSliceMediaEngine, FfprobeMediaProbe
from ai_ngerti_geopolitik.infrastructure.media_integrity import LocalMediaIntegrityInspector
from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--fixture", required=True, type=Path)
    p.add_argument("--evidence", required=True, type=Path)
    args = p.parse_args()
    fixture = args.fixture.resolve(strict=True)
    evidence = args.evidence.resolve()
    evidence.mkdir(parents=True, exist_ok=True)
    probe = FfprobeMediaProbe()
    engine = FfmpegSliceMediaEngine(probe)
    exporter = FfmpegMatrixQualificationExporter(engine)
    session = VerticalSliceSession.create(probe, JsonProjectRepository(), engine)
    asset = session.import_media(fixture)
    clip = session.add_to_timeline(asset)
    # 0.5 s / 15 input frames keeps UHD/H.265 runner memory bounded.
    session.trim_right(clip, 225)
    assert session.state.timeline_end_frame == 15
    toolchain = detect_export_toolchain()
    assert toolchain.baseline_detected
    assert toolchain.h265_encoder_found, "libx265 is required for T06 HEVC qualification"
    integrity = LocalMediaIntegrityInspector(probe)
    output_guard = LocalExportOutputInspector()
    initial_hash = digest(fixture)
    before = session.state.semantic_json(include_revision=True)
    outcomes: list[dict[str, object]] = []

    for profile in T06_CANDIDATE_PROFILES:
        output = evidence / (profile.cell.value + ".mp4")
        assert not output.exists(), "profile result exists before qualification"
        request = ExportRequest.for_project(
            session.state,
            session_id="windows-t06",
            request_id="t06-" + profile.cell.value,
            output_path=output,
            codec=profile.codec,
            width=profile.width,
            height=profile.height,
            fps=profile.fps,
        )
        result = exporter.export(
            session.state,
            request,
            session_id="windows-t06",
            media_inspector=integrity,
            target_inspector=output_guard,
            toolchain=toolchain,
        )
        raw = probe.raw_probe(output)
        videos = [s for s in raw["streams"] if s.get("codec_type") == "video"]
        audios = [s for s in raw["streams"] if s.get("codec_type") == "audio"]
        expected_frames = 15 * profile.fps // 30
        assert len(videos) == 1 and len(audios) == 1
        assert videos[0]["codec_name"] == profile.expected_decoder
        assert audios[0]["codec_name"] == "aac"
        assert int(videos[0]["width"]) == profile.width
        assert int(videos[0]["height"]) == profile.height
        assert videos[0]["avg_frame_rate"] == f"{profile.fps}/1"
        assert int(videos[0]["nb_frames"]) == expected_frames
        assert result.duration_frames == expected_frames
        assert abs(float(raw["format"]["duration"]) - 0.5) < 0.05
        assert digest(fixture) == initial_hash, "source changed during qualification"
        outcomes.append(
            {
                "cell": profile.cell.value,
                "codec": videos[0]["codec_name"],
                "encoder": profile.encoder,
                "width": profile.width,
                "height": profile.height,
                "fps": profile.fps,
                "frames": expected_frames,
                "duration_seconds": float(raw["format"]["duration"]),
                "sha256": digest(output),
                "note": "upscaled from original 1080p" if profile.height > 1080 else "native 1080p",
            }
        )
    assert session.state.semantic_json(include_revision=True) == before
    assert digest(fixture) == initial_hash
    assert not list(evidence.glob(".ang-t06-*"))
    report = {
        "status": "PASS",
        "git_sha": os.environ.get("GITHUB_SHA", "unknown"),
        "project_frames": 15,
        "input_duration_seconds": 0.5,
        "source_sha256": initial_hash,
        "output_matrix": outcomes,
        "unsupported": ["h265_4k60", "h265_1440p30", "h264_4k60"],
        "gui_render": "DISABLED_UNTIL_T08_T09",
        "native_toolchain": "External runner ffmpeg; not packaged",
    }
    (evidence / "matrix_qualification.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
