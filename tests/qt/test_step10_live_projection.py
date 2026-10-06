from pathlib import Path

from PySide6.QtGui import QColor, QPixmap
from PySide6.QtWidgets import QLabel

from ai_ngerti_geopolitik.application.ports import PreviewResult
from ai_ngerti_geopolitik.application.vertical_slice import TimelineClipView, TimelineProjection
from ai_ngerti_geopolitik.presentation.main_window import create_main_window


def test_live_projectstate_projection_updates_real_timeline_widgets(qtbot) -> None:
    window = create_main_window("UI-010", fixture_mode=True)
    qtbot.addWidget(window.window)
    window.show()

    projection = TimelineProjection(
        project_revision=8,
        track_id="V1",
        clips=(
            TimelineClipView("C001", "A001", 0, 150, 150),
            TimelineClipView("C002", "A001", 150, 210, 60),
        ),
    )
    window.apply_step10_timeline_projection(projection)

    current = window.stack.currentWidget()
    first = current.findChild(QLabel, "timeline_video_block_1")
    second = current.findChild(QLabel, "timeline_video_block_2")
    assert first is not None and first.text() == "C001  0-150f"
    assert second is not None and second.text() == "C002  150-210f"
    assert window.window.property("step10_project_revision") == 8
    window.close()


def test_real_preview_result_updates_real_qt_preview_canvas(qtbot, tmp_path: Path) -> None:
    window = create_main_window("UI-010", fixture_mode=True)
    qtbot.addWidget(window.window)
    window.show()

    preview_path = tmp_path / "preview.png"
    pixmap = QPixmap(320, 180)
    pixmap.fill(QColor("#24527A"))
    assert pixmap.save(str(preview_path), "PNG")

    result = PreviewResult(project_revision=8, timeline_frame=151, output_path=preview_path)
    window.apply_step10_preview(result)

    canvas = window.stack.currentWidget().findChild(QLabel, "preview_canvas")
    assert canvas is not None
    assert canvas.pixmap() is not None and not canvas.pixmap().isNull()
    assert canvas.property("step10_project_revision") == 8
    assert canvas.property("step10_timeline_frame") == 151
    window.close()
