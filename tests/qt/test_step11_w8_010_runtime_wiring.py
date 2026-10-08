"""W8-010 real UI-039/040/041 controller contract and GOLDEN-03 lifecycle."""

from __future__ import annotations

import hashlib
import zipfile
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QTableWidget,
)

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
from ai_ngerti_geopolitik.presentation.navigation import UiRoute


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

    try:
        qtbot.waitUntil(update, timeout=8000)
    except Exception as exc:
        raise AssertionError(
            f"Poll timeout: {controller.last_error!r}, "
            f"preview requested={controller.still_preview_desired!r}, "
            f"inflight={controller.still_preview_inflight!r}, "
            f"future={controller.still_preview_future!r}, "
            f"route={controller.window.window.property('ui_state')!r}"
        ) from exc


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


def test_wizard_continue_does_not_open_phantom_project(qtbot, tmp_path: Path, monkeypatch) -> None:
    controller, _router = setup(qtbot, initial_route="UI-002")
    controller.window.show_route(UiRoute.NEW_PROJECT_DOCX)
    root = controller.window.window
    docx = tmp_path / "scene_asset_mapping.docx"
    xml = (
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        "<w:body><w:p><w:r><w:t>Scene 1: 1</w:t></w:r></w:p>"
        "<w:p><w:r><w:t>Asset 1: Peta sejarah</w:t></w:r></w:p>"
        "</w:body></w:document>"
    )
    with zipfile.ZipFile(docx, "w", zipfile.ZIP_DEFLATED) as out:
        out.writestr("word/document.xml", xml)

    monkeypatch.setattr(
        QFileDialog,
        "getOpenFileName",
        lambda *args, **kwargs: (str(docx), "DOCX (*.docx)"),
    )
    monkeypatch.setattr(QFileDialog, "getExistingDirectory", lambda *args, **kwargs: "")
    browse = root.findChild(QPushButton, "btn_pick_docx")
    continue_button = root.findChild(QPushButton, "btn_continue_new_project")
    docx_field = root.findChild(QLineEdit, "field_scene_docx")
    assert browse is not None and continue_button is not None and docx_field is not None
    assert not continue_button.isEnabled()
    qtbot.mouseClick(browse, Qt.MouseButton.LeftButton)
    assert docx_field.text() == str(docx)
    assert continue_button.isEnabled()

    qtbot.mouseClick(continue_button, Qt.MouseButton.LeftButton)
    pump(qtbot, lambda: controller.scene_docx_future is None, controller)

    assert not controller.session.is_open
    assert root.property("ui_state") == "UI-003"
    assert controller.scene_docx_plan is not None
    assert controller.scene_docx_plan.asset_count == 1
    assert controller.scene_docx_plan.scenes[0].assets[0].canonical_id == "A001"
    assert "1 scene, 1 aset" in controller.last_error
    assert "project belum dibuat" in controller.last_error
    controller.shutdown()
    controller.window.close()


def test_wizard_missing_docx_does_not_replace_active_project(qtbot, tmp_path: Path) -> None:
    repo, project, _media, _asset = saved_project(tmp_path)
    controller, _router = setup(qtbot, repo)
    controller.request_open(project)
    pump(
        qtbot,
        lambda: controller.session.is_open and controller.validation_job_id is None,
        controller,
    )
    active_id = controller.session.session_id
    current_hash = controller.session.state.semantic_hash()
    source_bytes = project.read_bytes()

    missing = tmp_path / "not-found.docx"
    controller.handle(
        UiIntent(
            UiIntentType.NEW_PROJECT,
            (("action", "continue_wizard"), ("path", str(missing))),
        )
    )

    assert controller.session.is_open
    assert controller.session.current_path == project
    assert controller.session.session_id == active_id
    assert controller.session.state.semantic_hash() == current_hash
    assert project.read_bytes() == source_bytes
    assert "tidak tersedia" in controller.last_error
    controller.shutdown()
    controller.window.close()


def test_corrupt_existing_docx_is_rejected_by_worker_without_creating_project(
    qtbot, tmp_path: Path
) -> None:
    bad = tmp_path / "invalid-existing.docx"
    bad.write_bytes(b"not a ZIP/DOCX document")
    controller, _router = setup(qtbot, initial_route="UI-003")
    controller.handle(
        UiIntent(
            UiIntentType.NEW_PROJECT,
            (("action", "continue_wizard"), ("path", str(bad))),
        )
    )
    pump(qtbot, lambda: controller.scene_docx_future is None, controller)

    assert controller.scene_docx_plan is None
    assert not controller.session.is_open
    assert controller.window.window.property("ui_state") == "UI-003"
    assert "tidak sesuai format" in controller.last_error
    assert str(bad) not in controller.last_error
    controller.shutdown()
    controller.window.close()


def test_valid_docx_then_folder_scan_reports_ready_without_fake_project(
    qtbot, tmp_path: Path, monkeypatch
) -> None:
    document = tmp_path / "scenes.docx"
    xml = (
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        "<w:body><w:p><w:r><w:t>Scene 1: 1</w:t></w:r></w:p>"
        "<w:p><w:r><w:t>Asset 1: Map visual</w:t></w:r></w:p>"
        "</w:body></w:document>"
    )
    with zipfile.ZipFile(document, "w") as out:
        out.writestr("word/document.xml", xml)
    folder = tmp_path / "images"
    folder.mkdir()
    image = QImage(4, 4, QImage.Format.Format_RGB32)
    image.fill(0x00228844)
    assert image.save(str(folder / "A001.png"), "PNG")
    monkeypatch.setattr(QFileDialog, "getExistingDirectory", lambda *args, **kwargs: str(folder))
    controller, _router = setup(qtbot, initial_route="UI-003")

    controller.handle(
        UiIntent(
            UiIntentType.NEW_PROJECT,
            (("action", "continue_wizard"), ("path", str(document))),
        )
    )
    pump(
        qtbot,
        lambda: (
            controller.scene_docx_future is None
            and controller.scene_asset_future is None
            and controller.scene_asset_inventory is not None
        ),
        controller,
    )

    assert controller.scene_asset_inventory is not None
    assert controller.scene_asset_inventory.all_ready
    assert controller.scene_asset_inventory.ready_count == 1
    assert controller.scene_asset_inventory.bindings[0].asset_id == "A001"
    assert not controller.session.is_open
    assert controller.window.window.property("ui_state") == "UI-003"
    assert "1/1 READY" in controller.last_error
    assert "Project belum dibuat" in controller.last_error
    controller.shutdown()
    controller.window.close()


def test_duplicate_and_missing_assets_are_reported_without_project_creation(
    qtbot, tmp_path: Path, monkeypatch
) -> None:
    document = tmp_path / "double-scene.docx"
    xml = (
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        "<w:body><w:p><w:r><w:t>Scene 1: 2</w:t></w:r></w:p>"
        "<w:p><w:r><w:t>Asset 1: First visual</w:t></w:r></w:p>"
        "<w:p><w:r><w:t>Asset 2: Second visual</w:t></w:r></w:p>"
        "</w:body></w:document>"
    )
    with zipfile.ZipFile(document, "w") as out:
        out.writestr("word/document.xml", xml)
    folder = tmp_path / "images"
    subfolder = folder / "duplicate"
    subfolder.mkdir(parents=True)
    image = QImage(4, 4, QImage.Format.Format_RGB32)
    image.fill(0x00228844)
    assert image.save(str(folder / "A001.png"), "PNG")
    assert image.save(str(subfolder / "A001.png"), "PNG")
    monkeypatch.setattr(QFileDialog, "getExistingDirectory", lambda *args, **kwargs: str(folder))
    controller, _router = setup(qtbot, initial_route="UI-003")

    controller.handle(
        UiIntent(
            UiIntentType.NEW_PROJECT,
            (("action", "continue_wizard"), ("path", str(document))),
        )
    )
    pump(
        qtbot,
        lambda: (
            controller.scene_docx_future is None
            and controller.scene_asset_future is None
            and controller.scene_asset_inventory is not None
        ),
        controller,
    )

    assert controller.scene_asset_inventory is not None
    assert not controller.scene_asset_inventory.all_ready
    assert [(x.asset_id, x.status.value) for x in controller.scene_asset_inventory.blockers] == [
        ("A001", "DUPLICATE"),
        ("A002", "MISSING"),
    ]
    assert "A001:DUPLICATE" in controller.last_error
    assert "A002:MISSING" in controller.last_error
    assert not controller.session.is_open
    assert controller.window.window.property("ui_state") == "UI-003"
    controller.shutdown()
    controller.window.close()


def _saved_still_scene_project(tmp_path: Path) -> Path:
    from ai_ngerti_geopolitik.application.scene_docx_contract import parse_scene_docx_lines
    from ai_ngerti_geopolitik.application.scene_import_review import (
        build_scene_timeline_review,
        create_canonical_scene_image_project,
    )
    from ai_ngerti_geopolitik.infrastructure.scene_asset_discovery import (
        scan_scene_asset_folder,
        verify_scene_image_media,
    )

    plan = parse_scene_docx_lines(
        (
            "Scene 1: 1",
            "Asset 1: Red",
            "Scene 2: 2",
            "Asset 2: Green",
            "Asset 3: Blue",
        )
    )
    for number, rgb in ((1, 0xFFFF0000), (2, 0xFF00FF00), (3, 0xFF0000FF)):
        image = QImage(8, 8, QImage.Format.Format_ARGB32)
        image.fill(rgb)
        assert image.save(str(tmp_path / f"A{number:03d}.png"), "PNG")
    inventory = scan_scene_asset_folder(plan, tmp_path)
    review = build_scene_timeline_review(plan, inventory, (150, 90), fps=30)
    state = create_canonical_scene_image_project(
        review,
        verify_scene_image_media(inventory),
        project_id="P-QT-PREVIEW",
        project_name="Still Preview",
    )
    from dataclasses import replace

    state = replace(state, settings=replace(state.settings, width=13, height=8))
    path = tmp_path / "still-preview.angproj"
    JsonProjectRepository().save(state, path)
    return path


def test_w8_editor_seek_uses_real_still_pixels_on_existing_canvas(qtbot, tmp_path: Path) -> None:
    from PySide6.QtWidgets import QSlider

    source = _saved_still_scene_project(tmp_path)
    controller, router = setup(qtbot)
    controller.session.open_project(source)
    controller.request_still_preview(0)
    canvas = controller.window.stack.currentWidget().findChild(QLabel, "preview_canvas")
    assert canvas is not None
    pump(qtbot, lambda: canvas.property("still_timeline_frame") == 0, controller)
    assert canvas.pixmap() is not None
    first = canvas.pixmap().toImage()
    assert first.pixelColor(first.width() // 2, first.height() // 2).name() == "#ff0000"

    router(UiIntent(UiIntentType.PLAYBACK_SEEK, (("frame", "150"),)))
    pump(qtbot, lambda: canvas.property("still_timeline_frame") == 150, controller)
    pixmap = canvas.pixmap()
    assert pixmap is not None
    image = pixmap.toImage()
    assert image.pixelColor(image.width() // 4, image.height() // 2).name() == "#00ff00"
    assert image.pixelColor(3 * image.width() // 4, image.height() // 2).name() == "#0000ff"
    slider = controller.window.window.findChild(QSlider, "timeline_scrubber")
    assert slider is not None and slider.maximum() == 239 and slider.value() == 150

    router(UiIntent(UiIntentType.PLAYBACK_SEEK, (("delta", "1"),)))
    pump(qtbot, lambda: canvas.property("still_timeline_frame") == 151, controller)
    router(UiIntent(UiIntentType.PLAYBACK_PLAY))
    assert "belum didukung" in controller.last_error
    controller.shutdown()
    controller.window.close()


def test_w8_rapid_still_seeks_only_display_newest_frame(qtbot, tmp_path: Path, monkeypatch) -> None:
    from threading import Event

    from ai_ngerti_geopolitik.bootstrap import w8_controller as controller_module

    source = _saved_still_scene_project(tmp_path)
    controller, _router = setup(qtbot)
    controller.session.open_project(source)
    real_render = controller_module.render_still_frame
    started = Event()
    release = Event()
    rendered: list[int] = []

    def slow_first(state, frame):
        rendered.append(frame)
        if frame == 0:
            started.set()
            assert release.wait(5)
        return real_render(state, frame)

    monkeypatch.setattr(controller_module, "render_still_frame", slow_first)
    controller.request_still_preview(0)
    assert started.wait(3)
    controller.request_still_preview(149)
    controller.request_still_preview(150)
    release.set()
    canvas = controller.window.stack.currentWidget().findChild(QLabel, "preview_canvas")
    assert canvas is not None
    pump(qtbot, lambda: canvas.property("still_timeline_frame") == 150, controller)
    assert rendered == [0, 150]
    controller.shutdown()
    controller.window.close()


def test_w8_old_still_job_cannot_update_new_project(qtbot, tmp_path: Path, monkeypatch) -> None:
    from threading import Event
    from uuid import uuid4

    from ai_ngerti_geopolitik.bootstrap import w8_controller as controller_module

    source = _saved_still_scene_project(tmp_path)
    controller, _router = setup(qtbot)
    controller.session.open_project(source)
    real_render = controller_module.render_still_frame
    started = Event()
    release = Event()

    def slow_first(state, frame):
        if state.project_id == "P-QT-PREVIEW" and frame == 0:
            started.set()
            assert release.wait(5)
        return real_render(state, frame)

    monkeypatch.setattr(controller_module, "render_still_frame", slow_first)
    controller.request_still_preview(0)
    assert started.wait(3)

    from dataclasses import replace

    next_path = tmp_path / "next.angproj"
    next_state = replace(controller.session.state, project_id="P-QT-NEXT")
    JsonProjectRepository().save(next_state, next_path)
    controller.session.open_project(next_path)
    controller.session_id = uuid4().hex
    controller.request_still_preview(150)
    release.set()

    canvas = controller.window.stack.currentWidget().findChild(QLabel, "preview_canvas")
    assert canvas is not None
    pump(qtbot, lambda: canvas.property("still_timeline_frame") == 150, controller)
    assert controller.session.state.project_id == "P-QT-NEXT"
    image = canvas.pixmap().toImage()
    assert image.pixelColor(image.width() // 4, image.height() // 2).name() == "#00ff00"
    controller.shutdown()
    controller.window.close()
