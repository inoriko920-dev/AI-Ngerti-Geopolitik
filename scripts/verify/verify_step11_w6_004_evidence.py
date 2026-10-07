from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED_TRUE = (
    "invalid_auth_disables_affected_slot_only",
    "network_retry_is_bounded",
    "success_marks_slot_healthy",
    "quota_does_not_rotate_immediately",
    "quota_cooldown_is_bounded",
    "quota_cooldown_expires",
    "all_slots_unavailable_is_typed",
    "bulk_txt_trim_dedupe_max100_no_retention_contract",
    "raw_secret_absent_from_evidence",
)

REQUIRED_FALSE = (
    "gemini_network_called",
    "context_builder_started",
    "plan_verifier_started",
    "credential_ui_started",
    "quota_evasion_rotation",
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    evidence = args.evidence.resolve()

    report_path = evidence / "00_w6_004_report.json"
    health_path = evidence / "01_health_failover.json"
    if not report_path.is_file() or not health_path.is_file():
        raise SystemExit("W6-004 evidence files are incomplete")

    report = json.loads(report_path.read_text(encoding="utf-8"))
    health = json.loads(health_path.read_text(encoding="utf-8"))

    checks: list[tuple[str, bool]] = []
    checks.append(("status", report.get("status") == "PASS"))
    checks.extend((key, report.get(key) is True) for key in REQUIRED_TRUE)
    checks.extend((key, report.get(key) is False) for key in REQUIRED_FALSE)
    checks.append(
        (
            "failover-sequence",
            report.get("legal_failover_sequence") == [1, 2, 2, 3],
        )
    )
    checks.append(("invalid-slot-disabled", health.get("slot_1_enabled") is False))
    checks.append(("successful-slot-healthy", health.get("slot_3") == "HEALTHY"))

    failed = [name for name, passed in checks if not passed]
    if failed:
        raise SystemExit("W6-004 evidence verification failed: " + ", ".join(failed))

    print(f"W6-004 evidence verification PASS: {len(checks)}/{len(checks)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
