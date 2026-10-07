from __future__ import annotations

import json
from pathlib import Path


def main() -> int:
    root = Path("artifacts/step11/w7-009/evidence")
    required = (
        "00_w7_009_report.json",
        "01_w7_009_diffs.json",
    )
    for name in required:
        path = root / name
        if not path.is_file() or path.stat().st_size <= 0:
            raise SystemExit(f"missing W7-009 evidence: {name}")

    report = json.loads((root / "00_w7_009_report.json").read_text(encoding="utf-8"))
    diffs = json.loads((root / "01_w7_009_diffs.json").read_text(encoding="utf-8"))["diffs"]

    if report.get("status") != "PASS":
        raise SystemExit("W7-009 evidence status is not PASS")
    if report.get("approval_id") != "AI-APPROVAL:REQ-W7-009-EVIDENCE":
        raise SystemExit("W7-009 approval id mismatch")
    if report.get("batch_id") != "AI-BATCH:REQ-W7-009-EVIDENCE":
        raise SystemExit("W7-009 batch id mismatch")
    if report.get("diff_count") != 6 or len(diffs) != 6:
        raise SystemExit("W7-009 diff count mismatch")
    if report.get("mixed_timeline_end_frames") != 210:
        raise SystemExit("W7-009 timeline result mismatch")

    for key in (
        "diffs_bounded",
        "diffs_have_before_after_arrow",
        "canonical_unchanged_before_approval",
        "revision_increment_once_on_apply",
        "can_undo_after_apply",
        "undo_restores_before_semantic_hash",
        "can_redo_after_undo",
        "redo_restores_applied_semantic_hash",
    ):
        if report.get(key) is not True:
            raise SystemExit(f"W7-009 evidence gate false: {key}")

    if report.get("new_screen_or_layout_created") is not False:
        raise SystemExit("W7-009 unexpectedly created a new UI screen/layout")
    if report.get("w7_010_started") is not False:
        raise SystemExit("W7-009 crossed W7-010 boundary")
    if not all(isinstance(item, str) and "→" in item and len(item) <= 280 for item in diffs):
        raise SystemExit("W7-009 diff payload is not bounded before/after text")

    print("W7-009 evidence verification PASS: 2/2 files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
