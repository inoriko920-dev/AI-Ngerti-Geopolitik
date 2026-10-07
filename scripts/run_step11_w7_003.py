from __future__ import annotations

import json
from pathlib import Path

from ai_ngerti_geopolitik.application.ai_contracts import (
    PlanContractError,
    PlanErrorCode,
)
from ai_ngerti_geopolitik.application.ai_l2_parser import (
    AUTO_EDIT_PLAN_V2_JSON_SCHEMA,
    AutoEditPlanParser,
)


def _payload() -> str:
    return json.dumps(
        {
            "schema_version": 2,
            "base_project_revision": 61,
            "request_id": "REQ-W7-003-EVIDENCE",
            "summary": "Parse one bounded command from every W7 family.",
            "commands": [
                {
                    "command_type": "set_clip_effects",
                    "target_clip_id": "clip-1",
                    "enter_effect": "Rise",
                    "intensity_percent": 120,
                },
                {
                    "command_type": "set_clip_duration",
                    "target_clip_id": "clip-2",
                    "duration_frames": 150,
                },
                {
                    "command_type": "set_clip_speed",
                    "target_clip_id": "clip-3",
                    "rate_percent": 125,
                },
                {
                    "command_type": "set_clip_transform",
                    "target_clip_id": "clip-4",
                    "position_x": 40,
                    "scale_percent": 110,
                },
                {
                    "command_type": "set_clip_transition",
                    "target_clip_id": "clip-5",
                    "preset": "fade_black",
                    "duration_frames": 12,
                },
            ],
        }
    )


def _rejects(parser: AutoEditPlanParser, raw: str, code: PlanErrorCode) -> bool:
    try:
        parser.parse(raw)
    except PlanContractError as exc:
        return exc.code is code
    return False


def main() -> int:
    output = Path("artifacts/step11/w7-003/evidence")
    output.mkdir(parents=True, exist_ok=True)

    parser = AutoEditPlanParser()
    plan = parser.parse(_payload())
    schema_commands = AUTO_EDIT_PLAN_V2_JSON_SCHEMA["properties"]["commands"]
    variants = schema_commands["items"]["oneOf"]

    invalid_unknown = json.loads(_payload())
    invalid_unknown["commands"][0]["unlock"] = True

    invalid_bool = json.loads(_payload())
    invalid_bool["commands"][1]["duration_frames"] = True

    invalid_ripple = json.loads(_payload())
    invalid_ripple["commands"][1]["ripple"] = True

    invalid_crop = json.loads(_payload())
    invalid_crop["commands"][3]["crop_left_percent"] = 10

    invalid_command = json.loads(_payload())
    invalid_command["commands"][0]["command_type"] = "delete_clip"

    report = {
        "status": "PASS",
        "schema_version": plan.schema_version,
        "base_project_revision": plan.base_project_revision,
        "command_count": len(plan.commands),
        "command_types": [command.command_type for command in plan.commands],
        "command_classes": [type(command).__name__ for command in plan.commands],
        "schema_closed_root": AUTO_EDIT_PLAN_V2_JSON_SCHEMA["additionalProperties"] is False,
        "schema_variant_count": len(variants),
        "schema_all_variants_closed": all(
            variant["additionalProperties"] is False for variant in variants
        ),
        "schema_command_cap": schema_commands["maxItems"],
        "unknown_field_rejected": _rejects(
            parser,
            json.dumps(invalid_unknown),
            PlanErrorCode.SCHEMA_INVALID,
        ),
        "bool_integer_rejected": _rejects(
            parser,
            json.dumps(invalid_bool),
            PlanErrorCode.SCHEMA_INVALID,
        ),
        "provider_ripple_rejected": _rejects(
            parser,
            json.dumps(invalid_ripple),
            PlanErrorCode.SCHEMA_INVALID,
        ),
        "crop_rejected": _rejects(
            parser,
            json.dumps(invalid_crop),
            PlanErrorCode.SCHEMA_INVALID,
        ),
        "unknown_command_rejected": _rejects(
            parser,
            json.dumps(invalid_command),
            PlanErrorCode.SCHEMA_INVALID,
        ),
        "project_state_read": False,
        "selected_scope_checked": False,
        "lock_checked": False,
        "dynamic_ranges_checked": False,
        "sequential_dry_run_started": False,
        "provider_profile_changed": False,
        "runtime_ui_changed": False,
        "canonical_apply_started": False,
    }

    expected = {
        "schema_version": 2,
        "base_project_revision": 61,
        "command_count": 5,
        "command_types": [
            "set_clip_effects",
            "set_clip_duration",
            "set_clip_speed",
            "set_clip_transform",
            "set_clip_transition",
        ],
        "command_classes": [
            "EffectEditProposal",
            "DurationEditProposal",
            "SpeedEditProposal",
            "TransformEditProposal",
            "TransitionEditProposal",
        ],
        "schema_closed_root": True,
        "schema_variant_count": 5,
        "schema_all_variants_closed": True,
        "schema_command_cap": 40,
        "unknown_field_rejected": True,
        "bool_integer_rejected": True,
        "provider_ripple_rejected": True,
        "crop_rejected": True,
        "unknown_command_rejected": True,
        "project_state_read": False,
        "selected_scope_checked": False,
        "lock_checked": False,
        "dynamic_ranges_checked": False,
        "sequential_dry_run_started": False,
        "provider_profile_changed": False,
        "runtime_ui_changed": False,
        "canonical_apply_started": False,
    }
    for key, value in expected.items():
        if report[key] != value:
            raise SystemExit(f"W7-003 evidence mismatch: {key}")

    (output / "00_w7_003_parser_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output / "01_w7_003_json_schema.json").write_text(
        json.dumps(AUTO_EDIT_PLAN_V2_JSON_SCHEMA, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
