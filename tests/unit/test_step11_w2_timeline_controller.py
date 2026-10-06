from pathlib import Path

from ai_ngerti_geopolitik.application.commands import (
    AddClipCommand,
    CommandBatch,
    CommandBus,
    ImportAssetCommand,
)
from ai_ngerti_geopolitik.application.playback import PlaybackController
from ai_ngerti_geopolitik.application.ports import PreviewResult
from ai_ngerti_geopolitik.application.timeline import FollowMode, TimelineController
from ai_ngerti_geopolitik.domain import Asset, Clip, FrameTime, ProjectState


class PreviewEngine:
    def preview_frame(
        self,
        state: ProjectState,
        timeline_frame: int,
        output_path: Path,
    ) -> PreviewResult:
        return PreviewResult(state.revision, timeline_frame, output_path)

    def export(self, state, output_path, cancellation=None):  # type: ignore[no-untyped-def]
        raise AssertionError("export outside W2 controller test")


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


def _controller(tmp_path: Path) -> tuple[CommandBus, TimelineController, RecordingTransport]:
    bus = CommandBus(ProjectState.create("W2-CTL", "Timeline controller", 30))
    asset = Asset(
        "A001",
        "fixture.mp4",
        "video",
        FrameTime(300, 30),
        1920,
        1080,
        True,
        "b" * 64,
    )
    bus.execute(CommandBatch("B1", "import", "manual", 0, (ImportAssetCommand(asset),)))
    for clip in (
        Clip("C001", "A001", FrameTime(0, 30), FrameTime(0, 30), FrameTime(60, 30)),
        Clip("C002", "A001", FrameTime(60, 30), FrameTime(60, 30), FrameTime(120, 30)),
        Clip("C003", "A001", FrameTime(120, 30), FrameTime(120, 30), FrameTime(180, 30)),
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
    return bus, TimelineController(bus, playback), transport


def test_selection_range_snap_zoom_follow_do_not_mutate_project(tmp_path: Path) -> None:
    bus, controller, _transport = _controller(tmp_path)
    revision = bus.state.revision

    controller.select_clip("C002")
    controller.seek(58)
    controller.set_in(30)
    controller.set_out(150)
    snapped = controller.snap_frame(58)

    assert snapped.snapped is True
    assert snapped.resolved_frame == 60
    assert controller.selection is not None
    assert (controller.selection.in_frame, controller.selection.out_frame) == (30, 150)

    controller.set_zoom(2.0)
    controller.set_follow_mode(FollowMode.SMOOTH)
    controller.manual_scroll()
    assert controller.snapshot.follow_suspended is True
    controller.resume_follow()

    assert bus.state.revision == revision


def test_edit_while_playing_auto_pauses_and_reconciles_transport(tmp_path: Path) -> None:
    bus, controller, transport = _controller(tmp_path)
    controller.select_clip("C003")
    controller.seek(120)
    controller.play()
    assert controller.playback.snapshot.playing is True

    controller.reorder_selected(0)
    assert controller.playback.snapshot.playing is False
    assert [clip.clip_id for clip in bus.state.track("V1").clips] == [
        "C003",
        "C001",
        "C002",
    ]
    assert ("play", None) in transport.events
    assert transport.events.count(("pause", None)) >= 1


def test_split_duration_marker_and_range_are_coherent(tmp_path: Path) -> None:
    bus, controller, _transport = _controller(tmp_path)
    controller.select_clip("C002")
    controller.seek(90)
    controller.split_selected("C004")
    assert bus.state.clip("C002").timeline_end_frame == 90
    assert bus.state.clip("C004").timeline_start.frames == 90

    controller.select_clip("C004")
    controller.set_selected_duration(20)
    assert bus.state.clip("C004").duration_frames == 20

    controller.add_marker("M001", "Beat", frame=50)
    assert bus.state.marker("M001").frame.frames == 50
    controller.set_in(20)
    controller.set_out(100)
    controller.remove_selected()
    assert controller.selection is not None
    assert controller.selection.out_frame <= bus.state.timeline_end_frame
