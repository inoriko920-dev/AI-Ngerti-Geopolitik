"""T07 fail-closed subtitle, sharpen and quality qualification contracts."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from ai_ngerti_geopolitik.application.export_capabilities import ExportToolchain
from ai_ngerti_geopolitik.application.export_preflight import (
    ExportPreflightCode,
    ExportPreflightService,
)
from ai_ngerti_geopolitik.application.export_request import (
    ExportAudio,
    ExportFrameRange,
    ExportQuality,
    ExportRequest,
    ExportScope,
    ExportSharpen,
    ExportSubtitles,
)
from ai_ngerti_geopolitik.application.export_style_policy import T07_STYLE_CANDIDATES
from ai_ngerti_geopolitik.application.ports import ProbeResult
from ai_ngerti_geopolitik.application.validation import (
    MediaIntegrityObservation,
    MediaIntegrityStatus,
)
from ai_ngerti_geopolitik.domain import (
    Asset,
    Clip,
    FrameTime,
    ProjectState,
    SubtitleCue,
    SubtitleTrack,
    Track,
)
from ai_ngerti_geopolitik.infrastructure.export_output_inspector import LocalExportOutputInspector
from ai_ngerti_geopolitik.infrastructure.ffmpeg_export_style import FfmpegStyleQualificationExporter
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
            file_size=50,
            media_type="video",
            fingerprint_sha256="a" * 64,
        )


class FakeProbe:
    def __init__(self, *, wrong_audio: bool = False, wrong_frames: bool = False) -> None:
        self.wrong_audio = wrong_audio
        self.wrong_frames = wrong_frames

    def probe(self, path: Path) -> ProbeResult:
        return ProbeResult(path, 30, 30, 1920, 1080, True, "b" * 64)

    def raw_probe(self, path: Path) -> dict[str, object]:
        frames = 30
        if path.name == "styled.mp4" and self.wrong_frames:
            frames = 31
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
                {
                    "codec_type": "audio",
                    "codec_name": "mp3"
                    if path.name == "styled.mp4" and self.wrong_audio
                    else "aac",
                },
            ],
            "format": {"format_name": "mov,mp4,m4a,3gp,3g2,mj2", "duration": str(frames / 30)},
        }


class FakeRunner:
    def __init__(self, *, fail_step: int = 0, cancel_step: int = 0) -> None:
        self.commands: list[list[str]] = []
        self.fail_step = fail_step
        self.cancel_step = cancel_step

    def run(self, command: list[str], cancellation: object = None) -> ProcessResult:
        self.commands.append(command)
        Path(command[-1]).write_bytes(b"fake sample")
        if len(self.commands) == self.fail_step:
            raise MediaToolError("SIMULATED_FAILURE")
        if len(self.commands) == self.cancel_step:
            raise MediaOperationCancelled("SIMULATED_CANCEL")
        return ProcessResult("", "")


TOOLS = ExportToolchain(True, True, True, False, True)


def _state(tmp_path: Path) -> ProjectState:
    source = tmp_path / "video.mp4"
    source.write_bytes(b"unaltered")
    asset = Asset("A001", str(source), "video", FrameTime(30, 30), 1920, 1080, True, "a" * 64)
    clip = Clip("C001", "A001", FrameTime(0, 30), FrameTime(0, 30), FrameTime(30, 30))
    subtitle = SubtitleTrack(
        source_ref="fixture",
        cues=(SubtitleCue("S001", 1, FrameTime(5, 30), FrameTime(25, 30), "KNOWN CUE"),),
    )
    return replace(
        ProjectState.create("P001", "T07"),
        assets=(asset,),
        tracks=(Track("V1", "video", 0, (clip,)),),
        subtitle=subtitle,
    )


def _request(
    state: ProjectState,
    tmp_path: Path,
    *,
    option: int = 0,
) -> ExportRequest:
    style = T07_STYLE_CANDIDATES[option]
    return ExportRequest.for_project(
        state,
        request_id="T07-" + str(option),
        session_id="T07-session",
        output_path=tmp_path / "final.mp4",
        quality=style.quality,
        sharpen=style.sharpen,
        subtitles=style.subtitles,
    )


def _run(
    state: ProjectState,
    request: ExportRequest,
    runner: FakeRunner,
    *,
    probe: FakeProbe | None = None,
    token: MutableCancellationToken | None = None,
) -> object:
    engine = FfmpegSliceMediaEngine(probe or FakeProbe(), ffmpeg="fake", runner=runner)
    return FfmpegStyleQualificationExporter(engine).export(
        state,
        request,
        session_id="T07-session",
        media_inspector=FakeIntegrity(),
        target_inspector=LocalExportOutputInspector(),
        toolchain=TOOLS,
        cancellation=token,
    )


@pytest.mark.parametrize("option", range(6))
def test_exact_styles_map_to_real_arguments_and_do_not_mutate(tmp_path: Path, option: int) -> None:
    state = _state(tmp_path)
    request = _request(state, tmp_path, option=option)
    before = state.semantic_json(include_revision=True)
    runner = FakeRunner()
    result = _run(state, request, runner)
    style = T07_STYLE_CANDIDATES[option]
    assert result.output_path == request.output_path
    assert result.duration_frames == 30
    assert len(runner.commands) == 2
    first, second = runner.commands
    graph = first[first.index("-filter_complex") + 1]
    assert ("drawtext=" in graph) == (style.subtitles is ExportSubtitles.BURN_IN)
    assert second[second.index("-vf") + 1] == style.video_filter
    assert second[second.index("-preset") + 1] == style.preset
    assert second[second.index("-crf") + 1] == str(style.crf)
    assert second[second.index("-c:a") + 1] == "aac"
    assert request.output_path.read_bytes() == b"fake sample"
    assert state.semantic_json(include_revision=True) == before
    assert (tmp_path / "video.mp4").read_bytes() == b"unaltered"
    assert not list(tmp_path.glob(".ang-t07-*"))


def test_default_preflight_still_rejects_style_options(tmp_path: Path) -> None:
    state = _state(tmp_path)
    request = _request(state, tmp_path, option=1)
    result = ExportPreflightService(FakeIntegrity(), LocalExportOutputInspector()).check(
        state, request, "T07-session", TOOLS
    )
    assert ExportPreflightCode.UNSUPPORTED_PROFILE in result.failure_codes
    assert not result.can_start_render


@pytest.mark.parametrize(
    "replacements",
    [
        {"quality": ExportQuality.DOCUMENTARY_CRISP, "sharpen": ExportSharpen.CRISP},
        {"sharpen": ExportSharpen.LIGHT, "subtitles": ExportSubtitles.OFF},
        {"audio": ExportAudio.OFF},
        {"scope": ExportScope.SELECTION, "selection": ExportFrameRange(0, 10)},
    ],
)
def test_non_allowlisted_combinations_fail_before_ffmpeg(
    tmp_path: Path, replacements: dict[str, object]
) -> None:
    state = _state(tmp_path)
    request = replace(_request(state, tmp_path), **replacements)
    runner = FakeRunner()
    with pytest.raises(MediaToolError, match="T07_STYLE_NOT_QUALIFIED"):
        _run(state, request, runner)
    assert not runner.commands


@pytest.mark.parametrize(("bad_audio", "bad_frames"), [(True, False), (False, True)])
def test_invalid_result_never_published(tmp_path: Path, bad_audio: bool, bad_frames: bool) -> None:
    state = _state(tmp_path)
    request = _request(state, tmp_path)
    with pytest.raises(MediaToolError, match="T07_STREAM_VERIFICATION_FAILED"):
        _run(
            state,
            request,
            FakeRunner(),
            probe=FakeProbe(wrong_audio=bad_audio, wrong_frames=bad_frames),
        )
    assert not request.output_path.exists()
    assert not list(tmp_path.glob(".ang-t07-*"))


@pytest.mark.parametrize("fail_step", [1, 2])
def test_failure_on_either_stage_leaves_no_output(tmp_path: Path, fail_step: int) -> None:
    state = _state(tmp_path)
    request = _request(state, tmp_path)
    with pytest.raises(MediaToolError):
        _run(state, request, FakeRunner(fail_step=fail_step))
    assert not request.output_path.exists()
    assert not list(tmp_path.glob(".ang-t07-*"))


def test_existing_output_is_immutable(tmp_path: Path) -> None:
    state = _state(tmp_path)
    request = _request(state, tmp_path)
    request.output_path.write_bytes(b"existing")
    runner = FakeRunner()
    with pytest.raises(MediaToolError, match="OUTPUT_EXISTS"):
        _run(state, request, runner)
    assert request.output_path.read_bytes() == b"existing"
    assert not runner.commands


def test_pre_cancelled_render_never_starts(tmp_path: Path) -> None:
    state = _state(tmp_path)
    request = _request(state, tmp_path)
    token = MutableCancellationToken()
    token.cancel()
    runner = FakeRunner()
    with pytest.raises(MediaOperationCancelled, match="T07_CANCELLED"):
        _run(state, request, runner, token=token)
    assert not runner.commands
    assert not request.output_path.exists()


def test_repeat_same_request_cannot_overwrite(tmp_path: Path) -> None:
    state = _state(tmp_path)
    request = _request(state, tmp_path)
    runner = FakeRunner()
    _run(state, request, runner)
    with pytest.raises(MediaToolError, match="OUTPUT_EXISTS"):
        _run(state, request, runner)
    assert len(runner.commands) == 2


def test_style_policy_has_only_six_unique_profiles() -> None:
    values = [(x.quality, x.sharpen, x.subtitles) for x in T07_STYLE_CANDIDATES]
    assert len(values) == len(set(values)) == 6
    assert (ExportQuality.DOCUMENTARY_CRISP, ExportSharpen.CRISP, ExportSubtitles.OFF) not in values
