"""SF12-T05 selection frame accuracy and no-clobber contracts."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from ai_ngerti_geopolitik.application.export_capabilities import ExportToolchain
from ai_ngerti_geopolitik.application.export_preflight import ExportPreflightService
from ai_ngerti_geopolitik.application.export_request import (
    ExportContractError,
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
            file_size=2,
            media_type="video",
            fingerprint_sha256="a" * 64,
        )


class FakeProbe:
    def __init__(self, *, wrong_frames: bool = False) -> None:
        self.wrong_frames = wrong_frames

    def probe(self, path: Path) -> ProbeResult:
        return ProbeResult(path, 120, 30, 1920, 1080, True, "b" * 64)

    def raw_probe(self, path: Path) -> dict[str, object]:
        frames = 120 if path.name.startswith("composed") else 30
        if self.wrong_frames and path.name.startswith("selection"):
            frames += 1
        return {
            "streams": [
                {
                    "codec_type": "video",
                    "codec_name": "h264",
                    "width": 1920,
                    "height": 1080,
                    "avg_frame_rate": "30/1",
                    "nb_frames": str(frames),
                },
                {"codec_type": "audio", "codec_name": "aac"},
            ],
            "format": {"format_name": "mov,mp4,m4a,3gp,3g2,mj2", "duration": str(frames / 30)},
        }


class FakeRunner:
    def __init__(self, *, fail_on: int = 0, cancel_on: int = 0) -> None:
        self.calls: list[list[str]] = []
        self.fail_on = fail_on
        self.cancel_on = cancel_on

    def run(self, argv: list[str], cancellation: object = None) -> ProcessResult:
        self.calls.append(argv)
        Path(argv[-1]).write_bytes(b"synthetic output")
        if len(self.calls) == self.fail_on:
            raise MediaToolError("RENDER_FAILED")
        if len(self.calls) == self.cancel_on:
            raise MediaOperationCancelled("CANCELLED")
        return ProcessResult("", "")


TOOLS = ExportToolchain(True, True, True, False, True)


def _case(tmp_path: Path, start: int = 45, end: int = 75) -> tuple[ProjectState, ExportRequest]:
    source = tmp_path / "source.mp4"
    source.write_bytes(b"original")
    asset = Asset(
        "A001",
        str(source),
        "video",
        FrameTime(120, 30),
        1920,
        1080,
        True,
        "a" * 64,
    )
    clips = (
        Clip("C001", "A001", FrameTime(0, 30), FrameTime(0, 30), FrameTime(60, 30)),
        Clip("C002", "A001", FrameTime(60, 30), FrameTime(60, 30), FrameTime(120, 30)),
    )
    state = replace(
        ProjectState.create("P001", "Selection"),
        assets=(asset,),
        tracks=(Track("V1", "video", 0, clips),),
    )
    request = ExportRequest.for_project(
        state,
        session_id="session-1",
        request_id="range-1",
        output_path=tmp_path / "selected.mp4",
        scope=ExportScope.SELECTION,
        selection=ExportFrameRange(start, end),
    )
    return state, request


def _export(
    state: ProjectState,
    request: ExportRequest,
    runner: FakeRunner,
    *,
    probe: FakeProbe | None = None,
    cancellation: MutableCancellationToken | None = None,
) -> object:
    engine = FfmpegSliceMediaEngine(probe or FakeProbe(), ffmpeg="fake-ffmpeg", runner=runner)
    return engine.export_h264_selection(
        state,
        request,
        session_id="session-1",
        media_inspector=FakeIntegrity(),
        target_inspector=LocalExportOutputInspector(),
        toolchain=TOOLS,
        cancellation=cancellation,
    )


@pytest.mark.parametrize(("start", "end"), [(0, 30), (45, 75), (90, 120)])
def test_frame_range_filter_is_exact_and_audio_is_rebased(
    tmp_path: Path, start: int, end: int
) -> None:
    state, request = _case(tmp_path, start, end)
    runner = FakeRunner()
    before = state.semantic_json(include_revision=True)
    result = _export(state, request, runner)
    assert result.duration_frames == end - start
    assert result.output_path == request.output_path
    assert request.output_path.is_file()
    assert len(runner.calls) == 2
    ffmpeg = runner.calls[1]
    graph = ffmpeg[ffmpeg.index("-filter_complex") + 1]
    assert f"trim=start_frame={start}:end_frame={end}" in graph
    assert f"atrim=start={start / 30:.6f}:end={end / 30:.6f}" in graph
    assert graph.count("PTS-STARTPTS") == 2
    assert ffmpeg[ffmpeg.index("-frames:v") + 1] == str(end - start)
    assert state.semantic_json(include_revision=True) == before
    assert (tmp_path / "source.mp4").read_bytes() == b"original"
    assert not list(tmp_path.glob(".ang-range-*"))


def test_default_t03_preflight_still_rejects_selection(tmp_path: Path) -> None:
    state, request = _case(tmp_path)
    preflight = ExportPreflightService(FakeIntegrity(), LocalExportOutputInspector())
    result = preflight.check(state, request, "session-1", TOOLS)
    assert not result.precheck_pass
    assert "SELECTION_NOT_QUALIFIED" in tuple(code.value for code in result.failure_codes)
    assert not result.can_start_render


@pytest.mark.parametrize(("start", "end"), [(0, 0), (30, 30), (50, 40), (-1, 4), (90, 121)])
def test_outside_and_empty_ranges_rejected(tmp_path: Path, start: int, end: int) -> None:
    state, _ = _case(tmp_path)
    with pytest.raises(ExportContractError):
        ExportRequest.for_project(
            state,
            session_id="session-1",
            request_id="invalid",
            output_path=tmp_path / "bad.mp4",
            scope=ExportScope.SELECTION,
            selection=ExportFrameRange(start, end),
        )


def test_wrong_selected_nb_frames_never_published(tmp_path: Path) -> None:
    state, request = _case(tmp_path)
    with pytest.raises(MediaToolError, match="EXPORT_BASELINE_STREAM_VERIFICATION_FAILED"):
        _export(state, request, FakeRunner(), probe=FakeProbe(wrong_frames=True))
    assert not request.output_path.exists()
    assert not list(tmp_path.glob(".ang-range-*"))


@pytest.mark.parametrize("fail_on", [1, 2])
def test_render_error_cleans_every_intermediate(tmp_path: Path, fail_on: int) -> None:
    state, request = _case(tmp_path)
    with pytest.raises(MediaToolError):
        _export(state, request, FakeRunner(fail_on=fail_on))
    assert not request.output_path.exists()
    assert not list(tmp_path.glob(".ang-range-*"))


def test_cancellation_after_full_render_cleans_intermediate(tmp_path: Path) -> None:
    state, request = _case(tmp_path)
    with pytest.raises(MediaOperationCancelled):
        _export(state, request, FakeRunner(cancel_on=2))
    assert not request.output_path.exists()
    assert not list(tmp_path.glob(".ang-range-*"))


def test_existing_final_rejected_before_render(tmp_path: Path) -> None:
    state, request = _case(tmp_path)
    request.output_path.write_bytes(b"keep")
    runner = FakeRunner()
    with pytest.raises(MediaToolError, match="OUTPUT_EXISTS"):
        _export(state, request, runner)
    assert not runner.calls
    assert request.output_path.read_bytes() == b"keep"


def test_full_request_never_enters_selection_path(tmp_path: Path) -> None:
    state, _ = _case(tmp_path)
    request = ExportRequest.for_project(
        state,
        session_id="session-1",
        request_id="full",
        output_path=tmp_path / "full.mp4",
    )
    runner = FakeRunner()
    with pytest.raises(MediaToolError, match="EXPORT_SELECTION_REQUIRED"):
        _export(state, request, runner)
    assert not runner.calls
