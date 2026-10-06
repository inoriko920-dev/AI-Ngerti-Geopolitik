from pathlib import Path

import pytest

from ai_ngerti_geopolitik.application.commands import (
    AddClipCommand,
    CommandBatch,
    CommandBus,
    CommandError,
    ImportAssetCommand,
    SplitClipCommand,
    StaleRevisionError,
    TrimClipCommand,
)
from ai_ngerti_geopolitik.domain import Asset, Clip, FrameTime, ProjectState


def _asset() -> Asset:
    return Asset(
        asset_id="A001",
        path_ref=str(Path("fixture.mp4")),
        media_type="video",
        duration=FrameTime(240, 30),
        width=1920,
        height=1080,
        has_audio=True,
        fingerprint_sha256="a" * 64,
    )


def _bus_with_clip() -> CommandBus:
    bus = CommandBus(ProjectState.create("P1", "Test", 30))
    bus.execute(
        CommandBatch(
            "B1",
            "import",
            "manual",
            0,
            (ImportAssetCommand(_asset()),),
        )
    )
    bus.execute(
        CommandBatch(
            "B2",
            "add",
            "manual",
            1,
            (
                AddClipCommand(
                    Clip(
                        "C001",
                        "A001",
                        FrameTime(0, 30),
                        FrameTime(0, 30),
                        FrameTime(240, 30),
                    )
                ),
            ),
        )
    )
    return bus


def test_split_trim_undo_redo_preserves_semantic_identity() -> None:
    bus = _bus_with_clip()
    before = bus.state.semantic_hash()
    bus.execute(
        CommandBatch(
            "B3",
            "split",
            "manual",
            bus.state.revision,
            (SplitClipCommand("C001", 150, "C002"),),
        )
    )
    after_split = bus.state.semantic_hash()
    left = bus.state.clip("C001")
    right = bus.state.clip("C002")
    assert left.duration_frames + right.duration_frames == 240
    assert left.source_out.frames == right.source_in.frames
    assert right.timeline_start.frames == left.timeline_end_frame

    bus.execute(
        CommandBatch(
            "B4",
            "trim",
            "manual",
            bus.state.revision,
            (TrimClipCommand("C002", 30),),
        )
    )
    after_trim = bus.state.semantic_hash()
    assert bus.state.clip("C002").duration_frames == 60

    assert bus.undo().semantic_hash() == after_split
    assert bus.undo().semantic_hash() == before
    assert bus.redo().semantic_hash() == after_split
    assert bus.redo().semantic_hash() == after_trim


def test_failed_command_is_atomic_and_stale_revision_is_rejected() -> None:
    bus = _bus_with_clip()
    before = bus.state.semantic_hash()
    revision = bus.state.revision
    with pytest.raises(CommandError):
        bus.execute(
            CommandBatch(
                "BAD",
                "bad split",
                "manual",
                revision,
                (SplitClipCommand("C001", 0, "C002"),),
            )
        )
    assert bus.state.revision == revision
    assert bus.state.semantic_hash() == before

    with pytest.raises(StaleRevisionError):
        bus.execute(
            CommandBatch(
                "STALE",
                "stale",
                "manual",
                revision - 1,
                (TrimClipCommand("C001", 30),),
            )
        )
