from __future__ import annotations

import json
from dataclasses import replace

import pytest

from ai_ngerti_geopolitik.application.ai_contracts import (
    PlanContractError,
    PlanErrorCode,
    ProviderPlanResponse,
)
from ai_ngerti_geopolitik.application.ai_plan_verifier import (
    MAX_L1_PLAN_COMMANDS,
    PlanVerifier,
)
from ai_ngerti_geopolitik.domain import (
    Asset,
    Clip,
    ClipProperties,
    EffectProperties,
    FrameTime,
    ProjectState,
    Track,
)


def _state(*, revision: int = 7, track_locked: bool = False) -> ProjectState:
    fps = 30
    asset = Asset(
        asset_id="asset-1",
        path_ref="fixture.mp4",
        media_type="video",
        duration=FrameTime(600, fps),
        width=1920,
        height=1080,
        has_audio=True,
        fingerprint_sha256="d" * 64,
    )
    clips = (
        Clip(
            "clip-1",
            asset.asset_id,
            FrameTime(0, fps),
            FrameTime(0, fps),
            FrameTime(120, fps),
            properties=replace(
                ClipProperties(),
                effects=EffectProperties("Fade", "Drift", 80, False),
            ),
        ),
        Clip(
            "clip-2",
            asset.asset_id,
            FrameTime(120, fps),
            FrameTime(120, fps),
            FrameTime(240, fps),
            properties=replace(
                ClipProperties(),
                effects=EffectProperties("Pop", "Fade", 90, True),
            ),
        ),
        Clip(
            "clip-3",
            asset.asset_id,
            FrameTime(240, fps),
            FrameTime(240, fps),
            FrameTime(360, fps),
        ),
    )
    state = replace(
        ProjectState.create("project-w6-006", "Verifier fixture", fps),
        revision=revision,
        assets=(asset,),
        tracks=(Track("V1", "video", 0, clips=clips, locked=track_locked),),
    )
    state.validate()
    return state


def _payload(
    *,
    revision: int = 7,
    request_id: str = "REQ-006",
    commands: list[dict[str, object]] | None = None,
    **extra: object,
) -> str:
    value: dict[str, object] = {
        "schema_version": 1,
        "base_project_revision": revision,
        "request_id": request_id,
        "summary": "Use restrained render-qualified motion.",
        "commands": commands
        if commands is not None
        else [
            {
                "command_type": "set_clip_effects",
                "target_clip_id": "clip-1",
                "enter_effect": "Rise",
                "intensity_percent": 120,
            }
        ],
    }
    value.update(extra)
    return json.dumps(value)


def test_valid_plan_verifies_via_manual_w4_dry_run_without_mutating_state() -> None:
    state = _state()
    before = state.semantic_json(include_revision=True)

    verified = PlanVerifier().verify_payload(
        _payload(),
        state,
        ("clip-1",),
    )

    assert verified.plan.request_id == "REQ-006"
    assert verified.command_count == 1
    assert verified.candidate_revision == state.revision
    assert verified.candidate_semantic_hash != state.semantic_hash()
    assert state.semantic_json(include_revision=True) == before


def test_strict_parser_rejects_malformed_root_unknown_missing_and_wrong_types() -> None:
    verifier = PlanVerifier()

    cases = (
        "{",
        "[]",
        _payload(unknown_root=True),
        json.dumps(
            {
                "schema_version": 1,
                "base_project_revision": 7,
                "request_id": "REQ",
                "commands": [],
            }
        ),
        json.dumps(
            {
                "schema_version": True,
                "base_project_revision": 7,
                "request_id": "REQ",
                "summary": "x",
                "commands": [],
            }
        ),
    )
    for raw in cases:
        with pytest.raises(PlanContractError) as caught:
            verifier.parse(raw)
        assert caught.value.code is PlanErrorCode.SCHEMA_INVALID


def test_unknown_command_type_and_unknown_command_field_are_rejected() -> None:
    verifier = PlanVerifier()
    bad_type = _payload(
        commands=[
            {
                "command_type": "shell_exec",
                "target_clip_id": "clip-1",
                "enter_effect": "Fade",
            }
        ]
    )
    bad_field = _payload(
        commands=[
            {
                "command_type": "set_clip_effects",
                "target_clip_id": "clip-1",
                "enter_effect": "Fade",
                "unlock": True,
            }
        ]
    )

    for raw in (bad_type, bad_field):
        with pytest.raises(PlanContractError) as caught:
            verifier.parse(raw)
        assert caught.value.code is PlanErrorCode.SCHEMA_INVALID


def test_unknown_and_out_of_scope_targets_are_rejected() -> None:
    verifier = PlanVerifier()
    state = _state()

    unknown = _payload(
        commands=[
            {
                "command_type": "set_clip_effects",
                "target_clip_id": "clip-missing",
                "enter_effect": "Fade",
            }
        ]
    )
    with pytest.raises(PlanContractError) as caught_unknown:
        verifier.verify_payload(unknown, state, ("clip-missing",))
    assert caught_unknown.value.code is PlanErrorCode.SEMANTIC_INVALID

    with pytest.raises(PlanContractError) as caught_scope:
        verifier.verify_payload(_payload(), state, ("clip-3",))
    assert caught_scope.value.code is PlanErrorCode.SEMANTIC_INVALID


def test_unsupported_effect_out_of_range_and_non_integer_intensity_are_rejected() -> None:
    verifier = PlanVerifier()

    cases = (
        _payload(
            commands=[
                {
                    "command_type": "set_clip_effects",
                    "target_clip_id": "clip-1",
                    "enter_effect": "Wipe",
                }
            ]
        ),
        _payload(
            commands=[
                {
                    "command_type": "set_clip_effects",
                    "target_clip_id": "clip-1",
                    "intensity_percent": 201,
                }
            ]
        ),
    )
    for raw in cases:
        with pytest.raises(PlanContractError) as caught:
            verifier.parse(raw)
        assert caught.value.code is PlanErrorCode.SEMANTIC_INVALID

    non_integer = _payload(
        commands=[
            {
                "command_type": "set_clip_effects",
                "target_clip_id": "clip-1",
                "intensity_percent": True,
            }
        ]
    )
    with pytest.raises(PlanContractError) as caught_type:
        verifier.parse(non_integer)
    assert caught_type.value.code is PlanErrorCode.SCHEMA_INVALID


def test_effect_lock_rejects_plan_without_unlocking_or_mutating() -> None:
    state = _state()
    before = state.semantic_json(include_revision=True)
    raw = _payload(
        commands=[
            {
                "command_type": "set_clip_effects",
                "target_clip_id": "clip-2",
                "exit_effect": "Rise",
            }
        ]
    )

    with pytest.raises(PlanContractError) as caught:
        PlanVerifier().verify_payload(raw, state, ("clip-2",))
    assert caught.value.code is PlanErrorCode.LOCK_CONFLICT
    assert state.semantic_json(include_revision=True) == before


def test_track_lock_rejects_plan_without_mutation() -> None:
    state = _state(track_locked=True)
    before = state.semantic_json(include_revision=True)

    with pytest.raises(PlanContractError) as caught:
        PlanVerifier().verify_payload(_payload(), state, ("clip-1",))
    assert caught.value.code is PlanErrorCode.LOCK_CONFLICT
    assert state.semantic_json(include_revision=True) == before


def test_stale_revision_is_rejected_before_dry_run() -> None:
    state = _state(revision=8)

    with pytest.raises(PlanContractError) as caught:
        PlanVerifier().verify_payload(_payload(revision=7), state, ("clip-1",))
    assert caught.value.code is PlanErrorCode.STALE_PLAN


def test_partial_proposal_preserves_unspecified_effect_fields_during_dry_run() -> None:
    state = _state()
    raw = _payload(
        commands=[
            {
                "command_type": "set_clip_effects",
                "target_clip_id": "clip-1",
                "intensity_percent": 150,
            }
        ]
    )

    verified = PlanVerifier().verify_payload(raw, state, ("clip-1",))

    assert verified.command_count == 1
    assert verified.candidate_semantic_hash != state.semantic_hash()
    original = state.clip("clip-1").properties.effects
    assert original.enter_effect == "Fade"
    assert original.exit_effect == "Drift"
    assert original.intensity_percent == 80


def test_empty_and_over_bound_command_arrays_are_rejected() -> None:
    verifier = PlanVerifier()
    empty = _payload(commands=[])
    with pytest.raises(PlanContractError) as caught_empty:
        verifier.parse(empty)
    assert caught_empty.value.code is PlanErrorCode.SCHEMA_INVALID

    commands = [
        {
            "command_type": "set_clip_effects",
            "target_clip_id": "clip-1",
            "intensity_percent": index % 201,
        }
        for index in range(MAX_L1_PLAN_COMMANDS + 1)
    ]
    with pytest.raises(PlanContractError) as caught_many:
        verifier.parse(_payload(commands=commands))
    assert caught_many.value.code is PlanErrorCode.SCHEMA_INVALID


def test_response_request_id_must_match_inner_edit_plan_request_id() -> None:
    response = ProviderPlanResponse(
        request_id="REQ-OUTER",
        payload_json=_payload(request_id="REQ-INNER"),
    )

    with pytest.raises(PlanContractError) as caught:
        PlanVerifier().verify_response(response, _state(), ("clip-1",))
    assert caught.value.code is PlanErrorCode.SEMANTIC_INVALID


def test_sequential_commands_dry_run_in_order_and_never_touch_command_bus_history() -> None:
    state = _state()
    before = state.semantic_json(include_revision=True)
    raw = _payload(
        commands=[
            {
                "command_type": "set_clip_effects",
                "target_clip_id": "clip-1",
                "enter_effect": "Rise",
            },
            {
                "command_type": "set_clip_effects",
                "target_clip_id": "clip-1",
                "exit_effect": "Tumble",
                "intensity_percent": 110,
            },
        ]
    )

    verified = PlanVerifier().verify_payload(raw, state, ("clip-1",))

    assert verified.command_count == 2
    assert verified.candidate_revision == state.revision
    assert verified.candidate_semantic_hash != state.semantic_hash()
    assert state.semantic_json(include_revision=True) == before
