from __future__ import annotations

from typing import Any


def make_primary_button(text: str, object_name: str = "") -> Any:
    from PySide6.QtWidgets import QPushButton

    button = QPushButton(text)
    button.setProperty("primary", True)
    if object_name:
        button.setObjectName(object_name)
    return button


def icon_button(text: str, accessible_name: str, object_name: str = "") -> Any:
    from PySide6.QtWidgets import QPushButton

    button = QPushButton(text)
    button.setProperty("flat", True)
    button.setToolTip(accessible_name)
    button.setAccessibleName(accessible_name)
    if object_name:
        button.setObjectName(object_name)
    return button


def section_title(text: str) -> Any:
    from PySide6.QtGui import QFont
    from PySide6.QtWidgets import QLabel

    label = QLabel(text)
    font = QFont()
    font.setPointSize(11)
    font.setBold(True)
    label.setFont(font)
    return label


def muted_label(text: str) -> Any:
    from PySide6.QtWidgets import QLabel

    label = QLabel(text)
    label.setProperty("muted", True)
    label.setWordWrap(True)
    return label


def horizontal_rule() -> Any:
    from PySide6.QtWidgets import QFrame

    line = QFrame()
    line.setFixedHeight(1)
    line.setStyleSheet("background:#D8E2EE;")
    return line
