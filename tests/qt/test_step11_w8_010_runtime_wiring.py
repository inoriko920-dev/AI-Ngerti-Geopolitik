"""W8-010 real UI-039/040/041 controller contract and GOLDEN-03 lifecycle."""

from __future__ import annotations

import hashlib
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QLabel, QListWidget, QPushButton, QTableWidget

from ai_ngerti_geopolitik.application.commands import AddClipCommand, CommandBatch
from ai_ngerti_geopolitik.application.media_import import MediaImportService
from ai_ngerti_geopolitik.application.ports import ProbeResult
from ai_ngerti_geopolitik.application.project_session import ProjectSession
from ai_ngerti_geopolitik.application.recovery import RecoveryChoice
from ai_ngerti_geopolitik.application.relink_scan import RelinkScanJobService, ScanState
from ai_ngerti_geopolitik.application.ui_intents import UiIntent, UiIntentType
from ai_ngerti_geopolitik.application.validation import (
    RealMediaIntegrityRule,
    ValidationService,
)
from ai_ngerti_geopolitik.bootstrap.w8_controller import (
    W8IntentRouter,
    W8RuntimeController,
)
from ai_ngerti_geopolitik.domain import Clip, FrameTime, ProjectState
from ai_ngerti_geopolitik.infrastructure.media_integrity import LocalMediaIntegrityInspector
from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository
from ai_ngerti_geopolitik.infrastructure.relink_scan import LocalRelinkDirectoryScanner
from ai_ngerti_geopolitik.presentation.main_window import create_main_window


class OwnedProbe:
    def probe(self, path: Path) -> ProbeResult:
        data = path.read_bytes()
        return ProbeResult(
            path.resolve(),
            120,
            30,
            1920,
            1080,
            True,
            hashlib.sha256(data).hexdigest(),
            "video",
            4.0,
            len(data),
            48000,
        )


def setup(qtbot, repo: JsonProjectRepository | None = None, *, initial_route: str = "UI-010"):
    router = W8IntentRouter()
    window = create_main_window(initial_route, fixture_mode=True, intent_sink=router)
    qtbot.addWidget(window.window)
    probe = OwnedProbe()
    session = ProjectSession(repo or JsonProjectRepository())
    controller = W8RuntimeController(
        window,
        session=session,
        validation=ValidationService(
            (RealMediaIntegrityRule(LocalMediaIntegrityInspector(probe)),)
        ),
        relink=RelinkScanJobService(LocalRelinkDirectoryScanner(), probe),
        timer_enabled=False,
    )
    router.delegate = controller.handle
    window.show()
    return controller, router


def pump(qtbot, predicate, controller: W8RuntimeController) -> None:
    def update() -> bool:
        controller.poll()
        return bool(predicate())

    qtbot.waitUntil(update, timeout=8000)


def saved_project(tmp_path: Path):
    repo = JsonProjectRepository()
    path = tmp_path / "original.angproj"
    video = tmp_path / "original.mp4"
    video.write_bytes(b"owned deterministic sample media bytes")
    session = ProjectSession(repo)
    session.new_project("P-W8-010", "UI real data", 30)
    asset = MediaImportService(OwnedProbe()).import_path(session, video)
    session.execute(
        CommandBatch(
            "W8-010-ADD-CLIP",
            "Place asset",
            "manual",
            session.state.revision,
            (
                AddClipCommand(
                    Clip("C001", asset, FrameTime(0, 30), FrameTime(0, 30), FrameTime(120, 30))
                ),
            ),
        )
    )
    session.save(path)
    return repo, path, video, asset


def test_frozen_ui041_shows_real_blocker_after_file_deleted(qtbot, tmp_path: Path) -> None:
    repo, project, media, _asset = saved_project(tmp_path)
    controller, router = setup(qtbot, repo)
    controller.request_open(project)
    pump(
        qtbot,
        lambda: controller.session.is_open and controller.validation_job_id is None,
        controller,
    )
    media.unlink()
    controller.request_validation()
    pump(qtbot, lambda: controller.validation_job_id is None, controller)
    dialog = controller.window._active_dialog
    assert isinstance(dialog, QDialog)
    assert dialog.objectName() == "dlg_validation_center"
    label = dialog.findChild(QLabel, "label_validation_summary")
    assert label is not None and "Error" in label.text()
    assert "0 Error" not in label.text()
    relink = dialog.findChild(QPushButton, "btn_validation_issue_0_0_action")
    assert relink is not None and relink.isEnabled()
    qtbot.mouseClick(relink, Qt.MouseButton.LeftButton)
    assert controller.window._active_dialog.objectName() == "dlg_asset_scan"
    controller.shutdown()
    controller.window.close()


def test_golden03_missing_scan_manual_relink_validate_and_save(qtbot, tmp_path: Path) -> None:
    repo, project, media, asset = saved_project(tmp_path)
    controller, router = setup(qtbot, repo)
    controller.request_open(project)
    pump(
        qtbot,
        lambda: controller.session.is_open and controller.validation_job_id is None,
        controller,
    )
    source_bytes = project.read_bytes()
    candidate_dir = tmp_path / "recovery"
    candidate_dir.mkdir()
    candidate = candidate_dir / "renamed.mp4"
    media.rename(candidate)
    controller.request_validation()
    pump(qtbot, lambda: controller.validation_job_id is None, controller)
    blocker = controller.window._active_dialog.findChild(
        QPushButton, "btn_validation_issue_0_0_action"
    )
    assert blocker is not None and blocker.isEnabled()
    qtbot.mouseClick(blocker, Qt.MouseButton.LeftButton)
    assert controller.window._active_dialog.objectName() == "dlg_asset_scan"
    controller.handle(UiIntent(UiIntentType.ASSET_SCAN_START, (("root", str(candidate_dir)),)))
    pump(
        qtbot,
        lambda: (
            controller.scan_job_id is not None
            and controller.relink.snapshot(
                controller.scan_job_id,
                state=controller.session.state,
                session_id=controller.session_id,
            ).state
            is ScanState.SUCCESS
        ),
        controller,
    )
    controller.poll()
    table = controller.window._active_dialog.findChild(QTableWidget, "table_asset_scan_candidates")
    apply = controller.window._active_dialog.findChild(QPushButton, "btn_asset_scan_apply")
    assert table is not None and table.rowCount() == 1
    assert apply is not None and apply.isEnabled()
    assert controller.session.state.asset(asset).availability == "missing"
    # Merely finding a candidate must not alter canonical media identity.
    assert controller.session.state.asset(asset).path_ref == str(media.resolve())
    item = table.item(0, 0)
    assert item is not None
    item.setCheckState(Qt.CheckState.Checked)
    qtbot.mouseClick(apply, Qt.MouseButton.LeftButton)
    pump(qtbot, lambda: controller.validation_job_id is None, controller)
    summary = controller.window._active_dialog.findChild(QLabel, "label_validation_summary")
    assert summary is not None and "0 Error" in summary.text()
    assert controller.session.state.asset(asset).path_ref == str(candidate.resolve())
    assert controller.session.state.asset(asset).asset_id == asset
    assert controller.session.dirty
    assert project.read_bytes() == source_bytes
    updated_hash = controller.session.state.semantic_hash()
    controller.handle(UiIntent(UiIntentType.SAVE_PROJECT))
    assert not controller.session.dirty
    assert repo.load(project).semantic_hash() == updated_hash
    assert controller.session.undo().semantic_hash() != updated_hash
    assert controller.session.redo().semantic_hash() == updated_hash
    controller.shutdown()
    controller.window.close()


def test_ui039_shows_recover_ignore_and_source_is_never_overwritten(qtbot, tmp_path: Path) -> None:
    repo, project, _media, _asset = saved_project(tmp_path)
    first, _router = setup(qtbot, repo)
    first.request_open(project)
    pump(qtbot, lambda: first.session.is_open and first.validation_job_id is None, first)
    original = project.read_bytes()
    newer = first.session.state.with_revision(first.session.state.revision + 5)
    snapshot = first.session.autosave_catalog.create_snapshot(
        newer, project.parent / ".ang-autosave", source_path=project
    )
    # Dirty session => shutdown deliberately does NOT declare the marker clean.
    first.session.recover_snapshot(project, snapshot, discard_unsaved=True)
    assert first.session.dirty
    first.shutdown()
    first.window.close()

    second, router = setup(qtbot, repo)
    second.request_open(project)
    pump(qtbot, lambda: second.offer is not None, second)
    assert second.window._active_dialog.objectName() == "dlg_recovery"
    listbox = second.window._active_dialog.findChild(QListWidget, "list_recovery_candidates")
    assert listbox is not None and listbox.count() == 1
    ignore = second.window._active_dialog.findChild(QPushButton, "btn_recovery_ignore")
    assert ignore is not None
    qtbot.mouseClick(ignore, Qt.MouseButton.LeftButton)
    assert not second.session.is_open
    assert project.read_bytes() == original
    second.request_open(project)
    pump(qtbot, lambda: second.offer is not None, second)
    listbox = second.window._active_dialog.findChild(QListWidget, "list_recovery_candidates")
    assert listbox is not None
    listbox.setCurrentRow(0)
    restore = second.window._active_dialog.findChild(QPushButton, "btn_recovery_restore")
    assert restore is not None and restore.isEnabled()
    qtbot.mouseClick(restore, Qt.MouseButton.LeftButton)
    assert second.session.is_open
    assert second.session.dirty
    assert second.session.current_path == project
    assert project.read_bytes() == original
    second.shutdown()
    second.window.close()


def test_scan_cancel_blocks_late_manual_apply(qtbot, tmp_path: Path) -> None:
    repo, project, media, asset = saved_project(tmp_path)
    controller, router = setup(qtbot, repo)
    controller.request_open(project)
    pump(
        qtbot,
        lambda: controller.session.is_open and controller.validation_job_id is None,
        controller,
    )
    media.rename(tmp_path / "renamed.mp4")
    controller.show_asset_scan()
    controller.start_scan(tmp_path)
    job = controller.scan_job_id
    assert job is not None
    controller.handle(UiIntent(UiIntentType.ASSET_SCAN_CANCEL))
    controller.handle(
        UiIntent(UiIntentType.ASSET_SCAN_APPLY, ((asset, str(tmp_path / "renamed.mp4")),))
    )
    assert controller.session.state.asset(asset).path_ref == str(media.resolve())
    assert controller.scan_job_id is None
    controller.shutdown()
    controller.window.close()


def test_stale_background_validation_is_never_projected(qtbot, tmp_path: Path) -> None:
    repo, project, _media, _asset = saved_project(tmp_path)
    controller, router = setup(qtbot, repo)
    controller.request_open(project)
    pump(
        qtbot,
        lambda: controller.session.is_open and controller.validation_job_id is None,
        controller,
    )
    controller.request_validation()
    job_id = controller.validation_job_id
    assert job_id is not None
    from ai_ngerti_geopolitik.application.commands import (
        CommandBatch,
        UpdateProjectSettingsCommand,
    )

    revision = controller.session.state.revision
    controller.session.execute(
        CommandBatch(
            "W8-010-CHANGE",
            "edit",
            "manual",
            revision,
            (UpdateProjectSettingsCommand(1280, 720, 30, "16:9"),),
        )
    )
    controller.poll()
    assert controller.validation_job_id is None
    assert controller.session.dirty
    controller.shutdown()
    controller.window.close()


def test_invalid_new_project_inspection_keeps_existing_open_project(qtbot, tmp_path: Path) -> None:
    repo, opened, _media, _asset = saved_project(tmp_path)
    controller, _router = setup(qtbot, repo)
    controller.request_open(opened)
    pump(
        qtbot,
        lambda: controller.session.is_open and controller.validation_job_id is None,
        controller,
    )
    original_session = controller.session.session_id
    original_marker = controller.active_marker
    original_hash = controller.session.state.semantic_hash()
    original_bytes = opened.read_bytes()

    invalid = tmp_path / "BROKEN_PROJECT.angproj"
    invalid.write_text("{invalid-json", encoding="utf-8")
    controller.request_open(invalid)
    pump(qtbot, lambda: controller.recovery_future is None, controller)

    assert controller.session.is_open
    assert controller.session.current_path == opened
    assert controller.session.session_id == original_session
    assert controller.active_marker == original_marker
    assert controller.session.state.semantic_hash() == original_hash
    assert opened.read_bytes() == original_bytes
    assert "Tidak dapat memeriksa" in controller.last_error
    controller.shutdown()
    controller.window.close()


def test_reopening_current_file_does_not_invalidate_active_session(qtbot, tmp_path: Path) -> None:
    repo, opened, _media, _asset = saved_project(tmp_path)
    controller, _router = setup(qtbot, repo)
    controller.request_open(opened)
    pump(
        qtbot,
        lambda: controller.session.is_open and controller.validation_job_id is None,
        controller,
    )
    before_id = controller.session.session_id
    before_marker = controller.active_marker

    controller.request_open(opened)

    assert controller.recovery_future is None
    assert controller.session.is_open
    assert controller.session.session_id == before_id
    assert controller.session.current_path == opened
    assert controller.active_marker == before_marker
    controller.shutdown()
    controller.window.close()


def test_stale_recovery_offer_does_not_close_active_project(qtbot, tmp_path: Path) -> None:
    repo, opened, _media, _asset = saved_project(tmp_path)
    controller, _router = setup(qtbot, repo)
    controller.request_open(opened)
    pump(
        qtbot,
        lambda: controller.session.is_open and controller.validation_job_id is None,
        controller,
    )
    old_id = controller.session.session_id
    old_marker = controller.active_marker
    old_hash = controller.session.state.semantic_hash()
    old_bytes = opened.read_bytes()
    new_path = tmp_path / "candidate.angproj"
    repo.save(ProjectState.create("P-CANDIDATE", "Candidate", 30), new_path)
    controller.offer = controller.recovery.inspect(new_path)
    new_path.write_text("{corrupted after inspection", encoding="utf-8")

    controller._decide(RecoveryChoice.OPEN_SOURCE)

    assert controller.session.is_open
    assert controller.session.current_path == opened
    assert controller.session.session_id == old_id
    assert controller.active_marker == old_marker
    assert controller.session.state.semantic_hash() == old_hash
    assert opened.read_bytes() == old_bytes
    assert "Pemulihan gagal" in controller.last_error
    controller.shutdown()
    controller.window.close()


def test_failed_candidate_marker_write_preserves_active_project(
    qtbot, tmp_path: Path, monkeypatch
) -> None:
    repo, opened, _media, _asset = saved_project(tmp_path)
    controller, _router = setup(qtbot, repo)
    controller.request_open(opened)
    pump(
        qtbot,
        lambda: controller.session.is_open and controller.validation_job_id is None,
        controller,
    )
    old_id = controller.session.session_id
    old_marker = controller.active_marker
    old_hash = controller.session.state.semantic_hash()
    next_path = tmp_path / "next.angproj"
    repo.save(ProjectState.create("P-NEXT", "Next", 30), next_path)
    controller.offer = controller.recovery.inspect(next_path)
    marker_store = controller.recovery.markers
    original_write = marker_store.write

    def reject_next_marker(source: Path, marker) -> None:
        if source == next_path:
            raise PermissionError("marker write denied")
        original_write(source, marker)

    monkeypatch.setattr(marker_store, "write", reject_next_marker)
    controller._decide(RecoveryChoice.OPEN_SOURCE)

    assert controller.session.is_open
    assert controller.session.current_path == opened
    assert controller.session.session_id == old_id
    assert controller.active_marker == old_marker
    assert controller.session.state.semantic_hash() == old_hash
    assert "Pemulihan gagal" in controller.last_error
    controller.shutdown()
    controller.window.close()


def test_valid_switch_opens_staged_session_and_cleans_old_marker(qtbot, tmp_path: Path) -> None:
    repo, opened, _media, _asset = saved_project(tmp_path)
    controller, _router = setup(qtbot, repo)
    controller.request_open(opened)
    pump(
        qtbot,
        lambda: controller.session.is_open and controller.validation_job_id is None,
        controller,
    )
    old_marker = controller.active_marker
    old_id = controller.session.session_id
    old_bytes = opened.read_bytes()
    next_path = tmp_path / "valid-next.angproj"
    repo.save(ProjectState.create("P-NEXT", "Next", 30), next_path)
    next_bytes = next_path.read_bytes()
    controller.offer = controller.recovery.inspect(next_path)

    controller._decide(RecoveryChoice.OPEN_SOURCE)

    assert controller.session.is_open
    assert controller.session.current_path == next_path
    assert controller.session.session_id != old_id
    assert controller.active_marker is not None
    assert controller.session.state.project_id == "P-NEXT"
    assert opened.read_bytes() == old_bytes
    assert next_path.read_bytes() == next_bytes
    if old_marker is not None:
        assert controller.recovery.markers.read(opened, old_marker.project_id).status == "clean"
    controller.shutdown()
    controller.window.close()


def test_denied_old_clean_marker_write_does_not_drop_open_project(
    qtbot, tmp_path: Path, monkeypatch
) -> None:
    repo, opened, _media, _asset = saved_project(tmp_path)
    controller, _router = setup(qtbot, repo)
    controller.request_open(opened)
    pump(
        qtbot,
        lambda: controller.session.is_open and controller.validation_job_id is None,
        controller,
    )
    old_id = controller.session.session_id
    old_marker = controller.active_marker
    old_hash = controller.session.state.semantic_hash()
    old_bytes = opened.read_bytes()
    next_path = tmp_path / "next-safely-denied.angproj"
    repo.save(ProjectState.create("P-NEW", "Next", 30), next_path)
    controller.offer = controller.recovery.inspect(next_path)
    marker_store = controller.recovery.markers
    original_write = marker_store.write

    def deny_previous_marker_close(source: Path, marker) -> None:
        if source == opened and marker.status == "clean":
            raise PermissionError("old marker cannot be saved")
        original_write(source, marker)

    with monkeypatch.context() as patcher:
        patcher.setattr(marker_store, "write", deny_previous_marker_close)
        controller._decide(RecoveryChoice.OPEN_SOURCE)

    assert controller.session.is_open
    assert controller.session.session_id == old_id
    assert controller.session.current_path == opened
    assert controller.active_marker == old_marker
    assert controller.session.state.semantic_hash() == old_hash
    assert opened.read_bytes() == old_bytes
    assert old_marker is not None
    assert marker_store.read(opened, old_marker.project_id) == old_marker
    assert marker_store.read(next_path, "P-NEW").status == "clean"
    assert "Tidak dapat menutup" in controller.last_error
    controller.shutdown()
    controller.window.close()


def test_open_saved_project_from_home_switches_to_real_editor(qtbot, tmp_path: Path) -> None:
    repo, project, _media, _asset = saved_project(tmp_path)
    controller, _router = setup(qtbot, repo, initial_route="UI-002")
    assert controller.window.window.property("ui_state") == "UI-002"
    assert not controller.session.is_open

    controller.request_open(project)
    pump(
        qtbot,
        lambda: (
            controller.session.is_open
            and controller.validation_job_id is None
            and controller.window.window.property("ui_state") == "UI-010"
        ),
        controller,
    )

    assert controller.session.current_path == project
    assert controller.session.is_open
    assert controller.window.window.property("ui_state") == "UI-010"
    controller.shutdown()
    controller.window.close()


def test_corrupt_project_from_home_does_not_navigate_to_editor(qtbot, tmp_path: Path) -> None:
    repo = JsonProjectRepository()
    invalid = tmp_path / "invalid-home-open.angproj"
    invalid.write_text("{broken-json", encoding="utf-8")
    controller, _router = setup(qtbot, repo, initial_route="UI-002")
    assert controller.window.window.property("ui_state") == "UI-002"

    controller.request_open(invalid)
    pump(qtbot, lambda: controller.recovery_future is None, controller)

    assert controller.window.window.property("ui_state") == "UI-002"
    assert not controller.session.is_open
    assert "Tidak dapat memeriksa" in controller.last_error
    controller.shutdown()
    controller.window.close()
