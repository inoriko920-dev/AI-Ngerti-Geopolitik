"""STEP 12-02 — strict frozen export option validation and worker GUI wiring."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QLineEdit, QPushButton

from ai_ngerti_geopolitik.application.still_export_intent import (
    StillExportIntentError,
    validate_still_export_intent,
)
from ai_ngerti_geopolitik.application.ui_intents import RecordingIntentSink
from ai_ngerti_geopolitik.bootstrap import w8_controller
from ai_ngerti_geopolitik.bootstrap.w8_controller import (
    W8IntentRouter,
    W8RuntimeController,
)
from ai_ngerti_geopolitik.domain import Asset, Clip, FrameTime, ProjectState, Track
from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository
from ai_ngerti_geopolitik.infrastructure.pilot_a_still_mp4 import PilotAResult
from ai_ngerti_geopolitik.presentation.dialogs import create_export_dialog
from ai_ngerti_geopolitik.presentation.main_window import create_main_window
from ai_ngerti_geopolitik.presentation.navigation import UiRoute


def _state() -> ProjectState:
    state = ProjectState.create("STEP12-UI", "Export dialog sample", 30)
    return replace(
        state,
        assets=(
            Asset(
                "A001",
                "A001.png",
                "image",
                FrameTime(1, 30),
                64,
                48,
                False,
                "0" * 64,
            ),
        ),
        tracks=(
            Track(
                "V001",
                "video",
                0,
                clips=(
                    Clip(
                        "C001",
                        "A001",
                        FrameTime(0, 30),
                        FrameTime(0, 30),
                        FrameTime(1, 30),
                        image_hold_frames=1,
                    ),
                ),
            ),
        ),
    )


def _payload(tmp_path: Path) -> dict[str, str]:
    return {
        "action": "render_requested",
        "output_directory": str(tmp_path),
        "output_name": "Geopolitik Final",
        "format": "MP4 (H.264)",
        "preset": "Kualitas Tinggi (Rekomendasi)",
        "resolution": "1920 × 1080 (Full HD)",
        "fps": "30 fps",
        "quality": "78",
        "sharpen": "Normal",
        "subtitle": "Tanpa Subtitle",
    }


def test_frozen_ui_export_contract_accepts_only_exact_silent_settings(tmp_path: Path) -> None:
    state = _state()
    path = validate_still_export_intent(_payload(tmp_path), state)
    assert path == tmp_path / "Geopolitik Final.mp4"
    assert not path.exists()


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("format", "MP4 (H.265)"),
        ("preset", "YouTube Clean"),
        ("quality", "90"),
        ("sharpen", "Tajam Ringan"),
        ("subtitle", "Sertakan Subtitle (Burn-in ke Video)"),
        ("resolution", "2560 × 1440"),
        ("fps", "60 fps"),
        ("output_name", "../unsafe"),
    ],
)
def test_unsupported_preset_is_rejected_before_any_render(
    tmp_path: Path, field: str, value: str
) -> None:
    payload = _payload(tmp_path)
    payload[field] = value
    with pytest.raises(StillExportIntentError):
        validate_still_export_intent(payload, _state())
    assert not list(tmp_path.glob("*.mp4"))


def test_existing_mp4_cannot_be_overwritten(tmp_path: Path) -> None:
    original = tmp_path / "Geopolitik Final.mp4"
    original.write_bytes(b"original")
    with pytest.raises(StillExportIntentError):
        validate_still_export_intent(_payload(tmp_path), _state())
    assert original.read_bytes() == b"original"


def _controller(qtbot, tmp_path: Path):
    repository = JsonProjectRepository()
    project_path = tmp_path / "saved.angproj"
    repository.save(_state(), project_path)
    router = W8IntentRouter()
    window = create_main_window("UI-010", fixture_mode=True, intent_sink=router)
    qtbot.addWidget(window.window)
    controller = W8RuntimeController(window, timer_enabled=False)
    router.delegate = controller.handle
    controller.session.open_project(project_path)
    window.show()
    window.show_route(UiRoute.EXPORT_SETTINGS)
    dialog = window._active_dialog
    assert dialog is not None
    assert dialog.objectName() == "dlg_export_setup"
    return controller, window, dialog


def test_modal_emits_all_selections_without_changing_frozen_widget_layout(qtbot) -> None:
    recorder = RecordingIntentSink()
    dialog = create_export_dialog(intent_sink=recorder)
    qtbot.addWidget(dialog)
    dialog.show()
    options = dialog.findChildren(QComboBox)
    assert len(options) == 6
    options[-1].setCurrentText("Tanpa Subtitle")
    button = dialog.findChild(QPushButton, "btn_export_render")
    assert button is not None
    qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
    assert len(recorder.intents) == 1
    choices = dict(recorder.intents[0].payload)
    assert set(choices) == set(_payload(Path("C:/Folder")))
    assert choices["format"] == "MP4 (H.264)"
    assert choices["resolution"] == "1920 × 1080 (Full HD)"
    assert choices["fps"] == "30 fps"
    assert choices["subtitle"] == "Tanpa Subtitle"
    dialog.close()


def test_render_button_rejects_unsupported_subtitle_without_native_worker(
    qtbot, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("ANG_PILOT_A_FFMPEG", "1")
    controller, window, dialog = _controller(qtbot, tmp_path)
    folder = dialog.findChild(QLineEdit, "field_export_directory")
    filename = dialog.findChild(QLineEdit, "field_export_name")
    assert folder is not None and filename is not None
    folder.setText(str(tmp_path))
    filename.setText("no silent mismatch")
    button = dialog.findChild(QPushButton, "btn_export_render")
    assert button is not None
    qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
    assert controller.export_future is None
    assert "subtitle" in controller.last_error.lower()
    assert not (tmp_path / "no silent mismatch.mp4").exists()
    controller.shutdown()
    window.close()


def test_render_button_starts_worker_and_returns_to_editor_without_blocking(
    qtbot, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("ANG_PILOT_A_FFMPEG", "1")
    controller, window, dialog = _controller(qtbot, tmp_path)
    folder = dialog.findChild(QLineEdit, "field_export_directory")
    filename = dialog.findChild(QLineEdit, "field_export_name")
    assert folder is not None and filename is not None
    folder.setText(str(tmp_path))
    filename.setText("gui-project")
    options = dialog.findChildren(QComboBox)
    assert len(options) == 6
    options[-1].setCurrentText("Tanpa Subtitle")
    invoked: list[Path] = []

    def fake_native_worker(state: ProjectState, output: Path, cancel) -> PilotAResult:
        assert not cancel.is_set()
        assert state.project_id == "STEP12-UI"
        invoked.append(output)
        return PilotAResult(
            path=output,
            sha256="0" * 64,
            file_bytes=100,
            frame_count=1,
            fps=30,
            width=1920,
            height=1080,
            duration_seconds=1 / 30,
            rgb24_sha256="1" * 64,
        )

    monkeypatch.setattr(w8_controller, "_run_pilot_gui_export", fake_native_worker)
    button = dialog.findChild(QPushButton, "btn_export_render")
    assert button is not None
    qtbot.mouseClick(button, Qt.MouseButton.LeftButton)

    def done() -> bool:
        controller.poll()
        return controller.export_future is None

    qtbot.waitUntil(done, timeout=5000)
    assert invoked == [tmp_path / "gui-project.mp4"]
    assert window.window.property("ui_state") == UiRoute.EDITOR.value
    assert "terverifikasi" in controller.last_error
    controller.shutdown()
    window.close()
