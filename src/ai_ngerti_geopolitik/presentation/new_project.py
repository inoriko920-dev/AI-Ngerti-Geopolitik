from __future__ import annotations

from collections.abc import Callable
from typing import Any

from ai_ngerti_geopolitik.application.ui_intents import UiIntent, UiIntentSink, UiIntentType
from ai_ngerti_geopolitik.presentation.common import (
    horizontal_rule,
    make_primary_button,
    muted_label,
)


def create_new_project_screen(
    on_back: Callable[[], None],
    on_continue: Callable[[], None],
    intent_sink: UiIntentSink,
    *,
    fixture_mode: bool,
) -> Any:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import (
        QFileDialog,
        QFrame,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QPushButton,
        QVBoxLayout,
        QWidget,
    )

    root = QWidget()
    root.setObjectName("screen_new_project")
    page = QHBoxLayout(root)
    page.setContentsMargins(0, 0, 0, 0)
    page.setSpacing(0)

    sidebar = QFrame()
    sidebar.setObjectName("pane_project_sidebar")
    sidebar.setFixedWidth(260)
    sidebar.setStyleSheet("background:#F7FAFE; border-right:1px solid #D8E2EE;")
    side = QVBoxLayout(sidebar)
    side.setContentsMargins(18, 18, 18, 20)
    side.setSpacing(10)
    brand = QLabel("▣  AI Ngerti Geopolitik")
    brand.setStyleSheet("font-size:15px; font-weight:700; padding:8px;")
    side.addWidget(brand)
    side.addSpacing(10)
    items = [
        ("▣", "Proyek Baru", True),
        ("▱", "Proyek Saya", False),
        ("⚙", "Pengaturan", False),
        ("?", "Bantuan", False),
    ]
    for icon, item_text, active in items:
        item = QLabel(f"{icon}   {item_text}")
        item.setMinimumHeight(44)
        if active:
            item.setStyleSheet(
                "padding:8px 12px; background:#DBEAFE; color:#1D4ED8; "
                "border-radius:7px; font-weight:650;"
            )
        else:
            item.setStyleSheet("padding:8px 12px; color:#475569;")
        side.addWidget(item)
    side.addStretch(1)
    page.addWidget(sidebar)

    content = QWidget()
    outer = QVBoxLayout(content)
    outer.setContentsMargins(74, 36, 74, 36)
    outer.setSpacing(0)

    card = QFrame()
    card.setObjectName("panel_new_project_wizard")
    card.setProperty("panel", True)
    card.setMaximumWidth(1240)
    inner = QVBoxLayout(card)
    inner.setContentsMargins(36, 26, 36, 26)
    inner.setSpacing(16)

    stepper = QHBoxLayout()
    stepper.setSpacing(10)
    steps = [("1", "Scene DOCX", True), ("2", "Folder Aset", False), ("3", "Media", False)]
    for index, (number, label, active) in enumerate(steps):
        circle = QLabel(number)
        circle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        circle.setFixedSize(36, 36)
        circle.setStyleSheet(
            "background:#2563EB; color:white; border-radius:18px; font-weight:700;"
            if active
            else (
                "background:#F8FAFC; color:#64748B; border:1px solid #CBD5E1; "
                "border-radius:18px; font-weight:700;"
            )
        )
        step_label = QLabel(label)
        step_label.setStyleSheet(
            "font-weight:650; color:#1D4ED8;" if active else "color:#64748B;"
        )
        stepper.addWidget(circle)
        stepper.addWidget(step_label)
        if index < len(steps) - 1:
            line = QFrame()
            line.setFixedHeight(1)
            line.setMinimumWidth(120)
            line.setStyleSheet("background:#CBD5E1;")
            stepper.addWidget(line, 1)
    inner.addLayout(stepper)
    inner.addWidget(horizontal_rule())

    title = QLabel("Pilih Scene DOCX")
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    title.setStyleSheet("font-size:25px; font-weight:750; margin-top:6px;")
    desc = muted_label("Unggah file DOCX yang berisi daftar scene beserta mapping aset.")
    desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
    desc.setStyleSheet("font-size:14px; color:#64748B;")
    inner.addWidget(title)
    inner.addWidget(desc)

    dropzone = QFrame()
    dropzone.setObjectName("drop_scene_docx")
    dropzone.setMinimumHeight(270)
    dropzone.setStyleSheet(
        "QFrame {background:#F8FBFF; border:1px dashed #7FB2F4; border-radius:10px;} "
        "QLabel {background:transparent;}"
    )
    drop = QVBoxLayout(dropzone)
    drop.setContentsMargins(24, 24, 24, 24)
    drop.setSpacing(10)
    drop.addStretch(1)
    doc_icon = QLabel("DOCX")
    doc_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
    doc_icon.setFixedSize(78, 64)
    doc_icon.setStyleSheet(
        "font-size:16px; font-weight:800; color:white; background:#2563EB; border-radius:8px;"
    )
    icon_row = QHBoxLayout()
    icon_row.addStretch(1)
    icon_row.addWidget(doc_icon)
    icon_row.addStretch(1)
    drop.addLayout(icon_row)
    hint = QLabel("Tarik file DOCX ke sini atau pilih file")
    hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
    hint.setStyleSheet("color:#64748B; font-size:14px;")
    drop.addWidget(hint)
    path = QLineEdit()
    path.setObjectName("field_scene_docx")
    path.setVisible(fixture_mode)
    if fixture_mode:
        path.setText("scene_asset_Sejarah_Arab_Saudi.docx")
    else:
        path.setPlaceholderText("scene_asset_[Judul].docx")
    drop.addWidget(path)
    browse = QPushButton("▱  Pilih DOCX")
    browse.setObjectName("btn_pick_docx")
    browse.setMinimumWidth(160)
    browse.setAccessibleName("Pilih Scene DOCX")
    browse.setStyleSheet(
        "color:#1D4ED8; border:1px solid #2563EB; border-radius:7px; "
        "padding:9px 18px; font-weight:650; background:white;"
    )

    def browse_file() -> None:
        intent_sink(UiIntent(UiIntentType.NEW_PROJECT, (("action", "pick_docx"),)))
        chosen, _ = QFileDialog.getOpenFileName(root, "Pilih Scene DOCX", "", "DOCX (*.docx)")
        if chosen:
            path.setText(chosen)
            path.setVisible(True)
            next_button.setEnabled(True)

    browse.clicked.connect(browse_file)
    browse_row = QHBoxLayout()
    browse_row.addStretch(1)
    browse_row.addWidget(browse)
    browse_row.addStretch(1)
    drop.addLayout(browse_row)
    drop.addStretch(1)
    inner.addWidget(dropzone)

    info = QFrame()
    info.setStyleSheet("background:#F4F8FD; border:1px solid #D8E2EE; border-radius:8px;")
    info_layout = QHBoxLayout(info)
    info_layout.setContentsMargins(18, 12, 18, 12)
    info_icon = QLabel("i")
    info_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
    info_icon.setFixedSize(28, 28)
    info_icon.setStyleSheet(
        "font-weight:800; color:#2563EB; border:2px solid #2563EB; border-radius:14px;"
    )
    info_text = QVBoxLayout()
    info_title = QLabel("Persyaratan File DOCX")
    info_title.setStyleSheet("font-weight:700;")
    info_desc = muted_label(
        "File harus berisi daftar scene dan mapping aset sesuai format Prompt 1. "
        "Setiap scene wajib memiliki 1 atau 2 Asset ID canonical Axxx."
    )
    info_text.addWidget(info_title)
    info_text.addWidget(info_desc)
    info_layout.addWidget(info_icon)
    info_layout.addLayout(info_text, 1)
    inner.addWidget(info)
    inner.addWidget(horizontal_rule())

    footer = QHBoxLayout()
    cancel = QPushButton("Batal")
    cancel.setObjectName("btn_cancel_new_project")
    cancel.clicked.connect(on_back)
    next_button = make_primary_button("Lanjut", "btn_continue_new_project")
    next_button.setEnabled(fixture_mode)

    def continue_flow() -> None:
        intent_sink(UiIntent(UiIntentType.NEW_PROJECT, (("scene_docx", path.text()),)))
        on_continue()

    next_button.clicked.connect(continue_flow)
    footer.addWidget(cancel)
    footer.addStretch(1)
    footer.addWidget(next_button)
    inner.addLayout(footer)

    centered = QHBoxLayout()
    centered.addStretch(1)
    centered.addWidget(card, 1)
    centered.addStretch(1)
    outer.addLayout(centered, 1)
    page.addWidget(content, 1)
    return root
