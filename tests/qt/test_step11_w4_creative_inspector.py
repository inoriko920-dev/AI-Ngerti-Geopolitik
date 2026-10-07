from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QLabel,
    QLineEdit,
    QPushButton,
)

from ai_ngerti_geopolitik.application.ui_intents import (
    RecordingIntentSink,
    UiIntentType,
)
from ai_ngerti_geopolitik.presentation.editor_shell import (
    create_editor_shell,
)


def test_w4_creative_inspector_emits_semantic_intents(
    qtbot,
) -> None:
    sink = RecordingIntentSink()
    shell = create_editor_shell("single", sink)
    qtbot.addWidget(shell.root)
    shell.root.resize(1600, 900)
    shell.root.show()

    title_enabled = shell.root.findChild(
        QCheckBox,
        "creative_title_enabled",
    )
    title_text = shell.root.findChild(
        QLineEdit,
        "creative_title_text",
    )
    apply_title = shell.root.findChild(
        QPushButton,
        "btn_apply_creative_title",
    )
    assert title_enabled is not None
    assert title_text is not None
    assert apply_title is not None
    title_enabled.setChecked(True)
    title_text.setText("GEOPOLITIK")
    qtbot.mouseClick(
        apply_title,
        Qt.MouseButton.LeftButton,
    )
    assert sink.intents[-1].kind is UiIntentType.CREATIVE_SET_TITLE
    assert dict(sink.intents[-1].payload)["text"] == "GEOPOLITIK"

    transition = shell.root.findChild(
        QComboBox,
        "creative_transition_preset",
    )
    apply_transition = shell.root.findChild(
        QPushButton,
        "btn_apply_creative_transition",
    )
    assert transition is not None
    assert apply_transition is not None
    transition.setCurrentIndex(1)
    qtbot.mouseClick(
        apply_transition,
        Qt.MouseButton.LeftButton,
    )
    assert sink.intents[-1].kind is UiIntentType.CREATIVE_SET_TRANSITION
    assert dict(sink.intents[-1].payload)["preset"] == "fade_black"

    enter = shell.root.findChild(
        QComboBox,
        "creative_effect_enter",
    )
    exit_effect = shell.root.findChild(
        QComboBox,
        "creative_effect_exit",
    )
    apply_effects = shell.root.findChild(
        QPushButton,
        "btn_apply_creative_effects",
    )
    assert enter is not None
    assert exit_effect is not None
    assert apply_effects is not None
    enter.setCurrentText("Rise")
    exit_effect.setCurrentText("Fade")
    qtbot.mouseClick(
        apply_effects,
        Qt.MouseButton.LeftButton,
    )
    assert sink.intents[-1].kind is UiIntentType.CREATIVE_SET_EFFECTS
    payload = dict(sink.intents[-1].payload)
    assert payload["enter_effect"] == "Rise"
    assert payload["exit_effect"] == "Fade"

    unsupported = shell.root.findChild(
        QLabel,
        "label_w4_unsupported_effects",
    )
    assert unsupported is not None
    assert "Wipe" in unsupported.text()
    shell.root.close()
