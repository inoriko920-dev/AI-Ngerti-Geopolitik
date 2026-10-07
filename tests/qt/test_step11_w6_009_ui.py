from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QWidget,
)

from ai_ngerti_geopolitik.application.ai_contracts import MASKED_CREDENTIAL_VALUE
from ai_ngerti_geopolitik.application.ui_intents import RecordingIntentSink, UiIntentType
from ai_ngerti_geopolitik.presentation.editor_shell import create_editor_shell
from ai_ngerti_geopolitik.presentation.main_window import create_main_window
from ai_ngerti_geopolitik.presentation.w6_ai_workspace import (
    AIAgentProjection,
    AIAgentUiState,
    CredentialSlotProjection,
    create_provider_credentials_dialog,
    project_ai_agent_state,
    project_credential_slots,
)


def _workspace(shell) -> QWidget:
    widget = shell.root.findChild(QWidget, "w6_ai_workspace")
    assert widget is not None
    return widget


def test_w6_ai_workspace_replaces_placeholder_with_director_and_agent_l1_only(qtbot) -> None:
    sink = RecordingIntentSink()
    shell = create_editor_shell("overview", sink)
    qtbot.addWidget(shell.root)
    workspace = _workspace(shell)

    tabs = workspace.findChild(QTabWidget, "w6_ai_subtabs")
    capabilities = workspace.findChild(QLabel, "label_w6_l1_capabilities")
    assert tabs is not None
    assert [tabs.tabText(i) for i in range(tabs.count())] == ["AI Otomatis", "AI Agent"]
    assert capabilities is not None
    text = capabilities.text()
    for supported in (
        "Fade",
        "Pop",
        "Breathe",
        "Stomp",
        "Tumble",
        "Tectonic",
        "Rise",
        "Pan",
        "Drift",
    ):
        assert supported in text
    for unsupported in ("Blur", "Neon", "Sketch", "Gradient", "Wipe"):
        assert unsupported not in text
    shell.root.close()


def test_w6_director_and_ready_chat_emit_semantic_intents(qtbot) -> None:
    sink = RecordingIntentSink()
    shell = create_editor_shell("overview", sink)
    qtbot.addWidget(shell.root)
    workspace = _workspace(shell)

    scope = workspace.findChild(QComboBox, "combo_w6_ai_director_scope")
    auto = workspace.findChild(QPushButton, "btn_w6_ai_auto_plan")
    assert scope is not None and auto is not None
    scope.setCurrentIndex(1)
    qtbot.mouseClick(auto, Qt.MouseButton.LeftButton)
    assert sink.intents[-1].kind is UiIntentType.AUTO_AI
    assert dict(sink.intents[-1].payload)["scope"] == "selected_scene"

    project_ai_agent_state(
        workspace,
        AIAgentProjection(
            state=AIAgentUiState.READY,
            scope_text="Scene 01 · clip-1",
            request_id="REQ-UI",
        ),
    )
    instruction = workspace.findChild(QLineEdit, "edit_w6_ai_instruction")
    send = workspace.findChild(QPushButton, "btn_w6_ai_send")
    assert instruction is not None and send is not None
    instruction.setText("Gunakan efek masuk yang lembut.")
    qtbot.mouseClick(send, Qt.MouseButton.LeftButton)
    assert sink.intents[-1].kind is UiIntentType.AI_SUBMIT_PROMPT
    payload = dict(sink.intents[-1].payload)
    assert payload["instruction"] == "Gunakan efek masuk yang lembut."
    assert "clip-1" in payload["scope"]
    shell.root.close()


def test_w6_plan_approval_and_apply_buttons_are_state_gated(qtbot) -> None:
    sink = RecordingIntentSink()
    shell = create_editor_shell("overview", sink)
    qtbot.addWidget(shell.root)
    shell.root.show()
    workspace = _workspace(shell)

    projection = AIAgentProjection(
        state=AIAgentUiState.PLAN,
        summary="Dua perubahan efek L1.",
        commands=("clip-1: Fade → Rise", "clip-2: intensitas 90 → 115"),
        request_id="REQ-PLAN",
    )
    project_ai_agent_state(workspace, projection)
    items = workspace.findChild(QListWidget, "list_w6_plan_commands")
    approve = workspace.findChild(QPushButton, "btn_w6_plan_approve")
    apply_button = workspace.findChild(QPushButton, "btn_w6_plan_apply")
    reject = workspace.findChild(QPushButton, "btn_w6_plan_reject")
    assert items is not None and items.count() == 2
    assert approve is not None and approve.isVisibleTo(workspace)
    assert apply_button is not None and not apply_button.isVisibleTo(workspace)
    assert reject is not None

    qtbot.mouseClick(approve, Qt.MouseButton.LeftButton)
    assert sink.intents[-1].kind is UiIntentType.AI_APPROVE_PLAN
    assert dict(sink.intents[-1].payload)["request_id"] == "REQ-PLAN"

    project_ai_agent_state(
        workspace,
        AIAgentProjection(
            state=AIAgentUiState.APPROVAL,
            summary="Dua perubahan efek L1.",
            commands=projection.commands,
            request_id="REQ-PLAN",
        ),
    )
    assert not approve.isVisibleTo(workspace)
    assert apply_button.isVisibleTo(workspace)
    qtbot.mouseClick(apply_button, Qt.MouseButton.LeftButton)
    assert sink.intents[-1].kind is UiIntentType.AI_APPLY_PLAN

    qtbot.mouseClick(reject, Qt.MouseButton.LeftButton)
    assert sink.intents[-1].kind is UiIntentType.AI_REJECT_PLAN
    shell.root.close()


def test_w6_applying_success_and_undo_remain_semantic(qtbot) -> None:
    sink = RecordingIntentSink()
    shell = create_editor_shell("overview", sink)
    qtbot.addWidget(shell.root)
    workspace = _workspace(shell)

    project_ai_agent_state(
        workspace,
        AIAgentProjection(
            state=AIAgentUiState.APPLYING,
            request_id="REQ-APPLY",
        ),
    )
    cancel = workspace.findChild(QPushButton, "btn_w6_cancel_job")
    assert cancel is not None
    qtbot.mouseClick(cancel, Qt.MouseButton.LeftButton)
    assert sink.intents[-1].kind is UiIntentType.AI_CANCEL_JOB

    project_ai_agent_state(
        workspace,
        AIAgentProjection(
            state=AIAgentUiState.SUCCESS,
            message="2 perubahan diterapkan dalam 1 transaksi.",
            request_id="REQ-APPLY",
        ),
    )
    undo = workspace.findChild(QPushButton, "btn_w6_ai_undo")
    assert undo is not None
    qtbot.mouseClick(undo, Qt.MouseButton.LeftButton)
    assert sink.intents[-1].kind is UiIntentType.UNDO
    shell.root.close()


def test_w6_error_states_are_distinct_and_keep_manual_fallback_visible(qtbot) -> None:
    shell = create_editor_shell("overview", RecordingIntentSink())
    qtbot.addWidget(shell.root)
    workspace = _workspace(shell)
    fallback = workspace.findChild(QLabel, "label_w6_manual_fallback")
    message = workspace.findChild(QLabel, "label_w6_error_message")
    assert fallback is not None and message is not None

    cases = (
        (AIAgentUiState.PROVIDER_ERROR, "NO_CREDENTIAL", "credential"),
        (AIAgentUiState.LOCK_CONFLICT, "", "terkunci"),
        (AIAgentUiState.STALE, "", "berubah"),
    )
    for state, error_code, expected in cases:
        project_ai_agent_state(
            workspace,
            AIAgentProjection(state=state, error_code=error_code),
        )
        assert expected.lower() in message.text().lower()
        assert "manual tetap aktif" in fallback.text().lower()
    shell.root.close()


def test_w6_main_window_ai_menu_opens_real_workspace_and_credentials(qtbot) -> None:
    sink = RecordingIntentSink()
    window = create_main_window("UI-010", fixture_mode=True, intent_sink=sink)
    qtbot.addWidget(window.window)
    window.show()

    action = window.window.findChild(QAction, "action_open_ai_agent")
    credentials = window.window.findChild(QAction, "action_open_ai_credentials")
    assert action is not None and credentials is not None
    action.trigger()
    assert sink.intents[-1].kind is UiIntentType.AI_OPEN_AGENT
    current = window.stack.currentWidget()
    right = current.findChild(QTabWidget, "editor_right_tabs")
    assert right is not None and right.tabText(right.currentIndex()) == "AI Agent"

    credentials.trigger()
    assert sink.intents[-1].kind is UiIntentType.OPEN_AI_CREDENTIALS
    assert window._active_dialog is not None
    assert window._active_dialog.objectName() == "w6_credential_dialog"
    window.close()


def test_w6_credential_manager_masks_projection_and_never_puts_raw_in_ui_intent(qtbot) -> None:
    sink = RecordingIntentSink()
    submitted: list[object] = []

    def submit(slot_id: int, label: str, wrapped) -> None:
        submitted.append((slot_id, label, wrapped))

    dialog = create_provider_credentials_dialog(None, sink, secret_submit_sink=submit)
    qtbot.addWidget(dialog)
    dialog.show()
    project_credential_slots(
        dialog,
        (
            CredentialSlotProjection(1, "Gemini Utama", True, "HEALTHY"),
            CredentialSlotProjection(100, "Cadangan", False, "UNTESTED"),
        ),
    )

    mask = dialog.findChild(QLabel, "label_w6_credential_mask_001")
    assert mask is not None and mask.text() == MASKED_CREDENTIAL_VALUE

    raw_value = "runtime-ui-value"
    slot = dialog.findChild(QSpinBox, "spin_w6_credential_slot")
    label = dialog.findChild(QLineEdit, "edit_w6_credential_label")
    key = dialog.findChild(QLineEdit, "edit_w6_credential_value")
    save = dialog.findChild(QPushButton, "btn_w6_credential_save")
    assert slot is not None and label is not None and key is not None and save is not None
    slot.setValue(1)
    label.setText("Gemini UI")
    key.setText(raw_value)
    qtbot.mouseClick(save, Qt.MouseButton.LeftButton)

    assert key.text() == ""
    assert submitted
    wrapped = submitted[0][2]
    assert wrapped.reveal() == raw_value
    assert sink.intents[-1].kind is UiIntentType.CREDENTIAL_SAVE_SLOT
    assert raw_value not in repr(sink.intents[-1])
    assert raw_value not in dialog.windowTitle()
    dialog.close()


def test_w6_credential_slot_actions_emit_only_safe_metadata(qtbot) -> None:
    sink = RecordingIntentSink()
    dialog = create_provider_credentials_dialog(None, sink)
    qtbot.addWidget(dialog)
    dialog.show()
    project_credential_slots(
        dialog,
        (CredentialSlotProjection(2, "Gemini 2", True, "HEALTHY"),),
    )

    enabled = dialog.findChild(QCheckBox, "check_w6_credential_enabled_002")
    test = dialog.findChild(QPushButton, "btn_w6_credential_test_002")
    delete = dialog.findChild(QPushButton, "btn_w6_credential_delete_002")
    assert enabled is not None and test is not None and delete is not None

    enabled.setChecked(False)
    assert sink.intents[-1].kind is UiIntentType.CREDENTIAL_SET_ENABLED
    assert dict(sink.intents[-1].payload) == {"enabled": "false", "slot_id": "2"}

    qtbot.mouseClick(test, Qt.MouseButton.LeftButton)
    assert sink.intents[-1].kind is UiIntentType.CREDENTIAL_TEST_SLOT

    qtbot.mouseClick(delete, Qt.MouseButton.LeftButton)
    assert sink.intents[-1].kind is UiIntentType.CREDENTIAL_DELETE_SLOT
    dialog.close()
