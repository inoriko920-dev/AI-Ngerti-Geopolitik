from __future__ import annotations

import json
from pathlib import Path


def main() -> int:
    path = Path("artifacts/step11/w8-001/evidence/00_w8_001_validation_report.json")
    if not path.is_file():
        raise SystemExit("missing W8-001 validation evidence")
    report = json.loads(path.read_text(encoding="utf-8"))
    checks = [
        report.get("status") == "PASS",
        report.get("project_revision") == 12,
        report.get("issue_codes")
        == [
            "MEDIA_MISSING_REFERENCED",
            "MEDIA_OFFLINE_REFERENCED",
            "MEDIA_MISSING_UNREFERENCED",
        ],
        report.get("issue_severities") == ["BLOCKER", "ERROR", "WARNING"],
        report.get("issue_targets") == [["A001", "C001"], ["A003", "N001"], ["A002"]],
        report.get("blocker_count") == 1,
        report.get("error_count") == 1,
        report.get("warning_count") == 1,
        report.get("info_count") == 0,
        report.get("canonical_state_unchanged") is True,
        report.get("same_input_deterministic") is True,
        report.get("revision_stale_detected") is True,
        report.get("semantic_stale_detected") is True,
        report.get("project_stale_detected") is True,
        report.get("invalid_project_issue_count") == 1,
        report.get("invalid_project_code") == "PROJECT_INVALID",
        report.get("filesystem_probe_started") is False,
        report.get("relink_started") is False,
        report.get("recovery_started") is False,
        report.get("diagnostics_started") is False,
        report.get("runtime_ui_changed") is False,
        report.get("canonical_apply_started") is False,
    ]
    if not all(checks):
        raise SystemExit("W8-001 evidence verification failed")
    print(f"W8-001 evidence verification PASS: {len(checks)}/{len(checks)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
