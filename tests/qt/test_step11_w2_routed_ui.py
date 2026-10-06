from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QCheckBox, QComboBox, QPushButton, QSlider

from ai_ngerti_geopolitik.application.commands import (
    AddClipCommand,
    CommandBatch,
    CommandBus,
    ImportAssetCommand,
)
from ai_ngerti_geopolitik.application.playback import PlaybackController
from ai_ngerti_geopolitik.application.ports import PreviewResult
from ai_ngerti_geopolitik.application.timeline import (
    FollowMode,
    TimelineController,
    TimelineIntentRouter,
)
from ai_ngerti_geopolitik.domain import Asset, Clip, FrameTime, ProjectState
from ai_ngerti_geopolitik.presentation.main_window import create_main_window


class PreviewEngine:
    def preview_frame(
        self,
        state: ProjectState,
        timeline_frame: int,
        output_path: Path,
    ) -> PreviewResult:
        return PreviewResult(state.revision, timeline_frame, output_path)

    def export(self, state, output_path, cancellation=None):  # type: ignore[no-untyped-def]
        raise AssertionError("export is outside the routed W2 UI test")


class RecordingTransport:
    def __init__(self) -> None:
        self.events: list[tuple[str, int | None]] = []

    def load(self, state: ProjectState) -> None:
        self.events.append(("load", state.revision))

    def seek(self, frame: int) -> None:
        self.events.append(("seek", frame))

    def play(self) -> None:
        self.events.append(("play", None))

    def pause(self) -> None:
        self.events.append(("pause", None))

    def stop(self) -> None:
        self.events.append(("stop", None))


def _controller(tmp_path: Path) -> tuple[TimelineController, RecordingTransport]:
    bus = CommandBus(ProjectState.create("W2-QT", "Routed W2 UI", 30))
    asset = Asset(
        "A001",
        "fixture.mp4",
        "video",
        FrameTime(180, 30),
        1920,
        1080,
        True,
        "e" * 64,
    )
    bus.execute(CommandBatch("B1", "import", "manual", 0, (ImportAssetCommand(asset),)))
    for clip in (
        Clip("C001", "A001", FrameTime(0, 30), FrameTime(0, 30), FrameTime(60, 30)),
        Clip("C002", "A001", FrameTime(60, 30), FrameTime(60, 30), FrameTime(120, 30)),
    ):
        bus.execute(
            CommandBatch(
                f"B{bus.state.revision + 1}",
                "add clip",
                "manual",
                bus.state.revision,
                (AddClipCommand(clip),),
            )
        )
    transport = RecordingTransport()
    playback = PlaybackController(lambda: bus.state, PreviewEngine(), tmp_path, transport)
    return TimelineController(bus, playback), transport


def test_real_qt_controls_route_into_canonical_w2_controller(qtbot, tmp_path: Path) -> None:
    controller, transport = _controller(tmp_path)
    router = TimelineIntentRouter(controller)
    window = create_main_window("UI-010", fixture_mode=True, intent_sink=router)
    qtbot.addWidget(window.window)
    window.show()
    current = window.stack.currentWidget()

    play = current.findChild(QPushButton, "btn_playback_play")
    pause = current.findChild(QPushButton, "btn_playback_pause")
    previous = current.findChild(QPushButton, "btn_playback_previous")
    next_button = current.findChild(QPushButton, "btn_playback_next")
    scrubber = current.findChild(QSlider, "timeline_scrubber")
    assert all(item is not None for item in (play, pause, previous, next_button, scrubber))

    qtbot.mouseClick(play, Qt.MouseButton.LeftButton)
    assert controller.playback.snapshot.playing is True
    assert ("play", None) in transport.events

    scrubber.setValue(30)
    scrubber.sliderReleased.emit()
    assert controller.playback.snapshot.frame == 30
    assert controller.playback.snapshot.playing is False

    qtbot.mouseClick(previous, Qt.MouseButton.LeftButton)
    assert controller.playback.snapshot.frame == 29
    qtbot.mouseClick(next_button, Qt.MouseButton.LeftButton)
    assert controller.playback.snapshot.frame == 30
    qtbot.mouseClick(pause, Qt.MouseButton.LeftButton)

    snap = current.findChild(QCheckBox, "check_timeline_snap")
    zoom = current.findChild(QComboBox, "combo_timeline_zoom")
    follow = current.findChild(QComboBox, "combo_timeline_follow")
    assert snap is not None and zoom is not None and follow is not None
    snap.setChecked(False)
    assert controller.snap_enabled is False
    zoom.setCurrentText("200%")
    assert controller.zoom == 2.0
    follow.setCurrentText("Smooth")
    assert controller.follow_mode is FollowMode.SMOOTH

    controller.select_clip("C001")
    split = current.findChild(QPushButton, "btn_timeline_split")
    assert split is not None
    qtbot.mouseClick(split, Qt.MouseButton.LeftButton)
    assert controller.state.clip("C003").timeline_start.frames == 30
    assert controller.selected_clip_id == "C003"

    marker = current.findChild(QPushButton, "btn_timeline_add_marker")
    assert marker is not None
    qtbot.mouseClick(marker, Qt.MouseButton.LeftButton)
    assert controller.state.markers[0].marker_id == "M001"
    assert controller.state.markers[0].frame.frames == 30
    window.close()
