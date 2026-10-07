from __future__ import annotations

import json
from pathlib import Path


def main() -> int:
    path = Path("artifacts/step11/w8-002/evidence/00_w8_002_real_media_report.json")
    if not path.is_file():
        raise SystemExit("missing W8-002 real-media evidence")
    report = json.loads(path.read_text(encoding="utf-8"))
    checks = [
        report.get("status") == "PASS",
        report.get("clean_issue_count") == 0,
        report.get("missing_codes") == ["MEDIA_FILE_MISSING"],
        report.get("missing_blocker") is True,
        report.get("zero_codes") == ["MEDIA_ZERO_BYTE"],
        report.get("broken_codes") == ["MEDIA_PROBE_FAILED"],
        report.get("duplicate_codes") == ["MEDIA_DUPLICATE_FINGERPRINT"],
        report.get("duplicate_targets") == [["A001", "A002"]],
        report.get("fixture_fingerprint") == report.get("duplicate_fingerprint"),
        report.get("projection_total") == 1,
        report.get("projection_media_count") == 1,
        report.get("projection_stale_initial") is False,
        report.get("projection_stale_after_revision") is True,
        report.get("canonical_state_unchanged") is True,
        report.get("relink_started") is False,
        report.get("recovery_started") is False,
        report.get("diagnostics_started") is False,
        report.get("ui_redesign_started") is False,
    ]
    if not all(checks):
        raise SystemExit("W8-002 evidence verification failed")
    print(f"W8-002 evidence verification PASS: {len(checks)}/{len(checks)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
