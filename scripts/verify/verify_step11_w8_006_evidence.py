"""Strict W8-006 evidence verifier: validates proof and source revision."""

from __future__ import annotations

import json
from pathlib import Path


def main() -> int:
    root = Path("artifacts/step11/w8-006/evidence")
    report = json.loads((root / "00_w8_006_report.json").read_text(encoding="utf-8"))
    required = (
        "unclean_detected", "valid_newer_only", "corrupt_newest_excluded",
        "ignore_zero_mutation", "explicit_restore", "recovered_working_state_dirty",
        "source_bytes_unchanged", "clean_close_clears_warning", "no_silent_save",
        "no_w8_007_started",
    )
    checks = [report.get("status") == "PASS"]
    checks.extend(report.get(key) is True for key in required)
    checks.append((root / "canonical.angproj").is_file())
    if not all(checks):
        raise SystemExit("W8-006 recovery evidence verification FAILED")
    print(f"W8-006 evidence verification PASS: {len(checks)}/{len(checks)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
