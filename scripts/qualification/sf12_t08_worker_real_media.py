"""Windows proof: synchronous FFmpeg adapter moved off-thread; gated publication."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import threading
import time
from pathlib import Path

from ai_ngerti_geopolitik.application.export_jobs import (
    ExportJobService,
    ExportJobState,
)
from ai_ngerti_geopolitik.application.export_request import ExportRequest
from ai_ngerti_geopolitik.infrastructure.export_postflight import IndependentMp4Postflight
from ai_ngerti_geopolitik.application.vertical_slice import VerticalSliceSession
from ai_ngerti_geopolitik.infrastructure.export_capability_probe import detect_export_toolchain
from ai_ngerti_geopolitik.infrastructure.export_job_adapters import (
    AtomicExportPublisher,
    QualifiedStagedRender,
)
from ai_ngerti_geopolitik.infrastructure.ffmpeg_slice import (
    FfmpegSliceMediaEngine,
    FfprobeMediaProbe,
)
from ai_ngerti_geopolitik.infrastructure.media_integrity import LocalMediaIntegrityInspector
from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    source = args.fixture.resolve(strict=True)
    out_dir = args.evidence.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    probe = FfprobeMediaProbe()
    engine = FfmpegSliceMediaEngine(probe)
    session = VerticalSliceSession.create(probe, JsonProjectRepository(), engine)
    asset = session.import_media(source)
    clip = session.add_to_timeline(asset)
    session.trim_right(clip, 225)
    assert session.state.timeline_end_frame == 15
    original = session.state.semantic_json(include_revision=True)
    source_hash = digest(source)
    tools = detect_export_toolchain()
    assert tools.baseline_detected
    dispatcher = QualifiedStagedRender(engine, LocalMediaIntegrityInspector(probe), tools)
    publisher = AtomicExportPublisher()
    request = ExportRequest.for_project(
        session.state,
        session_id="T08-real-session",
        request_id="T08-real-request",
        output_path=out_dir / "accepted.mp4",
    )
    owner_thread = threading.get_ident()
    snapshots = []
    with ExportJobService(
        dispatcher, publisher, postflight=IndependentMp4Postflight(probe, ffmpeg=engine.ffmpeg)
    ) as jobs:
        first = jobs.submit(
            session.state, request, session_id="T08-real-session", timeout_seconds=120
        )
        assert first.status in (ExportJobState.QUEUED, ExportJobState.RUNNING)
        cutoff = time.monotonic() + 90
        while time.monotonic() < cutoff:
            state = jobs.snapshot(
                request.request_id,
                state=session.state,
                session_id="T08-real-session",
            )
            snapshots.append(state.status.value)
            assert state.progress_percent is None
            if state.status is ExportJobState.READY:
                break
            if state.terminal:
                raise AssertionError(f"premature terminal lifecycle state {state.status}")
            time.sleep(0.01)
        else:
            raise AssertionError("real FFmpeg worker did not finish")
        assert not request.output_path.exists(), "result was published without owner approval"
        assert owner_thread == threading.get_ident()
        accepted = jobs.accept(
            request.request_id, state=session.state, session_id="T08-real-session"
        )
        assert accepted.output_path == request.output_path
        assert accepted.duration_frames == 15
        assert (
            jobs.snapshot(
                request.request_id, state=session.state, session_id="T08-real-session"
            ).progress_percent
            == 100
        )
    info = probe.raw_probe(request.output_path)
    video = next(x for x in info["streams"] if x.get("codec_type") == "video")
    audio = next(x for x in info["streams"] if x.get("codec_type") == "audio")
    assert video["codec_name"] == "h264"
    assert audio["codec_name"] == "aac"
    assert video["avg_frame_rate"] == "30/1"
    assert int(video["nb_frames"]) == 15
    assert (int(video["width"]), int(video["height"])) == (1920, 1080)
    assert not list(out_dir.glob(".ang-export-job-*"))
    assert digest(source) == source_hash
    assert session.state.semantic_json(include_revision=True) == original
    report = {
        "status": "PASS",
        "git_sha": os.environ.get("GITHUB_SHA", "unknown"),
        "worker_phases_observed": sorted(set(snapshots)),
        "publication_requires_owner_accept": True,
        "output_sha256": digest(request.output_path),
        "source_sha256_unchanged": source_hash,
        "video_frames": 15,
        "fps": 30,
        "codec": "h264",
        "audio": "aac",
        "gui_render": "DISABLED_UNTIL_T09_T10",
        "note": "Qt heartbeat verified in tests/qt separately, not production UI wiring",
    }
    (out_dir / "worker_lifecycle.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
