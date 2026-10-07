from __future__ import annotations

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QTabWidget,
    QWidget,
)

from ai_ngerti_geopolitik.application.ui_intents import RecordingIntentSink, UiIntentType
from ai_ngerti_geopolitik.presentation.editor_shell import create_editor_shell
from ai_ngerti_geopolitik.presentation.w6_ai_workspace import (
    AIAgentProjection,
    AIAgentUiState,
    project_ai_agent_state,
)


def _workspace(shell) -> QWidget:
    right = shell.root.findChild(QTabWidget, "editor_right_tabs")
    assert right is not None
    ai_index = next(
        (index for index in range(right.count()) if right.tabText(index) == "AI Agent"),
        -1,
    )
    assert ai_index >= 0
    right.setCurrentIndex(ai_index)
    workspace = shell.root.findChild(QWidget, "w6_ai_workspace")
    assert workspace is not None
    return workspace


def _diffs() -> tuple[str, ...]:
    return (
        "clip-1 · set_clip_effects · effects[enter=Fade] → effects[enter=Rise]",
        "clip-1 · set_clip_duration · duration=120f → duration=150f",
        "clip-1 · set_clip_transform · transform[scale=100%] → transform[scale=125%]",
        "clip-1 · set_clip_transition · transition=none/0f → transition=fade_black/45f",
        "clip-2 · set_clip_speed · speed=100%, duration=120f → speed=200%, duration=60f",
        "clip-2 · set_clip_transition · transition=none/0f → transition=fade_black/30f",
    )


def test_w7_l2_mode_emits_profile_only_when_explicitly_selected(qtbot) -> None:
    sink = RecordingIntentSink()
    shell = create_editor_shell("overview", sink)
    qtbot.addWidget(shell.root)
    workspace = _workspace(shell)

    mode = workspace.findChild(QComboBox, "combo_w6_ai_model")
    instruction = workspace.findChild(QLineEdit, "edit_w6_ai_instruction")
    send = workspace.findChild(QPushButton, "btn_w6_ai_send")
    assert mode is not None and instruction is not None and send is not None

    l2_index = mode.findData("l2_auto_edit")
    assert l2_index >= 0
    mode.setCurrentIndex(l2_index)
    instruction.setText("Rapikan pacing dan motion pada pilihan aktif.")
    qtbot.mouseClick(send, Qt.MouseButton.LeftButton)

    assert sink.intents[-1].kind is UiIntentType.AI_SUBMIT_PROMPT
    payload = dict(sink.intents[-1].payload)
    assert payload["profile"] == "l2_auto_edit"
    assert payload["instruction"] == "Rapikan pacing dan motion pada pilihan aktif."
    shell.root.close()


def test_w7_plan_reuses_w6_surface_and_renders_bounded_before_after_diffs(qtbot) -> None:
    sink = RecordingIntentSink()
    shell = create_editor_shell("overview", sink)
    qtbot.addWidget(shell.root)
    shell.root.show()
    workspace = _workspace(shell)

    projection = AIAgentProjection(
        state=AIAgentUiState.PLAN,
        summary="Enam perubahan Auto Edit L2.",
        diffs=_diffs(),
        request_id="REQ-W7-009-UI",
    )
    project_ai_agent_state(workspace, projection)

    items = workspace.findChild(QListWidget, "list_w6_plan_commands")
    state_label = workspace.findChild(QLabel, "label_w6_plan_state")
    capability = workspace.findChild(QLabel, "label_w6_plan_capability_safety")
    mode = workspace.findChild(QComboBox, "combo_w6_ai_model")
    approve = workspace.findChild(QPushButton, "btn_w6_plan_approve")
    apply_button = workspace.findChild(QPushButton, "btn_w6_plan_apply")
    assert items is not None and items.count() == 6
    assert "→" in items.item(0).text()
    assert "duration=120f" in items.item(1).text()
    assert state_label is not None
    assert "Auto Edit L2" in state_label.text()
    assert capability is not None and "Auto Edit L2" in capability.text()
    assert mode is not None and mode.currentData() == "l2_auto_edit"
    assert approve is not None and not approve.isHidden()
    assert apply_button is not None and apply_button.isHidden()

    qtbot.mouseClick(approve, Qt.MouseButton.LeftButton)
    assert sink.intents[-1].kind is UiIntentType.AI_APPROVE_PLAN

    project_ai_agent_state(
        workspace,
        AIAgentProjection(
            state=AIAgentUiState.APPROVAL,
            summary=projection.summary,
            diffs=projection.diffs,
            request_id=projection.request_id,
        ),
    )
    assert approve.isHidden()
    assert not apply_button.isHidden()
    qtbot.mouseClick(apply_button, Qt.MouseButton.LeftButton)
    assert sink.intents[-1].kind is UiIntentType.AI_APPLY_PLAN
    shell.root.close()


def test_w7_diff_projection_is_bounded_to_schema_command_cap() -> None:
    with pytest.raises(ValueError, match="cannot exceed 40"):
        AIAgentProjection(
            state=AIAgentUiState.PLAN,
            diffs=tuple(f"diff-{index}" for index in range(41)),
        )
