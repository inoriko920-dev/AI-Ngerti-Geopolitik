"""T03 preflight negative boundaries, zero ProjectState mutation."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from ai_ngerti_geopolitik.application.export_capabilities import ExportToolchain
from ai_ngerti_geopolitik.application.export_preflight import ExportPreflightCode as Code
from ai_ngerti_geopolitik.application.export_preflight import (
    ExportPreflightService,
    OutputTargetInspection,
)
from ai_ngerti_geopolitik.application.export_request import (
    ExportCodec,
    ExportFrameRange,
    ExportRequest,
    ExportScope,
    ExportSharpen,
)
from ai_ngerti_geopolitik.application.validation import (
    MediaIntegrityObservation,
    MediaIntegrityStatus,
)
from ai_ngerti_geopolitik.domain import Asset, Clip, FrameTime, ProjectState, Track
from ai_ngerti_geopolitik.infrastructure.export_output_inspector import (
    LocalExportOutputInspector,
)


class MediaInspector:
    def __init__(self, status: MediaIntegrityStatus = MediaIntegrityStatus.OK) -> None:
        self.status = status

    def inspect(self, _path: Path) -> MediaIntegrityObservation:
        if self.status is MediaIntegrityStatus.OK:
            return MediaIntegrityObservation(
                MediaIntegrityStatus.OK,
                file_size=30,
                media_type="video",
                fingerprint_sha256="a" * 64,
            )
        return MediaIntegrityObservation(self.status)


class TargetInspector:
    def __init__(self, issue: Code | None = None) -> None:
        self.issue = issue
        self.calls = 0

    def inspect(
        self, output: Path, protected: tuple[Path, ...], min_bytes: int
    ) -> OutputTargetInspection:
        self.calls += 1
        assert output.suffix == ".mp4"
        assert min_bytes >= 256 * 1024 * 1024
        assert protected
        return OutputTargetInspection(self.issue)


TOOLS = ExportToolchain(True, True, True, False, True)


def _state(*, availability: str = "online") -> ProjectState:
    asset = Asset(
        "A001",
        "source.mp4",
        "video",
        FrameTime(90, 30),
        1920,
        1080,
        True,
        "a" * 64,
        availability=availability,
    )
    clip = Clip("C001", "A001", FrameTime(0, 30), FrameTime(0, 30), FrameTime(90, 30))
    return replace(
        ProjectState.create("P001", "Preflight"),
        assets=(asset,),
        tracks=(Track("V1", "video", 0, (clip,)),),
    )


def _request(state: ProjectState, root: Path, **options: object) -> ExportRequest:
    params: dict[str, object] = {
        "session_id": "session-1",
        "request_id": "request-1",
        "output_path": root / "final.mp4",
    }
    params.update(options)
    return ExportRequest.for_project(state, **params)


def test_precheck_pass_is_not_render_permission(tmp_path: Path) -> None:
    state = _state()
    before = state.semantic_json(include_revision=True)
    target = TargetInspector()
    request = _request(state, tmp_path)
    result = ExportPreflightService(MediaInspector(), target).check(
        state, request, "session-1", TOOLS
    )
    assert result.precheck_pass
    assert not result.can_start_render
    assert result.failure_codes == ()
    assert target.calls == 1
    assert state.semantic_json(include_revision=True) == before


@pytest.mark.parametrize(
    ("status", "issue"),
    [
        (MediaIntegrityStatus.MISSING, Code.INVALID_MEDIA),
        (MediaIntegrityStatus.ZERO_BYTE, Code.INVALID_MEDIA),
        (MediaIntegrityStatus.PROBE_FAILED, Code.INVALID_MEDIA),
    ],
)
def test_referenced_media_invalid_fail_closed(
    tmp_path: Path, status: MediaIntegrityStatus, issue: Code
) -> None:
    state = _state()
    result = ExportPreflightService(MediaInspector(status), TargetInspector()).check(
        state, _request(state, tmp_path), "session-1", TOOLS
    )
    assert issue in result.failure_codes


def test_stale_revision_and_semantic_swap_rejected(tmp_path: Path) -> None:
    state = _state()
    request = _request(state, tmp_path)
    service = ExportPreflightService(MediaInspector(), TargetInspector())
    for changed, session in (
        (state.with_revision(2), "session-1"),
        (replace(state, name="swap"), "session-1"),
        (state, "another-session"),
    ):
        result = service.check(changed, request, session, TOOLS)
        assert result.failure_codes == (Code.STALE_REQUEST,)


def test_missing_native_encoder(tmp_path: Path) -> None:
    state = _state()
    result = ExportPreflightService(MediaInspector(), TargetInspector()).check(
        state, _request(state, tmp_path), "session-1", ExportToolchain()
    )
    assert Code.ENCODER_UNAVAILABLE in result.failure_codes
    assert not result.can_start_render


@pytest.mark.parametrize(
    "options",
    [
        {"codec": ExportCodec.H265},
        {"width": 3840, "height": 2160},
        {"fps": 60},
        {"sharpen": ExportSharpen.LIGHT},
    ],
)
def test_unqualified_profiles_rejected(tmp_path: Path, options: dict[str, object]) -> None:
    state = _state()
    result = ExportPreflightService(MediaInspector(), TargetInspector()).check(
        state, _request(state, tmp_path, **options), "session-1", TOOLS
    )
    assert Code.UNSUPPORTED_PROFILE in result.failure_codes


def test_selection_remains_unqualified(tmp_path: Path) -> None:
    state = _state()
    result = ExportPreflightService(MediaInspector(), TargetInspector()).check(
        state,
        _request(state, tmp_path, scope=ExportScope.SELECTION, selection=ExportFrameRange(20, 80)),
        "session-1",
        TOOLS,
    )
    assert Code.SELECTION_NOT_QUALIFIED in result.failure_codes


@pytest.mark.parametrize(
    "issue",
    [
        Code.OUTPUT_COLLISION,
        Code.OUTPUT_EXISTS,
        Code.OUTPUT_PARENT_INVALID,
        Code.OUTPUT_NOT_WRITABLE,
        Code.INSUFFICIENT_DISK,
    ],
)
def test_output_inspection_failure_is_returned(tmp_path: Path, issue: Code) -> None:
    state = _state()
    result = ExportPreflightService(MediaInspector(), TargetInspector(issue)).check(
        state, _request(state, tmp_path), "session-1", TOOLS
    )
    assert issue in result.failure_codes


def test_local_target_never_overwrites_existing(tmp_path: Path) -> None:
    output = tmp_path / "final.mp4"
    output.write_bytes(b"existing")
    result = LocalExportOutputInspector().inspect(output, (), 1)
    assert result.issue is Code.OUTPUT_EXISTS
    assert output.read_bytes() == b"existing"


def test_local_target_rejects_source_collision(tmp_path: Path) -> None:
    source = tmp_path / "source.mp4"
    source.write_bytes(b"keep")
    result = LocalExportOutputInspector().inspect(source, (source,), 1)
    assert result.issue is Code.OUTPUT_COLLISION
    assert source.read_bytes() == b"keep"


def test_local_target_no_stray_probe_files(tmp_path: Path) -> None:
    output = tmp_path / "new.mp4"
    before = set(tmp_path.iterdir())
    result = LocalExportOutputInspector().inspect(output, (), 1)
    assert result.issue is None
    assert set(tmp_path.iterdir()) == before


def test_local_target_handles_missing_directory(tmp_path: Path) -> None:
    output = tmp_path / "missing" / "new.mp4"
    result = LocalExportOutputInspector().inspect(output, (), 1)
    assert result.issue is Code.OUTPUT_PARENT_INVALID


def test_validation_failure_no_sensitive_exception(tmp_path: Path) -> None:
    class BrokenMedia:
        def inspect(self, _path: Path) -> MediaIntegrityObservation:
            raise RuntimeError("SECRET /private/file")

    state = _state()
    result = ExportPreflightService(BrokenMedia(), TargetInspector()).check(
        state, _request(state, tmp_path), "session-1", TOOLS
    )
    assert result.failure_codes == (Code.VALIDATION_UNAVAILABLE,)
    assert "SECRET" not in str(result)


def test_missing_project_timeline_blocks(tmp_path: Path) -> None:
    state = ProjectState.create("P001", "Empty")
    request = _request(state, tmp_path)
    result = ExportPreflightService(MediaInspector(), TargetInspector()).check(
        state, request, "session-1", TOOLS
    )
    assert Code.EMPTY_TIMELINE in result.failure_codes


def test_real_target_disk_margin_is_enforced(tmp_path: Path, monkeypatch) -> None:
    class LowDisk:
        free = 0

    monkeypatch.setattr(
        "ai_ngerti_geopolitik.infrastructure.export_output_inspector.shutil.disk_usage",
        lambda _path: LowDisk(),
    )
    before = set(tmp_path.iterdir())
    result = LocalExportOutputInspector().inspect(tmp_path / "new.mp4", (), 256 * 1024 * 1024)
    assert result.issue is Code.INSUFFICIENT_DISK
    assert set(tmp_path.iterdir()) == before


def test_real_target_permission_failure_is_redacted(tmp_path: Path, monkeypatch) -> None:
    def reject(**_kwargs: object) -> None:
        raise PermissionError("private machine directory")

    monkeypatch.setattr(
        "ai_ngerti_geopolitik.infrastructure.export_output_inspector.tempfile.NamedTemporaryFile",
        reject,
    )
    result = LocalExportOutputInspector().inspect(tmp_path / "new.mp4", (), 1)
    assert result.issue is Code.OUTPUT_NOT_WRITABLE
    assert "private" not in str(result)
    assert not list(tmp_path.iterdir())


def test_unreferenced_missing_media_is_not_export_blocker(tmp_path: Path) -> None:
    state = _state()
    extra = Asset(
        "A002",
        "unused.mp4",
        "video",
        FrameTime(90, 30),
        1920,
        1080,
        True,
        "a" * 64,
        availability="missing",
    )
    state = replace(state, assets=(*state.assets, extra))
    result = ExportPreflightService(MediaInspector(), TargetInspector()).check(
        state, _request(state, tmp_path), "session-1", TOOLS
    )
    assert result.precheck_pass
    assert not result.can_start_render


def test_target_directory_probe_failure_is_safe(tmp_path: Path, monkeypatch) -> None:
    def deny(_path: Path) -> None:
        raise OSError("private drive identifier")

    monkeypatch.setattr(
        "ai_ngerti_geopolitik.infrastructure.export_output_inspector.shutil.disk_usage",
        deny,
    )
    result = LocalExportOutputInspector().inspect(tmp_path / "new.mp4", (), 1)
    assert result.issue is Code.OUTPUT_NOT_WRITABLE
    assert "private" not in str(result)
