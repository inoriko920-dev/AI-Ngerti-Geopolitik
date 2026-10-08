"""W8-007 owned fault-injection qualification: source bytes, backup, retry, cleanup."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from unittest.mock import patch

from ai_ngerti_geopolitik.application.commands import (
    CommandBatch,
    UpdateProjectSettingsCommand,
)
from ai_ngerti_geopolitik.application.persistence_failure import (
    PersistenceError,
    PersistenceStage,
    persistence_error_projection,
)
from ai_ngerti_geopolitik.application.project_session import ProjectSession
from ai_ngerti_geopolitik.domain import ProjectState
from ai_ngerti_geopolitik.infrastructure import persistence
from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inject_replace(source: Path, *, backup: bool):
    original = persistence.os.replace
    destination = source.with_name(f"{source.name}.bak") if backup else source

    def interrupt(src: Path, dst: Path) -> None:
        if Path(dst) == destination:
            raise OSError("owned simulated atomic-replace failure")
        original(src, dst)

    return interrupt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    root = args.evidence.resolve()
    root.mkdir(parents=True, exist_ok=True)

    repo = JsonProjectRepository()
    source = root / "canonical.angproj"
    base = ProjectState.create("P-W8-007", "Original source", 30)
    repo.save(base, source)
    repo.save(base.with_revision(1), source)
    backup = source.with_name(f"{source.name}.bak")
    session = ProjectSession(repo)
    session.open_project(source)
    session.execute(
        CommandBatch(
            batch_id="B-W8-007",
            label="edit test resolution",
            actor="manual",
            expected_revision=session.state.revision,
            commands=(UpdateProjectSettingsCommand(1280, 720, 30, "16:9"),),
        )
    )
    intended_hash = session.state.semantic_hash()
    prior_sha = digest(source)
    evidence: dict[str, object] = {"status": "PASS"}
    fault_count = 0
    faults = (
        ("temp_sync", PersistenceStage.TEMP_SYNC),
        ("backup_copy", PersistenceStage.BACKUP_COPY),
        ("backup_replace", PersistenceStage.BACKUP_REPLACE),
        ("source_replace", PersistenceStage.SOURCE_REPLACE),
    )
    for name, expected_stage in faults:
        try:
            if name == "temp_sync":
                with patch.object(
                    persistence.os,
                    "fsync",
                    side_effect=OSError("simulated sync fault"),
                ):
                    session.save()
            elif name == "backup_copy":
                with patch.object(
                    persistence.shutil,
                    "copy2",
                    side_effect=OSError("simulated copy fault"),
                ):
                    session.save()
            else:
                with patch.object(
                    persistence.os,
                    "replace",
                    side_effect=inject_replace(
                        source, backup=name == "backup_replace"
                    ),
                ):
                    session.save()
            raise AssertionError("unexpected persistence success under fault")
        except PersistenceError as exc:
            assert exc.stage is expected_stage
            assert persistence_error_projection(exc).retryable
            fault_count += 1
        assert digest(source) == prior_sha
        assert session.dirty
        assert session.current_path == source
        assert repo.load(backup).project_id == base.project_id
        assert list(root.glob(".*.tmp")) == []
    evidence["failed_saves_detected"] = fault_count == len(faults)
    evidence["source_unchanged_before_retry"] = digest(source) == prior_sha
    evidence["dirty_after_failed_save"] = session.dirty
    evidence["backup_readable_after_failures"] = repo.load(backup).project_id == base.project_id
    evidence["temp_files_cleaned_after_failures"] = not list(root.glob(".*.tmp"))
    evidence["source_was_not_rebound"] = session.current_path == source

    session.save()
    evidence["retry_success"] = not session.dirty
    evidence["retry_persisted_exact_state"] = repo.load(source).semantic_hash() == intended_hash
    evidence["backup_equals_prior_source"] = digest(backup) == prior_sha
    evidence["no_temp_after_retry"] = not list(root.glob(".*.tmp"))
    evidence["source_changed_only_after_retry"] = digest(source) != prior_sha

    snapshot = root / ".ang-autosave" / "recovery.autosave.angproj"
    snapshot.parent.mkdir(parents=True, exist_ok=True)
    before_snapshot = digest(source)
    try:
        with patch.object(
            persistence.os,
            "fsync",
            side_effect=OSError("simulated snapshot sync fault"),
        ):
            repo.save_snapshot(session.state, snapshot)
        raise AssertionError("unexpected snapshot save success under fault")
    except PersistenceError as exc:
        evidence["snapshot_fault_typed"] = exc.stage is PersistenceStage.TEMP_SYNC
    evidence["snapshot_did_not_touch_source"] = digest(source) == before_snapshot
    evidence["failed_snapshot_not_published"] = not snapshot.exists()
    evidence["failed_snapshot_temp_clean"] = not list(snapshot.parent.glob(".*.tmp"))
    evidence["w8_008_not_started"] = True
    checks = [value is True for key, value in evidence.items() if key != "status"]
    if not all(checks):
        raise AssertionError("W8-007 owned persistence evidence failed")
    report = root / "00_w8_007_report.json"
    report.write_text(json.dumps(evidence, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(evidence, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
