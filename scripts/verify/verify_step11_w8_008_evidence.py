"""W8-008 strict owned stale job evidence verifier."""

from __future__ import annotations

import json
from pathlib import Path


def main() -> int:
    root = Path("artifacts/step11/w8-008/evidence")
    report = json.loads((root / "00_w8_008_report.json").read_text(encoding="utf-8"))
    required = (
        "validation_edit_stale",
        "validation_result_discarded",
        "concurrent_edit_untouched",
        "close_session_id_cleared",
        "reopen_session_id_rotated",
        "same_project_same_revision_stale",
        "fresh_validation_completes",
        "fresh_validation_bound",
        "relink_closed_session_stale",
        "relink_different_project_stale",
        "recovery_cancelled",
        "recovery_cancel_rejects_result",
        "source_project_unchanged",
        "foreign_session_no_auto_mutation",
        "no_w8_009_started",
    )
    checks = [report.get("status") == "PASS"]
    checks.extend(report.get(key) is True for key in required)
    checks.append((root / "canonical.angproj").is_file())
    checks.append((root / "other.angproj").is_file())
    if len(report) != len(required) + 1 or not all(checks):
        raise SystemExit("W8-008 stale result evidence FAILED")
    print(f"W8-008 evidence verification PASS: {len(checks)}/{len(checks)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
