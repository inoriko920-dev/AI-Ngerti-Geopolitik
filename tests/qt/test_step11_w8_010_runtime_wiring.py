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
from ai_ngerti_geopolitik.domain import Clip, FrameTime
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


def setup(qtbot, repo: JsonProjectRepository | None = None):
    router = W8IntentRouter()
    window = create_main_window("UI-010", fixture_mode=True, intent_sink=router)
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
