"""Frozen-AAVC-compatible W3 property inspector controls."""

from __future__ import annotations

from typing import Any

from ai_ngerti_geopolitik.application.ui_intents import UiIntent, UiIntentSink, UiIntentType
from ai_ngerti_geopolitik.presentation.common import make_primary_button, muted_label, section_title


def _emit(
    sink: UiIntentSink | None,
    kind: UiIntentType,
    **payload: object,
) -> None:
    if sink is None:
        return
    normalized = tuple(sorted((key, str(value)) for key, value in payload.items()))
    sink(UiIntent(kind, normalized))


def create_property_inspector(
    mode: str,
    sink: UiIntentSink | None,
    *,
    clip_id: str = "C001",
) -> Any:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import (
        QCheckBox,
        QFormLayout,
        QHBoxLayout,
        QLabel,
        QPushButton,
        QSpinBox,
        QTabWidget,
        QVBoxLayout,
        QWidget,
    )

    root = QWidget()
    root.setObjectName("w3_property_inspector")
    outer = QVBoxLayout(root)
    outer.setContentsMargins(10, 10, 10, 10)
    outer.setSpacing(8)

    title = section_title("Properti Klip")
    outer.addWidget(title)
    target = QLabel(f"{clip_id} · {'DOUBLE' if mode == 'double' else 'SINGLE'}")
    target.setObjectName("label_inspector_target")
    target.setStyleSheet("font-weight:700; color:#172033;")
    outer.addWidget(target)
    note = muted_label("Perubahan masuk CommandBus dan dapat Undo/Redo.")
    note.setStyleSheet("color:#64748B; font-size:10px;")
    outer.addWidget(note)

    tabs = QTabWidget()
    tabs.setObjectName("tabs_w3_properties")
    outer.addWidget(tabs, 1)

    def spin(
        object_name: str,
        minimum: int,
        maximum: int,
        value: int,
        suffix: str = "",
    ) -> QSpinBox:
        widget = QSpinBox()
        widget.setObjectName(object_name)
        widget.setRange(minimum, maximum)
        widget.setValue(value)
        if suffix:
            widget.setSuffix(suffix)
        return widget

    video = QWidget()
    video_form = QFormLayout(video)
    position_x = spin("prop_video_position_x", -10000, 10000, 0, " px")
    position_y = spin("prop_video_position_y", -10000, 10000, 0, " px")
    scale_x = spin("prop_video_scale_x", 10, 400, 100, "%")
    scale_y = spin("prop_video_scale_y", 10, 400, 100, "%")
    rotation = spin("prop_video_rotation", -3600, 3600, 0, "° ×0.1")
    opacity = spin("prop_video_opacity", 0, 100, 100, "%")
    crop_left = spin("prop_video_crop_left", 0, 95, 0, "%")
    crop_top = spin("prop_video_crop_top", 0, 95, 0, "%")
    crop_right = spin("prop_video_crop_right", 0, 95, 0, "%")
    crop_bottom = spin("prop_video_crop_bottom", 0, 95, 0, "%")
    for label, widget in (
        ("Posisi X", position_x),
        ("Posisi Y", position_y),
        ("Skala X", scale_x),
        ("Skala Y", scale_y),
        ("Rotasi", rotation),
        ("Opacity", opacity),
        ("Crop Kiri", crop_left),
        ("Crop Atas", crop_top),
        ("Crop Kanan", crop_right),
        ("Crop Bawah", crop_bottom),
    ):
        video_form.addRow(label, widget)
    apply_video = make_primary_button("Terapkan Video", "btn_apply_video_properties")
    apply_video.clicked.connect(
        lambda: _emit(
            sink,
            UiIntentType.PROPERTY_SET_VIDEO,
            clip_id=clip_id,
            position_x=position_x.value(),
            position_y=position_y.value(),
            scale_x_percent=scale_x.value(),
            scale_y_percent=scale_y.value(),
            rotation_tenths=rotation.value(),
            opacity_percent=opacity.value(),
            crop_left_percent=crop_left.value(),
            crop_top_percent=crop_top.value(),
            crop_right_percent=crop_right.value(),
            crop_bottom_percent=crop_bottom.value(),
        )
    )
    video_form.addRow("", apply_video)
    tabs.addTab(video, "Video")

    audio = QWidget()
    audio_form = QFormLayout(audio)
    volume = spin("prop_audio_volume", 0, 400, 100, "%")
    pan = spin("prop_audio_pan", -100, 100, 0, "%")
    fade_in = spin("prop_audio_fade_in", 0, 1000000, 0, " f")
    fade_out = spin("prop_audio_fade_out", 0, 1000000, 0, " f")
    for label, widget in (
        ("Volume", volume),
        ("Pan", pan),
        ("Fade In", fade_in),
        ("Fade Out", fade_out),
    ):
        audio_form.addRow(label, widget)
    apply_audio = make_primary_button("Terapkan Audio", "btn_apply_audio_properties")
    apply_audio.clicked.connect(
        lambda: _emit(
            sink,
            UiIntentType.PROPERTY_SET_AUDIO,
            clip_id=clip_id,
            volume_percent=volume.value(),
            pan_percent=pan.value(),
            fade_in_frames=fade_in.value(),
            fade_out_frames=fade_out.value(),
        )
    )
    audio_form.addRow("", apply_audio)
    tabs.addTab(audio, "Audio")

    color = QWidget()
    color_form = QFormLayout(color)
    brightness = spin("prop_color_brightness", -100, 100, 0, "%")
    exposure = spin("prop_color_exposure", -50, 50, 0, " ×0.1 EV")
    contrast = spin("prop_color_contrast", -100, 100, 0, "%")
    saturation = spin("prop_color_saturation", -100, 200, 0, "%")
    temperature = spin("prop_color_temperature", -100, 100, 0, "%")
    tint = spin("prop_color_tint", -100, 100, 0, "%")
    for label, widget in (
        ("Brightness", brightness),
        ("Exposure", exposure),
        ("Contrast", contrast),
        ("Saturation", saturation),
        ("White Balance", temperature),
        ("Tint", tint),
    ):
        color_form.addRow(label, widget)
    apply_color = make_primary_button("Terapkan Warna", "btn_apply_color_properties")
    apply_color.clicked.connect(
        lambda: _emit(
            sink,
            UiIntentType.PROPERTY_SET_COLOR,
            clip_id=clip_id,
            brightness_percent=brightness.value(),
            exposure_tenths_ev=exposure.value(),
            contrast_percent=contrast.value(),
            saturation_percent=saturation.value(),
            temperature_percent=temperature.value(),
            tint_percent=tint.value(),
        )
    )
    color_form.addRow("", apply_color)
    tabs.addTab(color, "Warna")

    speed_page = QWidget()
    speed_layout = QVBoxLayout(speed_page)
    speed_form = QFormLayout()
    speed = spin("prop_speed_rate", 25, 400, 100, "%")
    speed_form.addRow("Kecepatan", speed)
    speed_layout.addLayout(speed_form)
    apply_speed = make_primary_button("Terapkan Kecepatan", "btn_apply_speed_properties")
    apply_speed.clicked.connect(
        lambda: _emit(
            sink,
            UiIntentType.PROPERTY_SET_SPEED,
            clip_id=clip_id,
            rate_percent=speed.value(),
            ripple="true",
        )
    )
    speed_layout.addWidget(apply_speed)

    reverse = QCheckBox("Reverse")
    reverse.setObjectName("check_reverse_disabled")
    reverse.setEnabled(False)
    reverse.setToolTip(
        "Belum didukung: Reverse menunggu qualification backend W3 yang aman."
    )
    speed_layout.addWidget(reverse)
    warning = QLabel("Reverse: dinonaktifkan sampai backend lolos qualification.")
    warning.setWordWrap(True)
    warning.setAlignment(Qt.AlignmentFlag.AlignLeft)
    warning.setStyleSheet(
        "color:#92400E; background:#FFFBEB; border:1px solid #FDE68A; "
        "border-radius:6px; padding:7px;"
    )
    speed_layout.addWidget(warning)
    speed_layout.addStretch(1)
    tabs.addTab(speed_page, "Speed")

    reset_row = QHBoxLayout()
    reset_row.addStretch(1)
    reset = QPushButton("Reset Tampilan")
    reset.setObjectName("btn_property_reset_view")
    reset.setToolTip("Reset visual control lokal; tidak mengubah project tanpa Terapkan.")
    reset_row.addWidget(reset)
    outer.addLayout(reset_row)
    return root
