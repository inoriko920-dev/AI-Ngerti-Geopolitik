from __future__ import annotations

import json
from pathlib import Path


def main() -> int:
    path = Path("artifacts/step11/w7-001/evidence/00_w7_001_contract_report.json")
    if not path.is_file():
        raise SystemExit("missing W7-001 contract evidence")
    report = json.loads(path.read_text(encoding="utf-8"))
    checks = [
        report.get("status") == "PASS",
        report.get("w7_schema_version") == 2,
        report.get("w6_schema_version_unchanged") == 1,
        report.get("w6_legacy_plan_valid") is True,
        report.get("allowed_command_types")
        == [
            "set_clip_effects",
            "set_clip_duration",
            "set_clip_speed",
            "set_clip_transform",
            "set_clip_transition",
        ],
        report.get("plan_command_count") == 5,
        report.get("plan_target_count") == 3,
        report.get("max_selected_targets") == 20,
        report.get("max_commands") == 40,
        report.get("duration_bounds_30fps_120frames") == [60, 240],
        report.get("position_bounds_1920x1080") == [[-960, 960], [-540, 540]],
        report.get("transition_max_30fps_300frames") == 60,
        report.get("provider_network_started") is False,
        report.get("context_builder_started") is False,
        report.get("v2_parser_started") is False,
        report.get("semantic_verifier_started") is False,
        report.get("runtime_ui_changed") is False,
        report.get("canonical_apply_started") is False,
    ]
    if not all(checks):
        raise SystemExit("W7-001 evidence verification failed")
    print(f"W7-001 evidence verification PASS: {len(checks)}/{len(checks)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
