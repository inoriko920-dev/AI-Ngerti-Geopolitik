from __future__ import annotations

import argparse
import json
from pathlib import Path

from ai_ngerti_geopolitik.application.commands import AddClipCommand, CommandBatch
from ai_ngerti_geopolitik.application.media_import import MediaImportService
from ai_ngerti_geopolitik.application.playback import PlaybackController
from ai_ngerti_geopolitik.application.project_session import ProjectSession
from ai_ngerti_geopolitik.application.timeline import FollowMode, TimelineController
from ai_ngerti_geopolitik.domain import Clip, FrameTime
from ai_ngerti_geopolitik.infrastructure.ffmpeg_slice import (
    FfmpegSliceMediaEngine,
    FfprobeMediaProbe,
)
from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def execute_clip(session: ProjectSession, clip: Clip) -> None:
    session.execute(
        CommandBatch(
            batch_id=f"W2-ADD-{session.state.revision + 1:06d}",
            label="Add W2 clip",
            actor="manual",
            expected_revision=session.state.revision,
            commands=(AddClipCommand(clip),),
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()

    video = args.video.resolve()
    evidence = args.evidence.resolve()
    evidence.mkdir(parents=True, exist_ok=True)

    probe = FfprobeMediaProbe()
    engine = FfmpegSliceMediaEngine(probe)
    repository = JsonProjectRepository()
    session = ProjectSession(repository)
    session.new_project("ANG-S11-W2", "W2 Timeline Playback Core")

    asset_id = MediaImportService(probe).import_path(session, video)
    asset = session.state.asset(asset_id)
    segment = asset.duration.frames // 3
    if segment < 30:
        raise AssertionError(f"W2 fixture is too short: {asset.duration.frames} frames")

    for clip_id, timeline_start, source_in, source_out in (
        ("C001", 0, 0, segment),
        ("C002", segment, segment, segment * 2),
        ("C003", segment * 2, segment * 2, segment * 3),
    ):
        execute_clip(
            session,
            Clip(
                clip_id,
                asset_id,
                FrameTime(timeline_start, session.state.fps),
                FrameTime(source_in, session.state.fps),
                FrameTime(source_out, session.state.fps),
            ),
        )

    preview_dir = evidence / "preview"
    playback = PlaybackController(lambda: session.state, engine, preview_dir)
    timeline = TimelineController(session.bus, playback)

    timeline.select_clip("C003")
    timeline.seek(segment * 2)
    timeline.play()
    if not timeline.playback.snapshot.playing:
        raise AssertionError("playback did not enter playing state")
    timeline.reorder_selected(0)
    if timeline.playback.snapshot.playing:
        raise AssertionError("canonical edit did not auto-pause playback")

    shortened = segment - 10
    timeline.set_selected_duration(shortened)
    split_frame = max(1, shortened // 2)
    timeline.seek(split_frame)
    timeline.split_selected("C004")

    timeline.add_marker("M001", "Narrative beat", frame=segment)
    session.undo()
    if session.state.markers:
        raise AssertionError("marker undo did not restore previous canonical state")
    session.redo()
    if session.state.marker("M001").label != "Narrative beat":
        raise AssertionError("marker redo did not restore marker")

    timeline.set_in(5)
    timeline.set_out(session.state.timeline_end_frame - 5)
    selection = timeline.selection
    if selection is None:
        raise AssertionError("W2 selection range was not established")

    first = session.state.clip("C003")
    snap = timeline.snap_frame(first.timeline_end_frame + 2)
    if not snap.snapped:
        raise AssertionError("W2 magnetic snap did not find a nearby clip boundary")

    timeline.set_zoom(2.0)
    timeline.set_follow_mode(FollowMode.SMOOTH)
    timeline.manual_scroll()
    follow_suspended = timeline.snapshot.follow_suspended
    timeline.resume_follow()

    timeline.seek(max(0, split_frame - 1))
    preview_left = timeline.playback.render_current()
    timeline.seek(split_frame)
    preview_right = timeline.playback.render_current()

    project_path = evidence / "w2_timeline.angproj"
    session.save(project_path)
    export_path = evidence / "w2_edited_timeline.mp4"
    export = engine.export(session.state, export_path)

    reopened = ProjectSession(repository)
    reopened.open_project(project_path)
    ordered = sorted(
        reopened.state.track("V1").clips,
        key=lambda clip: clip.timeline_start.frames,
    )
    starts = [clip.timeline_start.frames for clip in ordered]
    durations = [clip.duration_frames for clip in ordered]
    expected_starts = [0, split_frame, shortened, shortened + segment]
    if starts != expected_starts:
        raise AssertionError(f"unexpected W2 timeline starts: {starts}")

    write_json(
        evidence / "01_timeline.json",
        {
            "project_revision": reopened.state.revision,
            "clip_ids": [clip.clip_id for clip in ordered],
            "starts": starts,
            "durations": durations,
            "timeline_end_frame": reopened.state.timeline_end_frame,
            "marker": {
                "id": reopened.state.marker("M001").marker_id,
                "frame": reopened.state.marker("M001").frame.frames,
                "label": reopened.state.marker("M001").label,
            },
        },
    )
    write_json(
        evidence / "02_interaction.json",
        {
            "selection_in": selection.in_frame,
            "selection_out": selection.out_frame,
            "snap_pass": snap.snapped,
            "snap_requested": snap.requested_frame,
            "snap_resolved": snap.resolved_frame,
            "snap_target": snap.target,
            "zoom": timeline.zoom,
            "follow_mode": timeline.follow_mode.value,
            "follow_suspended_after_manual_scroll": follow_suspended,
            "edit_auto_paused": True,
        },
    )
    write_json(
        evidence / "03_preview_export.json",
        {
            "preview_left_frame": preview_left.timeline_frame,
            "preview_left_file": preview_left.output_path.name,
            "preview_right_frame": preview_right.timeline_frame,
            "preview_right_file": preview_right.output_path.name,
            "export_file": export.output_path.name,
            "export_duration_frames": export.duration_frames,
            "export_width": export.width,
            "export_height": export.height,
            "export_fps": export.fps,
        },
    )
    report = {
        "status": "PASS",
        "asset_id": asset_id,
        "clip_count": len(ordered),
        "clip_ids": [clip.clip_id for clip in ordered],
        "marker_count": len(reopened.state.markers),
        "selection_valid": selection.in_frame < selection.out_frame,
        "snap_pass": snap.snapped,
        "edit_auto_paused": True,
        "save_reopen_hash_match": reopened.state.semantic_hash() == session.state.semantic_hash(),
        "preview_files_valid": preview_left.output_path.is_file()
        and preview_right.output_path.is_file(),
        "export_valid": export.output_path.is_file() and export.output_path.stat().st_size > 0,
    }
    write_json(evidence / "00_w2_report.json", report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
