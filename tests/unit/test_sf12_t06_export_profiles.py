"""T06 matrix adapter: exact allowlist, safe publication and fail-closed verification."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from ai_ngerti_geopolitik.application.export_capabilities import ExportToolchain
from ai_ngerti_geopolitik.application.export_preflight import ExportPreflightCode, ExportPreflightService
from ai_ngerti_geopolitik.application.export_profiles import (
    T06_CANDIDATE_PROFILES,
    MatrixCell,
    candidate_for_request,
)
from ai_ngerti_geopolitik.application.export_request import (
    ExportCodec,
    ExportFrameRange,
    ExportRequest,
    ExportScope,
)
from ai_ngerti_geopolitik.application.ports import ProbeResult
from ai_ngerti_geopolitik.application.validation import (
    MediaIntegrityObservation,
    MediaIntegrityStatus,
)
from ai_ngerti_geopolitik.domain import Asset, Clip, FrameTime, ProjectState, Track
from ai_ngerti_geopolitik.infrastructure.export_output_inspector import LocalExportOutputInspector
from ai_ngerti_geopolitik.infrastructure.ffmpeg_export_profiles import FfmpegMatrixQualificationExporter
from ai_ngerti_geopolitik.infrastructure.ffmpeg_slice import (
    FfmpegSliceMediaEngine,
    MediaOperationCancelled,
    MediaToolError,
    MutableCancellationToken,
    ProcessResult,
)


class FakeIntegrity:
    def inspect(self, _path: Path) -> MediaIntegrityObservation:
        return MediaIntegrityObservation(
            MediaIntegrityStatus.OK,
            file_size=4,
            media_type="video",
            fingerprint_sha256="a" * 64,
        )


class FakeProbe:
    def __init__(self, *, incorrect_codec: bool = False, incorrect_frames: bool = False) -> None:
        self.incorrect_codec = incorrect_codec
        self.incorrect_frames = incorrect_frames

    def probe(self, path: Path) -> ProbeResult:
        return ProbeResult(path, 15, 30, 1920, 1080, True, "b" * 64)

    def raw_probe(self, path: Path) -> dict[str, object]:
        if path.name == "composed.mp4":
            width, height, fps, codec, frames = 1920, 1080, 30, "h264", 15
        else:
            # Parameters are supplied by tests through output filename suffix.
            profile = self.profile
            width, height, fps, codec = (
                profile.width,
                profile.height,
                profile.fps,
                profile.expected_decoder,
            )
            frames = 15 * fps // 30
            if self.incorrect_codec:
                codec = "mpeg4"
            if self.incorrect_frames:
                frames += 1
        return {
            "streams": [
                {
                    "codec_type": "video",
                    "codec_name": codec,
                    "width": width,
                    "height": height,
                    "avg_frame_rate": f"{fps}/1",
                    "nb_frames": str(frames),
                },
                {"codec_type": "audio", "codec_name": "aac"},
            ],
            "format": {"format_name": "mov,mp4,m4a,3gp,3g2,mj2", "duration": str(frames / fps)},
        }


class FakeRunner:
    def __init__(self, *, fail_step: int = 0, cancel_step: int = 0) -> None:
        self.calls: list[list[str]] = []
        self.fail_step = fail_step
        self.cancel_step = cancel_step
        self.write_competitor = False
        self.target: Path | None = None

    def run(self, argv: list[str], cancellation: object = None) -> ProcessResult:
        self.calls.append(argv)
        Path(argv[-1]).write_bytes(b"synthetic fixture")
        if len(self.calls) == self.fail_step:
            raise MediaToolError("simulated failed encoder")
        if len(self.calls) == self.cancel_step:
            raise MediaOperationCancelled("simulated cancel")
        return ProcessResult("", "")


TOOLS = ExportToolchain(True, True, True, True, True)


def _case(tmp_path: Path, *, cell: MatrixCell) -> tuple[ProjectState, ExportRequest]:
    (tmp_path / "source.mp4").write_bytes(b"unmodified source")
    asset = Asset(
        "A001",
        str(tmp_path / "source.mp4"),
        "video",
        FrameTime(15, 30),
        1920,
        1080,
        True,
        "a" * 64,
    )
    clip = Clip("C001", "A001", FrameTime(0, 30), FrameTime(0, 30), FrameTime(15, 30))
    state = replace(
        ProjectState.create("P001", "T06"),
        assets=(asset,),
        tracks=(Track("V1", "video", 0, (clip,)),),
    )
    p = next(x for x in T06_CANDIDATE_PROFILES if x.cell is cell)
    request = ExportRequest.for_project(
        state,
        session_id="session-t06",
        request_id="request-t06",
        output_path=tmp_path / "output.mp4",
        codec=p.codec,
        width=p.width,
        height=p.height,
        fps=p.fps,
    )
    return state, request


def _run(
    state: ProjectState,
    request: ExportRequest,
    runner: FakeRunner,
    *,
    probe: FakeProbe | None = None,
    toolchain: ExportToolchain = TOOLS,
    token: MutableCancellationToken | None = None,
) -> object:
    fake = probe or FakeProbe()
    profile = candidate_for_request(request)
    if profile is not None:
        fake.profile = profile
    engine = FfmpegSliceMediaEngine(fake, ffmpeg="fake", runner=runner)
    exporter = FfmpegMatrixQualificationExporter(engine)
    return exporter.export(
        state,
        request,
        session_id="session-t06",
        media_inspector=FakeIntegrity(),
        target_inspector=LocalExportOutputInspector(),
        toolchain=toolchain,
        cancellation=token,
    )


@pytest.mark.parametrize("cell", list(MatrixCell))
def test_four_explicit_cells_transcode_and_publish_without_mutation(
    tmp_path: Path, cell: MatrixCell
) -> None:
    state, request = _case(tmp_path, cell=cell)
    before = state.semantic_json(include_revision=True)
    runner = FakeRunner()
    result = _run(state, request, runner)
    profile = candidate_for_request(request)
    assert profile is not None
    assert (result.width, result.height, result.fps) == (
        request.width,
        request.height,
        request.fps,
    )
    assert result.duration_frames == 15 * request.fps // 30
    assert request.output_path.read_bytes() == b"synthetic fixture"
    assert len(runner.calls) == 2
    command = runner.calls[-1]
    assert command[command.index("-c:v") + 1] == profile.encoder
    assert command[command.index("-vf") + 1].startswith(
        f"scale={request.width}:{request.height}:flags=bicubic,"
    )
    assert command[command.index("-frames:v") + 1] == str(result.duration_frames)
    assert state.semantic_json(include_revision=True) == before
    assert (tmp_path / "source.mp4").read_bytes() == b"unmodified source"
    assert not list(tmp_path.glob(".ang-t06-*"))


def test_default_preflight_does_not_unlock_advanced_profiles(tmp_path: Path) -> None:
    state, request = _case(tmp_path, cell=MatrixCell.H265_1080P30)
    observed = ExportPreflightService(FakeIntegrity(), LocalExportOutputInspector()).check(
        state, request, "session-t06", TOOLS
    )
    assert ExportPreflightCode.UNSUPPORTED_PROFILE in observed.failure_codes
    assert observed.can_start_render is False


def test_unqualified_combination_is_rejected_even_with_encoders(tmp_path: Path) -> None:
    state, original = _case(tmp_path, cell=MatrixCell.H265_1080P30)
    request = replace(original, width=3840, height=2160, fps=60)
    runner = FakeRunner()
    with pytest.raises(MediaToolError, match="T06_PROFILE_NOT_QUALIFIED"):
        _run(state, request, runner)
    assert not runner.calls
    assert not request.output_path.exists()


def test_h265_missing_encoder_never_renders(tmp_path: Path) -> None:
    state, request = _case(tmp_path, cell=MatrixCell.H265_1080P30)
    runner = FakeRunner()
    with pytest.raises(MediaToolError, match="ENCODER_UNAVAILABLE"):
        _run(state, request, runner, toolchain=ExportToolchain(True, True, True, False, True))
    assert not runner.calls


@pytest.mark.parametrize(("bad_codec", "bad_frames"), [(True, False), (False, True)])
def test_mismatched_native_probe_is_never_published(
    tmp_path: Path, bad_codec: bool, bad_frames: bool
) -> None:
    state, request = _case(tmp_path, cell=MatrixCell.H264_1080P60)
    runner = FakeRunner()
    with pytest.raises(MediaToolError, match="T06_PROFILE_STREAM_VERIFICATION_FAILED"):
        _run(
            state,
            request,
            runner,
            probe=FakeProbe(incorrect_codec=bad_codec, incorrect_frames=bad_frames),
        )
    assert not request.output_path.exists()
    assert not list(tmp_path.glob(".ang-t06-*"))


@pytest.mark.parametrize("bad_step", [1, 2])
def test_transcode_error_does_not_leave_partial_or_final(
    tmp_path: Path, bad_step: int
) -> None:
    state, request = _case(tmp_path, cell=MatrixCell.H264_1440P30)
    runner = FakeRunner(fail_step=bad_step)
    with pytest.raises(MediaToolError):
        _run(state, request, runner)
    assert not request.output_path.exists()
    assert not list(tmp_path.glob(".ang-t06-*"))


def test_existing_destination_never_overwritten(tmp_path: Path) -> None:
    state, request = _case(tmp_path, cell=MatrixCell.H264_4K30)
    request.output_path.write_bytes(b"original output")
    runner = FakeRunner()
    with pytest.raises(MediaToolError, match="OUTPUT_EXISTS"):
        _run(state, request, runner)
    assert request.output_path.read_bytes() == b"original output"
    assert not runner.calls


def test_pre_cancelled_path_is_nonwriting(tmp_path: Path) -> None:
    state, request = _case(tmp_path, cell=MatrixCell.H264_1440P30)
    token = MutableCancellationToken()
    token.cancel()
    runner = FakeRunner()
    with pytest.raises(MediaOperationCancelled, match="T06_CANCELLED"):
        _run(state, request, runner, token=token)
    assert not runner.calls
    assert not request.output_path.exists()


def test_selection_not_misrouted_into_matrix(tmp_path: Path) -> None:
    state, request = _case(tmp_path, cell=MatrixCell.H264_1440P30)
    request = replace(
        request,
        scope=ExportScope.SELECTION,
        selection=ExportFrameRange(0, 10),
    )
    runner = FakeRunner()
    with pytest.raises(MediaToolError, match="T06_PROFILE_NOT_QUALIFIED"):
        _run(state, request, runner)
    assert not runner.calls
