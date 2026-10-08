"""SF12-T09 postflight rejects false codec/frames/audio/metadata and forged readiness."""

from __future__ import annotations

import threading
import time
from dataclasses import replace
from pathlib import Path

import pytest

from ai_ngerti_geopolitik.application.export_jobs import (
    ExportJobError,
    ExportJobService,
    ExportJobState,
)
from ai_ngerti_geopolitik.application.export_postflight import (
    ExportPostflightError,
    PostflightCode,
    PostflightReceipt,
)
from ai_ngerti_geopolitik.application.export_request import (
    ExportCodec,
    ExportFrameRange,
    ExportRequest,
    ExportScope,
)
from ai_ngerti_geopolitik.application.ports import ExportResult
from ai_ngerti_geopolitik.domain import Asset, Clip, FrameTime, ProjectState, Track
from ai_ngerti_geopolitik.infrastructure.export_job_adapters import AtomicExportPublisher
from ai_ngerti_geopolitik.infrastructure.export_postflight import IndependentMp4Postflight
from ai_ngerti_geopolitik.infrastructure.ffmpeg_slice import ProcessResult


class FakeProbe:
    def __init__(self, **bad: object) -> None:
        self.bad = bad

    def raw_probe(self, path: Path) -> dict[str, object]:
        raw: dict[str, object] = {
            "streams": [
                {
                    "codec_type": "video",
                    "codec_name": "h264",
                    "width": 1920,
                    "height": 1080,
                    "avg_frame_rate": "30/1",
                    "nb_frames": "30",
                },
                {"codec_type": "audio", "codec_name": "aac"},
            ],
            "format": {"format_name": "mov,mp4,m4a,3gp,3g2,mj2", "duration": "1.0"},
        }
        streams = raw["streams"]
        assert isinstance(streams, list)
        video = streams[0]
        audio = streams[1]
        assert isinstance(video, dict) and isinstance(audio, dict)
        fmt = raw["format"]
        assert isinstance(fmt, dict)
        for name, value in self.bad.items():
            if name == "container":
                fmt["format_name"] = value
            elif name == "duration":
                fmt["duration"] = value
            elif name == "audio":
                audio["codec_name"] = value
            elif name == "no_audio":
                streams.pop()
            elif name == "extra_subtitle":
                streams.append({"codec_type": "subtitle", "codec_name": "mov_text"})
            else:
                video[name] = value
        return raw


class FakeDecoder:
    def __init__(self, frames: int = 30, *, fail: bool = False) -> None:
        self.frames = frames
        self.fail = fail

    def run(self, args: list[str], cancellation: object) -> ProcessResult:
        if self.fail:
            raise RuntimeError("C:\\Users\\secret\\private.mov")
        return ProcessResult(f"frame={self.frames}\nprogress=end\n", "")


class NoCancellation:
    cancelled = False


def _state(tmp_path: Path) -> tuple[ProjectState, ExportRequest, Path, ExportResult]:
    original = tmp_path / "source.mp4"
    original.write_bytes(b"protected input")
    asset = Asset(
        "A001",
        str(original),
        "video",
        FrameTime(30, 30),
        1920,
        1080,
        True,
        "a" * 64,
    )
    clip = Clip("C001", "A001", FrameTime(0, 30), FrameTime(0, 30), FrameTime(30, 30))
    state = replace(
        ProjectState.create("P001", "Postflight"),
        assets=(asset,),
        tracks=(Track("V1", "video", 0, (clip,)),),
    )
    request = ExportRequest.for_project(
        state, session_id="t09", request_id="job-t09", output_path=tmp_path / "out.mp4"
    )
    stage = tmp_path / "staged.mp4"
    stage.write_bytes(b"synthetic inspect fixture")
    result = ExportResult(state.revision, stage, 30, 1920, 1080, 30)
    return state, request, stage, result


def _verify(
    state: ProjectState,
    request: ExportRequest,
    stage: Path,
    result: ExportResult,
    *,
    probe: FakeProbe | None = None,
    decoder: FakeDecoder | None = None,
) -> PostflightReceipt:
    check = IndependentMp4Postflight(
        probe or FakeProbe(),
        ffmpeg="fake",
        runner=decoder or FakeDecoder(),
    )
    return check.verify(stage, request, state, result, NoCancellation())


def test_full_probe_and_decode_returns_sealed_receipt(tmp_path: Path) -> None:
    state, request, stage, result = _state(tmp_path)
    receipt = _verify(state, request, stage, result)
    assert receipt.expected_frames == 30
    assert len(receipt.sha256) == 64
    assert receipt.still_current(stage)
    assert not receipt.still_current(tmp_path / "other.mp4")
    stage.write_bytes(b"changed data")
    assert not receipt.still_current(stage)


@pytest.mark.parametrize(
    ("bad", "expected"),
    [
        ({"container": "matroska,webm"}, PostflightCode.INVALID_CONTAINER),
        ({"no_audio": True}, PostflightCode.STREAM_STRUCTURE),
        ({"extra_subtitle": True}, PostflightCode.STREAM_STRUCTURE),
        ({"codec_name": "hevc"}, PostflightCode.CODEC_MISMATCH),
        ({"audio": "opus"}, PostflightCode.CODEC_MISMATCH),
        ({"width": 1280}, PostflightCode.SIZE_MISMATCH),
        ({"height": 720}, PostflightCode.SIZE_MISMATCH),
        ({"avg_frame_rate": "60/1"}, PostflightCode.FPS_MISMATCH),
        ({"nb_frames": "29"}, PostflightCode.FRAME_COUNT_MISMATCH),
        ({"duration": "0.40"}, PostflightCode.DURATION_MISMATCH),
    ],
)
def test_metadata_mismatch_is_typed_and_never_decoded(
    tmp_path: Path, bad: dict[str, object], expected: PostflightCode
) -> None:
    state, request, stage, result = _state(tmp_path)
    with pytest.raises(ExportPostflightError) as error:
        _verify(state, request, stage, result, probe=FakeProbe(**bad))
    assert error.value.code is expected
    assert "Users" not in str(error.value)


@pytest.mark.parametrize(
    ("wrong_result", "expected"),
    [
        ({"duration_frames": 31}, PostflightCode.RESULT_MISMATCH),
        ({"width": 1280}, PostflightCode.RESULT_MISMATCH),
        ({"fps": 60}, PostflightCode.RESULT_MISMATCH),
    ],
)
def test_forged_adapter_result_is_rejected(
    tmp_path: Path, wrong_result: dict[str, object], expected: PostflightCode
) -> None:
    state, request, stage, result = _state(tmp_path)
    with pytest.raises(ExportPostflightError) as caught:
        _verify(state, request, stage, replace(result, **wrong_result))
    assert caught.value.code is expected


@pytest.mark.parametrize(("frames", "fail"), [(29, False), (30, True)])
def test_unreadable_or_truncated_decode_fails_privately(
    tmp_path: Path, frames: int, fail: bool
) -> None:
    state, request, stage, result = _state(tmp_path)
    with pytest.raises(ExportPostflightError) as caught:
        _verify(state, request, stage, result, decoder=FakeDecoder(frames, fail=fail))
    assert caught.value.code is PostflightCode.DECODE_FAILED
    assert "secret" not in str(caught.value)


def test_missing_or_symlink_stage_fails(tmp_path: Path) -> None:
    state, request, stage, result = _state(tmp_path)
    stage.unlink()
    with pytest.raises(ExportPostflightError) as caught:
        _verify(state, request, stage, result)
    assert caught.value.code is PostflightCode.FILE_MISSING_OR_EMPTY


def test_forged_request_codec_rejected(tmp_path: Path) -> None:
    state, request, stage, result = _state(tmp_path)
    request = replace(request, codec=ExportCodec.H265)
    with pytest.raises(ExportPostflightError) as caught:
        _verify(state, request, stage, result)
    assert caught.value.code is PostflightCode.CODEC_MISMATCH


def test_selection_expected_frame_count_is_half_open(tmp_path: Path) -> None:
    state, request, stage, result = _state(tmp_path)
    request = replace(request, scope=ExportScope.SELECTION, selection=ExportFrameRange(5, 15))
    result = replace(result, duration_frames=10)
    probe = FakeProbe(nb_frames="10", duration="0.333333")
    receipt = _verify(state, request, stage, result, probe=probe, decoder=FakeDecoder(10))
    assert receipt.expected_frames == 10


class FakeRender:
    def __init__(self) -> None:
        self.started = threading.Event()

    def render(self, state, request, *, stage_path, cancellation):
        stage_path.write_bytes(b"faked payload that must not become READY")
        self.started.set()
        return ExportResult(state.revision, stage_path, 30, 1920, 1080, 30)


def test_job_worker_fails_closed_when_independent_postflight_rejects(tmp_path: Path) -> None:
    state, request, _, _ = _state(tmp_path)
    stage = tmp_path / "staged.mp4"
    stage.unlink()
    renderer = FakeRender()
    verifier = IndependentMp4Postflight(
        FakeProbe(codec_name="hevc"), ffmpeg="fake", runner=FakeDecoder()
    )
    with ExportJobService(renderer, AtomicExportPublisher(), postflight=verifier) as jobs:
        jobs.submit(state, request, session_id="t09")
        assert renderer.started.wait(3)
        cutoff = time.monotonic() + 5
        while time.monotonic() < cutoff:
            status = jobs.snapshot(request.request_id, state=state, session_id="t09")
            if status.terminal:
                break
            time.sleep(0.01)
        else:
            raise AssertionError("postflight failure was not terminal")
        assert status.status is ExportJobState.FAILED
        assert status.error_code == PostflightCode.CODEC_MISMATCH.value
        assert not request.output_path.exists()
        with pytest.raises(ExportJobError, match="EXPORT_NOT_READY"):
            jobs.accept(request.request_id, state=state, session_id="t09")
    assert not list(tmp_path.glob(".ang-export-job-*"))


def test_postflight_receipt_blocks_tampered_stage_before_accept(tmp_path: Path) -> None:
    state, request, stage, _ = _state(tmp_path)
    stage.unlink()

    class FakePass:
        def verify(self, file, _request, _state, result, _cancellation):
            return PostflightReceipt.capture(file, result.duration_frames)

    with ExportJobService(FakeRender(), AtomicExportPublisher(), postflight=FakePass()) as jobs:
        jobs.submit(state, request, session_id="t09")
        end = time.monotonic() + 5
        while time.monotonic() < end:
            snap = jobs.snapshot(request.request_id, state=state, session_id="t09")
            if snap.status is ExportJobState.READY:
                break
            time.sleep(0.01)
        else:
            raise AssertionError("READY not reached")
        internal = jobs._jobs[request.request_id].staged
        assert internal is not None
        internal.write_bytes(b"tampered")
        with pytest.raises(ExportJobError, match="POSTFLIGHT_STAGING_CHANGED"):
            jobs.accept(request.request_id, state=state, session_id="t09")
        assert not request.output_path.exists()
