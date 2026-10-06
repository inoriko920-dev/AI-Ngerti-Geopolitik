from __future__ import annotations

from collections.abc import Callable
from typing import Any

from ai_ngerti_geopolitik.presentation.visual_mock import project_thumb_pixmap
from ai_ngerti_geopolitik.presentation.common import make_primary_button, muted_label


def create_home_screen(
    on_new_project: Callable[[], None],
    on_open_editor: Callable[[], None],
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
    outer.setContentsMargins(30, 20, 30, 34)
    outer.setSpacing(20)

    header = QHBoxLayout()
    brand = QLabel("▣   AI Ngerti Geopolitik")
    brand.setStyleSheet("font-size:20px; font-weight:700;")
    quick_help = QPushButton("?  Bantuan Cepat")
    quick_help.setStyleSheet("color:#2563EB; border:none; font-weight:600;")
    header.addWidget(brand)
    header.addStretch(1)
    header.addWidget(quick_help)
    outer.addLayout(header)

    hero = QVBoxLayout()
    hero.setSpacing(6)
    title = QLabel("Mulai Proyek")
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    title.setStyleSheet("font-size:34px; font-weight:750; margin-top:12px;")
    subtitle = muted_label(
        "Buat proyek baru atau buka proyek yang sudah ada untuk mulai mengedit video "
        "dengan bantuan AI."
    )
    subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
    subtitle.setStyleSheet("font-size:15px; color:#64748B;")
    hero.addWidget(title)
    hero.addWidget(subtitle)
    outer.addLayout(hero)

    action_row = QHBoxLayout()
    action_row.setSpacing(18)
    action_row.addStretch(1)

    new_card = QFrame()
    new_card.setObjectName("card_new_project")
    new_card.setMinimumSize(460, 130)
    new_card.setMaximumWidth(560)
    new_card.setStyleSheet(
        "QFrame {background:#2563EB; border-radius:12px;} "
        "QLabel {color:white; background:transparent;}"
    )
    new_layout = QHBoxLayout(new_card)
    new_layout.setContentsMargins(34, 24, 34, 24)
    new_icon = QLabel("＋")
    new_icon.setStyleSheet("font-size:42px; font-weight:300;")
    new_text = QVBoxLayout()
    new_title = QLabel("Proyek Baru")
    new_title.setStyleSheet("font-size:20px; font-weight:700;")
    new_desc = QLabel("Buat proyek video baru\ndengan bantuan AI")
    new_desc.setStyleSheet("font-size:14px;")
    new_text.addWidget(new_title)
    new_text.addWidget(new_desc)
    new_layout.addWidget(new_icon)
    new_layout.addSpacing(18)
    new_layout.addLayout(new_text, 1)
    new_button = make_primary_button("Mulai", "btn_home_new_project")
    new_button.clicked.connect(on_new_project)
    new_button.setMaximumWidth(90)
    new_layout.addWidget(new_button)

    open_card = QFrame()
    open_card.setObjectName("card_open_project")
    open_card.setProperty("panel", True)
    open_card.setMinimumSize(460, 130)
    open_card.setMaximumWidth(560)
    open_layout = QHBoxLayout(open_card)
    open_layout.setContentsMargins(34, 24, 34, 24)
    open_icon = QLabel("▱")
    open_icon.setStyleSheet("font-size:42px; color:#2563EB;")
    open_text = QVBoxLayout()
    open_title = QLabel("Buka Proyek")
    open_title.setStyleSheet("font-size:20px; font-weight:700;")
    open_desc = muted_label("Buka proyek yang sudah ada\ndari perangkat Anda")
    open_desc.setStyleSheet("font-size:14px; color:#64748B;")
    open_text.addWidget(open_title)
    open_text.addWidget(open_desc)
    open_layout.addWidget(open_icon)
    open_layout.addSpacing(18)
    open_layout.addLayout(open_text, 1)
    open_button = QPushButton("Buka")
    open_button.setObjectName("btn_home_open_project")
    open_button.clicked.connect(on_open_editor)
    open_button.setMaximumWidth(90)
    open_layout.addWidget(open_button)

    action_row.addWidget(new_card)
    action_row.addWidget(open_card)
    action_row.addStretch(1)
    outer.addLayout(action_row)

    recent = QFrame()
    recent.setProperty("panel", True)
    recent.setMaximumWidth(1420)
    recent_layout = QVBoxLayout(recent)
    recent_layout.setContentsMargins(28, 20, 28, 20)
    recent_layout.setSpacing(0)
    recent_header = QHBoxLayout()
    recent_title = QLabel("Proyek Terbaru")
    recent_title.setStyleSheet("font-size:20px; font-weight:700;")
    see_all = QPushButton("Lihat Semua  ›")
    see_all.setStyleSheet("color:#2563EB; border:none; font-weight:600;")
    recent_header.addWidget(recent_title)
    recent_header.addStretch(1)
    recent_header.addWidget(see_all)
    recent_layout.addLayout(recent_header)

    samples = [
        ("Liburan ke Bromo", "D:\\Video Projects\\Liburan ke Bromo", "Selesai", "#DCFCE7"),
        (
            "Konten Promosi Produk",
            "D:\\Video Projects\\Konten Promosi Produk",
            "Dalam Proses",
            "#DBEAFE",
        ),
        (
            "Highlight Acara Seminar",
            "D:\\Video Projects\\Highlight Acara Seminar",
            "Jeda",
            "#FEF3C7",
        ),
        (
            "Travel Vlog Bali",
            "D:\\Video Projects\\Travel Vlog Bali",
            "Perlu Diperbaiki",
            "#FEE2E2",
        ),
    ]
    for index, (name, path, status, status_bg) in enumerate(samples):
        if index == 0:
            separator = QFrame()
            separator.setFixedHeight(1)
            separator.setStyleSheet("background:#D8E2EE;")
            recent_layout.addWidget(separator)
        row_widget = QWidget()
        row = QHBoxLayout(row_widget)
        row.setContentsMargins(0, 10, 0, 10)
        thumbnail = QLabel()
        thumbnail.setAlignment(Qt.AlignmentFlag.AlignCenter)
        thumbnail.setFixedSize(112, 58)
        thumbnail.setPixmap(project_thumb_pixmap(index))
        thumbnail.setScaledContents(True)
        thumbnail.setStyleSheet("border:1px solid #C8D8EA; border-radius:7px;")
        info = QVBoxLayout()
        project_name = QLabel(name)
        project_name.setStyleSheet("font-size:14px; font-weight:650;")
        opened = muted_label(f"Dibuka {12 - index} Sep 2026  ·  14:{32 - index * 7:02d}")
        info.addWidget(project_name)
        info.addWidget(opened)
        path_label = muted_label(f"▱  {path}")
        status_label = QLabel(status)
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_label.setMinimumWidth(128)
        status_label.setStyleSheet(
            f"background:{status_bg}; border-radius:13px; padding:5px 10px; font-weight:600;"
        )
        open_recent = QPushButton("•••")
        open_recent.clicked.connect(on_open_editor)
        open_recent.setMaximumWidth(50)
        open_recent.setStyleSheet("border:none; font-weight:700;")
        row.addWidget(thumbnail)
        row.addSpacing(12)
        row.addLayout(info, 2)
        row.addWidget(path_label, 3)
        row.addWidget(status_label)
        row.addWidget(open_recent)
        recent_layout.addWidget(row_widget)
        separator = QFrame()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background:#E5EDF6;")
        recent_layout.addWidget(separator)

    recent_wrap = QHBoxLayout()
    recent_wrap.addStretch(1)
    recent_wrap.addWidget(recent, 1)
    recent_wrap.addStretch(1)
    outer.addLayout(recent_wrap, 1)
    return root
