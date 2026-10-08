"""Fail-closed checks for W8-010 end-to-end evidence and unchanged UI parity."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path


def main() -> int:
    root = Path("artifacts/step11/w8-010/evidence")
    report = json.loads((root / "00_w8_010_report.json").read_text(encoding="utf-8"))
    required = (
        "validation_blocker_shown",
        "asset_scan_real_candidate",
        "candidate_not_auto_applied",
        "identity_exact",
        "validation_cleared",
        "source_unchanged_until_save",
        "save_reopen_exact",
        "undo_redo_exact",
        "prior_state_changed",
        "recovery_requires_choice",
        "recovery_restores_dirty",
        "snapshot_revision_exact",
        "crash_source_unchanged",
        "explicit_save_required",
        "diagnostic_redacted",
        "frozen_ui_reference_kept",
        "no_step12_started",
    )
    checks = [report.get("status") == "PASS"]
    checks.extend(report.get(key) is True for key in required)
    checks.extend(
        (root / filename).stat().st_size > 0
        for filename in (
            "golden03.angproj", "golden03.angproj.bak",
            "01_validation_missing.png", "02_asset_scan.png",
        )
    )
    archive = root / "redacted-support.zip"
    with zipfile.ZipFile(archive) as bundle:
        checks.append(bundle.namelist() == ["manifest.json", "events.json"])
    if len(report) != len(required) + 1 or not all(checks):
        raise SystemExit("W8-010 GOLDEN-03 evidence verification FAILED")
    print(f"W8-010 GOLDEN-03 evidence verification PASS: {len(checks)}/{len(checks)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
