from __future__ import annotations

import json
from pathlib import Path


def main() -> int:
    root = Path("artifacts/step11/w8-004/evidence")
    report_path = root / "00_w8_004_report.json"
    project_path = root / "relinked.angproj"
    if not report_path.is_file() or not project_path.is_file():
        raise SystemExit("missing W8-004 evidence output")
    if project_path.stat().st_size <= 0:
        raise SystemExit("empty W8-004 project evidence")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    required = (
        "ambiguous_requires_manual", "all_candidates_verified", "no_scan_mutation",
        "one_batch_revision", "stable_asset_id", "validation_clear",
        "save_reopen_exact", "undo_exact", "redo_exact",
    )
    checks = [report.get("status") == "PASS", report.get("candidate_count") == 2]
    checks.extend(report.get(key) is True for key in required)
    checks.extend(report.get(key) is False for key in ("ui_redesign", "auto_apply", "w8_005_started"))
    if not all(checks):
        raise SystemExit("W8-004 evidence verification failed")
    print(f"W8-004 evidence verification PASS: {len(checks)}/{len(checks)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
