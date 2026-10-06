from PySide6.QtCore import Qt
from PySide6.QtWidgets import QCheckBox, QPushButton, QSpinBox

from ai_ngerti_geopolitik.application.ui_intents import RecordingIntentSink, UiIntentType
from ai_ngerti_geopolitik.presentation.editor_shell import create_editor_shell


def test_w3_property_inspector_emits_semantic_video_audio_color_speed_intents(qtbot) -> None:
    sink = RecordingIntentSink()
    shell = create_editor_shell("single", sink)
    qtbot.addWidget(shell.root)
    shell.root.resize(1600, 900)
    shell.root.show()

    position_x = shell.root.findChild(QSpinBox, "prop_video_position_x")
    apply_video = shell.root.findChild(QPushButton, "btn_apply_video_properties")
    assert position_x is not None and apply_video is not None
    position_x.setValue(42)
    qtbot.mouseClick(apply_video, Qt.MouseButton.LeftButton)
    assert sink.intents[-1].kind is UiIntentType.PROPERTY_SET_VIDEO
    assert dict(sink.intents[-1].payload)["position_x"] == "42"
    assert dict(sink.intents[-1].payload)["clip_id"] == "C001"

    tabs = shell.root.findChild(type(shell.right_tabs), "tabs_w3_properties")
    assert tabs is not None

    audio_button = shell.root.findChild(QPushButton, "btn_apply_audio_properties")
    assert audio_button is not None
    qtbot.mouseClick(audio_button, Qt.MouseButton.LeftButton)
    assert sink.intents[-1].kind is UiIntentType.PROPERTY_SET_AUDIO

    color_button = shell.root.findChild(QPushButton, "btn_apply_color_properties")
    assert color_button is not None
    qtbot.mouseClick(color_button, Qt.MouseButton.LeftButton)
    assert sink.intents[-1].kind is UiIntentType.PROPERTY_SET_COLOR

    speed_button = shell.root.findChild(QPushButton, "btn_apply_speed_properties")
    speed = shell.root.findChild(QSpinBox, "prop_speed_rate")
    assert speed_button is not None and speed is not None
    speed.setValue(200)
    qtbot.mouseClick(speed_button, Qt.MouseButton.LeftButton)
    assert sink.intents[-1].kind is UiIntentType.PROPERTY_SET_SPEED
    assert dict(sink.intents[-1].payload)["rate_percent"] == "200"

    reverse = shell.root.findChild(QCheckBox, "check_reverse_disabled")
    assert reverse is not None
    assert reverse.isEnabled() is False
    assert "qualification" in reverse.toolTip().lower()
    shell.root.close()
