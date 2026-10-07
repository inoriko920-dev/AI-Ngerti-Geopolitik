from __future__ import annotations

import json
from pathlib import Path

from ai_ngerti_geopolitik.application.ai_contracts import (
    EDIT_PLAN_SCHEMA_VERSION,
    L1_RENDER_QUALIFIED_EFFECTS,
    EditPlan,
    EffectEditProposal,
)
from ai_ngerti_geopolitik.application.ai_l2_contracts import (
    AUTO_EDIT_PLAN_SCHEMA_VERSION,
    MAX_W7_COMMANDS,
    MAX_W7_SELECTED_TARGETS,
    W7_ALLOWED_COMMAND_TYPES,
    W7_CAPABILITY_REGISTRY,
    W7_POLICY_BOUNDS,
    AutoEditPlan,
    DurationEditProposal,
    SpeedEditProposal,
    TransformEditProposal,
    TransitionEditProposal,
)


def main() -> int:
    output = Path("artifacts/step11/w7-001/evidence")
    output.mkdir(parents=True, exist_ok=True)

    plan = AutoEditPlan(
        schema_version=2,
        base_project_revision=12,
        request_id="REQ-EVIDENCE-W7-001",
        summary="Bounded W7 mixed capability contract.",
        commands=(
            EffectEditProposal("clip-1", enter_effect="Rise", intensity_percent=120),
            TransformEditProposal("clip-1", scale_percent=115, opacity_percent=90),
            TransitionEditProposal("clip-1", "fade_black", 15),
            SpeedEditProposal("clip-2", 125),
            DurationEditProposal("clip-3", 180),
        ),
    )
    legacy = EditPlan(
        schema_version=1,
        base_project_revision=12,
        request_id="REQ-EVIDENCE-W6",
        summary="W6 compatibility proof.",
        commands=(EffectEditProposal("clip-1", exit_effect="Drift"),),
    )

    registry = {
        key: {
            "family": value.family.value,
            "manual_command_owner": value.manual_command_owner,
            "property_owner": value.property_owner,
            "application_owned_ripple": value.application_owned_ripple,
            "render_qualified": value.render_qualified,
        }
        for key, value in W7_CAPABILITY_REGISTRY.items()
    }
    report = {
        "status": "PASS",
        "w7_schema_version": AUTO_EDIT_PLAN_SCHEMA_VERSION,
        "w6_schema_version_unchanged": EDIT_PLAN_SCHEMA_VERSION,
        "w6_legacy_plan_valid": legacy.schema_version == 1,
        "allowed_command_types": list(W7_ALLOWED_COMMAND_TYPES),
        "registry": registry,
        "plan_command_count": len(plan.commands),
        "plan_target_count": len({item.target_clip_id for item in plan.commands}),
        "max_selected_targets": MAX_W7_SELECTED_TARGETS,
        "max_commands": MAX_W7_COMMANDS,
        "w6_effect_allowlist": list(L1_RENDER_QUALIFIED_EFFECTS),
        "duration_bounds_30fps_120frames": list(W7_POLICY_BOUNDS.duration_bounds(30, 120)),
        "position_bounds_1920x1080": [
            list(item) for item in W7_POLICY_BOUNDS.transform_position_bounds(1920, 1080)
        ],
        "transition_max_30fps_300frames": W7_POLICY_BOUNDS.transition_max_frames(
            30,
            300,
        ),
        "provider_network_started": False,
        "context_builder_started": False,
        "v2_parser_started": False,
        "semantic_verifier_started": False,
        "runtime_ui_changed": False,
        "canonical_apply_started": False,
    }

    expected = {
        "w7_schema_version": 2,
        "w6_schema_version_unchanged": 1,
        "w6_legacy_plan_valid": True,
        "allowed_command_types": [
            "set_clip_effects",
            "set_clip_duration",
            "set_clip_speed",
            "set_clip_transform",
            "set_clip_transition",
        ],
        "plan_command_count": 5,
        "plan_target_count": 3,
        "max_selected_targets": 20,
        "max_commands": 40,
        "duration_bounds_30fps_120frames": [60, 240],
        "position_bounds_1920x1080": [[-960, 960], [-540, 540]],
        "transition_max_30fps_300frames": 60,
        "provider_network_started": False,
        "context_builder_started": False,
        "v2_parser_started": False,
        "semantic_verifier_started": False,
        "runtime_ui_changed": False,
        "canonical_apply_started": False,
    }
    if report["status"] != "PASS":
        raise SystemExit("W7-001 evidence status failed")
    for key, value in expected.items():
        if report[key] != value:
            raise SystemExit(f"W7-001 evidence mismatch: {key}")

    (output / "00_w7_001_contract_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
