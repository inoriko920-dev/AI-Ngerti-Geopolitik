"""UI-040 Asset Scan progress/candidate projection: presentation only, no filesystem work."""

from __future__ import annotations

from dataclasses import dataclass

from ai_ngerti_geopolitik.application.relink_scan import (
    RankedRelinkCandidate,
    RelinkScanSnapshot,
    ScanState,
)


@dataclass(frozen=True, slots=True)
class AssetScanRow:
    asset_id: str
    candidate_path: str
    rank_text: str
    verified_text: str
    selectable: bool


@dataclass(frozen=True, slots=True)
class AssetScanProjection:
    status_text: str
    scanned_files: int
    rows: tuple[AssetScanRow, ...]
    start_enabled: bool
    cancel_enabled: bool
    apply_enabled: bool
    stale: bool
    ambiguous_assets: tuple[str, ...]


def asset_scan_projection(snapshot: RelinkScanSnapshot) -> AssetScanProjection:
    stale = snapshot.state is ScanState.STALE
    running = snapshot.state in {ScanState.QUEUED, ScanState.RUNNING}
    rows = tuple(
        AssetScanRow(
            asset_id=item.asset_id,
            candidate_path=str(item.path),
            rank_text=f"{item.rank}. {item.evidence}",
            verified_text="SHA-256 cocok" if item.fingerprint_verified else "Perlu verifikasi",
            selectable=(
                snapshot.state is ScanState.SUCCESS
                and not snapshot.applied
                and item.fingerprint_verified
            ),
        )
        for item in snapshot.candidates
    )
    message = {
        ScanState.QUEUED: "Menunggu worker scan",
        ScanState.RUNNING: "Memindai folder media",
        ScanState.SUCCESS: "Scan selesai; pilih kandidat secara manual",
        ScanState.CANCELLED: "Scan dibatalkan",
        ScanState.FAILED: "Scan gagal",
        ScanState.STALE: "Hasil scan sudah usang; scan ulang",
    }[snapshot.state]
    return AssetScanProjection(
        status_text=message,
        scanned_files=snapshot.scanned_files,
        rows=rows,
        start_enabled=not running,
        cancel_enabled=running,
        apply_enabled=any(row.selectable for row in rows),
        stale=stale,
        ambiguous_assets=snapshot.ambiguous_assets if not stale else (),
    )


def create_asset_scan_dialog(
    projection: AssetScanProjection,
    intent_sink: object = None,
    *,
    parent: object = None,
) -> object:
    """Frozen UI-040 action surface; a controller owns starting/polling worker jobs."""
    from PySide6.QtWidgets import (
        QDialog,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QPushButton,
        QTableWidget,
        QTableWidgetItem,
        QVBoxLayout,
    )

    from ai_ngerti_geopolitik.application.ui_intents import UiIntent, UiIntentType

    dialog = QDialog(parent)
    dialog.setObjectName("dlg_asset_scan")
    dialog.setWindowTitle("Asset Scan")
    dialog.resize(760, 650)
    dialog.setMinimumWidth(640)
    dialog.setStyleSheet("QDialog {background:#FFFFFF;} QPushButton {padding:6px 10px;}")

    layout = QVBoxLayout(dialog)
    layout.addWidget(QLabel("Asset Scan — Pemulihan Media"))
    root_field = QLineEdit()
    root_field.setObjectName("field_asset_scan_folder")
    root_field.setPlaceholderText("Folder media yang ingin dipindai")
    layout.addWidget(root_field)
    progress = QLabel(f"{projection.status_text} · {projection.scanned_files} file diperiksa")
    progress.setObjectName("label_asset_scan_progress")
    layout.addWidget(progress)
    table = QTableWidget(len(projection.rows), 4)
    table.setObjectName("table_asset_scan_candidates")
    table.setHorizontalHeaderLabels(("Asset ID", "Kandidat", "Peringkat", "Validasi"))
    for index, row in enumerate(projection.rows):
        id_cell = QTableWidgetItem(row.asset_id)
        path_cell = QTableWidgetItem(row.candidate_path)
        rank_cell = QTableWidgetItem(row.rank_text)
        status_cell = QTableWidgetItem(row.verified_text)
        for cell in (id_cell, path_cell, rank_cell, status_cell):
            cell.setFlags(cell.flags() & ~__import__("PySide6.QtCore", fromlist=["Qt"]).Qt.ItemFlag.ItemIsEditable)
        if row.selectable:
            from PySide6.QtCore import Qt
            id_cell.setFlags(id_cell.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            id_cell.setCheckState(Qt.CheckState.Unchecked)
        for column, cell in enumerate((id_cell, path_cell, rank_cell, status_cell)):
            table.setItem(index, column, cell)
    table.horizontalHeader().setStretchLastSection(True)
    layout.addWidget(table)

    buttons = QHBoxLayout()
    start = QPushButton("Mulai Scan")
    start.setObjectName("btn_asset_scan_start")
    start.setEnabled(projection.start_enabled)
    cancel = QPushButton("Batalkan")
    cancel.setObjectName("btn_asset_scan_cancel")
    cancel.setEnabled(projection.cancel_enabled)
    apply = QPushButton("Relink Terpilih")
    apply.setObjectName("btn_asset_scan_apply")
    apply.setEnabled(projection.apply_enabled)

    def emit(kind: UiIntentType, payload: tuple[tuple[str, str], ...] = ()) -> None:
        if callable(intent_sink):
            intent_sink(UiIntent(kind, payload))

    def request_apply() -> None:
        from PySide6.QtCore import Qt

        chosen = []
        for index, row in enumerate(projection.rows):
            item = table.item(index, 0)
            if row.selectable and item.checkState() is Qt.CheckState.Checked:
                chosen.append((row.asset_id, row.candidate_path))
        if chosen:
            emit(
                UiIntentType.ASSET_SCAN_APPLY,
                tuple((asset_id, candidate_path) for asset_id, candidate_path in chosen),
            )

    start.clicked.connect(
        lambda: emit(UiIntentType.ASSET_SCAN_START, (("root", root_field.text()),))
    )
    cancel.clicked.connect(lambda: emit(UiIntentType.ASSET_SCAN_CANCEL))
    apply.clicked.connect(request_apply)
    buttons.addWidget(start)
    buttons.addWidget(cancel)
    buttons.addWidget(apply)
    layout.addLayout(buttons)
    return dialog
