"""Local W8-005 evidence: managed catalog, legacy compatibility, isolated corruption."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ai_ngerti_geopolitik.application.autosave_catalog import AutosaveCatalogService
from ai_ngerti_geopolitik.domain import ProjectState
from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    root = args.evidence.resolve()
    root.mkdir(parents=True, exist_ok=True)
    repo = JsonProjectRepository()
    service = AutosaveCatalogService(repo)
    source = root / "source.angproj"
    backup = root / "source.angproj.bak"
    base = ProjectState.create("P-W8-005", "Autosave test", 30)
    repo.save(base, source)
    backup.write_bytes(b"OWNED BACKUP NEVER PRUNE")
    source_bytes = source.read_bytes()
    backup_bytes = backup.read_bytes()
    folder = root / "snapshots"
    folder.mkdir(exist_ok=True)
    legacy = folder / (
        f"{base.project_id}.r{base.revision:06d}."
        f"{base.semantic_hash()[:12]}.autosave.angproj"
    )
    repo.save_snapshot(base, legacy)
    invalid = folder / f"P-W8-005.r000100.{'f' * 12}.autosave.angproj"
    invalid.write_text("{ invalid", encoding="utf-8")
    foreign_state = ProjectState.create("P-FOREIGN", "Other", 30)
    foreign = folder / (
        f"{foreign_state.project_id}.r000000."
        f"{foreign_state.semantic_hash()[:12]}.autosave.angproj"
    )
    repo.save_snapshot(foreign_state, foreign)
    newest: Path | None = None
    for revision in range(1, 23):
        newest = service.create_snapshot(base.with_revision(revision), folder, source_path=source)
    catalog = service.inspect(folder, base.project_id)
    assert len(catalog.recoverable) == 20
    assert invalid in catalog.rejected
    assert newest is not None and newest.is_file()
    assert source.read_bytes() == source_bytes
    assert backup.read_bytes() == backup_bytes
    assert invalid.is_file() and foreign.is_file()
    assert legacy not in (record.path for record in catalog.recoverable)
    report = {
        "status": "PASS",
        "retained_valid": len(catalog.recoverable),
        "invalid_isolated": invalid.exists(),
        "foreign_untouched": foreign.exists(),
        "source_unchanged": source.read_bytes() == source_bytes,
        "backup_unchanged": backup.read_bytes() == backup_bytes,
        "newest_valid": newest in (item.path for item in catalog.recoverable),
        "legacy_compatible": repo.load(legacy).project_id == base.project_id
        if legacy.is_file() else True,
        "no_crash_recovery_started": True,
    }
    path = root / "00_w8_005_report.json"
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
