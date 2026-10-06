from __future__ import annotations

import argparse
import json
from pathlib import Path

from ai_ngerti_geopolitik.application.commands import (
    AddClipCommand,
    AddTrackCommand,
    Command,
    CommandBatch,
    CommandBus,
    DeleteTrackCommand,
    DuplicateClipCommand,
    ImportAssetCommand,
    MoveClipCommand,
    RenameTrackCommand,
    ReorderTrackCommand,
    SetTrackStateCommand,
    TrimClipCommand,
)
from ai_ngerti_geopolitik.domain import Asset, Clip, FrameTime, ProjectState
from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository


def execute_undo_redo(bus: CommandBus, label: str, command: Command) -> None:
    before = bus.state.semantic_hash()
    bus.execute(
        CommandBatch(
            f"W2-SEM-{bus.state.revision + 1:06d}",
            label,
            "manual",
            bus.state.revision,
            (command,),
        )
    )
    after = bus.state.semantic_hash()
    if before == after:
        raise AssertionError(f"{label} did not change semantic state")
    if bus.undo().semantic_hash() != before:
        raise AssertionError(f"{label} undo mismatch")
    if bus.redo().semantic_hash() != after:
        raise AssertionError(f"{label} redo mismatch")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    root = args.evidence.resolve()
    root.mkdir(parents=True, exist_ok=True)

    bus = CommandBus(ProjectState.create("ANG-W2-SEM", "W2 complete semantics", 30))
    asset = Asset(
        "A001",
        "owned-fixture.mp4",
        "video",
        FrameTime(600, 30),
        1920,
        1080,
        True,
        "a" * 64,
    )
    execute_undo_redo(bus, "import asset", ImportAssetCommand(asset))
    execute_undo_redo(bus, "add V1", AddTrackCommand("V1", "Video Utama"))
    execute_undo_redo(bus, "add V2", AddTrackCommand("V2", "Overlay"))

    execute_undo_redo(
        bus,
        "add C001",
        AddClipCommand(
            Clip("C001", "A001", FrameTime(0, 30), FrameTime(0, 30), FrameTime(60, 30)),
            "V1",
        ),
    )
    execute_undo_redo(
        bus,
        "add C002",
        AddClipCommand(
            Clip(
                "C002",
                "A001",
                FrameTime(60, 30),
                FrameTime(60, 30),
                FrameTime(120, 30),
            ),
            "V1",
        ),
    )

    execute_undo_redo(bus, "rename V2", RenameTrackCommand("V2", "B-roll"))
    execute_undo_redo(bus, "mute V2", SetTrackStateCommand("V2", muted=True))
    execute_undo_redo(bus, "hide V2", SetTrackStateCommand("V2", visible=False))
    execute_undo_redo(bus, "reorder V2", ReorderTrackCommand("V2", 0))
    execute_undo_redo(bus, "add temporary track", AddTrackCommand("V3", "Temporary"))
    execute_undo_redo(bus, "delete temporary track", DeleteTrackCommand("V3"))

    execute_undo_redo(
        bus,
        "duplicate C001",
        DuplicateClipCommand("C001", "C003", "V2", 0),
    )
    execute_undo_redo(bus, "move C003", MoveClipCommand("C003", "V2", 90))
    execute_undo_redo(bus, "trim left C002", TrimClipCommand("C002", 10, "left"))
    execute_undo_redo(bus, "trim right C001", TrimClipCommand("C001", 10, "right"))

    project_path = root / "w2_multitrack_semantics.angproj"
    repository = JsonProjectRepository()
    repository.save(bus.state, project_path)
    reopened = repository.load(project_path)
    if reopened.semantic_hash() != bus.state.semantic_hash():
        raise AssertionError("W2 complete semantic state did not survive save/reopen")

    report = {
        "status": "PASS",
        "track_ids": [
            track.track_id for track in sorted(reopened.tracks, key=lambda item: item.order)
        ],
        "v2_name": reopened.track("V2").name,
        "v2_muted": reopened.track("V2").muted,
        "v2_visible": reopened.track("V2").visible,
        "clip_ids": sorted(clip.clip_id for track in reopened.tracks for clip in track.clips),
        "c003_track": next(
            track.track_id
            for track in reopened.tracks
            if any(clip.clip_id == "C003" for clip in track.clips)
        ),
        "c003_start": reopened.clip("C003").timeline_start.frames,
        "c002_start_after_left_trim": reopened.clip("C002").timeline_start.frames,
        "c001_duration_after_right_trim": reopened.clip("C001").duration_frames,
        "save_reopen_hash_match": reopened.semantic_hash() == bus.state.semantic_hash(),
        "all_mutations_undo_redo_checked": True,
    }
    (root / "04_semantics.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
