"""T09 Windows actual full-stream decode, selection, HEVC/4K/FPS, corrupt reject."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from dataclasses import replace
from pathlib import Path

from ai_ngerti_geopolitik.application.export_jobs import ExportJobService, ExportJobState
from ai_ngerti_geopolitik.application.export_postflight import ExportPostflightError
from ai_ngerti_geopolitik.application.export_request import (
    ExportCodec,
    ExportFrameRange,
    ExportRequest,
    ExportScope,
)
from ai_ngerti_geopolitik.application.vertical_slice import VerticalSliceSession
from ai_ngerti_geopolitik.infrastructure.export_capability_probe import detect_export_toolchain
from ai_ngerti_geopolitik.infrastructure.export_job_adapters import (
    AtomicExportPublisher,
    QualifiedStagedRender,
)
from ai_ngerti_geopolitik.infrastructure.export_postflight import IndependentMp4Postflight
from ai_ngerti_geopolitik.infrastructure.ffmpeg_slice import (
    FfmpegSliceMediaEngine,
    FfprobeMediaProbe,
)
from ai_ngerti_geopolitik.infrastructure.media_integrity import LocalMediaIntegrityInspector
from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for data in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(data)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", required=True, type=Path)
    parser.add_argument("--evidence", required=True, type=Path)
    args = parser.parse_args()
    source = args.fixture.resolve(strict=True)
    evidence = args.evidence.resolve()
    evidence.mkdir(parents=True, exist_ok=True)
    probe = FfprobeMediaProbe()
    engine = FfmpegSliceMediaEngine(probe)
    project = VerticalSliceSession.create(probe, JsonProjectRepository(), engine)
    asset = project.import_media(source)
    clip = project.add_to_timeline(asset)
    project.trim_right(clip, 225)
    assert project.state.timeline_end_frame == 15
    original = project.state.semantic_json(include_revision=True)
    sha_original = digest(source)
    toolchain = detect_export_toolchain()
    assert toolchain.baseline_detected and toolchain.h265_encoder_found
    check = IndependentMp4Postflight(probe, ffmpeg=engine.ffmpeg)
    dispatcher = QualifiedStagedRender(engine, LocalMediaIntegrityInspector(probe), toolchain)
    cases = [
        ("h264_full", ExportCodec.H264, 1920, 1080, 30, None),
        ("h264_selection", ExportCodec.H264, 1920, 1080, 30, (5, 10)),
        ("h264_4k30", ExportCodec.H264, 3840, 2160, 30, None),
        ("h264_1080p60", ExportCodec.H264, 1920, 1080, 60, None),
        ("h265_1080p30", ExportCodec.H265, 1920, 1080, 30, None),
    ]
    results = []
    for name, codec, width, height, fps, bounds in cases:
        request = ExportRequest.for_project(
            project.state,
            request_id="t09-" + name,
            session_id="t09-owned-windows",
            output_path=evidence / (name + ".mp4"),
            codec=codec,
            width=width,
            height=height,
            fps=fps,
            scope=ExportScope.SELECTION if bounds else ExportScope.FULL,
            selection=ExportFrameRange(*bounds) if bounds else None,
        )
        with ExportJobService(dispatcher, AtomicExportPublisher(), postflight=check) as jobs:
            jobs.submit(
                project.state,
                request,
                session_id="t09-owned-windows",
                timeout_seconds=300,
            )
            cutoff = time.monotonic() + 220
            while time.monotonic() < cutoff:
                snap = jobs.snapshot(
                    request.request_id,
                    state=project.state,
                    session_id="t09-owned-windows",
                )
                if snap.status is ExportJobState.READY:
                    break
                if snap.terminal:
                    raise AssertionError(f"{name}: output rejected {snap.error_code}")
                time.sleep(0.01)
            else:
                raise AssertionError(f"{name}: render/verify timed out")
            assert not request.output_path.exists(), "READY must not publish output"
            accepted = jobs.accept(
                request.request_id,
                state=project.state,
                session_id="t09-owned-windows",
            )
            assert accepted.output_path == request.output_path
            assert (
                accepted.duration_frames == ((bounds[1] - bounds[0]) if bounds else 15) * fps // 30
            )
        info = probe.raw_probe(request.output_path)
        video = next(x for x in info["streams"] if x.get("codec_type") == "video")
        audio = next(x for x in info["streams"] if x.get("codec_type") == "audio")
        assert video["codec_name"] == ("h264" if codec is ExportCodec.H264 else "hevc")
        assert audio["codec_name"] == "aac"
        assert int(video["nb_frames"]) == accepted.duration_frames
        results.append(
            {
                "profile": name,
                "frames": accepted.duration_frames,
                "codec": video["codec_name"],
                "sha256": digest(request.output_path),
                "independent_full_decode": True,
                "atomic_no_overwrite": True,
            }
        )

    good_path = evidence / "h264_full.mp4"
    good_bytes = good_path.read_bytes()
    damaged = evidence.parent / "truncated_untrusted.mp4"
    damaged.write_bytes(good_bytes[: len(good_bytes) // 2])
    reference = ExportRequest.for_project(
        project.state,
        request_id="probe-damage",
        session_id="t09-owned-windows",
        output_path=damaged,
    )
    bad_result = replace(
        accepted, output_path=damaged, duration_frames=15, width=1920, height=1080, fps=30
    )
    failures = []
    try:
        check.verify(damaged, reference, project.state, bad_result, _NeverCancel())
    except ExportPostflightError as error:
        failures.append(error.code.value)
    assert failures, "truncated real media unexpectedly verified"
    damaged.unlink()
    assert digest(source) == sha_original
    assert project.state.semantic_json(include_revision=True) == original
    assert not list(evidence.glob(".ang-export-job-*"))
    report = {
        "status": "PASS",
        "git_sha": os.environ.get("GITHUB_SHA", "unknown"),
        "five_real_profiles": results,
        "corrupt_file_denied": failures,
        "source_sha256_unchanged": sha_original,
        "progress_claim": "phase-only; 100 after publish",
        "gui_export": "DISABLED_UNTIL_T10",
    }
    (evidence / "t09_postflight_evidence.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


class _NeverCancel:
    cancelled = False


if __name__ == "__main__":
    raise SystemExit(main())
