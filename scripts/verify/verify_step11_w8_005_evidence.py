"""Fail-closed verification of W8-005 owned catalog evidence."""

from __future__ import annotations

import json
from pathlib import Path


def main() -> int:
    root = Path("artifacts/step11/w8-005/evidence")
    report = json.loads((root / "00_w8_005_report.json").read_text(encoding="utf-8"))
    required = (
        "invalid_isolated",
        "foreign_untouched",
        "source_unchanged",
        "backup_unchanged",
        "newest_valid",
        "legacy_compatible",
        "legacy_old_pruned",
        "no_crash_recovery_started",
    )
    checks = [
        report.get("status") == "PASS",
        report.get("retained_valid") == 20,
        *(report.get(key) is True for key in required),
        (root / "source.angproj").is_file(),
        (root / "source.angproj.bak").read_bytes() == b"OWNED BACKUP NEVER PRUNE",
    ]
    if not all(checks):
        raise SystemExit("W8-005 managed catalog evidence verification FAILED")
    print(f"W8-005 evidence verification PASS: {len(checks)}/{len(checks)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
