from __future__ import annotations

import dataclasses

import pytest

from ai_ngerti_geopolitik.application.ai_contracts import (
    EDIT_PLAN_SCHEMA_VERSION,
    L1_RENDER_QUALIFIED_EFFECTS,
    EditPlan,
    EffectEditProposal,
    PlanContractError,
    PlanErrorCode,
)
from ai_ngerti_geopolitik.application.ai_l2_contracts import (
    AUTO_EDIT_PLAN_SCHEMA_VERSION,
    MAX_W7_COMMANDS,
    MAX_W7_SELECTED_TARGETS,
    W7_ALLOWED_COMMAND_TYPES,
    W7_CAPABILITY_REGISTRY,
    W7_POLICY_BOUNDS,
    W7_TRANSITION_PRESETS,
    AutoEditPlan,
    DurationEditProposal,
    SpeedEditProposal,
    TransformEditProposal,
    TransitionEditProposal,
    W7CommandFamily,
    capability_for,
)


def _plan(*commands) -> AutoEditPlan:
    return AutoEditPlan(
        schema_version=2,
        base_project_revision=9,
        request_id="REQ-W7-001",
        summary="Bounded mixed L1/L2 plan.",
        commands=tuple(commands),
    )


def test_w7_registry_is_exact_and_points_to_existing_manual_owners() -> None:
    assert tuple(W7_CAPABILITY_REGISTRY) == W7_ALLOWED_COMMAND_TYPES
    assert W7_ALLOWED_COMMAND_TYPES == (
        "set_clip_effects",
        "set_clip_duration",
        "set_clip_speed",
        "set_clip_transform",
        "set_clip_transition",
    )
    assert capability_for("set_clip_effects").manual_command_owner == "SetClipPropertiesCommand"
    assert capability_for("set_clip_duration").manual_command_owner == "SetClipDurationCommand"
    assert capability_for("set_clip_speed").manual_command_owner == "SetClipSpeedCommand"
    assert capability_for("set_clip_transform").property_owner == "VideoProperties"
    assert capability_for("set_clip_transition").property_owner == "TransitionProperties"
    assert capability_for("set_clip_duration").application_owned_ripple is True
    assert capability_for("set_clip_speed").application_owned_ripple is True


@pytest.mark.parametrize(
    "forbidden",
    [
        "split_clip",
        "trim_clip",
        "remove_clip",
        "move_clip",
        "set_crop",
        "reverse_clip",
        "crossfade",
        "set_subtitle",
        "set_audio",
        "set_color",
        "set_marker",
        "set_project_settings",
        "set_credential",
    ],
)
def test_w7_registry_hard_rejects_deferred_or_forbidden_capabilities(forbidden: str) -> None:
    with pytest.raises(PlanContractError) as caught:
        capability_for(forbidden)
    assert caught.value.code is PlanErrorCode.SCHEMA_INVALID


def test_w7_policy_bounds_are_typed_and_compute_dynamic_limits() -> None:
    assert W7_POLICY_BOUNDS.duration_bounds(30, 120) == (60, 240)
    assert W7_POLICY_BOUNDS.duration_bounds(30, 20) == (15, 40)
    assert W7_POLICY_BOUNDS.transform_position_bounds(1920, 1080) == (
        (-960, 960),
        (-540, 540),
    )
    assert W7_POLICY_BOUNDS.transition_max_frames(30, 300) == 60
    assert W7_POLICY_BOUNDS.transition_max_frames(30, 80) == 40
    assert W7_POLICY_BOUNDS.speed_min_percent == 50
    assert W7_POLICY_BOUNDS.speed_max_percent == 200


def test_duration_contract_has_application_owned_ripple_not_provider_field() -> None:
    proposal = DurationEditProposal("clip-1", 150)
    assert proposal.command_type == "set_clip_duration"
    assert not hasattr(proposal, "ripple")
    assert [field.name for field in dataclasses.fields(proposal)] == [
        "target_clip_id",
        "duration_frames",
        "command_type",
    ]
    with pytest.raises(PlanContractError):
        DurationEditProposal("clip-1", 0)
    with pytest.raises(PlanContractError):
        DurationEditProposal("clip-1", True)


@pytest.mark.parametrize("rate", [49, 201, True])
def test_speed_contract_uses_narrow_w7_ai_bounds(rate: object) -> None:
    with pytest.raises(PlanContractError):
        SpeedEditProposal("clip-1", rate)  # type: ignore[arg-type]
    assert SpeedEditProposal("clip-1", 50).rate_percent == 50
    assert SpeedEditProposal("clip-1", 200).rate_percent == 200


def test_transform_contract_is_uniform_bounded_and_exposes_no_crop() -> None:
    proposal = TransformEditProposal(
        "clip-1",
        position_x=100,
        position_y=-50,
        scale_percent=125,
        rotation_tenths=120,
        opacity_percent=85,
    )
    fields = {field.name for field in dataclasses.fields(proposal)}
    assert "crop_left_percent" not in fields
    assert "scale_x_percent" not in fields
    assert "scale_y_percent" not in fields
    assert proposal.scale_percent == 125

    with pytest.raises(PlanContractError):
        TransformEditProposal("clip-1")
    with pytest.raises(PlanContractError):
        TransformEditProposal("clip-1", scale_percent=49)
    with pytest.raises(PlanContractError):
        TransformEditProposal("clip-1", rotation_tenths=151)
    with pytest.raises(PlanContractError):
        TransformEditProposal("clip-1", opacity_percent=59)
    with pytest.raises(PlanContractError):
        TransformEditProposal("clip-1", position_x=True)


def test_transition_contract_is_only_none_or_fade_black() -> None:
    assert W7_TRANSITION_PRESETS == ("none", "fade_black")
    assert TransitionEditProposal("clip-1", "none", 0).duration_frames == 0
    assert TransitionEditProposal("clip-1", "fade_black", 1).duration_frames == 1
    with pytest.raises(PlanContractError):
        TransitionEditProposal("clip-1", "dissolve", 10)
    with pytest.raises(PlanContractError):
        TransitionEditProposal("clip-1", "none", 1)
    with pytest.raises(PlanContractError):
        TransitionEditProposal("clip-1", "fade_black", 0)


def test_effects_carry_forward_exact_w6_render_qualified_contract() -> None:
    effect = EffectEditProposal("clip-1", enter_effect="Rise", intensity_percent=120)
    plan = _plan(effect)
    assert plan.commands == (effect,)
    assert capability_for(effect.command_type).family is W7CommandFamily.EFFECTS
    assert tuple(L1_RENDER_QUALIFIED_EFFECTS) == (
        "None",
        "Fade",
        "Pop",
        "Breathe",
        "Stomp",
        "Tumble",
        "Tectonic",
        "Rise",
        "Pan",
        "Drift",
    )
    with pytest.raises(PlanContractError):
        EffectEditProposal("clip-1", enter_effect="Blur")


def test_auto_edit_plan_accepts_one_command_per_family_on_same_target() -> None:
    plan = _plan(
        EffectEditProposal("clip-1", enter_effect="Rise"),
        TransformEditProposal("clip-1", scale_percent=110),
        TransitionEditProposal("clip-1", "fade_black", 12),
    )
    assert plan.schema_version == AUTO_EDIT_PLAN_SCHEMA_VERSION
    assert len(plan.commands) == 3


def test_auto_edit_plan_rejects_duplicate_family_and_pacing_conflict() -> None:
    with pytest.raises(PlanContractError) as duplicate:
        _plan(
            TransformEditProposal("clip-1", scale_percent=110),
            TransformEditProposal("clip-1", opacity_percent=90),
        )
    assert duplicate.value.code is PlanErrorCode.SEMANTIC_INVALID

    with pytest.raises(PlanContractError) as pacing:
        _plan(
            DurationEditProposal("clip-1", 120),
            SpeedEditProposal("clip-1", 110),
        )
    assert pacing.value.code is PlanErrorCode.SEMANTIC_INVALID


def test_auto_edit_plan_enforces_command_and_unique_target_caps() -> None:
    commands = tuple(
        TransformEditProposal(f"clip-{index}", opacity_percent=90)
        for index in range(1, MAX_W7_SELECTED_TARGETS + 1)
    )
    assert len(_plan(*commands).commands) == MAX_W7_SELECTED_TARGETS

    with pytest.raises(PlanContractError) as targets:
        _plan(
            *(
                TransformEditProposal(f"clip-{index}", opacity_percent=90)
                for index in range(1, MAX_W7_SELECTED_TARGETS + 2)
            )
        )
    assert targets.value.code is PlanErrorCode.SEMANTIC_INVALID

    too_many = tuple(
        EffectEditProposal(f"clip-{index}", enter_effect="Rise")
        for index in range(1, MAX_W7_COMMANDS + 2)
    )
    with pytest.raises(PlanContractError) as command_cap:
        _plan(*too_many)
    assert command_cap.value.code is PlanErrorCode.SCHEMA_INVALID


def test_auto_edit_plan_root_contract_is_schema_v2_and_strict_integer_safe() -> None:
    command = TransformEditProposal("clip-1", opacity_percent=90)
    with pytest.raises(PlanContractError):
        AutoEditPlan(1, 0, "REQ", "summary", (command,))
    with pytest.raises(PlanContractError):
        AutoEditPlan(True, 0, "REQ", "summary", (command,))  # type: ignore[arg-type]
    with pytest.raises(PlanContractError):
        AutoEditPlan(2, True, "REQ", "summary", (command,))  # type: ignore[arg-type]
    with pytest.raises(PlanContractError):
        AutoEditPlan(2, 0, "", "summary", (command,))
    with pytest.raises(PlanContractError):
        AutoEditPlan(2, 0, "REQ", "", (command,))
    with pytest.raises(PlanContractError):
        AutoEditPlan(2, 0, "REQ", "summary", ())


def test_w7_does_not_change_w6_edit_plan_schema_or_behavior() -> None:
    assert EDIT_PLAN_SCHEMA_VERSION == 1
    legacy = EditPlan(
        schema_version=1,
        base_project_revision=3,
        request_id="REQ-W6",
        summary="Legacy W6 effect plan.",
        commands=(EffectEditProposal("clip-1", enter_effect="Rise"),),
    )
    assert legacy.schema_version == 1
    assert legacy.commands[0].command_type == "set_clip_effects"
