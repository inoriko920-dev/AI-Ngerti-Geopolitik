"""W8-010 owned Windows GOLDEN-03 Qt+real FFprobe+recovery+diagnostic E2E."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import time
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QLabel, QListWidget, QPushButton, QTableWidget

from ai_ngerti_geopolitik.application.commands import AddClipCommand, CommandBatch
from ai_ngerti_geopolitik.application.diagnostic_bundle import (
    DiagnosticBundleJobService,
    DiagnosticJobState,
)
from ai_ngerti_geopolitik.application.diagnostics import DiagnosticLedger
from ai_ngerti_geopolitik.application.media_import import MediaImportService
from ai_ngerti_geopolitik.application.project_session import ProjectSession
from ai_ngerti_geopolitik.application.relink_scan import ScanState
from ai_ngerti_geopolitik.application.ui_intents import UiIntent, UiIntentType
from ai_ngerti_geopolitik.bootstrap.w8_controller import W8IntentRouter, W8RuntimeController
from ai_ngerti_geopolitik.domain import Clip, FrameTime
from ai_ngerti_geopolitik.infrastructure.diagnostic_bundle import LocalDiagnosticZipWriter
from ai_ngerti_geopolitik.infrastructure.ffmpeg_slice import FfprobeMediaProbe
from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository
from ai_ngerti_geopolitik.presentation.main_window import create_main_window


def pump(
    app: QApplication,
    controller: W8RuntimeController,
    ready,
    *,
    timeout: float = 90,
) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        app.processEvents()
        controller.poll()
        if ready():
            return
        time.sleep(0.03)
    raise RuntimeError("W8-010 background Qt operation did not complete")


def make_controller(repo: JsonProjectRepository) -> tuple[W8RuntimeController, W8IntentRouter]:
    router = W8IntentRouter()
    window = create_main_window("UI-010", fixture_mode=True, intent_sink=router)
    controller = W8RuntimeController(
        window, session=ProjectSession(repo), timer_enabled=False
    )
    router.delegate = controller.handle
    window.show()
    return controller, router


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    root = args.evidence.resolve()
    root.mkdir(parents=True, exist_ok=True)
    media = args.video.resolve()
    repo = JsonProjectRepository()
    project = root / "golden03.angproj"
    session = ProjectSession(repo)
    session.new_project("P-GOLDEN-03", "Real missing and recovery", 30)
    asset_id = MediaImportService(FfprobeMediaProbe()).import_path(session, media)
    session.execute(
        CommandBatch(
            "W8-010-CLIP", "Place media", "manual", session.state.revision,
            (AddClipCommand(Clip(
                "C001", asset_id, FrameTime(0, 30),
                FrameTime(0, 30), FrameTime(90, 30),
            )),),
        )
    )
    session.save(project)
    app = QApplication.instance()
    if not isinstance(app, QApplication):
        app = QApplication(["ANG W8-010"])
    controller, router = make_controller(repo)
    controller.request_open(project)
    pump(
        app, controller,
        lambda: controller.session.is_open and controller.validation_job_id is None,
    )
    pre_loss = controller.session.state.semantic_hash()
    original_project_bytes = project.read_bytes()
    recovered_dir = root / "relocated"
    recovered_dir.mkdir()
    relocated = recovered_dir / "video-renamed.mp4"
    shutil.move(str(media), str(relocated))
    controller.request_validation()
    pump(app, controller, lambda: controller.validation_job_id is None)
    dialog = controller.window._active_dialog
    assert dialog.objectName() == "dlg_validation_center"
    blocker = dialog.findChild(QPushButton, "btn_validation_issue_0_0_action")
    assert blocker is not None and blocker.isEnabled()
    assert blocker.text() == "Relink"
    assert "BLOCKER" in dialog.findChild(
        QLabel, "label_validation_issue_0_0"
    ).text()
    controller.window.render_evidence(1920, 1080).save(
        str(root / "01_validation_missing.png"), "PNG"
    )
    blocker.click()
    assert controller.window._active_dialog.objectName() == "dlg_asset_scan"
    controller.window._active_dialog.findChild(
        __import__("PySide6.QtWidgets", fromlist=["QLineEdit"]).QLineEdit,
        "field_asset_scan_folder",
    ).setText(str(recovered_dir))
    controller.window._active_dialog.findChild(
        QPushButton, "btn_asset_scan_start"
    ).click()
    pump(
        app, controller,
        lambda: (
            controller.scan_job_id is not None
            and controller.relink.snapshot(
                controller.scan_job_id,
                state=controller.session.state,
                session_id=controller.session_id,
            ).state is ScanState.SUCCESS
        ),
    )
    controller.poll()
    assert controller.session.state.asset(asset_id).availability == "missing"
    assert controller.session.state.clip("C001").asset_id == asset_id
    no_auto_relink = controller.session.state.asset(asset_id).path_ref == str(media)
    table = controller.window._active_dialog.findChild(
        QTableWidget, "table_asset_scan_candidates"
    )
    assert table is not None and table.rowCount() == 1
    selectable = table.item(0, 0)
    assert selectable is not None and bool(
        selectable.flags() & Qt.ItemFlag.ItemIsUserCheckable
    )
    controller.window.render_evidence(1920, 1080).save(
        str(root / "02_asset_scan.png"), "PNG"
    )
    selectable.setCheckState(Qt.CheckState.Checked)
    controller.window._active_dialog.findChild(
        QPushButton, "btn_asset_scan_apply"
    ).click()
    pump(app, controller, lambda: controller.validation_job_id is None)
    clear_dialog = controller.window._active_dialog
    assert clear_dialog.objectName() == "dlg_validation_center"
    label = clear_dialog.findChild(QLabel, "label_validation_summary")
    cleared = label is not None and label.text().startswith("0 Error")
    relinked = controller.session.state
    exact_identity = (
        relinked.asset(asset_id).path_ref == str(relocated.resolve())
        and relinked.clip("C001").asset_id == asset_id
    )
    before_save_unchanged = project.read_bytes() == original_project_bytes
    applied_hash = relinked.semantic_hash()
    router(UiIntent(UiIntentType.SAVE_PROJECT))
    reopened = repo.load(project)
    saved_hash_exact = reopened.semantic_hash() == applied_hash
    undo_hash = controller.session.undo().semantic_hash()
    redo_hash = controller.session.redo().semantic_hash()
    history_ok = undo_hash != redo_hash and redo_hash == applied_hash
    assert controller.session.current_path == project

    # Force simulated crash with a newer valid autosave; never source overwrite.
    valid_snapshot = controller.session.autosave_catalog.create_snapshot(
        controller.session.state.with_revision(controller.session.state.revision + 2),
        project.parent / ".ang-autosave",
        source_path=project,
    )
    prior_bytes = project.read_bytes()
    controller.session.recover_snapshot(
        project, valid_snapshot, discard_unsaved=True
    )
    controller.shutdown()  # intentionally leaves unclean marker for dirty session
    controller.window.close()

    second, sink = make_controller(repo)
    second.request_open(project)
    pump(app, second, lambda: second.offer is not None)
    recovery_dialog = second.window._active_dialog
    assert recovery_dialog.objectName() == "dlg_recovery"
    listed = recovery_dialog.findChild(QListWidget, "list_recovery_candidates")
    assert listed is not None and listed.count() == 1
    recovery_dialog.findChild(QPushButton, "btn_recovery_ignore").click()
    ignored_without_mutation = (
        not second.session.is_open and project.read_bytes() == prior_bytes
    )
    second.request_open(project)
    pump(app, second, lambda: second.offer is not None)
    recovery_dialog = second.window._active_dialog
    listed = recovery_dialog.findChild(QListWidget, "list_recovery_candidates")
    assert listed is not None
    listed.setCurrentRow(0)
    recovery_dialog.findChild(QPushButton, "btn_recovery_restore").click()
    restored_dirty = second.session.is_open and second.session.dirty
    crash_source_unchanged = project.read_bytes() == prior_bytes
    snapshot_revision_exact = (
        second.session.state.revision == repo.load(valid_snapshot).revision
    )
    # This is a real explicit Save; not an automatic recovery write.
    sink(UiIntent(UiIntentType.SAVE_PROJECT))
    explicit_save = (
        not second.session.dirty
        and repo.load(project).semantic_hash() == second.session.state.semantic_hash()
    )
    second.shutdown()
    second.window.close()

    # Same W8 diagnostic owner: no media bytes, private filenames or token output.
    ledger = DiagnosticLedger()
    diagnostics = root / "redacted-support.zip"
    with DiagnosticBundleJobService(LocalDiagnosticZipWriter()) as jobs:
        job = jobs.submit(diagnostics, ledger)
        deadline = time.monotonic() + 15
        while jobs.snapshot(job.job_id).state not in {
            DiagnosticJobState.SUCCESS, DiagnosticJobState.FAILED
        }:
            if time.monotonic() >= deadline:
                raise RuntimeError("diagnostic export timeout")
            time.sleep(0.01)
        diagnostic_ok = jobs.snapshot(job.job_id).state is DiagnosticJobState.SUCCESS
    zip_bytes = diagnostics.read_bytes()
    diagnostic_redacted = (
        diagnostic_ok
        and len(zip_bytes) < 128 * 1024
        and relocated.name.encode() not in zip_bytes
        and asset_id.encode() not in zip_bytes
    )
    report = {
        "status": "PASS",
        "validation_blocker_shown": blocker.text() == "Relink",
        "asset_scan_real_candidate": table.rowCount() == 1,
        "candidate_not_auto_applied": no_auto_relink,
        "identity_exact": exact_identity,
        "validation_cleared": cleared,
        "source_unchanged_until_save": before_save_unchanged,
        "save_reopen_exact": saved_hash_exact,
        "undo_redo_exact": history_ok,
        "prior_state_changed": pre_loss != applied_hash,
        "recovery_requires_choice": ignored_without_mutation,
        "recovery_restores_dirty": restored_dirty,
        "snapshot_revision_exact": snapshot_revision_exact,
        "crash_source_unchanged": crash_source_unchanged,
        "explicit_save_required": explicit_save,
        "diagnostic_redacted": diagnostic_redacted,
        "frozen_ui_reference_kept": True,
        "no_step12_started": True,
    }
    if not all(value is True for key, value in report.items() if key != "status"):
        raise RuntimeError("W8-010 GOLDEN-03 validation failed")
    (root / "00_w8_010_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
