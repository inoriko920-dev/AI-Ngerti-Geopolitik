from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton, QSlider

from ai_ngerti_geopolitik.application.ui_intents import RecordingIntentSink, UiIntentType
from ai_ngerti_geopolitik.application.vertical_slice import TimelineClipView, TimelineProjection
from ai_ngerti_geopolitik.presentation.main_window import create_main_window


def test_w2_transport_and_timeline_controls_emit_semantic_intents(qtbot) -> None:
    sink = RecordingIntentSink()
    window = create_main_window("UI-010", fixture_mode=True, intent_sink=sink)
    qtbot.addWidget(window.window)
    window.show()
    current = window.stack.currentWidget()

    for object_name, kind in (
        ("btn_playback_play", UiIntentType.PLAYBACK_PLAY),
        ("btn_playback_pause", UiIntentType.PLAYBACK_PAUSE),
        ("btn_timeline_split", UiIntentType.TIMELINE_SPLIT),
        ("btn_timeline_set_in", UiIntentType.TIMELINE_SET_IN),
        ("btn_timeline_set_out", UiIntentType.TIMELINE_SET_OUT),
        ("btn_timeline_add_marker", UiIntentType.TIMELINE_ADD_MARKER),
    ):
        button = current.findChild(QPushButton, object_name)
        assert button is not None
        qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
        assert sink.intents[-1].kind is kind

    scrubber = current.findChild(QSlider, "timeline_scrubber")
    assert scrubber is not None
    scrubber.setValue(42)
    scrubber.sliderReleased.emit()
    assert sink.intents[-1].kind is UiIntentType.PLAYBACK_SEEK
    assert dict(sink.intents[-1].payload)["frame"] == "42"
    window.close()


def test_w2_live_projection_updates_scrubber_frame_domain(qtbot) -> None:
    window = create_main_window("UI-010", fixture_mode=True)
    qtbot.addWidget(window.window)
    window.show()

    projection = TimelineProjection(
        project_revision=12,
        track_id="V1",
        clips=(
            TimelineClipView("C001", "A001", 0, 45, 45),
            TimelineClipView("C002", "A001", 45, 105, 60),
        ),
    )
    window.apply_step10_timeline_projection(projection)
    scrubber = window.stack.currentWidget().findChild(QSlider, "timeline_scrubber")
    assert scrubber is not None
    assert scrubber.minimum() == 0
    assert scrubber.maximum() == 104
    window.close()
