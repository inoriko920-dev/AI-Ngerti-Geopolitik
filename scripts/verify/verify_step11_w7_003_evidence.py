from __future__ import annotations

import json
from pathlib import Path


def main() -> int:
    root = Path("artifacts/step11/w7-003/evidence")
    report_path = root / "00_w7_003_parser_report.json"
    schema_path = root / "01_w7_003_json_schema.json"
    if not report_path.is_file() or not schema_path.is_file():
        raise SystemExit("missing W7-003 evidence files")

    report = json.loads(report_path.read_text(encoding="utf-8"))
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    checks = [
        report.get("status") == "PASS",
        report.get("schema_version") == 2,
        report.get("base_project_revision") == 61,
        report.get("command_count") == 5,
        report.get("command_types")
        == [
            "set_clip_effects",
            "set_clip_duration",
            "set_clip_speed",
            "set_clip_transform",
            "set_clip_transition",
        ],
        report.get("schema_variant_count") == 5,
        report.get("schema_closed_root") is True,
        report.get("schema_all_variants_closed") is True,
        report.get("schema_command_cap") == 40,
        report.get("unknown_field_rejected") is True,
        report.get("bool_integer_rejected") is True,
        report.get("provider_ripple_rejected") is True,
        report.get("crop_rejected") is True,
        report.get("unknown_command_rejected") is True,
        report.get("project_state_read") is False,
        report.get("selected_scope_checked") is False,
        report.get("lock_checked") is False,
        report.get("dynamic_ranges_checked") is False,
        report.get("sequential_dry_run_started") is False,
        report.get("provider_profile_changed") is False,
        report.get("runtime_ui_changed") is False,
        report.get("canonical_apply_started") is False,
        schema.get("additionalProperties") is False,
        schema.get("properties", {}).get("commands", {}).get("maxItems") == 40,
    ]
    if not all(checks):
        raise SystemExit("W7-003 evidence verification failed")
    print(f"W7-003 evidence verification PASS: {len(checks)}/{len(checks)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
