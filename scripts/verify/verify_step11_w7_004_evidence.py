from __future__ import annotations

import json
from pathlib import Path


def main() -> int:
    path = Path("artifacts/step11/w7-004/evidence/00_w7_004_verifier_report.json")
    if not path.is_file():
        raise SystemExit("missing W7-004 evidence report")

    report = json.loads(path.read_text(encoding="utf-8"))
    checks = [
        report.get("status") == "PASS",
        report.get("schema_version") == 2,
        report.get("base_revision") == 81,
        report.get("candidate_revision") == 81,
        report.get("candidate_hash_changed") is True,
        report.get("command_count") == 5,
        report.get("target_count") == 5,
        report.get("selected_scope_count") == 5,
        report.get("translated_command_types")
        == [
            "SetClipPropertiesCommand",
            "SetClipDurationCommand",
            "SetClipSpeedCommand",
            "SetClipPropertiesCommand",
            "SetClipPropertiesCommand",
        ],
        report.get("duration_ripple_application_owned") is True,
        report.get("speed_ripple_application_owned") is True,
        report.get("stale_rejected") is True,
        report.get("out_of_scope_rejected") is True,
        report.get("lock_rejected") is True,
        report.get("duration_policy_rejected") is True,
        report.get("canvas_policy_rejected") is True,
        report.get("sequential_transition_rejected") is True,
        report.get("canonical_state_unchanged") is True,
        report.get("command_bus_history_unchanged") is True,
        report.get("provider_profile_changed") is False,
        report.get("runtime_ui_changed") is False,
        report.get("canonical_apply_started") is False,
        report.get("w7_005_pacing_qualification_started") is False,
    ]
    if not all(checks):
        raise SystemExit("W7-004 evidence verification failed")
    print(f"W7-004 evidence verification PASS: {len(checks)}/{len(checks)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
