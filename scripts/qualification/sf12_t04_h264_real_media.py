"""T04 real H.264/AAC qualification with source-owned synthetic media only."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

from ai_ngerti_geopolitik.application.export_request import ExportRequest
from ai_ngerti_geopolitik.application.vertical_slice import VerticalSliceSession
from ai_ngerti_geopolitik.infrastructure.export_capability_probe import (
    detect_export_toolchain,
)
from ai_ngerti_geopolitik.infrastructure.export_output_inspector import (
    LocalExportOutputInspector,
)
from ai_ngerti_geopolitik.infrastructure.ffmpeg_slice import (
    FfmpegSliceMediaEngine,
    FfprobeMediaProbe,
    MediaOperationCancelled,
    MediaToolError,
    MutableCancellationToken,
)
from ai_ngerti_geopolitik.infrastructure.media_integrity import (
    LocalMediaIntegrityInspector,
)
from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()

    fixture = args.fixture.resolve(strict=True)
    evidence = args.evidence.resolve()
    evidence.mkdir(parents=True, exist_ok=True)
    probe = FfprobeMediaProbe()
    engine = FfmpegSliceMediaEngine(probe)
    session = VerticalSliceSession.create(probe, JsonProjectRepository(), engine)
    asset_id = session.import_media(fixture)
    clip_id = session.add_to_timeline(asset_id)
    session.trim_right(clip_id, session.state.fps * 7)
    assert session.state.timeline_end_frame == 30

    before_semantic = session.state.semantic_json(include_revision=True)
    input_digest = sha256(fixture)
    tools = detect_export_toolchain()
    assert tools.baseline_detected, "real libx264, aac and ffprobe are required"
    inspector = LocalMediaIntegrityInspector(probe)
    output_inspector = LocalExportOutputInspector()
    output = evidence / "h264_baseline.mp4"
    assert not output.exists(), "qualification target must be fresh"
    request = ExportRequest.for_project(
        session.state,
        request_id="sf12-t04-real",
        session_id="sf12-t04-session",
        output_path=output,
    )
    result = engine.export_h264_baseline(
        session.state,
        request,
        session_id="sf12-t04-session",
        media_inspector=inspector,
        target_inspector=output_inspector,
        toolchain=tools,
    )
    assert result.output_path == output
    assert result.project_revision == session.state.revision
    assert (result.width, result.height, result.fps, result.duration_frames) == (
        1920, 1080, 30, 30
    )
    raw = probe.raw_probe(output)
    streams = raw["streams"]
    assert isinstance(streams, list)
    video = next(s for s in streams if s.get("codec_type") == "video")
    audio = next(s for s in streams if s.get("codec_type") == "audio")
    assert video["codec_name"] == "h264"
    assert audio["codec_name"] == "aac"
    assert int(video["width"]) == 1920 and int(video["height"]) == 1080
    assert str(video["avg_frame_rate"]) == "30/1"
    assert input_digest == sha256(fixture)
    assert session.state.semantic_json(include_revision=True) == before_semantic
    output_digest = sha256(output)

    blocked: list[str] = []

    def expect_reject(
        trial: ExportRequest,
        expected: str,
        cancellation: MutableCancellationToken | None = None,
    ) -> None:
        try:
            engine.export_h264_baseline(
                session.state,
                trial,
                session_id="sf12-t04-session",
                media_inspector=inspector,
                target_inspector=output_inspector,
                toolchain=tools,
                cancellation=cancellation,
            )
        except (MediaToolError, MediaOperationCancelled) as exc:
            assert expected in str(exc), str(exc)
            blocked.append(expected)
        else:
            raise AssertionError("an unsafe export was accepted")

    # Existing final file is immutable, even when request passes typed DTO.
    expect_reject(request, "OUTPUT_EXISTS")
    assert sha256(output) == output_digest

    # File-source identity must never be overwritten by its own export.
    collision = ExportRequest.for_project(
        session.state,
        session_id="sf12-t04-session",
        request_id="source-collision",
        output_path=fixture,
    )
    expect_reject(collision, "OUTPUT_COLLISION")
    assert sha256(fixture) == input_digest

    cancelled = MutableCancellationToken()
    cancelled.cancel()
    cancel_target = evidence / "pre_cancelled.mp4"
    cancel_request = ExportRequest.for_project(
        session.state,
        session_id="sf12-t04-session",
        request_id="pre-cancel",
        output_path=cancel_target,
    )
    expect_reject(cancel_request, "EXPORT_CANCELLED", cancelled)
    assert not cancel_target.exists()

    assert session.state.semantic_json(include_revision=True) == before_semantic
    assert sorted(path.name for path in evidence.iterdir()) == ["h264_baseline.mp4"]
    report = {
        "status": "PASS",
        "git_sha": os.environ.get("GITHUB_SHA", "UNSPECIFIED"),
        "media_scope": "synthetic source-owned FFmpeg fixture",
        "codec": "h264",
        "audio_codec": "aac",
        "video_width": int(video["width"]),
        "video_height": int(video["height"]),
        "fps": str(video["avg_frame_rate"]),
        "project_frames": session.state.timeline_end_frame,
        "output_sha256": output_digest,
        "source_unchanged_sha256": input_digest,
        "negative_checks": blocked,
        "render_gui": "DISABLED_UNTIL_T08_T09",
    }
    (evidence / "qualification.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
