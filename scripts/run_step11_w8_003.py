from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from ai_ngerti_geopolitik.application.commands import AddClipCommand, CommandBatch
from ai_ngerti_geopolitik.application.media_import import MediaImportService
from ai_ngerti_geopolitik.application.media_status import MediaStatusService
from ai_ngerti_geopolitik.application.project_session import ProjectSession
from ai_ngerti_geopolitik.application.relink import RelinkService
from ai_ngerti_geopolitik.application.validation import RealMediaIntegrityRule, ValidationService
from ai_ngerti_geopolitik.domain import Clip, FrameTime
from ai_ngerti_geopolitik.infrastructure.ffmpeg_slice import FfprobeMediaProbe
from ai_ngerti_geopolitik.infrastructure.media_integrity import LocalMediaIntegrityInspector
from ai_ngerti_geopolitik.infrastructure.media_status import LocalMediaAvailability
from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository


def _write(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    video = args.video.resolve()
    evidence = args.evidence.resolve()
    evidence.mkdir(parents=True, exist_ok=True)

    probe = FfprobeMediaProbe()
    repository = JsonProjectRepository()
    session = ProjectSession(repository)
    session.new_project("P-W8-003-REAL", "W8 single real relink", 30)
    asset_id = MediaImportService(probe).import_path(session, video)
    imported = session.state.asset(asset_id)
    session.execute(
        CommandBatch(
            "W8-003-SETUP",
            "Add relink proof clip",
            "manual",
            session.state.revision,
            (
                AddClipCommand(
                    Clip(
                        "C001",
                        asset_id,
                        FrameTime(0, 30),
                        FrameTime(0, 30),
                        FrameTime(120, 30),
                    )
                ),
            ),
        )
    )

    original_path = Path(imported.path_ref).resolve()
    original_fingerprint = imported.fingerprint_sha256
    original_duration = imported.duration.frames
    original_metadata = (
        imported.width,
        imported.height,
        imported.has_audio,
        imported.sample_rate,
        imported.file_size,
    )

    relocated = video.parent / "relocated" / "renamed-input-video.mp4"
    relocated.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(original_path), relocated)
    if original_path.exists() or not relocated.is_file():
        raise RuntimeError("real fixture relocation failed")

    changed = MediaStatusService(LocalMediaAvailability()).refresh(session)
    if changed != (asset_id,) or session.state.asset(asset_id).availability != "missing":
        raise RuntimeError("relocation did not produce canonical missing state")

    before_relink_hash = session.state.semantic_hash()
    before_relink_revision = session.state.revision
    before_clip_asset_id = session.state.clip("C001").asset_id

    result = RelinkService(probe).relink(session, asset_id, relocated)
    relinked = session.state.asset(asset_id)
    applied_hash = session.state.semantic_hash()

    validation = ValidationService(
        (RealMediaIntegrityRule(LocalMediaIntegrityInspector(probe)),)
    ).validate(session.state)

    project_path = evidence / "w8_003_relinked.angproj"
    session.save(project_path)
    reopened = ProjectSession(repository)
    reopened.open_project(project_path)

    undo_hash = session.undo().semantic_hash()
    redo_hash = session.redo().semantic_hash()

    report = {
        "status": "PASS",
        "asset_id_preserved": relinked.asset_id == asset_id == "A001",
        "clip_reference_preserved": (
            before_clip_asset_id == asset_id
            and session.state.clip("C001").asset_id == asset_id
            and reopened.state.clip("C001").asset_id == asset_id
        ),
        "old_path_absent_after_move": not original_path.exists(),
        "new_path_online": relinked.availability == "online" and relocated.is_file(),
        "path_updated": Path(relinked.path_ref).resolve() == relocated.resolve(),
        "source_name_updated": relinked.source_name == relocated.name,
        "fingerprint_preserved": relinked.fingerprint_sha256 == original_fingerprint,
        "duration_preserved": relinked.duration.frames == original_duration,
        "metadata_preserved": (
            relinked.width,
            relinked.height,
            relinked.has_audio,
            relinked.sample_rate,
            relinked.file_size,
        )
        == original_metadata,
        "one_revision_apply": (
            result.base_revision == before_relink_revision
            and result.applied_revision == before_relink_revision + 1
        ),
        "validation_clear_after_relink": len(validation.issues) == 0,
        "save_reopen_exact": reopened.state.semantic_hash() == applied_hash,
        "save_reopen_path_exact": reopened.state.asset(asset_id).path_ref == relinked.path_ref,
        "undo_restores_original_binding": undo_hash == before_relink_hash,
        "redo_restores_relink": redo_hash == applied_hash,
        "batch_scan_started": False,
        "candidate_ranking_started": False,
        "ui_redesign_started": False,
    }
    if not all(value is True for value in report.values() if isinstance(value, bool)):
        raise RuntimeError("W8-003 real relocation proof failed")

    _write(evidence / "00_w8_003_relink_report.json", report)
    _write(
        evidence / "01_w8_003_paths_and_identity.json",
        {
            "asset_id": asset_id,
            "old_path": str(original_path),
            "new_path": str(relocated.resolve()),
            "fingerprint_sha256": original_fingerprint,
            "base_revision": before_relink_revision,
            "applied_revision": result.applied_revision,
            "before_semantic_hash": before_relink_hash,
            "applied_semantic_hash": applied_hash,
            "undo_semantic_hash": undo_hash,
            "redo_semantic_hash": redo_hash,
        },
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
