from __future__ import annotations

from typing import Any


def _checker(painter: Any, width: int, height: int) -> None:
    from PySide6.QtGui import QColor

    size = 12
    for y in range(0, height, size):
        for x in range(0, width, size):
            color = QColor("#F8FAFC") if (x // size + y // size) % 2 == 0 else QColor("#E8EEF5")
            painter.fillRect(x, y, size, size, color)


def asset_pixmap(subject: str, width: int = 150, height: int = 86) -> Any:
    from PySide6.QtCore import QRectF, Qt
    from PySide6.QtGui import QColor, QFont, QPainter, QPen, QPixmap

    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    _checker(painter, width, height)

    palette = {
        "pohon": "#45A764",
        "rumah": "#D95C4F",
        "awan": "#94A3B8",
        "mobil": "#E34E46",
        "anak": "#2D7FE7",
        "tokoh": "#E26D8C",
        "matahari": "#FFD447",
        "gunung": "#587C9E",
        "papan": "#A97449",
        "anjing": "#B87342",
        "kucing": "#F0A04B",
        "burung": "#4E7FA9",
        "semak": "#4FAE68",
        "pagar": "#8B5E3C",
        "lampu": "#F4C95D",
    }
    painter.setPen(QPen(QColor("#29445E"), 2))
    painter.setBrush(QColor(palette.get(subject.lower(), "#64748B")))
    painter.drawRoundedRect(QRectF(width * 0.27, height * 0.18, width * 0.46, height * 0.48), 12, 12)
    painter.setPen(QColor("#172033"))
    font = QFont("Segoe UI", max(8, int(height * 0.12)))
    font.setBold(True)
    painter.setFont(font)
    painter.drawText(
        QRectF(4, height * 0.68, width - 8, height * 0.26),
        int(Qt.AlignmentFlag.AlignCenter),
        subject,
    )
    painter.end()
    return pixmap


def _draw_village(painter: Any, width: int, height: int) -> None:
    from PySide6.QtCore import QPointF, QRectF
    from PySide6.QtGui import QColor, QLinearGradient, QPen, QPolygonF

    gradient = QLinearGradient(0, 0, 0, height)
    gradient.setColorAt(0.0, QColor("#A7DAFF"))
    gradient.setColorAt(0.58, QColor("#EAF6D6"))
    gradient.setColorAt(1.0, QColor("#A6D27E"))
    painter.fillRect(0, 0, width, height, gradient)

    painter.setPen(QPen(QColor("#7697AC"), 2))
    painter.setBrush(QColor("#6E91AA"))
    painter.drawPolygon(
        QPolygonF(
            [
                QPointF(0, height * 0.57),
                QPointF(width * 0.22, height * 0.20),
                QPointF(width * 0.42, height * 0.57),
            ]
        )
    )
    painter.setBrush(QColor("#F8E7C7"))
    painter.drawRect(QRectF(width * 0.08, height * 0.50, width * 0.24, height * 0.22))
    painter.setBrush(QColor("#C65D49"))
    painter.drawPolygon(
        QPolygonF(
            [
                QPointF(width * 0.05, height * 0.50),
                QPointF(width * 0.20, height * 0.37),
                QPointF(width * 0.35, height * 0.50),
            ]
        )
    )
    painter.setBrush(QColor("#5A9C55"))
    painter.drawEllipse(QPointF(width * 0.78, height * 0.48), width * 0.11, height * 0.10)
    painter.fillRect(
        QRectF(width * 0.765, height * 0.49, width * 0.028, height * 0.28),
        QColor("#7A543B"),
    )
    painter.setPen(QPen(QColor("#B88B5A"), 5))
    fence_y = height * 0.74
    for x in range(int(width * 0.05), int(width * 0.94), max(20, int(width * 0.06))):
        painter.drawLine(QPointF(x, fence_y - 24), QPointF(x, fence_y + 26))
    painter.drawLine(QPointF(width * 0.04, fence_y), QPointF(width * 0.95, fence_y))


def _draw_animal(
    painter: Any,
    x: float,
    y: float,
    scale: float,
    kind: str,
    *,
    selected: bool = False,
    label: str = "",
) -> None:
    from PySide6.QtCore import QPointF, QRectF, Qt
    from PySide6.QtGui import QColor, QPen, QPolygonF

    fur = QColor("#F0A04B") if kind == "cat" else QColor("#B87342")
    painter.setPen(QPen(QColor("#5B3A2A"), max(1.0, 2.0 * scale)))
    painter.setBrush(fur)
    painter.drawEllipse(QPointF(x, y + 30 * scale), 38 * scale, 30 * scale)
    painter.drawEllipse(QPointF(x, y - 14 * scale), 31 * scale, 28 * scale)
    if kind == "cat":
        painter.drawPolygon(
            QPolygonF(
                [
                    QPointF(x - 26 * scale, y - 25 * scale),
                    QPointF(x - 16 * scale, y - 51 * scale),
                    QPointF(x - 6 * scale, y - 25 * scale),
                ]
            )
        )
        painter.drawPolygon(
            QPolygonF(
                [
                    QPointF(x + 26 * scale, y - 25 * scale),
                    QPointF(x + 16 * scale, y - 51 * scale),
                    QPointF(x + 6 * scale, y - 25 * scale),
                ]
            )
        )
    painter.setBrush(QColor("#FFFFFF"))
    painter.drawEllipse(QPointF(x - 10 * scale, y - 14 * scale), 7 * scale, 8 * scale)
    painter.drawEllipse(QPointF(x + 10 * scale, y - 14 * scale), 7 * scale, 8 * scale)
    painter.setBrush(QColor("#111827"))
    painter.drawEllipse(QPointF(x - 10 * scale, y - 13 * scale), 2.5 * scale, 3.5 * scale)
    painter.drawEllipse(QPointF(x + 10 * scale, y - 13 * scale), 2.5 * scale, 3.5 * scale)
    if selected:
        painter.setPen(QPen(QColor("#2563EB"), 3))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(QRectF(x - 58 * scale, y - 66 * scale, 116 * scale, 134 * scale))
        if label:
            painter.fillRect(
                QRectF(x - 58 * scale, y - 86 * scale, 62 * scale, 20 * scale),
                QColor("#2563EB"),
            )
            painter.setPen(QColor("#FFFFFF"))
            painter.drawText(
                QRectF(x - 56 * scale, y - 84 * scale, 58 * scale, 16 * scale),
                int(Qt.AlignmentFlag.AlignCenter),
                label,
            )


def scene_pixmap(mode: str, width: int = 1280, height: int = 720) -> Any:
    from PySide6.QtCore import QPointF, QRectF, Qt
    from PySide6.QtGui import QColor, QFont, QPainter, QPixmap

    pixmap = QPixmap(width, height)
    pixmap.fill(QColor("#FFFFFF"))
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    if mode == "overview":
        painter.fillRect(0, 0, width, height, QColor("#F6F2E8"))
        title = QFont("Segoe UI", int(height * 0.055))
        title.setBold(True)
        painter.setFont(title)
        painter.setPen(QColor("#143E61"))
        painter.drawText(
            QRectF(width * 0.07, height * 0.25, width * 0.40, height * 0.10),
            int(Qt.AlignmentFlag.AlignLeft),
            "INDONESIA",
        )
        subtitle = QFont("Segoe UI", int(height * 0.04))
        subtitle.setBold(True)
        painter.setFont(subtitle)
        painter.setPen(QColor("#C9272C"))
        painter.drawText(
            QRectF(width * 0.07, height * 0.36, width * 0.45, height * 0.08),
            int(Qt.AlignmentFlag.AlignLeft),
            "NEGERI KEPULAUAN",
        )
        painter.setPen(Qt.PenStyle.NoPen)
        for x, y, color in [
            (0.61, 0.27, "#2B8C4B"),
            (0.72, 0.31, "#4FAE68"),
            (0.64, 0.47, "#2E9EAA"),
            (0.78, 0.52, "#72C7D9"),
        ]:
            painter.setBrush(QColor(color))
            painter.drawEllipse(QPointF(width * x, height * y), width * 0.09, height * 0.08)
    else:
        _draw_village(painter, width, height)
        if mode == "single":
            _draw_animal(
                painter,
                width * 0.56,
                height * 0.62,
                1.65,
                "cat",
                selected=True,
                label="A021",
            )
        elif mode == "double":
            _draw_animal(
                painter,
                width * 0.46,
                height * 0.63,
                1.38,
                "cat",
                selected=True,
                label="A032",
            )
            _draw_animal(
                painter,
                width * 0.66,
                height * 0.63,
                1.38,
                "dog",
                selected=True,
                label="A033",
            )
        elif mode == "subtitle":
            _draw_animal(painter, width * 0.56, height * 0.62, 1.35, "cat")
            painter.fillRect(
                QRectF(width * 0.23, height * 0.76, width * 0.54, height * 0.14),
                QColor(15, 23, 42, 220),
            )
            painter.setPen(QColor("#FFFFFF"))
            font = QFont("Segoe UI", int(height * 0.026))
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(
                QRectF(width * 0.25, height * 0.775, width * 0.50, height * 0.11),
                int(Qt.AlignmentFlag.AlignCenter),
                "Pagi yang cerah di desa Bromo,\nseekor kucing kecil berjalan di taman.",
            )
    painter.end()
    return pixmap


def project_thumb_pixmap(index: int, width: int = 150, height: int = 78) -> Any:
    from PySide6.QtCore import QPointF, Qt
    from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPixmap, QPolygonF

    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    palettes = [
        ("#8CC9F4", "#D7E8C1"),
        ("#E8D8C6", "#B7845A"),
        ("#3F4F87", "#E06A5E"),
        ("#7ED1E6", "#5BA968"),
    ]
    first, second = palettes[index % len(palettes)]
    gradient = QLinearGradient(0, 0, width, height)
    gradient.setColorAt(0, QColor(first))
    gradient.setColorAt(1, QColor(second))
    painter.fillRect(0, 0, width, height, gradient)
    painter.setBrush(QColor("#334155"))
    painter.drawPolygon(
        QPolygonF(
            [
                QPointF(width * 0.08, height * 0.90),
                QPointF(width * 0.45, height * 0.20),
                QPointF(width * 0.90, height * 0.90),
            ]
        )
    )
    painter.end()
    return pixmap
