from __future__ import annotations

import argparse
import json
from pathlib import Path

from ai_ngerti_geopolitik.application.commands import (
    AddClipCommand,
    CommandBatch,
    SetAssetAvailabilityCommand,
    UpdateProjectSettingsCommand,
)
from ai_ngerti_geopolitik.application.media_import import MediaImportService
from ai_ngerti_geopolitik.application.media_library import MediaBinController, MediaBinQuery
from ai_ngerti_geopolitik.application.media_status import MediaStatusService
from ai_ngerti_geopolitik.application.project_session import (
    ProjectSession,
    UnsavedChangesError,
)
from ai_ngerti_geopolitik.domain import Clip, FrameTime
from ai_ngerti_geopolitik.infrastructure.ffmpeg_slice import FfprobeMediaProbe
from ai_ngerti_geopolitik.infrastructure.media_status import LocalMediaAvailability
from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def execute_one(session: ProjectSession, label: str, command: object) -> None:
    session.execute(
        CommandBatch(
            batch_id=f"W1-{session.state.revision + 1:06d}",
            label=label,
            actor="manual",
            expected_revision=session.state.revision,
            commands=(command,),
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--audio", type=Path, required=True)
    parser.add_argument("--image", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()

    video = args.video.resolve()
    audio = args.audio.resolve()
    image = args.image.resolve()
    evidence = args.evidence.resolve()
    evidence.mkdir(parents=True, exist_ok=True)

    repository = JsonProjectRepository()
    session = ProjectSession(repository)
    session.new_project("ANG-S11-W1", "W1 Project Media Persistence")

    execute_one(
        session,
        "Set project settings",
        UpdateProjectSettingsCommand(1280, 720, 30, "16:9"),
    )

    importer = MediaImportService(FfprobeMediaProbe())
    video_id = importer.import_path(session, video)
    audio_id = importer.import_path(session, audio)
    image_id = importer.import_path(session, image)

    video_asset = session.state.asset(video_id)
    execute_one(
        session,
        "Add video clip",
        AddClipCommand(
            Clip(
                clip_id="C001",
                asset_id=video_id,
                timeline_start=FrameTime(0, session.state.fps),
                source_in=FrameTime(0, session.state.fps),
                source_out=video_asset.duration,
            )
        ),
    )

    media_bin = MediaBinController(lambda: session.state)
    media_bin.select(audio_id)
    audio_query = media_bin.query(MediaBinQuery(media_types=("audio",), sort_by="name"))
    image_query = media_bin.query(MediaBinQuery(text="image"))

    canonical = evidence / "01_canonical.angproj"
    save_as = evidence / "02_save_as.angproj"
    session.save(canonical)
    if session.dirty:
        raise AssertionError("session remained dirty after Save")
    session.save_as(save_as)
    if session.current_path != save_as.resolve() or session.dirty:
        raise AssertionError("Save As did not establish the new clean project path")

    execute_one(
        session,
        "Mark audio offline",
        SetAssetAvailabilityCommand(audio_id, "offline"),
    )
    session.save()
    backup = save_as.with_name(f"{save_as.name}.bak")
    if not backup.is_file():
        raise AssertionError("second Save did not preserve previous backup")

    canonical_after_save_as = canonical.read_bytes()
    save_as_after_save = save_as.read_bytes()

    missing_target = video.with_name(f"{video.name}.w1-missing")
    if missing_target.exists():
        missing_target.unlink()
    video.replace(missing_target)
    try:
        changed = MediaStatusService(LocalMediaAvailability()).refresh(session)
        if video_id not in changed:
            raise AssertionError("missing video was not marked missing")
        if session.state.asset(video_id).availability != "missing":
            raise AssertionError("video availability did not become missing")
        if session.state.clip("C001").asset_id != video_id:
            raise AssertionError("clip identity changed when source media went missing")
        if len(session.state.track("V1").clips) != 1:
            raise AssertionError("missing-media refresh silently deleted a clip")

        autosave = session.autosave()
        if not session.dirty:
            raise AssertionError("autosave incorrectly cleared dirty state")
        if save_as.read_bytes() != save_as_after_save:
            raise AssertionError("autosave overwrote the canonical Save As project")
        if canonical.read_bytes() != canonical_after_save_as:
            raise AssertionError("later work mutated the original Save project")

        try:
            session.close()
        except UnsavedChangesError:
            close_guard = "PASS"
        else:
            raise AssertionError("dirty close unexpectedly discarded unsaved state")

        snapshot_state = repository.load(autosave)
        if snapshot_state.asset(video_id).availability != "missing":
            raise AssertionError("autosave did not persist missing media state")
        if snapshot_state.clip("C001").asset_id != video_id:
            raise AssertionError("autosave lost the clip referencing missing media")
    finally:
        missing_target.replace(video)

    reopened = ProjectSession(repository)
    reopened.open_project(save_as)
    if reopened.dirty:
        raise AssertionError("opened project should start clean")
    if reopened.state.settings.width != 1280 or reopened.state.settings.height != 720:
        raise AssertionError("project settings did not persist")
    if reopened.state.fps != 30 or reopened.state.settings.aspect_ratio != "16:9":
        raise AssertionError("FPS/aspect ratio did not persist")
    if reopened.state.asset(audio_id).availability != "offline":
        raise AssertionError("offline media state did not persist")
    if reopened.state.asset(video_id).availability != "online":
        raise AssertionError("canonical Save As should still contain the prior online state")

    backup_state = repository.load(backup)
    if backup_state.asset(audio_id).availability != "online":
        raise AssertionError("backup does not represent the previous successful Save As state")

    media_rows = [
        {
            "asset_id": asset.asset_id,
            "media_type": asset.media_type,
            "source_name": asset.source_name,
            "availability": asset.availability,
            "duration_frames": asset.duration.frames,
            "width": asset.width,
            "height": asset.height,
            "sample_rate": asset.sample_rate,
            "file_size": asset.file_size,
        }
        for asset in reopened.state.assets
    ]
    write_json(evidence / "03_media_inventory.json", media_rows)
    write_json(
        evidence / "04_media_bin_query.json",
        {
            "selected": list(media_bin.selected_asset_ids),
            "audio_query": [item.asset_id for item in audio_query],
            "image_query": [item.asset_id for item in image_query],
        },
    )
    write_json(
        evidence / "05_project_settings.json",
        {
            "width": reopened.state.settings.width,
            "height": reopened.state.settings.height,
            "fps": reopened.state.fps,
            "aspect_ratio": reopened.state.settings.aspect_ratio,
        },
    )
    write_json(
        evidence / "06_missing_media_snapshot.json",
        {
            "asset_id": video_id,
            "snapshot_availability": snapshot_state.asset(video_id).availability,
            "clip_id": snapshot_state.clip("C001").clip_id,
            "clip_asset_id": snapshot_state.clip("C001").asset_id,
            "clip_count": len(snapshot_state.track("V1").clips),
            "canonical_availability": reopened.state.asset(video_id).availability,
            "dirty_close_guard": close_guard,
            "autosave": autosave.name,
        },
    )

    report = {
        "status": "PASS",
        "project_id": reopened.state.project_id,
        "asset_ids": [video_id, audio_id, image_id],
        "media_types": [asset.media_type for asset in reopened.state.assets],
        "save": canonical.name,
        "save_as": save_as.name,
        "backup": backup.name,
        "autosave": autosave.name,
        "backup_previous_state": True,
        "autosave_did_not_overwrite_canonical": True,
        "missing_media_preserved_clip": True,
        "dirty_close_guard": close_guard,
        "media_bin_selected": list(media_bin.selected_asset_ids),
    }
    write_json(evidence / "00_w1_report.json", report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
