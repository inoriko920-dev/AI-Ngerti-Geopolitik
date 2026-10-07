"""Frozen W5 subtitle, narration and microphone presentation surfaces."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

from ai_ngerti_geopolitik.application.ui_intents import UiIntent, UiIntentSink, UiIntentType
from ai_ngerti_geopolitik.domain import (
    SUPPORTED_SUBTITLE_ANIMATIONS,
    UNSUPPORTED_SUBTITLE_ANIMATIONS,
)
from ai_ngerti_geopolitik.presentation.common import make_primary_button, muted_label, section_title

QUALIFIED_SUBTITLE_FONTS = ("Arial", "Segoe UI")


def _emit(
    sink: UiIntentSink | None,
    kind: UiIntentType,
    **payload: object,
) -> None:
    if sink is None:
        return
    normalized = tuple(sorted((key, str(value)) for key, value in payload.items()))
    sink(UiIntent(kind, normalized))


def _selected_cue_id(cue_list: Any) -> str:
    item = cue_list.currentItem()
    if item is None:
        return ""
    value = item.data(256)
    return str(value or "")


def _open_srt(parent: Any, sink: UiIntentSink | None) -> None:
    from PySide6.QtWidgets import QFileDialog

    path, _ = QFileDialog.getOpenFileName(
        parent,
        "Impor Subtitle SRT",
        "",
        "Subtitle SRT (*.srt)",
    )
    if path:
        _emit(sink, UiIntentType.SUBTITLE_IMPORT_SRT, path=path)


def _save_srt_copy(parent: Any, sink: UiIntentSink | None) -> None:
    from PySide6.QtWidgets import QFileDialog

    path, _ = QFileDialog.getSaveFileName(
        parent,
        "Simpan Salinan Subtitle",
        "subtitle-edited.srt",
        "Subtitle SRT (*.srt)",
    )
    if path:
        _emit(sink, UiIntentType.SUBTITLE_SAVE_COPY, path=path)


def create_subtitle_workspace(sink: UiIntentSink | None) -> Any:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import (
        QCheckBox,
        QComboBox,
        QFormLayout,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QListWidget,
        QListWidgetItem,
        QPushButton,
        QSpinBox,
        QTableWidget,
        QTableWidgetItem,
        QTabWidget,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )

    tabs = QTabWidget()
    tabs.setObjectName("w5_subtitle_tabs")

    text_page = QWidget()
    text_page.setObjectName("w5_subtitle_text_page")
    layout = QVBoxLayout(text_page)
    layout.setContentsMargins(8, 8, 8, 8)
    layout.setSpacing(7)

    header = QHBoxLayout()
    header.addWidget(section_title("Daftar Subtitle"))
    header.addStretch(1)
    import_srt = QPushButton("Impor SRT")
    import_srt.setObjectName("btn_w5_import_srt")
    import_srt.clicked.connect(lambda: _open_srt(text_page, sink))
    header.addWidget(import_srt)
    add_cue = QPushButton("＋ Tambah Cue")
    add_cue.setObjectName("btn_w5_add_cue")
    header.addWidget(add_cue)
    layout.addLayout(header)

    source_note = muted_label("Sumber SRT tidak pernah ditimpa diam-diam.")
    source_note.setObjectName("label_w5_srt_safety")
    layout.addWidget(source_note)

    cue_list = QListWidget()
    cue_list.setObjectName("w5_subtitle_cue_list")
    cues = [
        ("SRT-000001", "1   00:00:00:00 → 00:00:04:12\nPagi yang cerah di desa Bromo..."),
        ("SRT-000002", "2   00:00:04:12 → 00:00:08:20\nIa melihat bunga berwarna-warni..."),
        ("SRT-000003", "3   00:00:08:20 → 00:00:12:00\nLalu melompat ke arah pagar kayu..."),
        ("SRT-000004", "4   00:00:12:00 → 00:00:16:15\nUdara segar membuatnya bersemangat."),
    ]
    for cue_id, label in cues:
        item = QListWidgetItem(label)
        item.setData(Qt.ItemDataRole.UserRole, cue_id)
        cue_list.addItem(item)
    cue_list.setCurrentRow(2)
    cue_list.currentItemChanged.connect(
        lambda current, _previous: _emit(
            sink,
            UiIntentType.SUBTITLE_SELECT_CUE,
            cue_id=str(current.data(Qt.ItemDataRole.UserRole) if current else ""),
        )
    )
    layout.addWidget(cue_list, 1)

    edit_header = QHBoxLayout()
    edit_header.addWidget(section_title("Edit Cue"))
    edit_header.addStretch(1)
    dirty = QLabel("Working copy · perubahan belum disimpan")
    dirty.setObjectName("label_w5_working_copy")
    dirty.setStyleSheet("color:#92400E; background:#FFFBEB; padding:4px 7px;")
    edit_header.addWidget(dirty)
    layout.addLayout(edit_header)

    text = QTextEdit("Lalu melompat ke arah pagar kayu dengan lincah.")
    text.setObjectName("w5_subtitle_text")
    text.setMaximumHeight(72)
    layout.addWidget(text)

    form = QFormLayout()
    in_time = QLineEdit("00:00:08:20")
    in_time.setObjectName("w5_subtitle_in")
    out_time = QLineEdit("00:00:12:00")
    out_time.setObjectName("w5_subtitle_out")
    form.addRow("Waktu Mulai (IN)", in_time)
    form.addRow("Waktu Selesai (OUT)", out_time)
    layout.addLayout(form)

    apply_cue = make_primary_button("Terapkan Cue", "btn_w5_apply_cue")
    apply_cue.clicked.connect(
        lambda: _emit(
            sink,
            UiIntentType.SUBTITLE_EDIT_CUE,
            cue_id=_selected_cue_id(cue_list),
            text=text.toPlainText(),
            in_timecode=in_time.text(),
            out_timecode=out_time.text(),
        )
    )
    layout.addWidget(apply_cue)

    edit_row = QHBoxLayout()
    split_cue = QPushButton("Pisah Cue")
    split_cue.setObjectName("btn_w5_split_cue")
    split_cue.clicked.connect(
        lambda: _emit(
            sink,
            UiIntentType.SPLIT_CUE,
            cue_id=_selected_cue_id(cue_list),
        )
    )
    merge_cue = QPushButton("Gabung")
    merge_cue.setObjectName("btn_w5_merge_cue")
    merge_cue.clicked.connect(
        lambda: _emit(
            sink,
            UiIntentType.MERGE_CUE,
            cue_id=_selected_cue_id(cue_list),
        )
    )
    delete_cue = QPushButton("Hapus")
    delete_cue.setObjectName("btn_w5_delete_cue")
    delete_cue.clicked.connect(
        lambda: _emit(
            sink,
            UiIntentType.SUBTITLE_DELETE_CUE,
            cue_id=_selected_cue_id(cue_list),
        )
    )
    reload_srt = QPushButton("Muat Ulang SRT")
    reload_srt.setObjectName("btn_w5_reload_srt")
    reload_srt.clicked.connect(
        lambda: _emit(
            sink,
            UiIntentType.RELOAD_SRT,
            cue_id=_selected_cue_id(cue_list),
        )
    )
    for button in (split_cue, merge_cue, delete_cue, reload_srt):
        edit_row.addWidget(button)
    layout.addLayout(edit_row)

    add_cue.clicked.connect(
        lambda: _emit(
            sink,
            UiIntentType.SUBTITLE_INSERT_CUE,
            after_cue_id=_selected_cue_id(cue_list),
        )
    )

    save_copy = QPushButton("Simpan sebagai Salinan SRT…")
    save_copy.setObjectName("btn_w5_save_srt_copy")
    save_copy.clicked.connect(lambda: _save_srt_copy(text_page, sink))
    layout.addWidget(save_copy)
    timing_lock = QCheckBox("Kunci timing")
    timing_lock.setObjectName("check_w5_timing_lock")
    layout.addWidget(timing_lock)
    tabs.addTab(text_page, "Teks")

    style_page = QWidget()
    style_page.setObjectName("w5_subtitle_style_page")
    style_layout = QVBoxLayout(style_page)
    style_layout.setContentsMargins(8, 8, 8, 8)
    style_layout.addWidget(section_title("Gaya Subtitle"))
    style_form = QFormLayout()

    font_family = QComboBox()
    font_family.setObjectName("combo_w5_subtitle_font")
    font_family.addItems(QUALIFIED_SUBTITLE_FONTS)
    font_size = QSpinBox()
    font_size.setObjectName("spin_w5_subtitle_font_size")
    font_size.setRange(12, 160)
    font_size.setValue(54)
    fill = QLineEdit("#FFFFFF")
    fill.setObjectName("edit_w5_subtitle_fill")
    outline = QLineEdit("#111111")
    outline.setObjectName("edit_w5_subtitle_outline")
    outline_width = QSpinBox()
    outline_width.setObjectName("spin_w5_subtitle_outline_width")
    outline_width.setRange(0, 100)
    outline_width.setValue(30)
    outline_width.setSuffix(" /10")
    shadow = QSpinBox()
    shadow.setObjectName("spin_w5_subtitle_shadow")
    shadow.setRange(0, 100)
    shadow.setValue(10)
    shadow.setSuffix(" /10")
    background_box = QCheckBox("Aktif")
    background_box.setObjectName("check_w5_subtitle_background")
    background_opacity = QSpinBox()
    background_opacity.setObjectName("spin_w5_subtitle_background_opacity")
    background_opacity.setRange(0, 100)
    background_opacity.setSuffix("%")
    alignment = QComboBox()
    alignment.setObjectName("combo_w5_subtitle_alignment")
    alignment.addItem("Atas", "top_center")
    alignment.addItem("Tengah", "center")
    alignment.addItem("Bawah", "bottom_center")
    alignment.setCurrentIndex(2)
    margin = QSpinBox()
    margin.setObjectName("spin_w5_subtitle_margin")
    margin.setRange(0, 1000)
    margin.setValue(64)

    style_form.addRow("Font", font_family)
    style_form.addRow("Ukuran", font_size)
    style_form.addRow("Warna", fill)
    style_form.addRow("Outline", outline)
    style_form.addRow("Tebal Outline", outline_width)
    style_form.addRow("Shadow", shadow)
    style_form.addRow("Background", background_box)
    style_form.addRow("Opacity BG", background_opacity)
    style_form.addRow("Posisi", alignment)
    style_form.addRow("Margin Vertikal", margin)
    style_layout.addLayout(style_form)

    font_note = muted_label("Font render-qualified: Arial, Segoe UI.")
    font_note.setObjectName("label_w5_qualified_fonts")
    style_layout.addWidget(font_note)
    apply_style = make_primary_button("Terapkan Gaya", "btn_w5_apply_subtitle_style")
    apply_style.clicked.connect(
        lambda: _emit(
            sink,
            UiIntentType.SUBTITLE_SET_STYLE,
            font_family=font_family.currentText(),
            font_size=font_size.value(),
            fill_color=fill.text(),
            outline_color=outline.text(),
            outline_width_tenths=outline_width.value(),
            shadow_tenths=shadow.value(),
            background_box=str(background_box.isChecked()).lower(),
            background_opacity_percent=background_opacity.value(),
            alignment=alignment.currentData(),
            margin_v=margin.value(),
        )
    )
    style_layout.addWidget(apply_style)
    style_layout.addStretch(1)
    tabs.addTab(style_page, "Gaya")

    animation_page = QWidget()
    animation_page.setObjectName("w5_subtitle_animation_page")
    animation_layout = QVBoxLayout(animation_page)
    animation_layout.setContentsMargins(8, 8, 8, 8)
    animation_layout.addWidget(section_title("Animasi Subtitle"))
    animation_form = QFormLayout()

    preset = QComboBox()
    preset.setObjectName("combo_w5_subtitle_animation")
    for name in SUPPORTED_SUBTITLE_ANIMATIONS:
        label = "Tanpa Animasi" if name == "none" else name
        preset.addItem(label, name)
    enter_frames = QSpinBox()
    enter_frames.setObjectName("spin_w5_animation_enter")
    enter_frames.setRange(0, 300)
    enter_frames.setSuffix(" f")
    exit_frames = QSpinBox()
    exit_frames.setObjectName("spin_w5_animation_exit")
    exit_frames.setRange(0, 300)
    exit_frames.setSuffix(" f")
    intensity = QSpinBox()
    intensity.setObjectName("spin_w5_animation_intensity")
    intensity.setRange(0, 200)
    intensity.setValue(100)
    intensity.setSuffix("%")

    def update_animation_timing() -> None:
        animated = preset.currentData() != "none"
        enter_frames.setEnabled(animated)
        exit_frames.setEnabled(animated)
        intensity.setEnabled(animated)
        if not animated:
            enter_frames.setValue(0)
            exit_frames.setValue(0)
        elif enter_frames.value() == 0 and exit_frames.value() == 0:
            enter_frames.setValue(12)
            exit_frames.setValue(12)

    preset.currentIndexChanged.connect(update_animation_timing)
    update_animation_timing()
    animation_form.addRow("Preset", preset)
    animation_form.addRow("Masuk", enter_frames)
    animation_form.addRow("Keluar", exit_frames)
    animation_form.addRow("Intensitas", intensity)
    animation_layout.addLayout(animation_form)

    unsupported = QLabel("Belum render-qualified: " + ", ".join(UNSUPPORTED_SUBTITLE_ANIMATIONS))
    unsupported.setObjectName("label_w5_unqualified_subtitle_animations")
    unsupported.setWordWrap(True)
    unsupported.setStyleSheet("color:#64748B; font-size:10px;")
    animation_layout.addWidget(unsupported)

    apply_animation = make_primary_button(
        "Terapkan Animasi",
        "btn_w5_apply_subtitle_animation",
    )
    apply_animation.clicked.connect(
        lambda: _emit(
            sink,
            UiIntentType.SUBTITLE_SET_ANIMATION,
            preset=preset.currentData(),
            enter_frames=enter_frames.value(),
            exit_frames=exit_frames.value(),
            intensity_percent=intensity.value(),
        )
    )
    animation_layout.addWidget(apply_animation)

    animation_layout.addWidget(section_title("Timing Per Kata"))
    boundary = QLabel(
        "Distribusi rata hanya fallback deterministik — NOT speech alignment. "
        "Tidak ada ASR/transkripsi."
    )
    boundary.setObjectName("label_w5_not_speech_alignment")
    boundary.setWordWrap(True)
    boundary.setStyleSheet(
        "color:#92400E; background:#FFFBEB; border:1px solid #FDE68A; "
        "border-radius:6px; padding:7px;"
    )
    animation_layout.addWidget(boundary)

    timing_table = QTableWidget(3, 3)
    timing_table.setObjectName("table_w5_word_timing")
    timing_table.setHorizontalHeaderLabels(["Kata", "IN frame", "OUT frame"])
    for row, values in enumerate(
        (("AI", "30", "50"), ("ngerti", "50", "80"), ("geopolitik", "80", "120"))
    ):
        for column, value in enumerate(values):
            timing_table.setItem(row, column, QTableWidgetItem(value))
    timing_table.setMaximumHeight(126)
    animation_layout.addWidget(timing_table)

    apply_manual = QPushButton("Terapkan Timing Manual")
    apply_manual.setObjectName("btn_w5_apply_manual_word_timing")

    def emit_manual_timing() -> None:
        rows: list[str] = []
        for row in range(timing_table.rowCount()):
            values = []
            for column in range(3):
                item = timing_table.item(row, column)
                values.append(item.text().strip() if item else "")
            rows.append("|".join(values))
        _emit(
            sink,
            UiIntentType.SUBTITLE_SET_WORD_TIMING,
            mode="manual",
            timings=";".join(rows),
        )

    apply_manual.clicked.connect(emit_manual_timing)
    animation_layout.addWidget(apply_manual)

    acknowledge = QCheckBox("Saya paham: NOT speech alignment")
    acknowledge.setObjectName("check_w5_word_even_ack")
    animation_layout.addWidget(acknowledge)
    even_button = QPushButton("Distribusikan Rata")
    even_button.setObjectName("btn_w5_word_even")
    even_button.setEnabled(False)
    acknowledge.toggled.connect(even_button.setEnabled)
    even_button.clicked.connect(
        lambda: _emit(
            sink,
            UiIntentType.SUBTITLE_SET_WORD_TIMING,
            mode="even_not_speech_alignment",
            acknowledged="true",
        )
    )
    animation_layout.addWidget(even_button)

    highlight = muted_label(
        "Highlight/karaoke kata belum render-qualified — kontrol dinonaktifkan."
    )
    highlight.setObjectName("label_w5_word_highlight_unavailable")
    animation_layout.addWidget(highlight)
    animation_layout.addStretch(1)
    tabs.addTab(animation_page, "Animasi")
    return tabs


def _open_narration_audio(parent: Any, sink: UiIntentSink | None) -> None:
    from PySide6.QtWidgets import QFileDialog

    path, _ = QFileDialog.getOpenFileName(
        parent,
        "Impor Audio Narasi",
        "",
        "Audio (*.wav *.mp3 *.m4a *.aac *.flac *.ogg);;Semua File (*.*)",
    )
    if path:
        _emit(sink, UiIntentType.NARRATION_IMPORT_AUDIO, path=path)


def create_narration_workspace(
    sink: UiIntentSink | None,
    *,
    record_callback: Callable[[], None] | None = None,
) -> Any:
    from PySide6.QtWidgets import (
        QCheckBox,
        QFormLayout,
        QHBoxLayout,
        QLabel,
        QPushButton,
        QSpinBox,
        QVBoxLayout,
        QWidget,
    )

    root = QWidget()
    root.setObjectName("w5_narration_workspace")
    layout = QVBoxLayout(root)
    layout.setContentsMargins(10, 10, 10, 10)
    layout.setSpacing(8)
    layout.addWidget(section_title("Audio / Narasi"))

    source = QLabel("Belum ada narasi terikat")
    source.setObjectName("label_w5_narration_source")
    source.setStyleSheet("font-weight:700; color:#172033;")
    layout.addWidget(source)

    import_button = QPushButton("Impor Audio Narasi…")
    import_button.setObjectName("btn_w5_import_narration")
    import_button.clicked.connect(lambda: _open_narration_audio(root, sink))
    layout.addWidget(import_button)

    form = QFormLayout()
    offset = QSpinBox()
    offset.setObjectName("spin_w5_narration_start")
    offset.setRange(0, 10_000_000)
    offset.setSuffix(" f")
    gain = QSpinBox()
    gain.setObjectName("spin_w5_narration_gain")
    gain.setRange(0, 400)
    gain.setValue(100)
    gain.setSuffix("%")
    muted = QCheckBox("Mute")
    muted.setObjectName("check_w5_narration_muted")
    fade_in = QSpinBox()
    fade_in.setObjectName("spin_w5_narration_fade_in")
    fade_in.setRange(0, 100_000)
    fade_in.setSuffix(" f")
    fade_out = QSpinBox()
    fade_out.setObjectName("spin_w5_narration_fade_out")
    fade_out.setRange(0, 100_000)
    fade_out.setSuffix(" f")
    form.addRow("Mulai Timeline", offset)
    form.addRow("Gain", gain)
    form.addRow("", muted)
    form.addRow("Fade In", fade_in)
    form.addRow("Fade Out", fade_out)
    layout.addLayout(form)

    apply_controls = make_primary_button(
        "Terapkan Narasi",
        "btn_w5_apply_narration",
    )
    apply_controls.clicked.connect(
        lambda: _emit(
            sink,
            UiIntentType.NARRATION_SET_CONTROLS,
            timeline_start_frame=offset.value(),
            gain_percent=gain.value(),
            muted=str(muted.isChecked()).lower(),
            fade_in_frames=fade_in.value(),
            fade_out_frames=fade_out.value(),
        )
    )
    layout.addWidget(apply_controls)

    row = QHBoxLayout()
    preview = QPushButton("Pratinjau Audio")
    preview.setObjectName("btn_w5_preview_narration")
    preview.clicked.connect(
        lambda: _emit(
            sink,
            UiIntentType.NARRATION_PREVIEW,
            timeline_frame=offset.value(),
            duration_frames=90,
        )
    )
    record = QPushButton("● Rekam Narasi")
    record.setObjectName("btn_w5_open_recording")
    if record_callback is None:
        record.clicked.connect(lambda: _emit(sink, UiIntentType.RECORD_NARRATION))
    else:
        record.clicked.connect(record_callback)
    row.addWidget(preview)
    row.addWidget(record)
    layout.addLayout(row)

    provisional = QLabel(
        "Microphone software path siap. Kualifikasi perangkat fisik masih provisional "
        "sampai diuji pada Windows dengan input microphone nyata."
    )
    provisional.setObjectName("label_w5_microphone_provisional")
    provisional.setWordWrap(True)
    provisional.setStyleSheet(
        "color:#92400E; background:#FFFBEB; border:1px solid #FDE68A; "
        "border-radius:6px; padding:7px;"
    )
    layout.addWidget(provisional)
    layout.addStretch(1)
    return root


def create_narration_recording_dialog(
    parent: Any,
    sink: UiIntentSink | None,
) -> Any:
    from PySide6.QtWidgets import (
        QComboBox,
        QDialog,
        QDialogButtonBox,
        QFormLayout,
        QHBoxLayout,
        QLabel,
        QPushButton,
        QSpinBox,
        QVBoxLayout,
    )

    dialog = QDialog(parent)
    dialog.setObjectName("dialog_w5_narration_recording")
    dialog.setWindowTitle("Rekam Narasi")
    dialog.resize(520, 360)
    layout = QVBoxLayout(dialog)
    layout.addWidget(section_title("Rekam Narasi"))

    status = QLabel(
        "Hardware fisik belum terverifikasi di CI. Pilih hanya perangkat yang "
        "benar-benar terdeteksi di PC ini."
    )
    status.setObjectName("label_w5_recording_hardware_status")
    status.setWordWrap(True)
    status.setStyleSheet(
        "color:#92400E; background:#FFFBEB; border:1px solid #FDE68A; "
        "border-radius:6px; padding:8px;"
    )
    layout.addWidget(status)

    form = QFormLayout()
    devices = QComboBox()
    devices.setObjectName("combo_w5_microphone_device")
    devices.addItem("Belum ada perangkat — klik Muat Ulang", "")
    duration = QSpinBox()
    duration.setObjectName("spin_w5_microphone_duration")
    duration.setRange(1, 3600)
    duration.setValue(60)
    duration.setSuffix(" detik")
    start_frame = QSpinBox()
    start_frame.setObjectName("spin_w5_microphone_start_frame")
    start_frame.setRange(0, 10_000_000)
    start_frame.setSuffix(" f")
    form.addRow("Perangkat", devices)
    form.addRow("Maks. Durasi", duration)
    form.addRow("Mulai Timeline", start_frame)
    layout.addLayout(form)

    refresh = QPushButton("Muat Ulang Perangkat")
    refresh.setObjectName("btn_w5_refresh_microphones")
    refresh.clicked.connect(lambda: _emit(sink, UiIntentType.MICROPHONE_REFRESH_DEVICES))
    layout.addWidget(refresh)

    actions = QHBoxLayout()
    start = make_primary_button("Mulai Rekam", "btn_w5_start_recording")
    start.setEnabled(False)
    cancel_capture = QPushButton("Hentikan / Batal")
    cancel_capture.setObjectName("btn_w5_cancel_recording")
    cancel_capture.clicked.connect(lambda: _emit(sink, UiIntentType.MICROPHONE_CANCEL_RECORDING))
    start.clicked.connect(
        lambda: _emit(
            sink,
            UiIntentType.MICROPHONE_START_RECORDING,
            device_id=devices.currentData(),
            max_duration_seconds=duration.value(),
            timeline_start_frame=start_frame.value(),
        )
    )
    actions.addWidget(start)
    actions.addWidget(cancel_capture)
    layout.addLayout(actions)

    footer = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
    footer.rejected.connect(dialog.close)
    layout.addWidget(footer)

    def set_devices(values: Sequence[tuple[str, str]]) -> None:
        devices.clear()
        for device_id, name in values:
            devices.addItem(name, device_id)
        if values:
            status.setText(
                f"{len(values)} perangkat input terdeteksi. Hardware qualification "
                "proyek tetap provisional sampai real smoke PASS."
            )
            start.setEnabled(True)
        else:
            devices.addItem("Tidak ada perangkat input terdeteksi", "")
            status.setText(
                "Tidak ada microphone input yang terdeteksi. Rekaman tidak dapat dimulai."
            )
            start.setEnabled(False)

    dialog.set_devices = set_devices  # type: ignore[attr-defined]
    return dialog
