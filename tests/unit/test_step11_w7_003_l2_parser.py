from __future__ import annotations

import json

import pytest

from ai_ngerti_geopolitik.application.ai_contracts import (
    EffectEditProposal,
    PlanContractError,
    PlanErrorCode,
)
from ai_ngerti_geopolitik.application.ai_l2_contracts import (
    AUTO_EDIT_PLAN_SCHEMA_VERSION,
    MAX_W7_COMMANDS,
    DurationEditProposal,
    SpeedEditProposal,
    TransformEditProposal,
    TransitionEditProposal,
)
from ai_ngerti_geopolitik.application.ai_l2_parser import (
    AUTO_EDIT_PLAN_V2_JSON_SCHEMA,
    AutoEditPlanParser,
)


def _root(commands: list[dict[str, object]], **extra: object) -> str:
    payload: dict[str, object] = {
        "schema_version": 2,
        "base_project_revision": 61,
        "request_id": "REQ-W7-003",
        "summary": "Bounded mixed L1/L2 plan.",
        "commands": commands,
    }
    payload.update(extra)
    return json.dumps(payload)


def _valid_commands() -> list[dict[str, object]]:
    return [
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
            "rotation_tenths": -20,
            "opacity_percent": 95,
        },
        {
            "command_type": "set_clip_transition",
            "target_clip_id": "clip-5",
            "preset": "fade_black",
            "duration_frames": 12,
        },
    ]


def test_parser_decodes_all_five_registered_command_families() -> None:
    plan = AutoEditPlanParser().parse(_root(_valid_commands()))

    assert plan.schema_version == AUTO_EDIT_PLAN_SCHEMA_VERSION == 2
    assert plan.base_project_revision == 61
    assert plan.request_id == "REQ-W7-003"
    assert len(plan.commands) == 5
    assert isinstance(plan.commands[0], EffectEditProposal)
    assert isinstance(plan.commands[1], DurationEditProposal)
    assert isinstance(plan.commands[2], SpeedEditProposal)
    assert isinstance(plan.commands[3], TransformEditProposal)
    assert isinstance(plan.commands[4], TransitionEditProposal)


def test_canonical_json_schema_is_closed_and_bounded() -> None:
    schema = AUTO_EDIT_PLAN_V2_JSON_SCHEMA
    assert schema["type"] == "object"
    assert schema["additionalProperties"] is False
    assert schema["required"] == [
        "schema_version",
        "base_project_revision",
        "request_id",
        "summary",
        "commands",
    ]
    commands = schema["properties"]["commands"]
    assert commands["minItems"] == 1
    assert commands["maxItems"] == MAX_W7_COMMANDS == 40
    variants = commands["items"]["oneOf"]
    assert len(variants) == 5
    assert all(item["additionalProperties"] is False for item in variants)
    assert [item["properties"]["command_type"]["const"] for item in variants] == [
        "set_clip_effects",
        "set_clip_duration",
        "set_clip_speed",
        "set_clip_transform",
        "set_clip_transition",
    ]


@pytest.mark.parametrize(
    "raw",
    [
        "",
        "{",
        "[]",
        json.dumps(
            {
                "schema_version": 2,
                "base_project_revision": 61,
                "request_id": "REQ",
                "commands": [],
            }
        ),
        _root(_valid_commands(), unknown_root=True),
    ],
)
def test_parser_rejects_malformed_non_object_missing_and_unknown_root(raw: str) -> None:
    with pytest.raises(PlanContractError) as caught:
        AutoEditPlanParser().parse(raw)
    assert caught.value.code is PlanErrorCode.SCHEMA_INVALID


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("schema_version", True),
        ("schema_version", 1),
        ("base_project_revision", True),
        ("base_project_revision", -1),
        ("request_id", 7),
        ("request_id", "   "),
        ("summary", None),
        ("summary", ""),
        ("commands", "not-an-array"),
    ],
)
def test_parser_rejects_invalid_root_types_and_values(field: str, value: object) -> None:
    payload = json.loads(_root(_valid_commands()))
    payload[field] = value
    with pytest.raises(PlanContractError) as caught:
        AutoEditPlanParser().parse(json.dumps(payload))
    assert caught.value.code is PlanErrorCode.SCHEMA_INVALID


def test_parser_rejects_unknown_command_and_non_object_command() -> None:
    cases: list[list[object]] = [
        [{"command_type": "delete_clip", "target_clip_id": "clip-1"}],
        ["set_clip_speed"],
    ]
    for commands in cases:
        with pytest.raises(PlanContractError) as caught:
            AutoEditPlanParser().parse(_root(commands))  # type: ignore[arg-type]
        assert caught.value.code is PlanErrorCode.SCHEMA_INVALID


@pytest.mark.parametrize(
    "command",
    [
        {
            "command_type": "set_clip_duration",
            "target_clip_id": "clip-1",
            "duration_frames": 120,
            "ripple": True,
        },
        {
            "command_type": "set_clip_speed",
            "target_clip_id": "clip-1",
            "rate_percent": 120,
            "ripple": True,
        },
        {
            "command_type": "set_clip_transform",
            "target_clip_id": "clip-1",
            "scale_percent": 110,
            "crop_left_percent": 10,
        },
        {
            "command_type": "set_clip_effects",
            "target_clip_id": "clip-1",
            "enter_effect": "Rise",
            "unlock": True,
        },
        {
            "command_type": "set_clip_transition",
            "target_clip_id": "clip-1",
            "preset": "fade_black",
            "duration_frames": 10,
            "crossfade": True,
        },
    ],
)
def test_parser_rejects_provider_owned_or_forbidden_extra_fields(
    command: dict[str, object],
) -> None:
    with pytest.raises(PlanContractError) as caught:
        AutoEditPlanParser().parse(_root([command]))
    assert caught.value.code is PlanErrorCode.SCHEMA_INVALID


@pytest.mark.parametrize(
    "command",
    [
        {
            "command_type": "set_clip_duration",
            "target_clip_id": "clip-1",
            "duration_frames": True,
        },
        {
            "command_type": "set_clip_speed",
            "target_clip_id": "clip-1",
            "rate_percent": False,
        },
        {
            "command_type": "set_clip_transform",
            "target_clip_id": "clip-1",
            "position_x": True,
        },
        {
            "command_type": "set_clip_effects",
            "target_clip_id": "clip-1",
            "intensity_percent": True,
        },
        {
            "command_type": "set_clip_transition",
            "target_clip_id": "clip-1",
            "preset": "fade_black",
            "duration_frames": True,
        },
    ],
)
def test_parser_rejects_boolean_values_masquerading_as_integers(
    command: dict[str, object],
) -> None:
    with pytest.raises(PlanContractError) as caught:
        AutoEditPlanParser().parse(_root([command]))
    assert caught.value.code is PlanErrorCode.SCHEMA_INVALID


@pytest.mark.parametrize(
    "command",
    [
        {
            "command_type": "set_clip_effects",
            "target_clip_id": "clip-1",
        },
        {
            "command_type": "set_clip_duration",
            "target_clip_id": "clip-1",
        },
        {
            "command_type": "set_clip_speed",
            "target_clip_id": "clip-1",
        },
        {
            "command_type": "set_clip_transform",
            "target_clip_id": "clip-1",
        },
        {
            "command_type": "set_clip_transition",
            "target_clip_id": "clip-1",
            "preset": "none",
        },
    ],
)
def test_parser_rejects_missing_command_fields(command: dict[str, object]) -> None:
    with pytest.raises(PlanContractError) as caught:
        AutoEditPlanParser().parse(_root([command]))
    assert caught.value.code is PlanErrorCode.SCHEMA_INVALID


@pytest.mark.parametrize(
    "command",
    [
        {
            "command_type": "set_clip_speed",
            "target_clip_id": "clip-1",
            "rate_percent": 49,
        },
        {
            "command_type": "set_clip_transform",
            "target_clip_id": "clip-1",
            "scale_percent": 201,
        },
        {
            "command_type": "set_clip_effects",
            "target_clip_id": "clip-1",
            "enter_effect": "Blur",
        },
        {
            "command_type": "set_clip_transition",
            "target_clip_id": "clip-1",
            "preset": "dissolve",
            "duration_frames": 10,
        },
        {
            "command_type": "set_clip_transition",
            "target_clip_id": "clip-1",
            "preset": "none",
            "duration_frames": 1,
        },
    ],
)
def test_parser_preserves_static_dto_policy_errors(command: dict[str, object]) -> None:
    with pytest.raises(PlanContractError) as caught:
        AutoEditPlanParser().parse(_root([command]))
    assert caught.value.code is PlanErrorCode.SEMANTIC_INVALID


def test_parser_rejects_outer_whitespace_target_ids() -> None:
    command = {
        "command_type": "set_clip_transform",
        "target_clip_id": " clip-1 ",
        "opacity_percent": 90,
    }
    with pytest.raises(PlanContractError) as caught:
        AutoEditPlanParser().parse(_root([command]))
    assert caught.value.code is PlanErrorCode.SCHEMA_INVALID


def test_parser_enforces_command_cap_before_dto_semantics() -> None:
    commands = [
        {
            "command_type": "set_clip_transform",
            "target_clip_id": f"clip-{index}",
            "opacity_percent": 90,
        }
        for index in range(MAX_W7_COMMANDS + 1)
    ]
    with pytest.raises(PlanContractError) as caught:
        AutoEditPlanParser().parse(_root(commands))
    assert caught.value.code is PlanErrorCode.SCHEMA_INVALID


def test_parser_preserves_plan_duplicate_family_and_pacing_conflict_guards() -> None:
    duplicate = [
        {
            "command_type": "set_clip_transform",
            "target_clip_id": "clip-1",
            "opacity_percent": 90,
        },
        {
            "command_type": "set_clip_transform",
            "target_clip_id": "clip-1",
            "scale_percent": 110,
        },
    ]
    pacing = [
        {
            "command_type": "set_clip_duration",
            "target_clip_id": "clip-1",
            "duration_frames": 120,
        },
        {
            "command_type": "set_clip_speed",
            "target_clip_id": "clip-1",
            "rate_percent": 110,
        },
    ]
    for commands in (duplicate, pacing):
        with pytest.raises(PlanContractError) as caught:
            AutoEditPlanParser().parse(_root(commands))
        assert caught.value.code is PlanErrorCode.SEMANTIC_INVALID


def test_w7_parser_does_not_change_w6_parser_contract() -> None:
    from ai_ngerti_geopolitik.application.ai_plan_verifier import PlanVerifier

    legacy = json.dumps(
        {
            "schema_version": 1,
            "base_project_revision": 7,
            "request_id": "REQ-W6",
            "summary": "Legacy W6 effect plan.",
            "commands": [
                {
                    "command_type": "set_clip_effects",
                    "target_clip_id": "clip-1",
                    "enter_effect": "Rise",
                }
            ],
        }
    )
    assert PlanVerifier().parse(legacy).schema_version == 1
