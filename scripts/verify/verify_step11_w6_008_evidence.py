from __future__ import annotations

import json
from pathlib import Path


def main() -> int:
    path = Path("artifacts/step11/w6-008/evidence/00_w6_008_report.json")
    if not path.is_file():
        raise SystemExit("missing W6-008 evidence report")
    report = json.loads(path.read_text(encoding="utf-8"))
    checks = [
        report.get("status") == "PASS",
        report.get("staged_state") == "PENDING",
        report.get("approved_state") == "APPROVED",
        report.get("applied_state") == "APPLIED",
        report.get("stage_zero_mutation") is True,
        report.get("approval_zero_mutation") is True,
        report.get("one_revision_apply") is True,
        report.get("atomic_two_command_effect") is True,
        report.get("undo_exact_before_semantics") is True,
        report.get("undo_is_single_transaction") is True,
        report.get("redo_exact_applied_semantics") is True,
        report.get("batch_id") == "AI-BATCH:REQ-EVIDENCE-008",
        report.get("approval_apply_only") is True,
        report.get("w6_ui_started") is False,
        report.get("live_gemini_used") is False,
    ]
    if not all(checks):
        raise SystemExit("W6-008 evidence verification failed")
    print(f"W6-008 evidence verification PASS: {len(checks)}/{len(checks)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
