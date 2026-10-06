from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QPushButton, QWidget

from ai_ngerti_geopolitik.application.ui_intents import RecordingIntentSink, UiIntentType
from ai_ngerti_geopolitik.presentation.editor_shell import create_editor_shell
from ai_ngerti_geopolitik.presentation.main_window import create_main_window
from ai_ngerti_geopolitik.presentation.navigation import UiRoute


def test_home_routes_to_new_project_and_emits_intent(qtbot) -> None:
    sink = RecordingIntentSink()
    window = create_main_window("UI-002", fixture_mode=True, intent_sink=sink)
    qtbot.addWidget(window.window)
    window.show()

    button = window.window.findChild(QPushButton, "btn_home_new_project")
    assert button is not None
    qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
    assert window.window.property("ui_state") == "UI-003"
    assert sink.intents[-1].kind is UiIntentType.NEW_PROJECT
    window.close()


def test_all_representative_routes_have_real_qt_surfaces(qtbot) -> None:
    window = create_main_window("UI-002", fixture_mode=True)
    qtbot.addWidget(window.window)
    window.show()

    for route in UiRoute:
        window.show_route(route)
        assert window.window.property("ui_state") == route.value
        assert isinstance(window.stack.currentWidget(), QWidget)
        if route in {UiRoute.EXPORT_SETTINGS, UiRoute.VALIDATION_CENTER}:
            assert isinstance(window._active_dialog, QDialog)
            assert window._active_dialog.isVisible()
    window.close()


def test_editor_shell_exposes_real_left_preview_right_timeline_panes(qtbot) -> None:
    shell = create_editor_shell("overview")
    qtbot.addWidget(shell.root)
    shell.root.resize(1920, 1000)
    shell.root.show()
    qtbot.wait(50)

    assert shell.left_tabs.width() > 150
    assert shell.preview_frame.width() > 400
    assert shell.preview_frame.height() > 180
    assert shell.right_tabs.width() > 200
    assert shell.timeline.height() >= 180
    assert shell.status_label.text()
    shell.root.close()


def test_toolbar_critical_icon_actions_have_accessible_names(qtbot) -> None:
    window = create_main_window("UI-010", fixture_mode=True)
    qtbot.addWidget(window.window)
    window.show()

    export = window.window.findChild(QPushButton, "btn_export_video")
    validation = window.window.findChild(QPushButton, "btn_open_validation")
    assert export is not None and export.accessibleName() == "Ekspor Video"
    assert validation is not None and validation.accessibleName() == "Buka Pusat Validasi"
    window.close()
