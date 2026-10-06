from __future__ import annotations

from collections.abc import Callable
from typing import Any

from ai_ngerti_geopolitik.application.ui_intents import UiIntent, UiIntentSink, UiIntentType
from ai_ngerti_geopolitik.presentation.common import muted_label
from ai_ngerti_geopolitik.presentation.visual_mock import project_thumb_pixmap


def create_home_screen(
    on_new_project: Callable[[], None],
    on_open_editor: Callable[[], None],
    intent_sink: UiIntentSink,
    *,
    fixture_mode: bool,
) -> Any:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import (
        QFrame,
        QHBoxLayout,
        QLabel,
        QPushButton,
        QVBoxLayout,
        QWidget,
    )

    root = QWidget()
    root.setObjectName("screen_home")
    outer = QVBoxLayout(root)
    outer.setContentsMargins(30, 18, 30, 30)
    outer.setSpacing(16)

    header = QHBoxLayout()
    brand = QLabel("▣   AI Ngerti Geopolitik")
    brand.setObjectName("label_brand")
    brand.setStyleSheet("font-size:19px; font-weight:700;")
    quick_help = QPushButton("?  Bantuan Cepat")
    quick_help.setObjectName("btn_quick_help")
    quick_help.setStyleSheet("color:#2563EB; border:none; font-weight:600;")
    quick_help.setAccessibleName("Bantuan Cepat")
    settings = QPushButton("⚙")
    settings.setObjectName("btn_settings")
    settings.setToolTip("Pengaturan")
    settings.setAccessibleName("Pengaturan")
    settings.setProperty("flat", True)
    header.addWidget(brand)
    header.addStretch(1)
    header.addWidget(quick_help)
    header.addWidget(settings)
    outer.addLayout(header)

    title = QLabel("Mulai Proyek")
    title.setObjectName("label_home_title")
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    title.setStyleSheet("font-size:34px; font-weight:750; margin-top:10px;")
    subtitle = muted_label(
        "Buat proyek baru atau buka proyek yang sudah ada\n"
        "untuk mulai mengedit video dengan bantuan AI."
    )
    subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
    subtitle.setStyleSheet("font-size:15px; color:#64748B;")
    outer.addWidget(title)
    outer.addWidget(subtitle)

    cards = QHBoxLayout()
    cards.setSpacing(18)
    cards.addStretch(1)

    def action_card(
        title_text: str,
        desc: str,
        icon: str,
        *,
        primary: bool,
        callback: Callable[[], None],
        object_name: str,
    ) -> QPushButton:
        card = QPushButton()
        card.setObjectName(object_name)
        card.setAccessibleName(title_text)
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        card.setMinimumSize(420, 128)
        card.setMaximumWidth(520)
        if primary:
            card.setStyleSheet(
                "QPushButton {background:#2563EB; border:1px solid #2563EB; border-radius:12px;} "
                "QLabel {color:white; background:transparent; border:none;}"
            )
        else:
            card.setStyleSheet(
                "QPushButton {background:#FFFFFF; border:1px solid #D8E2EE; border-radius:12px;} "
                "QPushButton:hover {border-color:#2563EB;} "
                "QLabel {background:transparent; border:none;}"
            )
        layout = QHBoxLayout(card)
        layout.setContentsMargins(28, 22, 28, 22)
        icon_label = QLabel(icon)
        icon_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setFixedWidth(80)
        icon_label.setStyleSheet(
            "font-size:38px; color:white;" if primary else "font-size:38px; color:#2563EB;"
        )
        texts = QVBoxLayout()
        title_label = QLabel(title_text)
        title_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        title_label.setStyleSheet("font-size:20px; font-weight:700;")
        desc_label = QLabel(desc)
        desc_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet(
            "font-size:14px; color:white;" if primary else "font-size:14px; color:#64748B;"
        )
        texts.addWidget(title_label)
        texts.addWidget(desc_label)
        layout.addWidget(icon_label)
        layout.addLayout(texts, 1)
        card.clicked.connect(callback)
        return card

    def open_new() -> None:
        intent_sink(UiIntent(UiIntentType.NEW_PROJECT))
        on_new_project()

    def open_existing() -> None:
        intent_sink(UiIntent(UiIntentType.OPEN_PROJECT))
        on_open_editor()

    cards.addWidget(
        action_card(
            "Proyek Baru",
            "Buat proyek video baru\ndengan bantuan AI",
            "+",
            primary=True,
            callback=open_new,
            object_name="card_new_project",
        )
    )
    cards.addWidget(
        action_card(
            "Buka Proyek",
            "Buka proyek yang sudah ada\ndari perangkat Anda",
            "▱",
            primary=False,
            callback=open_existing,
            object_name="card_open_project",
        )
    )
    cards.addStretch(1)
    outer.addLayout(cards)

    panel = QFrame()
    panel.setObjectName("panel_recent_projects")
    panel.setProperty("panel", True)
    panel.setMaximumWidth(1260)
    panel_layout = QVBoxLayout(panel)
    panel_layout.setContentsMargins(30, 20, 30, 20)
    panel_layout.setSpacing(8)
    head = QHBoxLayout()
    recent_title = QLabel("Proyek Terbaru")
    recent_title.setStyleSheet("font-size:19px; font-weight:700;")
    see_all = QPushButton("Lihat Semua  ›")
    see_all.setStyleSheet("color:#2563EB; border:none; font-weight:600;")
    head.addWidget(recent_title)
    head.addStretch(1)
    head.addWidget(see_all)
    panel_layout.addLayout(head)

    if fixture_mode:
        projects = [
            (
                "Liburan ke Bromo",
                "Dibuka 12 Sep 2024 14:32",
                "D:/Video Projects/Liburan ke Bromo",
                "Selesai",
                "#16A34A",
            ),
            (
                "Konten Promosi Produk",
                "Dibuka 11 Sep 2024 10:15",
                "D:/Video Projects/Konten Promosi Produk",
                "Dalam Proses",
                "#0284C7",
            ),
            (
                "Highlight Acara Seminar",
                "Dibuka 9 Sep 2024 16:20",
                "D:/Video Projects/Highlight Acara Seminar",
                "Jeda",
                "#D97706",
            ),
            (
                "Travel Vlog Bali",
                "Dibuka 7 Sep 2024 09:48",
                "D:/Video Projects/Travel Vlog Bali",
                "Perlu Diperbaiki",
                "#DC2626",
            ),
        ]
        for index, (name, date, path, status, color) in enumerate(projects):
            if index:
                line = QFrame()
                line.setFixedHeight(1)
                line.setStyleSheet("background:#E2E8F0;")
                panel_layout.addWidget(line)
            row = QHBoxLayout()
            thumb = QLabel()
            thumb.setFixedSize(138, 72)
            thumb.setPixmap(project_thumb_pixmap(index, 138, 72))
            thumb.setScaledContents(True)
            info = QVBoxLayout()
            name_label = QLabel(name)
            name_label.setStyleSheet("font-size:14px; font-weight:700;")
            date_label = muted_label("◷  " + date)
            date_label.setStyleSheet("color:#64748B;")
            info.addWidget(name_label)
            info.addWidget(date_label)
            path_label = muted_label("▱  " + path)
            path_label.setMinimumWidth(380)
            badge = QLabel("●  " + status)
            badge.setStyleSheet(
                f"color:{color}; background:#F8FAFC; border-radius:12px; "
                "padding:5px 10px; font-weight:600;"
            )
            more = QPushButton("•••")
            more.setProperty("flat", True)
            more.setAccessibleName(f"Menu {name}")
            row.addWidget(thumb)
            row.addSpacing(12)
            row.addLayout(info, 2)
            row.addWidget(path_label, 3)
            row.addWidget(badge)
            row.addWidget(more)
            panel_layout.addLayout(row)
    else:
        empty = muted_label("Belum ada riwayat proyek. Gunakan Proyek Baru atau Buka Proyek.")
        empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty.setMinimumHeight(180)
        panel_layout.addWidget(empty)

    wrap = QHBoxLayout()
    wrap.addStretch(1)
    wrap.addWidget(panel, 1)
    wrap.addStretch(1)
    outer.addLayout(wrap, 1)
    return root
