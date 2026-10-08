from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QLineEdit, QPushButton, QSlider

from ai_ngerti_geopolitik.application.export_capabilities import (
    ExportCapabilities,
    ExportToolchain,
)
from ai_ngerti_geopolitik.application.ui_intents import RecordingIntentSink
from ai_ngerti_geopolitik.presentation.dialogs import create_export_dialog


def test_unwired_export_dialog_is_fail_closed(qtbot) -> None:
    sink = RecordingIntentSink()
    dialog = create_export_dialog(intent_sink=sink)
    qtbot.addWidget(dialog)
    dialog.show()
    render = dialog.findChild(QPushButton, "btn_export_render")
    codec = dialog.findChild(QComboBox, "combo_export_format")
    directory = dialog.findChild(QLineEdit, "field_export_directory")
    assert render is not None and not render.isEnabled()
    assert codec is not None and not codec.isEnabled()
    assert not codec.model().item(1).isEnabled()
    assert directory is not None and str(Path.home()) in directory.text()
    assert "Liburan ke Bromo" not in directory.text()
    for name in (
        "combo_export_resolution",
        "combo_export_fps",
        "combo_export_preset",
        "combo_export_sharpen",
        "combo_export_subtitle",
    ):
        control = dialog.findChild(QComboBox, name)
        assert control is not None and not control.isEnabled()
    slider = dialog.findChild(QSlider, "slider_export_quality")
    assert slider is not None and not slider.isEnabled()
    qtbot.mouseClick(render, Qt.MouseButton.LeftButton)
    assert not sink.intents
    dialog.close()


def test_discovered_binary_is_not_fake_render_success(qtbot) -> None:
    toolchain = ExportToolchain(
        ffmpeg_found=True,
        ffprobe_found=True,
        h264_encoder_found=True,
        h265_encoder_found=True,
        aac_encoder_found=True,
    )
    dialog = create_export_dialog(capabilities=ExportCapabilities(toolchain=toolchain))
    qtbot.addWidget(dialog)
    dialog.show()
    codec = dialog.findChild(QComboBox, "combo_export_format")
    render = dialog.findChild(QPushButton, "btn_export_render")
    assert codec is not None and codec.isEnabled()
    assert not codec.model().item(1).isEnabled()
    assert render is not None and not render.isEnabled()
    assert "belum" in render.toolTip().lower()
    dialog.close()
