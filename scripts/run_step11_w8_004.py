"""W8-004 owned real-media background scan and explicit relink evidence."""

from __future__ import annotations

import argparse
import json
import shutil
import time
from pathlib import Path

from ai_ngerti_geopolitik.application.media_import import MediaImportService
from ai_ngerti_geopolitik.application.media_status import MediaStatusService
from ai_ngerti_geopolitik.application.project_session import ProjectSession
from ai_ngerti_geopolitik.application.relink_scan import RelinkScanJobService, ScanState
from ai_ngerti_geopolitik.application.validation import RealMediaIntegrityRule, ValidationService
from ai_ngerti_geopolitik.infrastructure.ffmpeg_slice import FfprobeMediaProbe
from ai_ngerti_geopolitik.infrastructure.media_integrity import LocalMediaIntegrityInspector
from ai_ngerti_geopolitik.infrastructure.media_status import LocalMediaAvailability
from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository
from ai_ngerti_geopolitik.infrastructure.relink_scan import LocalRelinkDirectoryScanner


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    root = args.evidence.resolve()
    root.mkdir(parents=True, exist_ok=True)
    source = args.video.resolve()

    probe = FfprobeMediaProbe()
    repo = JsonProjectRepository()
    session = ProjectSession(repo)
    session.new_project("P-W8-004", "Directory scan proof", 30)
    asset_id = MediaImportService(probe).import_path(session, source)
    candidate_dir = source.parent / "recovered"
    candidate_dir.mkdir(exist_ok=True)
    renamed = candidate_dir / "relocated-one.mp4"
    duplicate = candidate_dir / "relocated-two.mp4"
    shutil.move(str(source), renamed)
    shutil.copy2(renamed, duplicate)
    MediaStatusService(LocalMediaAvailability()).refresh(session)
    assert session.state.asset(asset_id).availability == "missing"
    before_hash = session.state.semantic_hash()

    with RelinkScanJobService(LocalRelinkDirectoryScanner(), probe) as service:
        job = service.submit(session.state, candidate_dir, session_id="W8-004-SESSION")
        deadline = time.monotonic() + 120
        while True:
            current = service.snapshot(job.job_id, state=session.state, session_id="W8-004-SESSION")
            if current.state not in {ScanState.QUEUED, ScanState.RUNNING}:
                break
            if time.monotonic() > deadline:
                raise RuntimeError("W8-004 scan timed out")
            time.sleep(0.025)
        assert current.state is ScanState.SUCCESS
        assert len(current.candidates) == 2
        assert current.ambiguous_assets == (asset_id,)
        assert all(item.fingerprint_verified for item in current.candidates)
        assert session.state.semantic_hash() == before_hash
        applied = service.apply_selected(
            job.job_id,
            session,
            session_id="W8-004-SESSION",
            selections=((asset_id, renamed),),
        )
        applied_hash = applied.semantic_hash()
        assert applied.revision == job.token.revision + 1
        validation = ValidationService(
            (RealMediaIntegrityRule(LocalMediaIntegrityInspector(probe)),)
        ).validate(applied)
        assert not validation.issues
        path = root / "relinked.angproj"
        session.save(path)
        reopened = ProjectSession(repo)
        reopened.open_project(path)
        assert reopened.state.semantic_hash() == applied_hash
        undo_hash = session.undo().semantic_hash()
        redo_hash = session.redo().semantic_hash()
        assert undo_hash == before_hash and redo_hash == applied_hash
        report = {
            "status": "PASS",
            "scanned_files": current.scanned_files,
            "candidate_count": len(current.candidates),
            "ambiguous_requires_manual": current.ambiguous_assets == (asset_id,),
            "all_candidates_verified": all(
                item.fingerprint_verified for item in current.candidates
            ),
            "no_scan_mutation": True,
            "one_batch_revision": applied.revision == job.token.revision + 1,
            "stable_asset_id": reopened.state.asset(asset_id).asset_id == asset_id,
            "validation_clear": not validation.issues,
            "save_reopen_exact": reopened.state.semantic_hash() == applied_hash,
            "undo_exact": undo_hash == before_hash,
            "redo_exact": redo_hash == applied_hash,
            "ui_redesign": False,
            "auto_apply": False,
            "w8_005_started": False,
        }
        if not all(
            value is True
            for key, value in report.items()
            if key
            not in {
                "status",
                "scanned_files",
                "candidate_count",
                "ui_redesign",
                "auto_apply",
                "w8_005_started",
            }
        ):
            raise RuntimeError("W8-004 real-media evidence mismatch")
        (root / "00_w8_004_report.json").write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
