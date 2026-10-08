from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest

from ai_ngerti_geopolitik.application.export_request import (
    ExportAudio,
    ExportCodec,
    ExportContractError,
    ExportFrameRange,
    ExportQuality,
    ExportRequest,
    ExportScope,
    ExportSharpen,
    ExportSubtitles,
)
from ai_ngerti_geopolitik.domain import Asset, Clip, FrameTime, ProjectState, Track


def _state() -> ProjectState:
    asset = Asset("A001", "source.mp4", "video", FrameTime(90, 30), 1920, 1080, True)
    clip = Clip("C001", "A001", FrameTime(0, 30), FrameTime(0, 30), FrameTime(90, 30))
    return replace(
        ProjectState.create("P001", "Export contracts"),
        assets=(asset,),
        tracks=(Track("V1", "video", 0, (clip,)),),
    )


def _request(tmp_path: Path, **overrides: object) -> ExportRequest:
    options: dict[str, object] = {
        "session_id": "session-1",
        "request_id": "request-1",
        "output_path": tmp_path / "final.mp4",
    }
    options.update(overrides)
    return ExportRequest.for_project(_state(), **options)


def test_frozen_snapshot_does_not_mutate_project(tmp_path: Path) -> None:
    state = _state()
    before = state.semantic_json(include_revision=True)
    request = ExportRequest.for_project(
        state, session_id="session-1", request_id="request-1", output_path=tmp_path / "final.mp4"
    )
    assert request.project_semantic_hash == state.semantic_hash()
    assert request.project_revision == state.revision
    assert request.scope is ExportScope.FULL
    assert request.codec is ExportCodec.H264
    assert state.semantic_json(include_revision=True) == before
    request.assert_current(state, "session-1")
    with pytest.raises(FrozenInstanceError):
        request.fps = 60  # type: ignore[misc]


def test_selection_half_open_bounds_and_identity(tmp_path: Path) -> None:
    request = _request(tmp_path, scope=ExportScope.SELECTION, selection=ExportFrameRange(30, 90))
    assert request.selection == ExportFrameRange(30, 90)
    request.assert_current(_state(), "session-1")
    with pytest.raises(ExportContractError, match="INVALID_SELECTION_BOUNDS"):
        _request(tmp_path, scope=ExportScope.SELECTION, selection=ExportFrameRange(0, 91))


@pytest.mark.parametrize("start,end", [(-1, 3), (3, 3), (5, 2), (True, 3), (0, False)])
def test_selection_invalid_bounds(start: int, end: int) -> None:
    with pytest.raises(ExportContractError, match="INVALID_FRAME_RANGE"):
        ExportFrameRange(start, end)


def test_selection_required_only_for_selected_mode(tmp_path: Path) -> None:
    with pytest.raises(ExportContractError, match="SELECTION_REQUIRED"):
        _request(tmp_path, scope=ExportScope.SELECTION)
    with pytest.raises(ExportContractError, match="SELECTION_NOT_ALLOWED"):
        _request(tmp_path, scope=ExportScope.FULL, selection=ExportFrameRange(0, 10))


@pytest.mark.parametrize("fps", [0, 24, 29, 61, True, "30"])
def test_reject_unqualified_fps(tmp_path: Path, fps: object) -> None:
    with pytest.raises(ExportContractError, match="INVALID_FPS"):
        _request(tmp_path, fps=fps)


@pytest.mark.parametrize("size", [(1920, 720), (1920, 1440), (True, 1080), (0, 0)])
def test_reject_unqualified_resolutions(tmp_path: Path, size: tuple[object, object]) -> None:
    with pytest.raises(ExportContractError, match="INVALID_RESOLUTION"):
        _request(tmp_path, width=size[0], height=size[1])


def test_explicit_enums_are_typed_not_free_form_ui_text(tmp_path: Path) -> None:
    for name, value in (
        ("scope", "selection"),
        ("codec", "h265"),
        ("quality", "high"),
        ("sharpen", "light"),
        ("subtitles", "off"),
        ("audio", "aac"),
    ):
        with pytest.raises(ExportContractError, match="INVALID_EXPORT_OPTION"):
            _request(tmp_path, **{name: value})


def test_supported_options_are_requests_not_capability_proofs(tmp_path: Path) -> None:
    request = _request(
        tmp_path,
        codec=ExportCodec.H265,
        width=3840,
        height=2160,
        fps=60,
        quality=ExportQuality.DOCUMENTARY_CRISP,
        sharpen=ExportSharpen.CRISP,
        subtitles=ExportSubtitles.OFF,
        audio=ExportAudio.OFF,
    )
    assert request.codec is ExportCodec.H265
    assert request.fps == 60
    assert request.subtitles is ExportSubtitles.OFF


@pytest.mark.parametrize(
    "path_fn",
    [
        lambda root: Path("relative.mp4"),
        lambda root: root / "video.avi",
        lambda root: root / "nested" / ".." / "file.mp4",
        lambda root: root / "unsafe\x00.mp4",
    ],
)
def test_unsafe_output_names_fail_closed(tmp_path: Path, path_fn: object) -> None:
    assert callable(path_fn)
    with pytest.raises(ExportContractError, match="INVALID_OUTPUT_PATH"):
        _request(tmp_path, output_path=path_fn(tmp_path))


def test_invalid_identity_revision_hash_are_safe(tmp_path: Path) -> None:
    request = _request(tmp_path)
    for changes, code in (
        ({"session_id": ""}, "INVALID_IDENTITY"),
        ({"project_revision": True}, "INVALID_REVISION"),
        ({"project_revision": -1}, "INVALID_REVISION"),
        ({"project_semantic_hash": "not-a-sha256"}, "INVALID_SEMANTIC_HASH"),
        ({"request_id": "bad\nrequest"}, "INVALID_IDENTITY"),
    ):
        with pytest.raises(ExportContractError, match=code):
            replace(request, **changes)


def test_stale_revision_same_revision_semantic_swap_and_session(tmp_path: Path) -> None:
    state = _state()
    request = _request(tmp_path)
    request.assert_current(state, "session-1")
    for altered, session in (
        (state.with_revision(1), "session-1"),
        (replace(state, name="different"), "session-1"),
        (replace(state, project_id="P-OTHER"), "session-1"),
        (state, "new-session"),
        (state, None),
    ):
        with pytest.raises(ExportContractError, match="STALE_EXPORT_REQUEST"):
            request.assert_current(altered, session)


def test_error_message_and_repr_do_not_leak_private_path(tmp_path: Path) -> None:
    secret_path = tmp_path / "Private Narration Name" / "out.mp4"
    request = _request(tmp_path, output_path=secret_path)
    assert str(secret_path) not in repr(request)
    with pytest.raises(ExportContractError) as error:
        replace(request, output_path=secret_path.with_suffix(".txt"))
    assert str(secret_path.parent) not in str(error.value)
