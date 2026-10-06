from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from ai_ngerti_geopolitik.application.commands import (
    CommandBatch,
    CommandBus,
    ReorderClipCommand,
)
from ai_ngerti_geopolitik.domain import Asset, Clip, FrameTime, ProjectState, Track


def build_stress_state(track_count: int, clips_per_track: int) -> ProjectState:
    fps = 30
    clip_frames = 4
    source_frames = clips_per_track * clip_frames + 120
    asset = Asset(
        "A001",
        "stress-fixture.mp4",
        "video",
        FrameTime(source_frames, fps),
        1920,
        1080,
        True,
        "b" * 64,
    )
    tracks: list[Track] = []
    for track_index in range(track_count):
        clips: list[Clip] = []
        for index in range(clips_per_track):
            start = index * clip_frames
            clip_id = f"C{track_index + 1:02d}{index + 1:04d}"
            clips.append(
                Clip(
                    clip_id,
                    "A001",
                    FrameTime(start, fps),
                    FrameTime(start, fps),
                    FrameTime(start + clip_frames, fps),
                )
            )
        tracks.append(
            Track(
                f"V{track_index + 1}",
                "video",
                track_index,
                tuple(clips),
                name=f"Stress Track {track_index + 1}",
            )
        )
    state = ProjectState(
        project_id="ANG-W2-STRESS",
        name="W2 stress",
        schema_version=1,
        fps=fps,
        revision=0,
        assets=(asset,),
        tracks=tuple(tracks),
    )
    state.validate()
    return state


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--tracks", type=int, default=4)
    parser.add_argument("--clips-per-track", type=int, default=250)
    parser.add_argument("--budget-ms", type=float, default=8000.0)
    args = parser.parse_args()

    root = args.evidence.resolve()
    root.mkdir(parents=True, exist_ok=True)

    started = time.perf_counter()
    state = build_stress_state(args.tracks, args.clips_per_track)
    bus = CommandBus(state)
    first_track = bus.state.track("V1")
    selected = first_track.clips[-1].clip_id
    for index in range(40):
        target = 0 if index % 2 == 0 else len(first_track.clips) - 1
        bus.execute(
            CommandBatch(
                f"STRESS-{index:03d}",
                "stress reorder",
                "manual",
                bus.state.revision,
                (ReorderClipCommand(selected, target, "V1"),),
            )
        )
        bus.undo()
        bus.redo()
    bus.state.validate()
    _ = bus.state.semantic_hash()
    elapsed_ms = (time.perf_counter() - started) * 1000.0

    report = {
        "status": "PASS" if elapsed_ms <= args.budget_ms else "FAIL",
        "tracks": args.tracks,
        "clips_per_track": args.clips_per_track,
        "total_clips": args.tracks * args.clips_per_track,
        "reorder_undo_redo_cycles": 40,
        "elapsed_ms": round(elapsed_ms, 3),
        "budget_ms": args.budget_ms,
    }
    (root / "05_stress.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
