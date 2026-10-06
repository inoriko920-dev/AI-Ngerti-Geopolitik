from pathlib import Path

import pytest

from ai_ngerti_geopolitik.application.commands import (
    AddClipCommand,
    AddTrackCommand,
    Command,
    CommandBatch,
    CommandBus,
    CommandError,
    DeleteTrackCommand,
    DuplicateClipCommand,
    ImportAssetCommand,
    MoveClipCommand,
    RenameTrackCommand,
    ReorderClipCommand,
    ReorderTrackCommand,
    SetTrackStateCommand,
    TrimClipCommand,
)
from ai_ngerti_geopolitik.domain import Asset, Clip, FrameTime, ProjectState
from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository


def _execute(bus: CommandBus, label: str, command: Command) -> None:
    before = bus.state.semantic_hash()
    bus.execute(
        CommandBatch(
            f"W2-{bus.state.revision + 1}",
            label,
            "manual",
            bus.state.revision,
            (command,),
        )
    )
    after = bus.state.semantic_hash()
    assert after != before
    assert bus.undo().semantic_hash() == before
    assert bus.redo().semantic_hash() == after


def _bus() -> CommandBus:
    bus = CommandBus(ProjectState.create("W2-MULTI", "W2 multi-track", 30))
    asset = Asset(
        "A001",
        "fixture.mp4",
        "video",
        FrameTime(600, 30),
        1920,
        1080,
        True,
        "f" * 64,
    )
    _execute(bus, "import", ImportAssetCommand(asset))
    _execute(bus, "add V1", AddTrackCommand("V1", "Video Utama"))
    _execute(bus, "add V2", AddTrackCommand("V2", "Overlay"))
    for clip, track_id in (
        (
            Clip("C001", "A001", FrameTime(0, 30), FrameTime(0, 30), FrameTime(60, 30)),
            "V1",
        ),
        (
            Clip(
                "C002",
                "A001",
                FrameTime(60, 30),
                FrameTime(60, 30),
                FrameTime(120, 30),
            ),
            "V1",
        ),
    ):
        _execute(bus, f"add {clip.clip_id}", AddClipCommand(clip, track_id))
    return bus


def test_track_crud_state_order_and_round_trip_are_undoable(tmp_path: Path) -> None:
    bus = _bus()
    _execute(bus, "rename", RenameTrackCommand("V2", "B-roll"))
    _execute(bus, "state", SetTrackStateCommand("V2", muted=True, visible=False))
    _execute(bus, "reorder", ReorderTrackCommand("V2", 0))
    assert [track.track_id for track in sorted(bus.state.tracks, key=lambda item: item.order)] == [
        "V2",
        "V1",
    ]
    assert bus.state.track("V2").name == "B-roll"
    assert bus.state.track("V2").muted is True
    assert bus.state.track("V2").visible is False

    _execute(bus, "add temp", AddTrackCommand("V3", "Temporary"))
    _execute(bus, "delete temp", DeleteTrackCommand("V3"))
    assert {track.track_id for track in bus.state.tracks} == {"V1", "V2"}

    path = tmp_path / "multitrack.angproj"
    JsonProjectRepository().save(bus.state, path)
    reopened = JsonProjectRepository().load(path)
    assert reopened.semantic_hash() == bus.state.semantic_hash()
    assert reopened.track("V2").name == "B-roll"
    assert reopened.track("V2").muted is True
    assert reopened.track("V2").visible is False


def test_duplicate_move_trim_and_lock_semantics_preserve_stable_ids() -> None:
    bus = _bus()
    _execute(bus, "duplicate", DuplicateClipCommand("C001", "C003", "V2", 0))
    assert bus.state.clip("C003").asset_id == "A001"

    _execute(bus, "move", MoveClipCommand("C003", "V2", 80))
    assert bus.state.clip("C003").timeline_start.frames == 80

    _execute(bus, "trim left", TrimClipCommand("C002", 10, "left"))
    assert bus.state.clip("C002").timeline_start.frames == 70
    assert bus.state.clip("C002").source_in.frames == 70

    _execute(bus, "trim right", TrimClipCommand("C001", 10, "right"))
    assert bus.state.clip("C001").duration_frames == 50

    _execute(bus, "lock V1", SetTrackStateCommand("V1", locked=True))
    with pytest.raises(CommandError, match="track is locked"):
        bus.execute(
            CommandBatch(
                "LOCKED",
                "illegal edit",
                "manual",
                bus.state.revision,
                (ReorderClipCommand("C001", 1, "V1"),),
            )
        )
    assert bus.state.track("V1").locked is True


def test_move_and_duplicate_reject_overlap_instead_of_creating_invalid_state() -> None:
    bus = _bus()
    _execute(bus, "duplicate", DuplicateClipCommand("C001", "C003", "V2", 0))
    before = bus.state.semantic_hash()

    with pytest.raises(CommandError, match="invalid overlap"):
        bus.execute(
            CommandBatch(
                "BAD-MOVE",
                "overlap",
                "manual",
                bus.state.revision,
                (MoveClipCommand("C003", "V1", 30),),
            )
        )
    assert bus.state.semantic_hash() == before
