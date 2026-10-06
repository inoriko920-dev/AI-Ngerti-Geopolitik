from pathlib import Path

from ai_ngerti_geopolitik.application.commands import (
    AddClipCommand,
    AddMarkerCommand,
    CommandBatch,
    CommandBus,
    DeleteMarkerCommand,
    ImportAssetCommand,
    RemoveClipCommand,
    ReorderClipCommand,
    SetClipDurationCommand,
    UpdateMarkerCommand,
)
from ai_ngerti_geopolitik.domain import Asset, Clip, FrameTime, Marker, ProjectState


def _bus() -> CommandBus:
    bus = CommandBus(ProjectState.create("W2-CMD", "W2 commands", 30))
    asset = Asset(
        "A001",
        str(Path("fixture.mp4")),
        "video",
        FrameTime(300, 30),
        1920,
        1080,
        True,
        "a" * 64,
    )
    bus.execute(CommandBatch("B1", "import", "manual", 0, (ImportAssetCommand(asset),)))
    clips = (
        Clip("C001", "A001", FrameTime(0, 30), FrameTime(0, 30), FrameTime(60, 30)),
        Clip("C002", "A001", FrameTime(60, 30), FrameTime(60, 30), FrameTime(120, 30)),
        Clip("C003", "A001", FrameTime(120, 30), FrameTime(120, 30), FrameTime(180, 30)),
    )
    revision = bus.state.revision
    for index, clip in enumerate(clips, start=2):
        bus.execute(
            CommandBatch(
                f"B{index}",
                "add clip",
                "manual",
                revision,
                (AddClipCommand(clip),),
            )
        )
        revision = bus.state.revision
    return bus


def _execute(bus: CommandBus, label: str, command: object) -> None:
    bus.execute(
        CommandBatch(
            f"W2-{bus.state.revision + 1}",
            label,
            "manual",
            bus.state.revision,
            (command,),
        )
    )


def test_reorder_is_one_undoable_ripple_transaction() -> None:
    bus = _bus()
    before = bus.state.semantic_hash()

    _execute(bus, "reorder", ReorderClipCommand("C003", 0))
    ordered = sorted(bus.state.track("V1").clips, key=lambda item: item.timeline_start.frames)
    assert [clip.clip_id for clip in ordered] == ["C003", "C001", "C002"]
    assert [clip.timeline_start.frames for clip in ordered] == [0, 60, 120]

    reordered_hash = bus.state.semantic_hash()
    assert reordered_hash != before
    assert bus.undo().semantic_hash() == before
    assert bus.redo().semantic_hash() == reordered_hash


def test_duration_and_delete_ripple_keep_contiguous_timeline() -> None:
    bus = _bus()

    _execute(bus, "duration", SetClipDurationCommand("C001", 45))
    ordered = sorted(bus.state.track("V1").clips, key=lambda item: item.timeline_start.frames)
    assert [clip.duration_frames for clip in ordered] == [45, 60, 60]
    assert [clip.timeline_start.frames for clip in ordered] == [0, 45, 105]
    assert bus.state.timeline_end_frame == 165

    _execute(bus, "delete", RemoveClipCommand("C002"))
    ordered = sorted(bus.state.track("V1").clips, key=lambda item: item.timeline_start.frames)
    assert [clip.clip_id for clip in ordered] == ["C001", "C003"]
    assert [clip.timeline_start.frames for clip in ordered] == [0, 45]
    assert bus.state.timeline_end_frame == 105


def test_marker_commands_are_semantic_and_undoable() -> None:
    bus = _bus()
    marker = Marker("M001", FrameTime(30, 30), "Opening", "chapter")

    _execute(bus, "add marker", AddMarkerCommand(marker))
    assert bus.state.marker("M001").label == "Opening"

    _execute(
        bus,
        "update marker",
        UpdateMarkerCommand("M001", FrameTime(45, 30), "Hook", "note"),
    )
    assert bus.state.marker("M001").frame.frames == 45
    assert bus.state.marker("M001").marker_type == "note"

    _execute(bus, "delete marker", DeleteMarkerCommand("M001"))
    assert bus.state.markers == ()
    assert bus.undo().marker("M001").label == "Hook"
