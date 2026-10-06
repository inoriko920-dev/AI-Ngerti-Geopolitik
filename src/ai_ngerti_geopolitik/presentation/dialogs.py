from __future__ import annotations

from typing import Any

from ai_ngerti_geopolitik.application.ui_intents import UiIntent, UiIntentSink, UiIntentType
from ai_ngerti_geopolitik.presentation.common import make_primary_button, muted_label, section_title


def create_export_dialog(parent: Any, intent_sink: UiIntentSink) -> Any:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import (
        QCheckBox,
        QComboBox,
        QDialog,
        QFormLayout,
        QFrame,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QPushButton,
        QSlider,
        QVBoxLayout,
    )

    dialog = QDialog(parent)
    dialog.setObjectName("dlg_export_setup")
    dialog.setWindowTitle("Ekspor Video")
    dialog.resize(980, 690)
    dialog.setStyleSheet("QDialog {background:#FFFFFF;}")
    layout = QVBoxLayout(dialog)
    layout.setContentsMargins(24, 20, 24, 20)
    layout.setSpacing(12)

    header = QHBoxLayout()
    title = QLabel("Ekspor Video")
    title.setStyleSheet("font-size:22px; font-weight:750;")
    close = QPushButton("×")
    close.setObjectName("btn_export_close")
    close.setAccessibleName("Tutup dialog ekspor")
    close.setMaximumWidth(36)
    close.setStyleSheet("font-size:20px; border:none;")
    close.clicked.connect(dialog.reject)
    header.addWidget(title)
    header.addStretch(1)
    header.addWidget(close)
    layout.addLayout(header)
    layout.addWidget(
        muted_label(
            "Atur kualitas final. Preview boleh lebih ringan; render final memakai kualitas penuh."
        )
    )

    body = QHBoxLayout()
    body.setSpacing(18)

    settings = QFrame()
    settings.setProperty("panel", True)
    settings_layout = QVBoxLayout(settings)
    settings_layout.setContentsMargins(18, 18, 18, 18)
    settings_layout.addWidget(section_title("Pengaturan Output"))
    form = QFormLayout()
    output = QLineEdit(r"D:\Video Projects\Dokumenter Indonesia\Hasil Akhir")
    output.setObjectName("field_export_directory")
    name = QLineEdit("Dokumenter Indonesia - Final")
    name.setObjectName("field_export_name")
    format_box = QComboBox()
    format_box.addItems(["MP4 (H.264)", "MP4 (H.265)"])
    preset = QComboBox()
    preset.addItems(["Kualitas Tinggi (Rekomendasi)", "YouTube Clean", "Documentary Crisp"])
    resolution = QComboBox()
    resolution.addItems(["1920 × 1080 (Full HD)", "2560 × 1440", "3840 × 2160 (4K)"])
    fps = QComboBox()
    fps.addItems(["30 fps", "60 fps"])
    form.addRow("Lokasi Output", output)
    form.addRow("Nama File", name)
    form.addRow("Format", format_box)
    form.addRow("Preset", preset)
    form.addRow("Resolusi", resolution)
    form.addRow("Frame Rate", fps)
    settings_layout.addLayout(form)

    quality = QSlider(Qt.Orientation.Horizontal)
    quality.setValue(78)
    quality_row = QHBoxLayout()
    quality_row.addWidget(QLabel("Bitrate / Kualitas"))
    quality_row.addWidget(quality, 1)
    quality_row.addWidget(QLabel("78%"))
    settings_layout.addLayout(quality_row)
    sharpen = QComboBox()
    sharpen.addItems(["Normal", "Tajam Ringan", "Documentary Crisp"])
    settings_layout.addWidget(QLabel("Ketajaman Video"))
    settings_layout.addWidget(sharpen)
    subtitle = QCheckBox("Sertakan Subtitle (Burn-in ke Video)")
    subtitle.setChecked(True)
    settings_layout.addWidget(subtitle)
    settings_layout.addStretch(1)

    summary = QFrame()
    summary.setObjectName("panel_export_summary")
    summary.setProperty("panel", True)
    summary_layout = QVBoxLayout(summary)
    summary_layout.setContentsMargins(18, 18, 18, 18)
    summary_layout.addWidget(section_title("Ringkasan Export"))
    monitor = QFrame()
    monitor.setMinimumHeight(210)
    monitor.setStyleSheet("background:#171C24; border-radius:7px;")
    monitor_layout = QVBoxLayout(monitor)
    monitor_text = QLabel("16:9\n\nDokumenter Indonesia")
    monitor_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
    monitor_text.setStyleSheet("color:white; font-size:16px; font-weight:650;")
    monitor_layout.addWidget(monitor_text)
    summary_layout.addWidget(monitor)
    for label, value in [
        ("Durasi", "00:01:28"),
        ("Resolusi", "1920 × 1080"),
        ("Frame Rate", "30 fps"),
        ("Codec", "H.264"),
        ("Subtitle", "Burn-in"),
        ("Perkiraan", "± 84 MB"),
    ]:
        row = QHBoxLayout()
        row.addWidget(muted_label(label))
        row.addStretch(1)
        result = QLabel(value)
        result.setStyleSheet("font-weight:650;")
        row.addWidget(result)
        summary_layout.addLayout(row)
    shell_note = QLabel("STEP 09 UI shell — render nyata belum dihubungkan.")
    shell_note.setWordWrap(True)
    shell_note.setStyleSheet(
        "background:#EFF6FF; color:#1D4ED8; border:1px solid #BFDBFE; "
        "border-radius:6px; padding:8px;"
    )
    summary_layout.addWidget(shell_note)
    summary_layout.addStretch(1)

    body.addWidget(settings, 3)
    body.addWidget(summary, 2)
    layout.addLayout(body, 1)

    footer = QHBoxLayout()
    footer.addStretch(1)
    cancel = QPushButton("Batal")
    cancel.clicked.connect(dialog.reject)
    render = make_primary_button("Mulai Render", "btn_export_render")

    def request_render() -> None:
        intent_sink(
            UiIntent(
                UiIntentType.OPEN_EXPORT,
                (("action", "render_requested"), ("format", format_box.currentText())),
            )
        )
        shell_note.setText(
            "Permintaan render dicatat sebagai intent. Engine belum diaktifkan di STEP 09."
        )

    render.clicked.connect(request_render)
    footer.addWidget(cancel)
    footer.addWidget(render)
    layout.addLayout(footer)
    return dialog


def create_validation_dialog(parent: Any, intent_sink: UiIntentSink) -> Any:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import (
        QDialog,
        QFrame,
        QHBoxLayout,
        QLabel,
        QPushButton,
        QTabWidget,
        QVBoxLayout,
        QWidget,
    )

    dialog = QDialog(parent)
    dialog.setObjectName("dlg_validation_center")
    dialog.setWindowTitle("Pusat Error / Validasi")
    dialog.resize(650, 900)
    dialog.setMinimumWidth(600)
    dialog.setStyleSheet(
        "QDialog {background:#FFFFFF; border-left:1px solid #CBD5E1;} "
        "QTabWidget::pane {border:none; border-top:1px solid #E2E8F0;}"
    )
    layout = QVBoxLayout(dialog)
    layout.setContentsMargins(20, 16, 20, 18)
    layout.setSpacing(14)

    title_row = QHBoxLayout()
    title = QLabel("Pusat Error / Validasi")
    title.setStyleSheet("font-size:20px; font-weight:750;")
    close = QPushButton("×")
    close.setAccessibleName("Tutup pusat validasi")
    close.setMaximumWidth(36)
    close.setStyleSheet("border:none; font-size:20px;")
    close.clicked.connect(dialog.close)
    title_row.addWidget(title)
    title_row.addStretch(1)
    title_row.addWidget(close)
    layout.addLayout(title_row)

    summary = QFrame()
    summary.setStyleSheet("background:#FFF7F7; border:1px solid #FECACA; border-radius:9px;")
    summary_layout = QHBoxLayout(summary)
    summary_layout.setContentsMargins(14, 12, 14, 12)
    badge = QLabel("!")
    badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
    badge.setFixedSize(38, 38)
    badge.setStyleSheet(
        "background:#DC2626; color:white; border-radius:19px; font-size:22px; font-weight:800;"
    )
    summary_text = QVBoxLayout()
    headline = QLabel("2 Error, 3 Peringatan")
    headline.setStyleSheet("font-size:18px; font-weight:750; color:#B91C1C;")
    summary_text.addWidget(headline)
    summary_text.addWidget(muted_label("Ditemukan 5 masalah dalam project ini"))
    revalidate = make_primary_button("Validasi Ulang", "btn_validation_rerun")
    revalidate.clicked.connect(
        lambda: intent_sink(UiIntent(UiIntentType.OPEN_VALIDATION, (("action", "rerun"),)))
    )
    summary_layout.addWidget(badge)
    summary_layout.addLayout(summary_text, 1)
    summary_layout.addWidget(revalidate)
    layout.addWidget(summary)

    tabs = QTabWidget()
    tabs.setObjectName("tabs_validation")
    names = ["Semua (5)", "Project (1)", "Media (1)", "Scene (1)", "AI (1)", "Render (1)"]
    issues = [
        ("ERROR", "A037 MISSING — Scene 12, 13", "File media tidak ditemukan.", "Relink"),
        (
            "ERROR",
            "Subtitle cue tumpang tindih",
            "3 subtitle saling tumpang tindih.",
            "Buka Subtitle",
        ),
        ("WARN", "Durasi scene terlalu pendek", "Scene 04 hanya 0,8 detik.", "Buka Scene"),
        (
            "WARN",
            "Audio tidak normalisasi",
            "Audio track A1 belum dinormalisasi.",
            "Perbaiki Audio",
        ),
        ("WARN", "Provider Gemini quota", "Sisa quota hanya 12%.", "Buka Provider"),
    ]
    for tab_name in names:
        page = QWidget()
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(4, 14, 4, 6)
        page_layout.setSpacing(10)
        if tab_name.startswith("Semua"):
            for index, (severity, issue_title, description, action) in enumerate(issues):
                if index in {0, 2}:
                    group = QLabel("Error (2)" if index == 0 else "Peringatan (3)")
                    group.setStyleSheet("font-size:15px; font-weight:750;")
                    page_layout.addWidget(group)
                row = QFrame()
                is_error = severity == "ERROR"
                accent = "#DC2626" if is_error else "#F59E0B"
                row.setStyleSheet(
                    "QFrame {background:#FFFFFF; border:1px solid #E2E8F0; "
                    f"border-left:4px solid {accent}; border-radius:6px;}}"
                )
                row_layout = QHBoxLayout(row)
                marker = QLabel("!" if is_error else "▲")
                marker.setAlignment(Qt.AlignmentFlag.AlignCenter)
                marker.setFixedSize(30, 30)
                marker.setStyleSheet(f"color:{accent}; font-weight:800;")
                text = QVBoxLayout()
                issue = QLabel(issue_title)
                issue.setStyleSheet("font-weight:700; border:none;")
                text.addWidget(issue)
                text.addWidget(muted_label(description))
                action_button = QPushButton(action)
                action_button.setStyleSheet(
                    "color:#1D4ED8; border:none; font-weight:650; background:transparent;"
                )
                action_button.clicked.connect(
                    lambda _checked=False, target=action: intent_sink(
                        UiIntent(UiIntentType.OPEN_VALIDATION, (("action", target),))
                    )
                )
                row_layout.addWidget(marker)
                row_layout.addLayout(text, 1)
                row_layout.addWidget(action_button)
                page_layout.addWidget(row)
        page_layout.addStretch(1)
        tabs.addTab(page, tab_name)
    layout.addWidget(tabs, 1)
    return dialog
