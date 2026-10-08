"""T04 additive pipeline negative boundaries (fake FFmpeg runner, no codec claims)."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from ai_ngerti_geopolitik.application.export_capabilities import ExportToolchain
from ai_ngerti_geopolitik.application.export_request import ExportCodec, ExportRequest
from ai_ngerti_geopolitik.application.ports import ProbeResult
from ai_ngerti_geopolitik.application.validation import (
    MediaIntegrityObservation,
    MediaIntegrityStatus,
)
from ai_ngerti_geopolitik.domain import Asset, Clip, FrameTime, ProjectState, Track
from ai_ngerti_geopolitik.infrastructure.export_output_inspector import (
    LocalExportOutputInspector,
)
from ai_ngerti_geopolitik.infrastructure.ffmpeg_slice import (
    FfmpegSliceMediaEngine,
    MediaOperationCancelled,
    MediaToolError,
    MutableCancellationToken,
    ProcessResult,
)


class FakeMediaInspector:
    def inspect(self, _path: Path) -> MediaIntegrityObservation:
        return MediaIntegrityObservation(
            MediaIntegrityStatus.OK,
            file_size=42,
            media_type="video",
            fingerprint_sha256="a" * 64,
        )


class FakeProbe:
    def __init__(self, *, codec: str = "h264", audio: str = "aac", fps: str = "30/1") -> None:
        self.codec, self.audio, self.fps = codec, audio, fps

    def probe(self, path: Path) -> ProbeResult:
        return ProbeResult(path, 30, 30, 1920, 1080, True, "b" * 64)

    def raw_probe(self, path: Path) -> dict[str, object]:
        return {
            "streams": [
                {
                    "codec_type": "video",
                    "codec_name": self.codec,
                    "width": 1920,
                    "height": 1080,
                    "avg_frame_rate": self.fps,
                },
                {"codec_type": "audio", "codec_name": self.audio},
            ],
            "format": {"format_name": "mov,mp4,m4a,3gp,3g2,mj2", "duration": "1.0"},
        }


class FakeRunner:
    def __init__(self, *, fail: bool = False, cancel: bool = False) -> None:
        self.fail = fail
        self.cancel = cancel
        self.calls = 0

    def run(self, argv: list[str], cancellation: object = None) -> ProcessResult:
        self.calls += 1
        Path(argv[-1]).write_bytes(b"synthetic MP4 placeholder")
        if self.fail:
            raise MediaToolError("synthetic fail")
        if self.cancel:
            raise MediaOperationCancelled("synthetic cancel")
        return ProcessResult("", "")


TOOLS = ExportToolchain(True, True, True, False, True)


def _setup(tmp_path: Path) -> tuple[ProjectState, ExportRequest]:
    source = tmp_path / "source.mp4"
    source.write_bytes(b"synthetic")
    asset = Asset("A001", str(source), "video", FrameTime(30, 30), 1920, 1080, True, "a" * 64)
    clip = Clip("C001", "A001", FrameTime(0, 30), FrameTime(0, 30), FrameTime(30, 30))
    state = replace(
        ProjectState.create("P001", "Export"),
        assets=(asset,),
        tracks=(Track("V1", "video", 0, (clip,)),),
    )
    request = ExportRequest.for_project(
        state, session_id="session-1", request_id="request-1", output_path=tmp_path / "final.mp4"
    )
    return state, request


def _run(
    state: ProjectState,
    request: ExportRequest,
    probe: FakeProbe,
    runner: FakeRunner,
) -> object:
    engine = FfmpegSliceMediaEngine(probe, ffmpeg="fake-ffmpeg", runner=runner)
    return engine.export_h264_baseline(
        state,
        request,
        session_id="session-1",
        media_inspector=FakeMediaInspector(),
        target_inspector=LocalExportOutputInspector(),
        toolchain=TOOLS,
    )


def test_staged_export_publishes_once_without_touching_source(tmp_path: Path) -> None:
    state, request = _setup(tmp_path)
    before = state.semantic_json(include_revision=True)
    source_bytes = (tmp_path / "source.mp4").read_bytes()
    runner = FakeRunner()
    result = _run(state, request, FakeProbe(), runner)
    assert result.output_path == request.output_path
    assert request.output_path.read_bytes() == b"synthetic MP4 placeholder"
    assert runner.calls == 1
    assert (tmp_path / "source.mp4").read_bytes() == source_bytes
    assert state.semantic_json(include_revision=True) == before
    assert not list(tmp_path.glob(".ang-h264-*"))
    with pytest.raises(MediaToolError, match="OUTPUT_EXISTS"):
        _run(state, request, FakeProbe(), runner)
    assert runner.calls == 1


@pytest.mark.parametrize(
    ("codec", "audio", "fps"),
    [
        ("hevc", "aac", "30/1"),
        ("h264", "mp3", "30/1"),
        ("h264", "aac", "60/1"),
    ],
)
def test_wrong_output_stream_never_publishes(
    tmp_path: Path, codec: str, audio: str, fps: str
) -> None:
    state, request = _setup(tmp_path)
    runner = FakeRunner()
    with pytest.raises(MediaToolError, match="EXPORT_BASELINE_STREAM_VERIFICATION_FAILED"):
        _run(state, request, FakeProbe(codec=codec, audio=audio, fps=fps), runner)
    assert not request.output_path.exists()
    assert not list(tmp_path.glob(".ang-h264-*"))


@pytest.mark.parametrize(("fail", "cancel"), [(True, False), (False, True)])
def test_renderer_fail_or_cancel_leaves_no_publication(
    tmp_path: Path, fail: bool, cancel: bool
) -> None:
    state, request = _setup(tmp_path)
    with pytest.raises(MediaToolError):
        _run(state, request, FakeProbe(), FakeRunner(fail=fail, cancel=cancel))
    assert not request.output_path.exists()
    assert not list(tmp_path.glob(".ang-h264-*"))


def test_input_source_collision_rejected_before_process(tmp_path: Path) -> None:
    state, _request = _setup(tmp_path)
    source = tmp_path / "source.mp4"
    request = ExportRequest.for_project(
        state, session_id="session-1", request_id="collision", output_path=source
    )
    runner = FakeRunner()
    with pytest.raises(MediaToolError, match="OUTPUT_COLLISION"):
        _run(state, request, FakeProbe(), runner)
    assert runner.calls == 0
    assert source.read_bytes() == b"synthetic"


def test_unqualified_codec_rejected_before_process(tmp_path: Path) -> None:
    state, _request = _setup(tmp_path)
    request = ExportRequest.for_project(
        state,
        session_id="session-1",
        request_id="hevc",
        output_path=tmp_path / "hevc.mp4",
        codec=ExportCodec.H265,
    )
    runner = FakeRunner()
    with pytest.raises(MediaToolError, match="UNSUPPORTED_PROFILE"):
        _run(state, request, FakeProbe(), runner)
    assert runner.calls == 0
    assert not request.output_path.exists()


def test_cancelled_before_start_does_not_write(tmp_path: Path) -> None:
    state, request = _setup(tmp_path)
    token = MutableCancellationToken()
    token.cancel()
    runner = FakeRunner()
    engine = FfmpegSliceMediaEngine(FakeProbe(), ffmpeg="fake", runner=runner)
    with pytest.raises(MediaOperationCancelled, match="EXPORT_CANCELLED"):
        engine.export_h264_baseline(
            state,
            request,
            session_id="session-1",
            media_inspector=FakeMediaInspector(),
            target_inspector=LocalExportOutputInspector(),
            toolchain=TOOLS,
            cancellation=token,
        )
    assert runner.calls == 0
    assert not request.output_path.exists()
