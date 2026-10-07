from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QLabel,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QTextEdit,
)

from ai_ngerti_geopolitik.application.ui_intents import (
    RecordingIntentSink,
    UiIntentType,
)
from ai_ngerti_geopolitik.presentation.editor_shell import create_editor_shell
from ai_ngerti_geopolitik.presentation.main_window import create_main_window


def test_w5_subtitle_text_workspace_emits_semantic_editing_intents(qtbot) -> None:
    sink = RecordingIntentSink()
    shell = create_editor_shell("subtitle", sink)
    qtbot.addWidget(shell.root)
    shell.root.resize(1600, 900)
    shell.root.show()

    right = shell.root.findChild(QTabWidget, "editor_right_tabs")
    tabs = shell.root.findChild(QTabWidget, "w5_subtitle_tabs")
    text = shell.root.findChild(QTextEdit, "w5_subtitle_text")
    apply_cue = shell.root.findChild(QPushButton, "btn_w5_apply_cue")
    split = shell.root.findChild(QPushButton, "btn_w5_split_cue")
    merge = shell.root.findChild(QPushButton, "btn_w5_merge_cue")
    reload_srt = shell.root.findChild(QPushButton, "btn_w5_reload_srt")

    assert right is not None
    assert [right.tabText(i) for i in range(right.count())] == [
        "Subtitle",
        "Narasi",
        "AI Agent",
    ]
    assert tabs is not None
    assert [tabs.tabText(i) for i in range(tabs.count())] == ["Teks", "Gaya", "Animasi"]
    assert text is not None
    assert apply_cue is not None
    assert split is not None
    assert merge is not None
    assert reload_srt is not None

    text.setPlainText("Subtitle final yang diedit.")
    qtbot.mouseClick(apply_cue, Qt.MouseButton.LeftButton)
    assert sink.intents[-1].kind is UiIntentType.SUBTITLE_EDIT_CUE
    assert dict(sink.intents[-1].payload)["text"] == "Subtitle final yang diedit."

    qtbot.mouseClick(split, Qt.MouseButton.LeftButton)
    assert sink.intents[-1].kind is UiIntentType.SPLIT_CUE
    qtbot.mouseClick(merge, Qt.MouseButton.LeftButton)
    assert sink.intents[-1].kind is UiIntentType.MERGE_CUE
    qtbot.mouseClick(reload_srt, Qt.MouseButton.LeftButton)
    assert sink.intents[-1].kind is UiIntentType.RELOAD_SRT
    shell.root.close()


def test_w5_style_exposes_only_render_qualified_fonts(qtbot) -> None:
    sink = RecordingIntentSink()
    shell = create_editor_shell("subtitle", sink)
    qtbot.addWidget(shell.root)

    tabs = shell.root.findChild(QTabWidget, "w5_subtitle_tabs")
    font = shell.root.findChild(QComboBox, "combo_w5_subtitle_font")
    size = shell.root.findChild(QSpinBox, "spin_w5_subtitle_font_size")
    apply_style = shell.root.findChild(QPushButton, "btn_w5_apply_subtitle_style")
    assert tabs is not None
    tabs.setCurrentIndex(1)
    assert font is not None
    assert [font.itemText(i) for i in range(font.count())] == ["Arial", "Segoe UI"]
    assert size is not None
    assert apply_style is not None

    font.setCurrentText("Segoe UI")
    size.setValue(64)
    qtbot.mouseClick(apply_style, Qt.MouseButton.LeftButton)
    assert sink.intents[-1].kind is UiIntentType.SUBTITLE_SET_STYLE
    payload = dict(sink.intents[-1].payload)
    assert payload["font_family"] == "Segoe UI"
    assert payload["font_size"] == "64"
    shell.root.close()


def test_w5_animation_hides_unqualified_presets_and_emits_only_supported(qtbot) -> None:
    sink = RecordingIntentSink()
    shell = create_editor_shell("subtitle", sink)
    qtbot.addWidget(shell.root)

    tabs = shell.root.findChild(QTabWidget, "w5_subtitle_tabs")
    combo = shell.root.findChild(QComboBox, "combo_w5_subtitle_animation")
    apply_animation = shell.root.findChild(QPushButton, "btn_w5_apply_subtitle_animation")
    unsupported = shell.root.findChild(QLabel, "label_w5_unqualified_subtitle_animations")
    assert tabs is not None
    tabs.setCurrentIndex(2)
    assert combo is not None
    values = [combo.itemData(i) for i in range(combo.count())]
    assert values == ["none", "Fade", "Pop", "Slide Up", "Clean Documentary"]
    assert "Karaoke Highlight" not in values
    assert unsupported is not None and "Karaoke Highlight" in unsupported.text()
    assert apply_animation is not None

    combo.setCurrentIndex(2)
    qtbot.mouseClick(apply_animation, Qt.MouseButton.LeftButton)
    assert sink.intents[-1].kind is UiIntentType.SUBTITLE_SET_ANIMATION
    assert dict(sink.intents[-1].payload)["preset"] == "Pop"
    shell.root.close()


def test_w5_even_word_distribution_requires_explicit_not_speech_alignment_ack(qtbot) -> None:
    sink = RecordingIntentSink()
    shell = create_editor_shell("subtitle", sink)
    qtbot.addWidget(shell.root)

    label = shell.root.findChild(QLabel, "label_w5_not_speech_alignment")
    ack = shell.root.findChild(QCheckBox, "check_w5_word_even_ack")
    button = shell.root.findChild(QPushButton, "btn_w5_word_even")
    highlight = shell.root.findChild(QLabel, "label_w5_word_highlight_unavailable")
    assert label is not None and "NOT speech alignment" in label.text()
    assert ack is not None
    assert button is not None and not button.isEnabled()
    assert highlight is not None and "belum render-qualified" in highlight.text()

    ack.setChecked(True)
    assert button.isEnabled()
    qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
    assert sink.intents[-1].kind is UiIntentType.SUBTITLE_SET_WORD_TIMING
    payload = dict(sink.intents[-1].payload)
    assert payload["mode"] == "even_not_speech_alignment"
    assert payload["acknowledged"] == "true"
    shell.root.close()


def test_w5_narration_workspace_emits_controls_and_record_open_intent(qtbot) -> None:
    sink = RecordingIntentSink()
    shell = create_editor_shell("subtitle", sink)
    qtbot.addWidget(shell.root)

    right = shell.root.findChild(QTabWidget, "editor_right_tabs")
    gain = shell.root.findChild(QSpinBox, "spin_w5_narration_gain")
    muted = shell.root.findChild(QCheckBox, "check_w5_narration_muted")
    apply_narration = shell.root.findChild(QPushButton, "btn_w5_apply_narration")
    record = shell.root.findChild(QPushButton, "btn_w5_open_recording")
    provisional = shell.root.findChild(QLabel, "label_w5_microphone_provisional")
    assert right is not None
    right.setCurrentIndex(1)
    assert gain is not None
    assert muted is not None
    assert apply_narration is not None
    assert record is not None
    assert provisional is not None and "provisional" in provisional.text()

    gain.setValue(135)
    muted.setChecked(True)
    qtbot.mouseClick(apply_narration, Qt.MouseButton.LeftButton)
    assert sink.intents[-1].kind is UiIntentType.NARRATION_SET_CONTROLS
    payload = dict(sink.intents[-1].payload)
    assert payload["gain_percent"] == "135"
    assert payload["muted"] == "true"

    qtbot.mouseClick(record, Qt.MouseButton.LeftButton)
    assert sink.intents[-1].kind is UiIntentType.RECORD_NARRATION
    shell.root.close()


def test_w5_recording_dialog_is_device_gated_and_semantic(qtbot) -> None:
    sink = RecordingIntentSink()
    window = create_main_window("UI-027", fixture_mode=True, intent_sink=sink)
    qtbot.addWidget(window.window)
    window.show()

    action = window.window.findChild(QAction, "action_record_narration")
    assert action is not None
    action.trigger()
    assert sink.intents[-1].kind is UiIntentType.RECORD_NARRATION

    start = window._active_dialog.findChild(QPushButton, "btn_w5_start_recording")
    cancel = window._active_dialog.findChild(QPushButton, "btn_w5_cancel_recording")
    status = window._active_dialog.findChild(QLabel, "label_w5_recording_hardware_status")
    assert start is not None and not start.isEnabled()
    assert cancel is not None
    assert status is not None and "belum terverifikasi" in status.text()

    window.apply_microphone_devices((("MIC1", "Test Microphone"),))
    assert start.isEnabled()
    qtbot.mouseClick(start, Qt.MouseButton.LeftButton)
    assert sink.intents[-1].kind is UiIntentType.MICROPHONE_START_RECORDING
    assert dict(sink.intents[-1].payload)["device_id"] == "MIC1"

    qtbot.mouseClick(cancel, Qt.MouseButton.LeftButton)
    assert sink.intents[-1].kind is UiIntentType.MICROPHONE_CANCEL_RECORDING
    window.close()
