from __future__ import annotations

import json
from pathlib import Path


def main() -> int:
    root = Path("artifacts/step11/w7-002/evidence")
    report_path = root / "00_w7_002_context_report.json"
    context_path = root / "01_w7_002_context_shape.json"
    if not report_path.is_file() or not context_path.is_file():
        raise SystemExit("missing W7-002 evidence files")

    report = json.loads(report_path.read_text(encoding="utf-8"))
    context = json.loads(context_path.read_text(encoding="utf-8"))
    checks = [
        report.get("status") == "PASS",
        report.get("schema_version") == 2,
        report.get("auto_edit_plan_schema_version") == 2,
        report.get("selected_clip_ids") == ["clip-2", "clip-1"],
        report.get("target_count") == 2,
        report.get("allowed_command_types")
        == [
            "set_clip_effects",
            "set_clip_duration",
            "set_clip_speed",
            "set_clip_transform",
            "set_clip_transition",
        ],
        report.get("max_selected_targets") == 20,
        report.get("max_plan_commands") == 40,
        report.get("duration_minimum_half_second_frames") == 15,
        report.get("speed_bounds") == [50, 200],
        report.get("position_x_bounds") == [-960, 960],
        report.get("transition_presets") == ["none", "fade_black"],
        report.get("source_duration_available") is True,
        report.get("neighbors_bounded") is True,
        report.get("project_unchanged") is True,
        report.get("path_absent") is True,
        report.get("source_name_absent") is True,
        report.get("parser_started") is False,
        report.get("semantic_verifier_started") is False,
        report.get("provider_profile_changed") is False,
        report.get("runtime_ui_changed") is False,
        report.get("canonical_apply_started") is False,
        context.get("selected_scope", {}).get("max_targets") == 20,
        context.get("policy", {}).get("selected_scope_only") is True,
    ]
    if not all(checks):
        raise SystemExit("W7-002 evidence verification failed")
    print(f"W7-002 evidence verification PASS: {len(checks)}/{len(checks)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
