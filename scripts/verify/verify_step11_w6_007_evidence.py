from __future__ import annotations

import json
from pathlib import Path


def main() -> int:
    path = Path("artifacts/step11/w6-007/evidence/00_w6_007_report.json")
    if not path.is_file():
        raise SystemExit("missing W6-007 evidence report")
    report = json.loads(path.read_text(encoding="utf-8"))
    checks = [
        report.get("status") == "PASS",
        report.get("provider_off_caller_thread") is True,
        report.get("job_state") == "SUCCESS",
        report.get("provider_calls") == 1,
        report.get("verified_command_count") == 1,
        report.get("candidate_revision") == 21,
        report.get("canonical_state_unchanged") is True,
        report.get("credential_not_in_snapshot") is True,
        report.get("gemini_network_used_in_deterministic_evidence") is False,
        report.get("approval_apply_started") is False,
        report.get("w6_ui_started") is False,
    ]
    if not all(checks):
        raise SystemExit("W6-007 evidence verification failed")
    print(f"W6-007 evidence verification PASS: {len(checks)}/{len(checks)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
