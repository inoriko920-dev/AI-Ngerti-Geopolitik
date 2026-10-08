from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QPushButton, QTableWidget

from ai_ngerti_geopolitik.application.relink_scan import (
    RankedRelinkCandidate,
    RelinkScanSnapshot,
    RelinkScanToken,
    ScanState,
)
from ai_ngerti_geopolitik.application.ui_intents import RecordingIntentSink, UiIntentType
from ai_ngerti_geopolitik.presentation.asset_scan import (
    asset_scan_projection,
    create_asset_scan_dialog,
)


def _snapshot(status: ScanState) -> RelinkScanSnapshot:
    token = RelinkScanToken("P01", "S01", 1, "a" * 64)
    candidate = RankedRelinkCandidate("A001", Path("renamed.mp4"), 3, True, "exact SHA-256")
    weak = RankedRelinkCandidate("A001", Path("maybe.mp4"), 4, False, "metadata only")
    return RelinkScanSnapshot("J01", token, status, 5, (candidate, weak))


def test_ui040_renders_progress_cancel_as_semantic_intent(qtbot) -> None:
    sink = RecordingIntentSink()
    dialog = create_asset_scan_dialog(
        asset_scan_projection(_snapshot(ScanState.RUNNING)), sink
    )
    qtbot.addWidget(dialog)
    dialog.show()
    assert dialog.objectName() == "dlg_asset_scan"
    label = dialog.findChild(QLabel, "label_asset_scan_progress")
    assert label is not None and "5 file" in label.text()
    start = dialog.findChild(QPushButton, "btn_asset_scan_start")
    cancel = dialog.findChild(QPushButton, "btn_asset_scan_cancel")
    apply = dialog.findChild(QPushButton, "btn_asset_scan_apply")
    assert start is not None and not start.isEnabled()
    assert cancel is not None and cancel.isEnabled()
    assert apply is not None and not apply.isEnabled()
    qtbot.mouseClick(cancel, Qt.MouseButton.LeftButton)
    assert sink.intents[-1].kind is UiIntentType.ASSET_SCAN_CANCEL
    dialog.close()


def test_ui040_success_requires_explicit_checked_exact_candidate(qtbot) -> None:
    sink = RecordingIntentSink()
    dialog = create_asset_scan_dialog(
        asset_scan_projection(_snapshot(ScanState.SUCCESS)), sink
    )
    qtbot.addWidget(dialog)
    dialog.show()
    table = dialog.findChild(QTableWidget, "table_asset_scan_candidates")
    apply = dialog.findChild(QPushButton, "btn_asset_scan_apply")
    assert table is not None and table.rowCount() == 2
    assert apply is not None and apply.isEnabled()
    qtbot.mouseClick(apply, Qt.MouseButton.LeftButton)
    assert sink.intents == []
    selected = table.item(0, 0)
    weak = table.item(1, 0)
    assert selected is not None and weak is not None
    assert bool(selected.flags() & Qt.ItemFlag.ItemIsUserCheckable)
    assert not bool(weak.flags() & Qt.ItemFlag.ItemIsUserCheckable)
    selected.setCheckState(Qt.CheckState.Checked)
    qtbot.mouseClick(apply, Qt.MouseButton.LeftButton)
    assert sink.intents[-1].kind is UiIntentType.ASSET_SCAN_APPLY
    assert sink.intents[-1].payload == (("A001", "renamed.mp4"),)
    dialog.close()


def test_ui040_stale_result_blocks_apply_and_allows_restart(qtbot) -> None:
    sink = RecordingIntentSink()
    dialog = create_asset_scan_dialog(
        asset_scan_projection(_snapshot(ScanState.STALE)), sink
    )
    qtbot.addWidget(dialog)
    dialog.show()
    apply = dialog.findChild(QPushButton, "btn_asset_scan_apply")
    start = dialog.findChild(QPushButton, "btn_asset_scan_start")
    assert apply is not None and not apply.isEnabled()
    assert start is not None and start.isEnabled()
    qtbot.mouseClick(start, Qt.MouseButton.LeftButton)
    assert sink.intents[-1].kind is UiIntentType.ASSET_SCAN_START
    dialog.close()
