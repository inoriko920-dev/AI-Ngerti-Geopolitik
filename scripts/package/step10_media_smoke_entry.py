from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from pathlib import Path

from ai_ngerti_geopolitik.application.export_jobs import ExportJobService, ExportJobState
from ai_ngerti_geopolitik.application.export_request import (
    ExportCodec,
    ExportFrameRange,
    ExportQuality,
    ExportRequest,
    ExportScope,
    ExportSharpen,
    ExportSubtitles,
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

TOKEN = "ANG_S10_PACKAGED_MEDIA_SMOKE_OK"
T10_TOKEN = "ANG_SF12_T10_PACKAGED_EXPORT_QUALIFICATION_OK"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()



def verify_sf12_t10_packaged(fixture: Path, output_dir: Path) -> int:
    """T10 standalone frozen-package qualification; NOT a production UI render binding."""

    probe = FfprobeMediaProbe()
    engine = FfmpegSliceMediaEngine(probe)
    session = VerticalSliceSession.create(probe, JsonProjectRepository(), engine)
    imported = session.import_media(fixture)
    clip = session.add_to_timeline(imported)
    session.trim_right(clip, 225)
    assert session.state.timeline_end_frame == 15
    before = session.state.semantic_json(include_revision=True)
    source_digest = sha256(fixture)
    available = detect_export_toolchain()
    if not available.baseline_detected or not available.h265_encoder_found:
        raise RuntimeError("T10_EXTERNAL_NATIVE_ENCODERS_REQUIRED")
    dispatcher = QualifiedStagedRender(engine, LocalMediaIntegrityInspector(probe), available)
    verifier = IndependentMp4Postflight(probe, ffmpeg=engine.ffmpeg)
    publisher = AtomicExportPublisher()
    profiles = [
        ("h264_1080p30", ExportCodec.H264, 1920, 1080, 30, ExportScope.FULL,
         None, ExportQuality.HIGH, ExportSharpen.NONE, ExportSubtitles.BURN_IN),
        ("h264_selection", ExportCodec.H264, 1920, 1080, 30, ExportScope.SELECTION,
         ExportFrameRange(5, 10), ExportQuality.HIGH, ExportSharpen.NONE, ExportSubtitles.BURN_IN),
        ("h264_1440p30", ExportCodec.H264, 2560, 1440, 30, ExportScope.FULL,
         None, ExportQuality.HIGH, ExportSharpen.NONE, ExportSubtitles.BURN_IN),
        ("h264_4k30", ExportCodec.H264, 3840, 2160, 30, ExportScope.FULL,
         None, ExportQuality.HIGH, ExportSharpen.NONE, ExportSubtitles.BURN_IN),
        ("h264_1080p60", ExportCodec.H264, 1920, 1080, 60, ExportScope.FULL,
         None, ExportQuality.HIGH, ExportSharpen.NONE, ExportSubtitles.BURN_IN),
        ("h265_1080p30", ExportCodec.H265, 1920, 1080, 30, ExportScope.FULL,
         None, ExportQuality.HIGH, ExportSharpen.NONE, ExportSubtitles.BURN_IN),
        ("subtitle_off", ExportCodec.H264, 1920, 1080, 30, ExportScope.FULL,
         None, ExportQuality.HIGH, ExportSharpen.NONE, ExportSubtitles.OFF),
        ("quality_crisp", ExportCodec.H264, 1920, 1080, 30, ExportScope.FULL,
         None, ExportQuality.DOCUMENTARY_CRISP, ExportSharpen.NONE, ExportSubtitles.BURN_IN),
        ("sharpen_light", ExportCodec.H264, 1920, 1080, 30, ExportScope.FULL,
         None, ExportQuality.HIGH, ExportSharpen.LIGHT, ExportSubtitles.BURN_IN),
    ]
    results: list[dict[str, object]] = []
    for idx, item in enumerate(profiles):
        name, codec, width, height, fps, scope, selection, quality, sharpen, subtitles = item
        request = ExportRequest.for_project(
            session.state,
            session_id="t10-packaged-session",
            request_id=f"t10-packaged-{idx}",
            output_path=output_dir / f"{name}.mp4",
            codec=codec,
            width=width,
            height=height,
            fps=fps,
            scope=scope,
            selection=selection,
            quality=quality,
            sharpen=sharpen,
            subtitles=subtitles,
        )
        with ExportJobService(dispatcher, publisher, postflight=verifier) as jobs:
            jobs.submit(session.state, request, session_id="t10-packaged-session",
                        timeout_seconds=300.0)
            deadline = time.monotonic() + 250.0
            while time.monotonic() < deadline:
                status = jobs.snapshot(request.request_id, state=session.state,
                                       session_id="t10-packaged-session")
                if status.status is ExportJobState.READY:
                    break
                if status.terminal:
                    raise RuntimeError(f"T10_PACKAGED_PROFILE_FAILED:{name}:{status.error_code}")
                time.sleep(0.025)
            else:
                raise RuntimeError(f"T10_PACKAGED_PROFILE_TIMED_OUT:{name}")
            assert not request.output_path.exists(), "worker published before explicit accept"
            result = jobs.accept(request.request_id, state=session.state,
                                 session_id="t10-packaged-session")
            assert result.output_path.is_file()
        video_info = probe.raw_probe(request.output_path)
        stream = next(x for x in video_info["streams"] if x.get("codec_type") == "video")
        audio = next(x for x in video_info["streams"] if x.get("codec_type") == "audio")
        assert stream["codec_name"] == ("hevc" if codec is ExportCodec.H265 else "h264")
        assert audio["codec_name"] == "aac"
        assert (int(stream["width"]), int(stream["height"])) == (width, height)
        assert stream["avg_frame_rate"] == f"{fps}/1"
        assert int(stream["nb_frames"]) == result.duration_frames
        results.append(
            {
                "profile": name,
                "codec": stream["codec_name"],
                "resolution": [width, height],
                "fps": fps,
                "frames": result.duration_frames,
                "sha256": sha256(request.output_path),
                "full_decode": True,
                "owner_only_accept": True,
            }
        )
    assert session.state.semantic_json(include_revision=True) == before
    assert sha256(fixture) == source_digest
    assert not list(output_dir.glob(".ang-export-job-*"))
    report = {
        "scope": "packaged CLI media qualification only; separate frozen UI shell",
        "status": "PASS",
        "git_sha": os.environ.get("GITHUB_SHA", "not-provided"),
        "source_sha256": source_digest,
        "verified_mp4_profiles": results,
        "external_toolchain_only": True,
        "portable_final_editor": False,
        "qt_render_connected": False,
        "release_permission": False,
    }
    (output_dir / "sf12_t10_packaged_qualification.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(T10_TOKEN)
    print(json.dumps(report, sort_keys=True))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--sf12-t10", action="store_true")
    args = parser.parse_args()

    fixture = args.fixture.resolve()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.sf12_t10:
        return verify_sf12_t10_packaged(fixture, output_dir)

    probe = FfprobeMediaProbe()
    repository = JsonProjectRepository()
    engine = FfmpegSliceMediaEngine(probe)
    session = VerticalSliceSession.create(probe, repository, engine)

    asset_id = session.import_media(fixture)
    clip_id = session.add_to_timeline(asset_id)
    right_clip_id = session.split_clip(clip_id, 150)
    session.trim_right(right_clip_id, 30)

    project_path = output_dir / "packaged_smoke.angproj"
    session.save(project_path)
    assert repository.load(project_path).semantic_hash() == session.state.semantic_hash()

    before = session.preview_frame(149, output_dir / "preview_149.png")
    after = session.preview_frame(151, output_dir / "preview_151.png")
    assert before.output_path.is_file()
    assert after.output_path.is_file()
    assert sha256(before.output_path) != sha256(after.output_path)

    export_path = output_dir / "packaged_smoke.mp4"
    result = session.export(export_path)
    assert result.width == 1920
    assert result.height == 1080
    assert result.fps == 30
    assert abs(result.duration_frames - 210) <= 1

    print(TOKEN)
    print(f"project={project_path}")
    print(f"export={export_path}")
    print(f"export_sha256={sha256(export_path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
