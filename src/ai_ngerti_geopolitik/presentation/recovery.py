"""Frozen UI-039 recovery state projection and explicit-action dialog."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ai_ngerti_geopolitik.application.recovery import RecoveryOffer
from ai_ngerti_geopolitik.application.ui_intents import UiIntentSink


@dataclass(frozen=True, slots=True)
class RecoveryCandidateRow:
    path: str
    revision: int
    timestamp_ns: int


@dataclass(frozen=True, slots=True)
class RecoveryProjection:
    status: str
    source: str
    candidates: tuple[RecoveryCandidateRow, ...]
    source_enabled: bool
    restore_enabled: bool
    ignore_enabled: bool


def recovery_projection(offer: RecoveryOffer) -> RecoveryProjection:
    candidates = tuple(
        RecoveryCandidateRow(str(record.path), record.revision, record.timestamp_ns)
        for record in offer.candidates
    )
    return RecoveryProjection(
        status=(
            "Pemulihan tersedia — pilih snapshot terverifikasi"
            if offer.can_recover
            else "Tidak ada snapshot lebih baru yang dapat dipulihkan"
        ),
        source=str(offer.source),
        candidates=candidates,
        source_enabled=True,
        restore_enabled=offer.can_recover,
        ignore_enabled=True,
    )


def create_recovery_dialog(
    projection: RecoveryProjection, sink: UiIntentSink | None = None, *,
    parent: Any = None,
) -> Any:
    """UI emits intents only. RecoveryManager owns disk read and decision."""
    from PySide6.QtWidgets import (
        QDialog,
        QHBoxLayout,
        QLabel,
        QListWidget,
        QPushButton,
        QVBoxLayout,
    )

    from ai_ngerti_geopolitik.application.ui_intents import UiIntent, UiIntentType

    dialog = QDialog(parent)
    dialog.setObjectName("dlg_recovery")
    dialog.setWindowTitle("Pemulihan Project")
    dialog.resize(700, 520)
    layout = QVBoxLayout(dialog)
    layout.addWidget(QLabel("Pemulihan Project"))
    status = QLabel(projection.status)
    status.setObjectName("label_recovery_status")
    layout.addWidget(status)
    layout.addWidget(QLabel("Proyek asli: " + projection.source))
    candidates = QListWidget()
    candidates.setObjectName("list_recovery_candidates")
    for row in projection.candidates:
        candidates.addItem(f"Revisi {row.revision} — {row.path}")
    layout.addWidget(candidates)
    buttons = QHBoxLayout()
    open_button = QPushButton("Buka Proyek Asli")
    open_button.setObjectName("btn_recovery_open_source")
    open_button.setEnabled(projection.source_enabled)
    recover_button = QPushButton("Pulihkan Snapshot")
    recover_button.setObjectName("btn_recovery_restore")
    recover_button.setEnabled(False)
    ignore_button = QPushButton("Abaikan")
    ignore_button.setObjectName("btn_recovery_ignore")
    ignore_button.setEnabled(projection.ignore_enabled)

    def emit(kind: UiIntentType, payload: tuple[tuple[str, str], ...] = ()) -> None:
        if sink is not None:
            sink(UiIntent(kind, payload))

    def update_selection(index: int) -> None:
        recover_button.setEnabled(
            projection.restore_enabled and 0 <= index < len(projection.candidates)
        )

    def restore() -> None:
        index = candidates.currentRow()
        if projection.restore_enabled and 0 <= index < len(projection.candidates):
            emit(
                UiIntentType.RECOVERY_RESTORE_SNAPSHOT,
                (("source", projection.source), ("snapshot", projection.candidates[index].path)),
            )

    candidates.currentRowChanged.connect(update_selection)
    open_button.clicked.connect(
        lambda: emit(UiIntentType.RECOVERY_OPEN_SOURCE, (("source", projection.source),))
    )
    recover_button.clicked.connect(restore)
    ignore_button.clicked.connect(lambda: emit(UiIntentType.RECOVERY_IGNORE))
    buttons.addWidget(open_button)
    buttons.addWidget(recover_button)
    buttons.addWidget(ignore_button)
    layout.addLayout(buttons)
    return dialog
