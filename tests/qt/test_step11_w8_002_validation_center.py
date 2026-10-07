from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QPushButton, QTabWidget

from ai_ngerti_geopolitik.application.ui_intents import RecordingIntentSink, UiIntentType
from ai_ngerti_geopolitik.application.validation import ValidationService
from ai_ngerti_geopolitik.domain import Asset, Clip, FrameTime, ProjectState, Track
from ai_ngerti_geopolitik.presentation.dialogs import create_validation_dialog
from ai_ngerti_geopolitik.presentation.validation_center import project_validation_center


def _state() -> ProjectState:
    asset = Asset(
        "A001",
        "missing.mp4",
        "video",
        FrameTime(120, 30),
        1920,
        1080,
        True,
        "a" * 64,
        availability="missing",
    )
    clip = Clip("C001", "A001", FrameTime(0, 30), FrameTime(0, 30), FrameTime(90, 30))
    return ProjectState(
        "P-W8-002-UI",
        "Validation UI",
        1,
        30,
        7,
        assets=(asset,),
        tracks=(Track("V1", "video", 0, (clip,)),),
    )


def test_ui041_projects_real_validation_without_layout_redesign(qtbot) -> None:
    state = _state()
    result = ValidationService().validate(state)
    projection = project_validation_center(result, state)
    sink = RecordingIntentSink()
    dialog = create_validation_dialog(intent_sink=sink, projection=projection)
    qtbot.addWidget(dialog)
    dialog.show()

    assert dialog.objectName() == "dlg_validation_center"
    assert dialog.minimumWidth() == 600
    tabs = dialog.findChild(QTabWidget, "tabs_validation")
    summary = dialog.findChild(QLabel, "label_validation_summary")
    title = dialog.findChild(QLabel, "label_validation_issue_0_0")
    action = dialog.findChild(QPushButton, "btn_validation_issue_0_0_action")
    assert tabs is not None
    assert [tabs.tabText(i) for i in range(tabs.count())] == [
        "Semua (1)",
        "Project (0)",
        "Media (1)",
        "Scene (0)",
        "AI (0)",
        "Render (0)",
    ]
    assert summary is not None and summary.text() == "1 Error, 0 Peringatan"
    assert title is not None and title.text().startswith("BLOCKER ·")
    assert action is not None and action.text() == "Relink" and action.isEnabled()

    qtbot.mouseClick(action, Qt.MouseButton.LeftButton)
    assert sink.intents[-1].kind is UiIntentType.OPEN_VALIDATION
    payload = dict(sink.intents[-1].payload)
    assert payload["action"] == "RELINK_MEDIA"
    assert payload["issue_code"] == "MEDIA_MISSING_REFERENCED"
    assert payload["targets"] == "A001,C001"
    dialog.close()


def test_ui041_stale_projection_disables_issue_action_but_keeps_rerun(qtbot) -> None:
    state = _state()
    result = ValidationService().validate(state)
    projection = project_validation_center(result, state.with_revision(8))
    sink = RecordingIntentSink()
    dialog = create_validation_dialog(intent_sink=sink, projection=projection)
    qtbot.addWidget(dialog)
    dialog.show()

    summary = dialog.findChild(QLabel, "label_validation_summary")
    action = dialog.findChild(QPushButton, "btn_validation_issue_0_0_action")
    rerun = dialog.findChild(QPushButton, "btn_validation_rerun")
    assert summary is not None and "usang" in summary.text().lower()
    assert action is not None and not action.isEnabled()
    assert rerun is not None and rerun.isEnabled()

    qtbot.mouseClick(rerun, Qt.MouseButton.LeftButton)
    assert sink.intents[-1].kind is UiIntentType.OPEN_VALIDATION
    assert dict(sink.intents[-1].payload)["action"] == "rerun"
    dialog.close()
