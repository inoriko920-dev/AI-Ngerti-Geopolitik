"""AAVC-compatible W4 title/transition/effect inspector."""

from __future__ import annotations

from typing import Any

from ai_ngerti_geopolitik.application.ui_intents import (
    UiIntent,
    UiIntentSink,
    UiIntentType,
)
from ai_ngerti_geopolitik.domain import (
    SUPPORTED_W4_EFFECTS,
    UNSUPPORTED_LEGACY_EFFECTS,
)
from ai_ngerti_geopolitik.presentation.common import (
    make_primary_button,
    muted_label,
    section_title,
)


def _emit(
    sink: UiIntentSink | None,
    kind: UiIntentType,
    **payload: object,
) -> None:
    if sink is None:
        return
    normalized = tuple(sorted((key, str(value)) for key, value in payload.items()))
    sink(UiIntent(kind, normalized))


def create_creative_inspector(
    sink: UiIntentSink | None,
    *,
    clip_id: str = "C001",
) -> Any:
    from PySide6.QtWidgets import (
        QCheckBox,
        QComboBox,
        QFormLayout,
        QLabel,
        QLineEdit,
        QSpinBox,
        QTabWidget,
        QVBoxLayout,
        QWidget,
    )

    root = QWidget()
    root.setObjectName("w4_creative_inspector")
    outer = QVBoxLayout(root)
    outer.setContentsMargins(10, 10, 10, 10)
    outer.setSpacing(8)

    outer.addWidget(section_title("Animasi & Teks"))
    target = QLabel(f"{clip_id} · render-backed")
    target.setObjectName("label_w4_creative_target")
    target.setStyleSheet("font-weight:700; color:#172033;")
    outer.addWidget(target)
    note = muted_label("Perubahan masuk CommandBus dan dapat Undo/Redo.")
    note.setStyleSheet("color:#64748B; font-size:10px;")
    outer.addWidget(note)

    tabs = QTabWidget()
    tabs.setObjectName("tabs_w4_creative")
    outer.addWidget(tabs, 1)

    title_page = QWidget()
    title_form = QFormLayout(title_page)
    title_enabled = QCheckBox("Aktif")
    title_enabled.setObjectName("creative_title_enabled")
    title_text = QLineEdit()
    title_text.setObjectName("creative_title_text")
    title_text.setMaxLength(160)
    title_text.setPlaceholderText("Teks judul...")
    font_size = QSpinBox()
    font_size.setObjectName("creative_title_font_size")
    font_size.setRange(12, 160)
    font_size.setValue(54)
    position = QComboBox()
    position.setObjectName("creative_title_position")
    position.addItem("Atas", "top")
    position.addItem("Tengah", "center")
    position.addItem("Bawah", "bottom")
    position.setCurrentIndex(2)
    background = QSpinBox()
    background.setObjectName("creative_title_background")
    background.setRange(0, 100)
    background.setValue(55)
    background.setSuffix("%")
    title_form.addRow("Judul", title_enabled)
    title_form.addRow("Teks", title_text)
    title_form.addRow("Ukuran", font_size)
    title_form.addRow("Posisi", position)
    title_form.addRow("Background", background)
    apply_title = make_primary_button(
        "Terapkan Judul",
        "btn_apply_creative_title",
    )
    apply_title.clicked.connect(
        lambda: _emit(
            sink,
            UiIntentType.CREATIVE_SET_TITLE,
            clip_id=clip_id,
            enabled=str(title_enabled.isChecked()).lower(),
            text=title_text.text(),
            font_size=font_size.value(),
            position=position.currentData(),
            color_hex="FFFFFF",
            background_opacity_percent=background.value(),
        )
    )
    title_form.addRow("", apply_title)
    tabs.addTab(title_page, "Teks")

    transition_page = QWidget()
    transition_form = QFormLayout(transition_page)
    transition = QComboBox()
    transition.setObjectName("creative_transition_preset")
    transition.addItem("Tanpa Transisi", "none")
    transition.addItem("Fade via Black", "fade_black")
    transition_frames = QSpinBox()
    transition_frames.setObjectName("creative_transition_frames")
    transition_frames.setRange(0, 300)
    transition_frames.setValue(12)
    transition_frames.setSuffix(" f")
    transition_form.addRow("Preset", transition)
    transition_form.addRow("Durasi", transition_frames)
    transition_note = QLabel(
        "Dissolve/crossfade belum ditampilkan karena timeline canonical "
        "belum mendukung clip overlap."
    )
    transition_note.setWordWrap(True)
    transition_note.setStyleSheet(
        "color:#92400E; background:#FFFBEB; "
        "border:1px solid #FDE68A; border-radius:6px; padding:7px;"
    )
    transition_form.addRow("", transition_note)
    apply_transition = make_primary_button(
        "Terapkan Transisi",
        "btn_apply_creative_transition",
    )
    apply_transition.clicked.connect(
        lambda: _emit(
            sink,
            UiIntentType.CREATIVE_SET_TRANSITION,
            clip_id=clip_id,
            preset=transition.currentData(),
            duration_frames=(
                transition_frames.value() if transition.currentData() != "none" else 0
            ),
        )
    )
    transition_form.addRow("", apply_transition)
    tabs.addTab(transition_page, "Transisi")

    effects_page = QWidget()
    effects_layout = QVBoxLayout(effects_page)
    effects_form = QFormLayout()
    enter_effect = QComboBox()
    enter_effect.setObjectName("creative_effect_enter")
    exit_effect = QComboBox()
    exit_effect.setObjectName("creative_effect_exit")
    for name in SUPPORTED_W4_EFFECTS:
        enter_effect.addItem(name)
        exit_effect.addItem(name)
    intensity = QSpinBox()
    intensity.setObjectName("creative_effect_intensity")
    intensity.setRange(0, 200)
    intensity.setValue(100)
    intensity.setSuffix("%")
    locked = QCheckBox("Kunci assignment")
    locked.setObjectName("creative_effect_locked")
    effects_form.addRow("Masuk", enter_effect)
    effects_form.addRow("Keluar", exit_effect)
    effects_form.addRow("Intensitas", intensity)
    effects_form.addRow("", locked)
    effects_layout.addLayout(effects_form)

    unsupported = QLabel("Belum render-backed: " + ", ".join(UNSUPPORTED_LEGACY_EFFECTS))
    unsupported.setObjectName("label_w4_unsupported_effects")
    unsupported.setWordWrap(True)
    unsupported.setStyleSheet("color:#64748B; font-size:10px;")
    effects_layout.addWidget(unsupported)
    apply_effects = make_primary_button(
        "Terapkan Efek",
        "btn_apply_creative_effects",
    )
    apply_effects.clicked.connect(
        lambda: _emit(
            sink,
            UiIntentType.CREATIVE_SET_EFFECTS,
            clip_id=clip_id,
            enter_effect=enter_effect.currentText(),
            exit_effect=exit_effect.currentText(),
            intensity_percent=intensity.value(),
            locked=str(locked.isChecked()).lower(),
        )
    )
    effects_layout.addWidget(apply_effects)
    effects_layout.addStretch(1)
    tabs.addTab(effects_page, "Efek")
    return root
