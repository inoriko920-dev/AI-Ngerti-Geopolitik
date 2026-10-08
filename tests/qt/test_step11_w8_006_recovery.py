"""Frozen UI-039 semantic controls: never mutate project from Qt widgets."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QListWidget, QPushButton

from ai_ngerti_geopolitik.application.autosave_catalog import AutosaveRecord
from ai_ngerti_geopolitik.application.recovery import RecoveryOffer
from ai_ngerti_geopolitik.application.ui_intents import RecordingIntentSink, UiIntentType
from ai_ngerti_geopolitik.presentation.recovery import (
    create_recovery_dialog,
    recovery_projection,
)


def offer(*, candidates: bool) -> RecoveryOffer:
    item = AutosaveRecord(
        Path("recovered.autosave.angproj"), "P01", 3, "a" * 64, "b" * 64,
        1_700_000_000_000_000_000, False,
    )
    return RecoveryOffer(
        Path("source.angproj"), "P01", "c" * 64, 2, "d" * 64, None,
        (item,) if candidates else (),
    )


def test_ui039_actions_show_only_explicit_choices(qtbot) -> None:
    sink = RecordingIntentSink()
    dialog = create_recovery_dialog(recovery_projection(offer(candidates=True)), sink)
    qtbot.addWidget(dialog)
    dialog.show()
    assert dialog.objectName() == "dlg_recovery"
    listed = dialog.findChild(QListWidget, "list_recovery_candidates")
    restore = dialog.findChild(QPushButton, "btn_recovery_restore")
    open_source = dialog.findChild(QPushButton, "btn_recovery_open_source")
    ignore = dialog.findChild(QPushButton, "btn_recovery_ignore")
    assert listed is not None and listed.count() == 1
    assert restore is not None and not restore.isEnabled()
    assert open_source is not None and open_source.isEnabled()
    assert ignore is not None and ignore.isEnabled()
    qtbot.mouseClick(open_source, Qt.MouseButton.LeftButton)
    assert sink.intents[-1].kind is UiIntentType.RECOVERY_OPEN_SOURCE
    qtbot.mouseClick(ignore, Qt.MouseButton.LeftButton)
    assert sink.intents[-1].kind is UiIntentType.RECOVERY_IGNORE
    assert not restore.isEnabled()
    dialog.close()


def test_ui039_requires_selected_snapshot_and_never_auto_restores(qtbot) -> None:
    sink = RecordingIntentSink()
    dialog = create_recovery_dialog(recovery_projection(offer(candidates=True)), sink)
    qtbot.addWidget(dialog)
    dialog.show()
    listed = dialog.findChild(QListWidget, "list_recovery_candidates")
    restore = dialog.findChild(QPushButton, "btn_recovery_restore")
    assert listed is not None and restore is not None
    assert sink.intents == []
    listed.setCurrentRow(0)
    assert restore.isEnabled()
    qtbot.mouseClick(restore, Qt.MouseButton.LeftButton)
    assert sink.intents[-1].kind is UiIntentType.RECOVERY_RESTORE_SNAPSHOT
    assert sink.intents[-1].payload == (
        ("source", "source.angproj"),
        ("snapshot", "recovered.autosave.angproj"),
    )
    dialog.close()


def test_ui039_no_candidates_keeps_recover_disabled(qtbot) -> None:
    sink = RecordingIntentSink()
    dialog = create_recovery_dialog(recovery_projection(offer(candidates=False)), sink)
    qtbot.addWidget(dialog)
    dialog.show()
    restore = dialog.findChild(QPushButton, "btn_recovery_restore")
    status = dialog.findChild(QLabel, "label_recovery_status")
    assert restore is not None and not restore.isEnabled()
    assert status is not None and "Tidak ada" in status.text()
    assert sink.intents == []
    dialog.close()
