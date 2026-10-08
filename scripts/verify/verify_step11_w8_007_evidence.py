"""Strict W8-007 evidence verifier; no fabricated pass flags."""

from __future__ import annotations

import json
from pathlib import Path


def main() -> int:
    root = Path("artifacts/step11/w8-007/evidence")
    report = json.loads((root / "00_w8_007_report.json").read_text(encoding="utf-8"))
    required = (
        "failed_saves_detected",
        "source_unchanged_before_retry",
        "dirty_after_failed_save",
        "backup_readable_after_failures",
        "temp_files_cleaned_after_failures",
        "source_was_not_rebound",
        "retry_success",
        "retry_persisted_exact_state",
        "backup_equals_prior_source",
        "no_temp_after_retry",
        "source_changed_only_after_retry",
        "snapshot_fault_typed",
        "snapshot_did_not_touch_source",
        "failed_snapshot_not_published",
        "failed_snapshot_temp_clean",
        "w8_008_not_started",
    )
    checks = [report.get("status") == "PASS"]
    checks.extend(report.get(key) is True for key in required)
    checks.append((root / "canonical.angproj").is_file())
    checks.append((root / "canonical.angproj.bak").is_file())
    if len(report) != len(required) + 1 or not all(checks):
        raise SystemExit("W8-007 atomic persistence evidence verification FAILED")
    print(f"W8-007 evidence verification PASS: {len(checks)}/{len(checks)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
