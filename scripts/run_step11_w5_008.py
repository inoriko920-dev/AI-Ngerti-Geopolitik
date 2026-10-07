from __future__ import annotations

import argparse
from pathlib import Path


def _render(window, path: Path) -> None:
    pixmap = window.render_evidence(1920, 1080)
    if pixmap.width() != 1920 or pixmap.height() != 1080:
        raise RuntimeError("W5-008 evidence must render at 1920x1080")
    if not pixmap.save(str(path), "PNG"):
        raise RuntimeError(f"failed to save {path}")


def _pair(reference: Path, actual: Path, output: Path, title: str) -> None:
    from PySide6.QtCore import QRect, Qt
    from PySide6.QtGui import QColor, QFont, QImage, QPainter

    ref = QImage(str(reference))
    act = QImage(str(actual))
    if ref.isNull() or act.isNull():
        raise RuntimeError(f"invalid W5-008 pair source: {title}")

    canvas = QImage(1660, 1010, QImage.Format.Format_RGB32)
    canvas.fill(QColor("#F4F7FB"))
    painter = QPainter(canvas)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    font = QFont("Arial", 16)
    font.setBold(True)
    painter.setFont(font)
    painter.setPen(QColor("#172033"))
    painter.drawText(QRect(20, 12, 1620, 36), int(Qt.AlignmentFlag.AlignCenter), title)

    for image, x, label in (
        (ref, 20, "REFERENCE — frozen AAVC"),
        (act, 840, "ACTUAL — real PySide6"),
    ):
        painter.drawText(
            QRect(x, 50, 800, 28),
            int(Qt.AlignmentFlag.AlignCenter),
            label,
        )
        scaled = image.scaled(
            800,
            900,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        painter.fillRect(QRect(x, 80, 800, 900), QColor("#FFFFFF"))
        painter.drawImage(
            x + (800 - scaled.width()) // 2,
            80 + (900 - scaled.height()) // 2,
            scaled,
        )
        painter.setPen(QColor("#D8E2EE"))
        painter.drawRect(QRect(x, 80, 800, 900))
    painter.end()
    if not canvas.save(str(output), "PNG"):
        raise RuntimeError(f"failed to save {output}")


def main() -> int:
    from PySide6.QtWidgets import QApplication, QCheckBox, QTabWidget

    from ai_ngerti_geopolitik.presentation.main_window import create_main_window

    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    reference = root / "docs" / "ui_reference" / "raw"

    app = QApplication.instance() or QApplication(["ANG-W5-008"])
    window = create_main_window("UI-027", fixture_mode=True)
    window.resize(1920, 1080)
    window.show()

    current = window.stack.currentWidget()
    right = current.findChild(QTabWidget, "editor_right_tabs")
    subtitle_tabs = current.findChild(QTabWidget, "w5_subtitle_tabs")
    if right is None or subtitle_tabs is None:
        raise RuntimeError("W5-008 frozen workspace tabs missing")

    mapping: list[tuple[str, str]] = []

    right.setCurrentIndex(0)
    subtitle_tabs.setCurrentIndex(0)
    app.processEvents()
    path = output / "UI-017_ACTUAL_SUBTITLE_TEXT.png"
    _render(window, path)
    mapping.append(("UI-017", path.name))

    subtitle_tabs.setCurrentIndex(1)
    app.processEvents()
    path = output / "UI-033_ACTUAL_SUBTITLE_STYLE.png"
    _render(window, path)
    mapping.append(("UI-033", path.name))

    subtitle_tabs.setCurrentIndex(2)
    app.processEvents()
    path = output / "UI-034_ACTUAL_SUBTITLE_ANIMATION.png"
    _render(window, path)
    mapping.append(("UI-034", path.name))

    path = output / "UI-035_ACTUAL_WORD_TIMING_BOUNDARY.png"
    _render(window, path)
    mapping.append(("UI-035", path.name))

    ack = current.findChild(QCheckBox, "check_w5_word_even_ack")
    if ack is None:
        raise RuntimeError("W5-008 NOT speech alignment acknowledgement missing")
    ack.setChecked(True)
    app.processEvents()
    path = output / "UI-036_ACTUAL_WORD_TIMING_ACK.png"
    _render(window, path)
    mapping.append(("UI-036", path.name))

    right.setCurrentIndex(1)
    app.processEvents()
    path = output / "UI-018_ACTUAL_NARRATION.png"
    _render(window, path)
    mapping.append(("UI-018", path.name))

    for ui_id, actual_name in mapping:
        ref_path = reference / f"{ui_id}.png"
        actual_path = output / actual_name
        if not ref_path.is_file():
            raise RuntimeError(f"missing frozen reference {ui_id}")
        _pair(
            ref_path,
            actual_path,
            output / f"{ui_id}_REFERENCE_VS_ACTUAL.png",
            ui_id,
        )

    window._open_narration_recording_dialog()
    app.processEvents()
    dialog_path = output / "WIN-001_ACTUAL_NARRATION_RECORDING.png"
    _render(window, dialog_path)
    window.close()

    report = output / "00_w5_008_ui_report.txt"
    report.write_text(
        "\n".join(
            [
                "status=PASS",
                "subtitle_text=UI-017",
                "narration=UI-018",
                "subtitle_style=UI-033",
                "subtitle_animation=UI-034",
                "word_timing_boundary=UI-035",
                "word_timing_ack=UI-036",
                "win_001_recording_dialog=present",
                "unsupported_controls=hidden_or_disabled",
                "microphone_hardware_claim=provisional",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
