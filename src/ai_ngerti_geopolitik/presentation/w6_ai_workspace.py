"""W6-009 frozen AI Agent and Gemini credential-manager presentation.

This module owns only real PySide6 widgets and semantic UI intents. It never calls
Gemini, secure storage, ProjectState mutation, or CommandBus directly.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from ai_ngerti_geopolitik.application.ai_contracts import (
    L1_RENDER_QUALIFIED_EFFECTS,
    MASKED_CREDENTIAL_VALUE,
    MAX_CREDENTIAL_SLOTS,
    CredentialSecret,
)
from ai_ngerti_geopolitik.application.ui_intents import UiIntent, UiIntentSink, UiIntentType
from ai_ngerti_geopolitik.presentation.common import make_primary_button, muted_label, section_title
from ai_ngerti_geopolitik.presentation.design_tokens import COLORS


class AIAgentUiState(StrEnum):
    READY = "READY"
    PLAN = "PLAN"
    APPROVAL = "APPROVAL"
    APPLYING = "APPLYING"
    SUCCESS = "SUCCESS"
    PROVIDER_ERROR = "PROVIDER_ERROR"
    LOCK_CONFLICT = "LOCK_CONFLICT"
    STALE = "STALE"


@dataclass(frozen=True, slots=True)
class AIAgentProjection:
    state: AIAgentUiState = AIAgentUiState.READY
    provider_label: str = "Gemini"
    provider_status: str = "Online"
    scope_text: str = "Scene terpilih · maksimal 20 target"
    summary: str = ""
    commands: tuple[str, ...] = ()
    message: str = ""
    error_code: str = ""
    request_id: str = ""

    def __post_init__(self) -> None:
        if len(self.commands) > 20:
            raise ValueError("W6 UI plan projection cannot exceed 20 commands")


@dataclass(frozen=True, slots=True)
class CredentialSlotProjection:
    slot_id: int
    label: str
    enabled: bool
    health: str = "UNTESTED"
    last_result: str = ""

    def __post_init__(self) -> None:
        if not 1 <= self.slot_id <= MAX_CREDENTIAL_SLOTS:
            raise ValueError("credential UI slot must be between 1 and 100")
        if not self.label.strip():
            raise ValueError("credential UI label is required")

    @property
    def masked_value(self) -> str:
        return MASKED_CREDENTIAL_VALUE


CredentialSecretSubmitSink = Callable[[int, str, CredentialSecret], None]


def _emit(intent_sink: UiIntentSink | None, kind: UiIntentType, **payload: str) -> None:
    if intent_sink is None:
        return
    intent_sink(UiIntent(kind, tuple(sorted(payload.items()))))


def _badge(label: Any, text: str, category: str) -> None:
    label.setText(text)
    color = {
        "ready": COLORS.success,
        "warning": COLORS.warning,
        "error": COLORS.error,
    }.get(category, COLORS.muted)
    label.setStyleSheet(f"color:{color}; font-weight:700;")


def _request_id(workspace: Any) -> str:
    return str(workspace.property("w6_request_id") or "")


def create_ai_agent_workspace(
    intent_sink: UiIntentSink | None,
    *,
    open_credentials_callback: Callable[[], None] | None = None,
) -> Any:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import (
        QComboBox,
        QFrame,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QListWidget,
        QProgressBar,
        QPushButton,
        QSlider,
        QStackedWidget,
        QTabWidget,
        QTextBrowser,
        QVBoxLayout,
        QWidget,
    )

    root = QWidget()
    root.setObjectName("w6_ai_workspace")
    root.setProperty("w6_request_id", "")
    layout = QVBoxLayout(root)
    layout.setContentsMargins(8, 8, 8, 8)
    layout.setSpacing(8)

    tabs = QTabWidget()
    tabs.setObjectName("w6_ai_subtabs")
    layout.addWidget(tabs, 1)

    director = QWidget()
    director.setObjectName("w6_ai_director_page")
    director_layout = QVBoxLayout(director)
    director_layout.setContentsMargins(10, 10, 10, 10)
    director_layout.setSpacing(9)
    director_layout.addWidget(section_title("Animasi  ›  AI Director"))
    director_tabs = QHBoxLayout()
    for text_value, selected in (("Preset", False), ("AI Director", True), ("Kustom", False)):
        tab_button = QPushButton(text_value)
        tab_button.setEnabled(selected)
        tab_button.setStyleSheet(
            "font-weight:700; border-bottom:2px solid #2563EB;"
            if selected
            else "color:#64748B;"
        )
        director_tabs.addWidget(tab_button)
    director_layout.addLayout(director_tabs)

    provider_row = QHBoxLayout()
    provider_combo = QComboBox()
    provider_combo.setObjectName("combo_w6_director_provider")
    provider_combo.addItem("Gemini · Siap", "gemini")
    provider_row.addWidget(provider_combo, 1)
    manage_director_keys = QPushButton("Provider")
    manage_director_keys.setObjectName("btn_w6_director_manage_credentials")
    provider_row.addWidget(manage_director_keys)
    director_layout.addLayout(provider_row)

    scope_card = QFrame()
    scope_card.setProperty("panel", True)
    scope_layout = QVBoxLayout(scope_card)
    scope_layout.addWidget(QLabel("Buat Animasi"))
    director_prompt = QLineEdit()
    director_prompt.setObjectName("edit_w6_director_prompt")
    director_prompt.setPlaceholderText("Jelaskan gaya animasi yang diinginkan...")
    scope_layout.addWidget(director_prompt)
    scope_layout.addWidget(QLabel("Lingkup Animasi"))
    scope = QComboBox()
    scope.setObjectName("combo_w6_ai_director_scope")
    scope.addItem("Aset Terpilih", "selected_asset")
    scope.addItem("Scene Terpilih", "selected_scene")
    scope.addItem("Pilihan Aktif (maks. 20)", "selected_scope")
    scope_layout.addWidget(scope)
    scope_layout.addWidget(QLabel("Intensitas"))
    intensity = QSlider(Qt.Orientation.Horizontal)
    intensity.setObjectName("slider_w6_director_intensity")
    intensity.setRange(0, 200)
    intensity.setValue(100)
    scope_layout.addWidget(intensity)
    scope_layout.addWidget(QLabel("Variasi Efek"))
    variation = QSlider(Qt.Orientation.Horizontal)
    variation.setObjectName("slider_w6_director_variation")
    variation.setRange(0, 100)
    variation.setValue(50)
    scope_layout.addWidget(variation)
    director_layout.addWidget(scope_card)

    capability = QFrame()
    capability.setProperty("panel", True)
    capability_layout = QVBoxLayout(capability)
    capability_layout.addWidget(QLabel("Efek L1 yang tersedia"))
    capability_text = QLabel(" · ".join(L1_RENDER_QUALIFIED_EFFECTS))
    capability_text.setObjectName("label_w6_l1_capabilities")
    capability_text.setWordWrap(True)
    capability_layout.addWidget(capability_text)
    capability_layout.addWidget(
        muted_label("Tidak mengubah pacing, durasi, transform, subtitle, narasi, atau render.")
    )
    director_layout.addWidget(capability)

    recommendations = QFrame()
    recommendations.setProperty("panel", True)
    recommendations_layout = QVBoxLayout(recommendations)
    recommendations_layout.addWidget(QLabel("Rekomendasi Animasi · 3 saran"))
    for text_value in (
        "Scene 1 · Fade → Rise · halus",
        "Scene 4 · Breathe · fokus subjek",
        "Scene 5 · Pan · gerak ringan",
    ):
        recommendations_layout.addWidget(muted_label(text_value))
    director_layout.addWidget(recommendations)

    auto_plan = make_primary_button("Buat Rencana AI")
    auto_plan.setObjectName("btn_w6_ai_auto_plan")
    auto_plan.clicked.connect(
        lambda: _emit(
            intent_sink,
            UiIntentType.AUTO_AI,
            scope=str(scope.currentData()),
            capability="l1_effects",
            instruction=director_prompt.text().strip(),
            intensity=str(intensity.value()),
            variation=str(variation.value()),
        )
    )
    director_layout.addWidget(auto_plan)
    open_chat = QPushButton("Buka AI Agent")
    open_chat.setObjectName("btn_w6_open_agent_chat")
    director_layout.addWidget(open_chat)
    director_layout.addStretch(1)
    tabs.addTab(director, "AI Otomatis")

    agent = QWidget()
    agent.setObjectName("w6_ai_agent_page")
    agent_layout = QVBoxLayout(agent)
    agent_layout.setContentsMargins(10, 10, 10, 10)
    agent_layout.setSpacing(8)

    header = QHBoxLayout()
    title = QLabel("AI Agent")
    title.setStyleSheet("font-size:14px; font-weight:700;")
    header.addWidget(title)
    header.addStretch(1)
    provider = QLabel("Gemini · Online")
    provider.setObjectName("label_w6_ai_provider")
    _badge(provider, "Gemini · Online", "ready")
    header.addWidget(provider)
    agent_layout.addLayout(header)

    config_row = QHBoxLayout()
    assistant_combo = QComboBox()
    assistant_combo.setObjectName("combo_w6_ai_assistant")
    assistant_combo.addItem("SRT-AI", "srt_ai")
    config_row.addWidget(assistant_combo, 1)
    model_combo = QComboBox()
    model_combo.setObjectName("combo_w6_ai_model")
    model_combo.addItem("Mode: L1 Effects", "l1_effects")
    config_row.addWidget(model_combo, 1)
    agent_layout.addLayout(config_row)

    scope_label = muted_label("Scope: Scene terpilih · maksimal 20 target")
    scope_label.setObjectName("label_w6_ai_scope")
    scope_label.setWordWrap(True)
    agent_layout.addWidget(scope_label)

    workspace_row = QHBoxLayout()
    workspace_row.addWidget(QLabel("Ruang kerja AI"))
    for text_value in ("Semua", "Scene Aktif", "Aset Terpilih"):
        scope_button = QPushButton(text_value)
        scope_button.setProperty("compact", True)
        workspace_row.addWidget(scope_button)
    agent_layout.addLayout(workspace_row)

    manage_keys = QPushButton("Provider & API Key")
    manage_keys.setObjectName("btn_w6_manage_credentials")
    agent_layout.addWidget(manage_keys)

    state_stack = QStackedWidget()
    state_stack.setObjectName("w6_ai_state_stack")
    agent_layout.addWidget(state_stack, 1)

    ready = QWidget()
    ready.setObjectName("w6_ai_ready_page")
    ready_layout = QVBoxLayout(ready)
    ready_layout.setContentsMargins(0, 4, 0, 0)
    transcript = QTextBrowser()
    transcript.setObjectName("w6_ai_chat_transcript")
    transcript.setHtml(
        "<p><b>AI Agent siap.</b><br>"
        "Saya hanya dapat merencanakan efek animasi L1 yang sudah render-qualified.</p>"
        "<p style='background:#DBEAFE;padding:8px;border-radius:6px;'>"
        "Tolong jadikan pembuka Scene 1 lebih halus tanpa mengubah durasi.</p>"
        "<p><b>Siap.</b> Saya akan membuat rencana L1 dan meminta persetujuan sebelum "
        "perubahan diterapkan.</p>"
        "<p style='color:#16A34A;'>Konteks aman · lock dihormati · target stabil</p>"
    )
    ready_layout.addWidget(transcript, 1)
    quick = QLabel("Saran cepat")
    quick.setStyleSheet("font-weight:600;")
    ready_layout.addWidget(quick)
    instruction = QLineEdit()
    instruction.setObjectName("edit_w6_ai_instruction")
    instruction.setPlaceholderText("Tulis perintah animasi L1...")
    for object_name, label_text, prompt in (
        ("btn_w6_quick_subtle", "Animasi lebih halus", "Buat animasi masuk lebih halus."),
        ("btn_w6_quick_entry", "Variasikan efek masuk", "Variasikan efek masuk pada target."),
        (
            "btn_w6_quick_intensity",
            "Rapikan intensitas",
            "Rapikan intensitas efek tanpa mengubah lock.",
        ),
    ):
        button = QPushButton(label_text)
        button.setObjectName(object_name)
        button.clicked.connect(lambda _checked=False, value=prompt: instruction.setText(value))
        ready_layout.addWidget(button)
    input_row = QHBoxLayout()
    input_row.addWidget(instruction, 1)
    send = make_primary_button("Kirim")
    send.setObjectName("btn_w6_ai_send")
    input_row.addWidget(send)
    ready_layout.addLayout(input_row)
    state_stack.addWidget(ready)

    plan = QWidget()
    plan.setObjectName("w6_ai_plan_page")
    plan_layout = QVBoxLayout(plan)
    plan_layout.setContentsMargins(0, 4, 0, 0)
    plan_layout.addWidget(section_title("Rencana Aksi"))
    plan_state = QLabel("Rencana siap ditinjau")
    plan_state.setObjectName("label_w6_plan_state")
    plan_state.setStyleSheet("font-weight:700; color:#2563EB;")
    plan_layout.addWidget(plan_state)
    plan_summary = QLabel("Belum ada ringkasan rencana.")
    plan_summary.setObjectName("label_w6_plan_summary")
    plan_summary.setWordWrap(True)
    plan_layout.addWidget(QLabel("Tujuan Instruksi"))
    plan_layout.addWidget(plan_summary)
    plan_layout.addWidget(QLabel("Langkah yang Akan Dilakukan"))
    plan_commands = QListWidget()
    plan_commands.setObjectName("list_w6_plan_commands")
    plan_layout.addWidget(plan_commands, 1)
    impact = QFrame()
    impact.setProperty("panel", True)
    impact_layout = QVBoxLayout(impact)
    impact_layout.addWidget(QLabel("Lingkup Terdampak"))
    impact_layout.addWidget(muted_label("Scene terpilih · hanya target stabil yang diverifikasi"))
    plan_layout.addWidget(impact)
    plan_layout.addWidget(QLabel("Validasi & Pengaman"))
    plan_layout.addWidget(muted_label("✓ Lock dihormati"))
    plan_layout.addWidget(muted_label("✓ Efek hanya dari allowlist L1"))
    plan_layout.addWidget(muted_label("✓ Stale plan ditolak sebelum apply"))
    plan_layout.addWidget(muted_label("⚠ AI memberi saran; keputusan akhir tetap pada pengguna."))
    plan_buttons = QHBoxLayout()
    reject = QPushButton("Ubah Manual")
    reject.setObjectName("btn_w6_plan_reject")
    approve = QPushButton("Tinjau & Setujui")
    approve.setObjectName("btn_w6_plan_approve")
    cancel_plan = QPushButton("Batal")
    cancel_plan.setObjectName("btn_w6_plan_cancel")
    apply_button = make_primary_button("Terapkan Rencana")
    apply_button.setObjectName("btn_w6_plan_apply")
    plan_buttons.addWidget(reject)
    plan_buttons.addWidget(approve)
    plan_buttons.addWidget(cancel_plan)
    plan_buttons.addWidget(apply_button)
    plan_layout.addLayout(plan_buttons)
    state_stack.addWidget(plan)

    applying = QWidget()
    applying.setObjectName("w6_ai_applying_page")
    applying_layout = QVBoxLayout(applying)
    applying_layout.addWidget(section_title("Menerapkan Rencana"))
    applying_label = QLabel("Menjalankan satu transaksi CommandBatch...")
    applying_label.setObjectName("label_w6_applying")
    applying_layout.addWidget(applying_label)
    progress = QProgressBar()
    progress.setObjectName("progress_w6_ai_apply")
    progress.setRange(0, 0)
    applying_layout.addWidget(progress)
    applying_layout.addWidget(
        muted_label("Editor manual tetap tersedia setelah transaksi selesai.")
    )
    cancel_job = QPushButton("Batalkan Job")
    cancel_job.setObjectName("btn_w6_cancel_job")
    applying_layout.addWidget(cancel_job)
    applying_layout.addStretch(1)
    state_stack.addWidget(applying)

    success = QWidget()
    success.setObjectName("w6_ai_success_page")
    success_layout = QVBoxLayout(success)
    success_layout.addWidget(section_title("AI Agent"))
    success_banner = QFrame()
    success_banner.setStyleSheet(
        "background:#F0FDF4; border:1px solid #BBF7D0; border-radius:7px;"
    )
    success_banner_layout = QVBoxLayout(success_banner)
    success_banner_layout.addWidget(QLabel("✓ Rencana berhasil diterapkan"))
    success_layout.addWidget(success_banner)
    success_badge = QLabel("✓ SUCCESS")
    success_badge.setObjectName("label_w6_success_badge")
    _badge(success_badge, "✓ SUCCESS", "ready")
    success_layout.addWidget(success_badge)
    success_message = QLabel("Rencana AI diterapkan sebagai satu transaksi.")
    success_message.setObjectName("label_w6_success_message")
    success_message.setWordWrap(True)
    success_layout.addWidget(success_message)
    stats = QHBoxLayout()
    stats.addWidget(muted_label("5 Scene Diubah"))
    stats.addWidget(muted_label("4 Efek Diterapkan"))
    success_layout.addLayout(stats)
    success_layout.addWidget(QLabel("Rincian Perubahan"))
    for text_value in (
        "Scene 1 · Fade → Rise",
        "Scene 2 · Breathe",
        "Scene 3 · Intensity disesuaikan",
        "Scene 4 · Pan",
        "Scene 5 · Drift",
    ):
        success_layout.addWidget(muted_label(f"✓ {text_value}"))
    success_layout.addWidget(
        muted_label("Undo akan membatalkan seluruh perubahan AI pada transaksi ini.")
    )
    undo = QPushButton("Batalkan Perubahan")
    undo.setObjectName("btn_w6_ai_undo")
    success_layout.addWidget(undo)
    timeline_button = QPushButton("Lihat di Timeline")
    timeline_button.setObjectName("btn_w6_ai_view_timeline")
    success_layout.addWidget(timeline_button)
    success_layout.addStretch(1)
    state_stack.addWidget(success)

    error = QWidget()
    error.setObjectName("w6_ai_error_page")
    error_layout = QVBoxLayout(error)
    error_layout.addWidget(section_title("AI Agent"))
    error_banner = QFrame()
    error_banner.setStyleSheet(
        "background:#FEF2F2; border:1px solid #FECACA; border-radius:7px;"
    )
    error_banner_layout = QVBoxLayout(error_banner)
    error_banner_layout.addWidget(QLabel("! PROVIDER TIDAK TERSEDIA"))
    error_layout.addWidget(error_banner)
    error_badge = QLabel("PROVIDER_ERROR")
    error_badge.setObjectName("label_w6_error_badge")
    _badge(error_badge, "PROVIDER_ERROR", "error")
    error_layout.addWidget(error_badge)
    error_code = QLabel("")
    error_code.setObjectName("label_w6_error_code")
    error_code.setStyleSheet("font-weight:600;")
    error_layout.addWidget(error_code)
    error_message = QLabel("Provider tidak tersedia.")
    error_message.setObjectName("label_w6_error_message")
    error_message.setWordWrap(True)
    error_layout.addWidget(error_message)
    error_layout.addWidget(QLabel("Daftar Provider"))
    for text_value, status_value in (
        ("Gemini Utama", "GAGAL"),
        ("Gemini Cadangan", "COOLDOWN"),
        ("Gemini Slot Lain", "SIAP"),
    ):
        provider_row = QFrame()
        provider_row.setProperty("panel", True)
        provider_row_layout = QHBoxLayout(provider_row)
        provider_row_layout.addWidget(QLabel(text_value), 1)
        provider_row_layout.addWidget(QLabel(status_value))
        error_layout.addWidget(provider_row)
    fallback = muted_label(
        "Editor manual tetap aktif. Tidak ada perubahan project yang diterapkan."
    )
    fallback.setObjectName("label_w6_manual_fallback")
    fallback.setWordWrap(True)
    error_layout.addWidget(fallback)
    retry = make_primary_button("Coba Lagi")
    retry.setObjectName("btn_w6_ai_retry")
    error_layout.addWidget(retry)
    error_manage = QPushButton("Kelola Provider & API Key")
    error_manage.setObjectName("btn_w6_error_manage_credentials")
    error_layout.addWidget(error_manage)
    error_layout.addWidget(QPushButton("Pilih Slot Credential Lain"))
    error_layout.addStretch(1)
    state_stack.addWidget(error)

    tabs.addTab(agent, "AI Agent")
    tabs.setCurrentIndex(0)

    def open_credentials() -> None:
        if open_credentials_callback is not None:
            open_credentials_callback()
        else:
            _emit(intent_sink, UiIntentType.OPEN_AI_CREDENTIALS)

    manage_keys.clicked.connect(open_credentials)
    manage_director_keys.clicked.connect(open_credentials)
    error_manage.clicked.connect(open_credentials)
    open_chat.clicked.connect(lambda: tabs.setCurrentIndex(1))
    open_chat.clicked.connect(lambda: _emit(intent_sink, UiIntentType.AI_OPEN_AGENT, view="agent"))
    send.clicked.connect(lambda: _submit_instruction(root, instruction, scope_label, intent_sink))
    instruction.returnPressed.connect(
        lambda: _submit_instruction(root, instruction, scope_label, intent_sink)
    )
    approve.clicked.connect(
        lambda: _emit(
            intent_sink,
            UiIntentType.AI_APPROVE_PLAN,
            request_id=_request_id(root),
        )
    )
    reject.clicked.connect(
        lambda: _emit(
            intent_sink,
            UiIntentType.AI_REJECT_PLAN,
            request_id=_request_id(root),
        )
    )
    cancel_plan.clicked.connect(
        lambda: _emit(
            intent_sink,
            UiIntentType.AI_CANCEL_PLAN,
            request_id=_request_id(root),
        )
    )
    apply_button.clicked.connect(
        lambda: _emit(
            intent_sink,
            UiIntentType.AI_APPLY_PLAN,
            request_id=_request_id(root),
        )
    )
    cancel_job.clicked.connect(
        lambda: _emit(
            intent_sink,
            UiIntentType.AI_CANCEL_JOB,
            request_id=_request_id(root),
        )
    )
    undo.clicked.connect(lambda: _emit(intent_sink, UiIntentType.UNDO))
    retry.clicked.connect(
        lambda: _emit(
            intent_sink,
            UiIntentType.AI_RETRY,
            request_id=_request_id(root),
        )
    )

    project_ai_agent_state(root, AIAgentProjection())
    return root


def _submit_instruction(
    workspace: Any,
    instruction: Any,
    scope_label: Any,
    intent_sink: UiIntentSink | None,
) -> None:
    text = instruction.text().strip()
    if not text:
        return
    _emit(
        intent_sink,
        UiIntentType.AI_SUBMIT_PROMPT,
        instruction=text,
        scope=scope_label.text(),
    )
    instruction.clear()
    workspace.setProperty("w6_last_instruction_submitted", True)


def set_ai_agent_subview(workspace: Any, view: str) -> None:
    from PySide6.QtWidgets import QTabWidget

    tabs = workspace.findChild(QTabWidget, "w6_ai_subtabs")
    if tabs is None:
        raise RuntimeError("W6 AI sub-tabs are missing")
    if view == "director":
        tabs.setCurrentIndex(0)
    elif view == "agent":
        tabs.setCurrentIndex(1)
    else:
        raise ValueError(f"unknown W6 AI subview: {view}")
    workspace.setProperty("w6_ai_subview", view)


def _default_error_message(state: AIAgentUiState, code: str) -> str:
    if state is AIAgentUiState.LOCK_CONFLICT:
        return "Target terkunci. AI tidak akan membuka lock secara otomatis."
    if state is AIAgentUiState.STALE:
        return "Project berubah sejak rencana dibuat. Buat rencana baru sebelum menerapkan."
    mapping = {
        "NO_CREDENTIAL": "Belum ada credential Gemini aktif.",
        "INVALID_AUTH": "Credential Gemini ditolak. Periksa slot yang digunakan.",
        "RATE_LIMIT_OR_QUOTA": (
            "Batas provider atau kuota sedang aktif. Tidak ada rotasi untuk "
            "menghindari kebijakan provider."
        ),
        "NETWORK_TIMEOUT": "Jaringan atau provider tidak merespons dalam batas waktu.",
        "MALFORMED_RESPONSE": "Respons provider tidak dapat digunakan sebagai rencana yang valid.",
        "ALL_SLOTS_UNAVAILABLE": "Semua slot credential yang diizinkan sedang tidak tersedia.",
    }
    return mapping.get(code, "Provider Gemini tidak tersedia untuk operasi ini.")


def project_ai_agent_state(workspace: Any, projection: AIAgentProjection) -> None:
    from PySide6.QtWidgets import (
        QLabel,
        QListWidget,
        QPushButton,
        QStackedWidget,
        QTabWidget,
        QWidget,
    )

    workspace.setProperty("w6_ai_state", projection.state.value)
    workspace.setProperty("w6_request_id", projection.request_id)

    tabs = workspace.findChild(QTabWidget, "w6_ai_subtabs")
    stack = workspace.findChild(QStackedWidget, "w6_ai_state_stack")
    provider = workspace.findChild(QLabel, "label_w6_ai_provider")
    scope = workspace.findChild(QLabel, "label_w6_ai_scope")
    if tabs is None or stack is None or provider is None or scope is None:
        raise RuntimeError("W6 AI workspace projection targets are missing")

    tabs.setCurrentIndex(1)
    workspace.setProperty("w6_ai_subview", "agent")
    scope.setText(f"Scope: {projection.scope_text}")
    provider_text = f"{projection.provider_label} · {projection.provider_status}"
    provider_category = (
        "error"
        if projection.state is AIAgentUiState.PROVIDER_ERROR
        else "warning"
        if projection.state in {AIAgentUiState.LOCK_CONFLICT, AIAgentUiState.STALE}
        else "ready"
    )
    _badge(provider, provider_text, provider_category)

    def page(name: str) -> Any:
        found = workspace.findChild(QWidget, name)
        if found is None:
            raise RuntimeError(f"W6 AI page missing: {name}")
        return found

    if projection.state is AIAgentUiState.READY:
        stack.setCurrentWidget(page("w6_ai_ready_page"))
        return

    if projection.state in {AIAgentUiState.PLAN, AIAgentUiState.APPROVAL}:
        stack.setCurrentWidget(page("w6_ai_plan_page"))
        summary = workspace.findChild(QLabel, "label_w6_plan_summary")
        state_label = workspace.findChild(QLabel, "label_w6_plan_state")
        commands = workspace.findChild(QListWidget, "list_w6_plan_commands")
        approve = workspace.findChild(QPushButton, "btn_w6_plan_approve")
        reject = workspace.findChild(QPushButton, "btn_w6_plan_reject")
        cancel_plan = workspace.findChild(QPushButton, "btn_w6_plan_cancel")
        apply_button = workspace.findChild(QPushButton, "btn_w6_plan_apply")
        if (
            summary is None
            or state_label is None
            or commands is None
            or approve is None
            or reject is None
            or cancel_plan is None
            or apply_button is None
        ):
            raise RuntimeError("W6 plan widgets are missing")
        summary.setText(projection.summary or "Rencana AI siap ditinjau.")
        commands.clear()
        for index, command in enumerate(projection.commands, start=1):
            commands.addItem(f"{index:02d}. {command}")
        is_approval = projection.state is AIAgentUiState.APPROVAL
        state_label.setText(
            "Rencana disetujui · siap diterapkan" if is_approval else "Rencana siap ditinjau"
        )
        approve.setVisible(not is_approval)
        reject.setVisible(not is_approval)
        cancel_plan.setVisible(is_approval)
        apply_button.setVisible(is_approval)
        return

    if projection.state is AIAgentUiState.APPLYING:
        stack.setCurrentWidget(page("w6_ai_applying_page"))
        applying = workspace.findChild(QLabel, "label_w6_applying")
        if applying is not None:
            applying.setText(projection.message or "Menjalankan satu transaksi CommandBatch...")
        return

    if projection.state is AIAgentUiState.SUCCESS:
        stack.setCurrentWidget(page("w6_ai_success_page"))
        message = workspace.findChild(QLabel, "label_w6_success_message")
        if message is not None:
            message.setText(projection.message or "Rencana AI diterapkan sebagai satu transaksi.")
        return

    stack.setCurrentWidget(page("w6_ai_error_page"))
    error_badge = workspace.findChild(QLabel, "label_w6_error_badge")
    error_code = workspace.findChild(QLabel, "label_w6_error_code")
    error_message = workspace.findChild(QLabel, "label_w6_error_message")
    if error_badge is None or error_code is None or error_message is None:
        raise RuntimeError("W6 error widgets are missing")
    _badge(error_badge, projection.state.value, "error")
    code = projection.error_code or (
        "LOCK_CONFLICT"
        if projection.state is AIAgentUiState.LOCK_CONFLICT
        else "STALE_PLAN"
        if projection.state is AIAgentUiState.STALE
        else "PROVIDER_ERROR"
    )
    error_code.setText(code)
    error_message.setText(projection.message or _default_error_message(projection.state, code))


def create_provider_credentials_dialog(
    parent: Any,
    intent_sink: UiIntentSink | None,
    *,
    secret_submit_sink: CredentialSecretSubmitSink | None = None,
) -> Any:
    from PySide6.QtWidgets import (
        QDialog,
        QFileDialog,
        QFrame,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QPushButton,
        QScrollArea,
        QSpinBox,
        QVBoxLayout,
        QWidget,
    )

    dialog = QDialog(parent)
    dialog.setObjectName("w6_credential_dialog")
    dialog.setWindowTitle("Provider & API Key Manager")
    dialog.resize(880, 620)
    dialog.__dict__["_w6_intent_sink"] = intent_sink

    layout = QVBoxLayout(dialog)
    layout.setContentsMargins(14, 14, 14, 14)
    layout.setSpacing(10)
    layout.addWidget(section_title("Pengaturan"))

    body = QHBoxLayout()
    nav = QFrame()
    nav.setProperty("panel", True)
    nav.setFixedWidth(170)
    nav_layout = QVBoxLayout(nav)
    for text_value, selected in (
        ("Umum", False),
        ("Provider & API Key", True),
        ("Export", False),
        ("Render", False),
        ("AI Otomatis", False),
        ("Pelaporan", False),
    ):
        nav_button = QPushButton(text_value)
        nav_button.setEnabled(selected)
        nav_button.setStyleSheet(
            "background:#2563EB;color:white;font-weight:700;"
            if selected
            else "color:#64748B;"
        )
        nav_layout.addWidget(nav_button)
    nav_layout.addStretch(1)
    body.addWidget(nav)

    content = QWidget()
    right_layout = QVBoxLayout(content)
    right_layout.setContentsMargins(4, 0, 0, 0)
    right_layout.addWidget(section_title("Provider & API Key"))
    right_layout.addWidget(
        muted_label(
            "Kelola provider Gemini dan slot credential aman tanpa menampilkan key tersimpan."
        )
    )
    body.addWidget(content, 1)
    layout.addLayout(body, 1)

    provider_card = QFrame()
    provider_card.setProperty("panel", True)
    provider_layout = QVBoxLayout(provider_card)
    provider_layout.addWidget(QLabel("Gemini · Provider V1"))
    provider_layout.addWidget(
        muted_label(
            "Slot 1–100 untuk ketahanan operasional. Rotasi tidak digunakan untuk "
            "menghindari rate limit atau kuota provider."
        )
    )
    right_layout.addWidget(provider_card)

    count = QLabel("0 slot terkonfigurasi")
    count.setObjectName("label_w6_credential_count")
    right_layout.addWidget(count)

    scroll = QScrollArea()
    scroll.setObjectName("scroll_w6_credential_slots")
    scroll.setWidgetResizable(True)
    slot_host = QWidget()
    slot_host.setObjectName("w6_credential_slot_host")
    slot_layout = QVBoxLayout(slot_host)
    slot_layout.setObjectName("layout_w6_credential_slots")
    slot_layout.setContentsMargins(0, 0, 0, 0)
    slot_layout.setSpacing(6)
    scroll.setWidget(slot_host)
    right_layout.addWidget(scroll, 1)

    form = QFrame()
    form.setProperty("panel", True)
    form_layout = QVBoxLayout(form)
    form_layout.addWidget(QLabel("Tambah / Perbarui Credential"))
    row = QHBoxLayout()
    slot = QSpinBox()
    slot.setObjectName("spin_w6_credential_slot")
    slot.setRange(1, MAX_CREDENTIAL_SLOTS)
    slot.setPrefix("Slot ")
    row.addWidget(slot)
    label = QLineEdit()
    label.setObjectName("edit_w6_credential_label")
    label.setPlaceholderText("Label, contoh: Gemini Utama")
    row.addWidget(label, 1)
    key = QLineEdit()
    key.setObjectName("edit_w6_credential_value")
    key.setPlaceholderText("API key baru")
    key.setEchoMode(QLineEdit.EchoMode.Password)
    row.addWidget(key, 1)
    save = make_primary_button("Simpan Key")
    save.setObjectName("btn_w6_credential_save")
    row.addWidget(save)
    form_layout.addLayout(row)
    status = muted_label("Key tersimpan tidak pernah ditampilkan kembali.")
    status.setObjectName("label_w6_credential_form_status")
    form_layout.addWidget(status)
    right_layout.addWidget(form)

    policy = QFrame()
    policy.setProperty("panel", True)
    policy_layout = QVBoxLayout(policy)
    policy_layout.addWidget(QLabel("Urutan Fallback Provider"))
    policy_layout.addWidget(
        muted_label("Gemini slot sehat → retry jaringan terbatas → berhenti pada quota/cooldown.")
    )
    policy_layout.addWidget(muted_label("Maks. percobaan mengikuti policy W6; tidak ada quota evasion."))
    right_layout.addWidget(policy)

    footer = QHBoxLayout()
    import_txt = QPushButton("Tambah dari TXT")
    import_txt.setObjectName("btn_w6_credential_import_txt")
    footer.addWidget(import_txt)
    footer.addStretch(1)
    close = QPushButton("Tutup")
    close.setObjectName("btn_w6_credential_close")
    close.clicked.connect(dialog.close)
    footer.addWidget(close)
    right_layout.addLayout(footer)

    def submit() -> None:
        raw_value = key.text().strip()
        label_value = label.text().strip() or f"Gemini Slot {slot.value():03d}"
        if not raw_value:
            _badge(status, "API key baru wajib diisi.", "error")
            return
        try:
            wrapped = CredentialSecret(raw_value)
            if secret_submit_sink is not None:
                secret_submit_sink(slot.value(), label_value, wrapped)
        except Exception:
            key.clear()
            _badge(status, "Credential tidak dapat disimpan melalui application boundary.", "error")
            return
        _emit(
            intent_sink,
            UiIntentType.CREDENTIAL_SAVE_SLOT,
            slot_id=str(slot.value()),
            label=label_value,
            secret_present="true",
        )
        key.clear()
        _badge(
            status,
            "Permintaan simpan dikirim. Nilai key tidak disimpan atau ditampilkan oleh UI.",
            "ready",
        )

    save.clicked.connect(submit)

    def import_file() -> None:
        path, _selected = QFileDialog.getOpenFileName(
            dialog,
            "Impor API Key dari TXT",
            "",
            "Text (*.txt);;Semua File (*.*)",
        )
        if not path:
            return
        _emit(intent_sink, UiIntentType.CREDENTIAL_IMPORT_TXT, path=path)
        _badge(
            status,
            "Permintaan impor TXT dikirim. Isi sumber tidak disimpan oleh UI.",
            "ready",
        )

    import_txt.clicked.connect(import_file)
    project_credential_slots(dialog, ())
    return dialog


def project_credential_slots(dialog: Any, slots: tuple[CredentialSlotProjection, ...]) -> None:
    from PySide6.QtWidgets import (
        QCheckBox,
        QFrame,
        QHBoxLayout,
        QLabel,
        QPushButton,
        QVBoxLayout,
        QWidget,
    )

    host = dialog.findChild(QWidget, "w6_credential_slot_host")
    count = dialog.findChild(QLabel, "label_w6_credential_count")
    if host is None or count is None:
        raise RuntimeError("W6 credential projection targets are missing")
    layout = host.layout()
    if layout is None:
        raise RuntimeError("W6 credential slot layout is missing")

    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()

    count.setText(f"{len(slots)} slot terkonfigurasi")
    sink = getattr(dialog, "_w6_intent_sink", None)

    for projection in slots:
        row = QFrame()
        row.setObjectName(f"w6_credential_slot_{projection.slot_id:03d}")
        row.setProperty("panel", True)
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(8, 6, 8, 6)
        identity = QVBoxLayout()
        title = QLabel(f"Slot {projection.slot_id:03d} · {projection.label}")
        title.setStyleSheet("font-weight:600;")
        identity.addWidget(title)
        masked = QLabel(projection.masked_value)
        masked.setObjectName(f"label_w6_credential_mask_{projection.slot_id:03d}")
        masked.setStyleSheet("font-family:Consolas; color:#64748B;")
        identity.addWidget(masked)
        row_layout.addLayout(identity, 1)

        health = QLabel(projection.health)
        health.setObjectName(f"label_w6_credential_health_{projection.slot_id:03d}")
        category = (
            "ready"
            if projection.health in {"HEALTHY", "VALID", "READY"}
            else "error"
            if projection.health in {"INVALID_AUTH", "ERROR"}
            else "warning"
        )
        _badge(health, projection.health, category)
        row_layout.addWidget(health)

        enabled = QCheckBox("Aktif")
        enabled.setObjectName(f"check_w6_credential_enabled_{projection.slot_id:03d}")
        enabled.setChecked(projection.enabled)
        row_layout.addWidget(enabled)

        test = QPushButton("Test")
        test.setObjectName(f"btn_w6_credential_test_{projection.slot_id:03d}")
        row_layout.addWidget(test)
        delete = QPushButton("Hapus")
        delete.setObjectName(f"btn_w6_credential_delete_{projection.slot_id:03d}")
        row_layout.addWidget(delete)

        enabled.toggled.connect(
            lambda checked, slot_id=projection.slot_id: _emit(
                sink,
                UiIntentType.CREDENTIAL_SET_ENABLED,
                slot_id=str(slot_id),
                enabled=str(checked).lower(),
            )
        )
        test.clicked.connect(
            lambda _checked=False, slot_id=projection.slot_id: _emit(
                sink,
                UiIntentType.CREDENTIAL_TEST_SLOT,
                slot_id=str(slot_id),
            )
        )
        delete.clicked.connect(
            lambda _checked=False, slot_id=projection.slot_id: _emit(
                sink,
                UiIntentType.CREDENTIAL_DELETE_SLOT,
                slot_id=str(slot_id),
            )
        )
        layout.addWidget(row)

    layout.addStretch(1)
