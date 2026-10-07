from __future__ import annotations

import json
from pathlib import Path


def main() -> int:
    root = Path("artifacts/step11/w8-003/evidence")
    report_path = root / "00_w8_003_relink_report.json"
    identity_path = root / "01_w8_003_paths_and_identity.json"
    project_path = root / "w8_003_relinked.angproj"
    for path in (report_path, identity_path, project_path):
        if not path.is_file() or path.stat().st_size <= 0:
            raise SystemExit(f"missing W8-003 evidence: {path.name}")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    identity = json.loads(identity_path.read_text(encoding="utf-8"))
    checks = [
        report.get("status") == "PASS",
        report.get("asset_id_preserved") is True,
        report.get("clip_reference_preserved") is True,
        report.get("old_path_absent_after_move") is True,
        report.get("new_path_online") is True,
        report.get("path_updated") is True,
        report.get("source_name_updated") is True,
        report.get("fingerprint_preserved") is True,
        report.get("duration_preserved") is True,
        report.get("metadata_preserved") is True,
        report.get("one_revision_apply") is True,
        report.get("validation_clear_after_relink") is True,
        report.get("save_reopen_exact") is True,
        report.get("save_reopen_path_exact") is True,
        report.get("undo_restores_original_binding") is True,
        report.get("redo_restores_relink") is True,
        report.get("batch_scan_started") is False,
        report.get("candidate_ranking_started") is False,
        report.get("ui_redesign_started") is False,
        identity.get("asset_id") == "A001",
        identity.get("applied_revision") == identity.get("base_revision") + 1,
        identity.get("undo_semantic_hash") == identity.get("before_semantic_hash"),
        identity.get("redo_semantic_hash") == identity.get("applied_semantic_hash"),
    ]
    if not all(checks):
        raise SystemExit("W8-003 evidence verification failed")
    print(f"W8-003 evidence verification PASS: {len(checks)}/{len(checks)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
