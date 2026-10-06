from __future__ import annotations

import argparse
from pathlib import Path

STATES = (
    "UI-002",
    "UI-003",
    "UI-010",
    "UI-013",
    "UI-014",
    "UI-027",
    "UI-035",
    "UI-041",
)


def fit_rect(
    source_width: int,
    source_height: int,
    target_width: int,
    target_height: int,
) -> tuple[int, int]:
    scale = min(target_width / source_width, target_height / source_height)
    return max(1, int(source_width * scale)), max(1, int(source_height * scale))


def main() -> int:
    from PySide6.QtCore import QRect, Qt
    from PySide6.QtGui import QColor, QFont, QGuiApplication, QImage, QPainter

    _app = QGuiApplication([])
    parser = argparse.ArgumentParser(
        description="Build actual-vs-reference STEP 09 visual evidence"
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--actual", type=Path, default=Path("artifacts/step09_actual"))
    parser.add_argument("--output", type=Path, default=Path("artifacts/step09_visual"))
    args = parser.parse_args()

    root = args.root.resolve()
    actual_dir = (root / args.actual).resolve() if not args.actual.is_absolute() else args.actual
    output_dir = (root / args.output).resolve() if not args.output.is_absolute() else args.output
    reference_dir = root / "docs/ui_reference/raw"
    output_dir.mkdir(parents=True, exist_ok=True)

    pair_width = 1660
    pair_height = 1010
    image_width = 800
    image_height = 900
    header_height = 70
    contact = QImage(pair_width, pair_height * len(STATES), QImage.Format.Format_RGB32)
    contact.fill(QColor("#F4F7FB"))
    contact_painter = QPainter(contact)
    contact_painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

    for index, state in enumerate(STATES):
        reference = QImage(str(reference_dir / f"{state}.png"))
        actual = QImage(str(actual_dir / f"{state}_ACTUAL.png"))
        if reference.isNull() or actual.isNull():
            raise RuntimeError(f"Missing/invalid visual evidence for {state}")

        pair = QImage(pair_width, pair_height, QImage.Format.Format_RGB32)
        pair.fill(QColor("#F4F7FB"))
        painter = QPainter(pair)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        title_font = QFont("Segoe UI", 18)
        title_font.setBold(True)
        painter.setFont(title_font)
        painter.setPen(QColor("#172033"))
        painter.drawText(
            QRect(20, 12, pair_width - 40, 36),
            int(Qt.AlignmentFlag.AlignCenter),
            state,
        )

        label_font = QFont("Segoe UI", 11)
        label_font.setBold(True)
        painter.setFont(label_font)
        painter.drawText(
            QRect(20, 48, image_width, 28),
            int(Qt.AlignmentFlag.AlignCenter),
            "REFERENCE — frozen AAVC 1:1",
        )
        painter.drawText(
            QRect(840, 48, image_width, 28),
            int(Qt.AlignmentFlag.AlignCenter),
            "ACTUAL — PySide6 real widgets",
        )

        for image, x in ((reference, 20), (actual, 840)):
            width, height = fit_rect(
                image.width(),
                image.height(),
                image_width,
                image_height,
            )
            scaled = image.scaled(
                width,
                height,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            target_x = x + (image_width - width) // 2
            target_y = header_height + (image_height - height) // 2
            painter.fillRect(
                QRect(x, header_height, image_width, image_height),
                QColor("#FFFFFF"),
            )
            painter.drawImage(target_x, target_y, scaled)
            painter.setPen(QColor("#D8E2EE"))
            painter.drawRect(QRect(x, header_height, image_width, image_height))
        painter.end()

        pair_path = output_dir / f"{state}_REFERENCE_VS_ACTUAL.png"
        if not pair.save(str(pair_path), "PNG"):
            raise RuntimeError(f"Failed to save {pair_path}")
        contact_painter.drawImage(0, index * pair_height, pair)

    contact_painter.end()
    contact_path = output_dir / "S09_REPRESENTATIVE_REFERENCE_VS_ACTUAL_CONTACT.png"
    if not contact.save(str(contact_path), "PNG"):
        raise RuntimeError(f"Failed to save {contact_path}")
    print(contact_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
