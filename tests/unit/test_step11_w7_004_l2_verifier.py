from __future__ import annotations

import json
from dataclasses import replace

import pytest

from ai_ngerti_geopolitik.application.ai_contracts import (
    EffectEditProposal,
    PlanContractError,
    PlanErrorCode,
    ProviderPlanResponse,
)
from ai_ngerti_geopolitik.application.ai_l2_contracts import (
    AutoEditPlan,
    DurationEditProposal,
    SpeedEditProposal,
    TransformEditProposal,
    TransitionEditProposal,
)
from ai_ngerti_geopolitik.application.ai_l2_scope import W7SelectedScope
from ai_ngerti_geopolitik.application.ai_l2_verifier import (
    AutoEditPlanVerifier,
)
from ai_ngerti_geopolitik.application.commands import (
    CommandBus,
    SetClipDurationCommand,
    SetClipPropertiesCommand,
    SetClipSpeedCommand,
)
from ai_ngerti_geopolitik.domain import (
    Asset,
    Clip,
    ClipProperties,
    EffectProperties,
    FrameTime,
    ProjectState,
    SpeedProperties,
    Track,
    TransitionProperties,
    VideoProperties,
)


def _state(
    *,
    revision: int = 70,
    track_locked: bool = False,
    effect_locked: bool = False,
    clip2_speed: int = 100,
    asset_frames: int = 2400,
) -> ProjectState:
    fps = 30
    asset = Asset(
        "asset-w7-004",
        "fixture.mp4",
        "video",
        FrameTime(asset_frames, fps),
        1920,
        1080,
        True,
        "4" * 64,
    )
    clips: list[Clip] = []
    starts = (0, 180, 360, 540, 720)
    for index, timeline_start in enumerate(starts):
        source_in = index * 180
        speed = clip2_speed if index == 1 else 100
        properties = replace(
            ClipProperties(),
            speed=SpeedProperties(speed),
            video=VideoProperties(
                position_x=index * 10,
                position_y=-index * 5,
                scale_x_percent=100,
                scale_y_percent=100,
                rotation_tenths=0,
                opacity_percent=100,
                crop_left_percent=3,
            ),
            transition=TransitionProperties(),
            effects=EffectProperties(
                enter_effect="Fade",
                exit_effect="Drift",
                intensity_percent=80 + index,
                locked=effect_locked if index == 0 else False,
            ),
        )
        clips.append(
            Clip(
                f"clip-{index + 1}",
                asset.asset_id,
                FrameTime(timeline_start, fps),
                FrameTime(source_in, fps),
                FrameTime(source_in + 120, fps),
                properties=properties,
            )
        )
    state = replace(
        ProjectState.create("project-w7-004", "Verifier fixture", fps),
        revision=revision,
        assets=(asset,),
        tracks=(Track("V1", "video", 0, clips=tuple(clips), locked=track_locked),),
    )
    state.validate()
    return state


def _replace_clip(state: ProjectState, clip_id: str, clip: Clip) -> ProjectState:
    track = state.track("V1")
    candidate = replace(
        state,
        tracks=(
            replace(
                track,
                clips=tuple(clip if item.clip_id == clip_id else item for item in track.clips),
            ),
        ),
    )
    candidate.validate()
    return candidate


def _plan(
    *commands,
    revision: int = 70,
    request_id: str = "REQ-W7-004",
) -> AutoEditPlan:
    return AutoEditPlan(
        2,
        revision,
        request_id,
        "Bounded semantic verification fixture.",
        tuple(commands),
    )


def _scope(*clip_ids: str) -> W7SelectedScope:
    return W7SelectedScope(tuple(clip_ids))


def test_valid_mixed_plan_translates_manual_commands_sequentially_without_mutation() -> None:
    state = _state()
    before = state.semantic_json(include_revision=True)
    bus = CommandBus(state)
    plan = _plan(
        EffectEditProposal("clip-1", enter_effect="Rise", intensity_percent=120),
        DurationEditProposal("clip-2", 180),
        SpeedEditProposal("clip-3", 150),
        TransformEditProposal("clip-4", position_x=100, scale_percent=110, opacity_percent=90),
        TransitionEditProposal("clip-5", "fade_black", 12),
    )

    verified = AutoEditPlanVerifier().verify(
        plan,
        state,
        _scope("clip-1", "clip-2", "clip-3", "clip-4", "clip-5"),
    )

    assert verified.command_count == 5
    assert verified.target_count == 5
    assert verified.selected_scope_count == 5
    assert verified.candidate_revision == state.revision
    assert verified.candidate_semantic_hash != state.semantic_hash()
    assert verified.translated_command_types == (
        "SetClipPropertiesCommand",
        "SetClipDurationCommand",
        "SetClipSpeedCommand",
        "SetClipPropertiesCommand",
        "SetClipPropertiesCommand",
    )
    assert isinstance(verified.translated_commands[1], SetClipDurationCommand)
    assert verified.translated_commands[1].ripple is True
    assert isinstance(verified.translated_commands[2], SetClipSpeedCommand)
    assert verified.translated_commands[2].ripple is True
    assert state.semantic_json(include_revision=True) == before
    assert bus.state.semantic_json(include_revision=True) == before
    assert bus.can_undo is False
    assert bus.can_redo is False


def test_selected_scope_target_and_scope_existence_are_enforced() -> None:
    state = _state()
    verifier = AutoEditPlanVerifier()
    plan = _plan(TransformEditProposal("clip-2", opacity_percent=90))

    with pytest.raises(PlanContractError) as outside:
        verifier.verify(plan, state, _scope("clip-1"))
    assert outside.value.code is PlanErrorCode.SEMANTIC_INVALID

    missing_plan = _plan(TransformEditProposal("clip-missing", opacity_percent=90))
    with pytest.raises(PlanContractError) as missing:
        verifier.verify(missing_plan, state, _scope("clip-missing"))
    assert missing.value.code is PlanErrorCode.SEMANTIC_INVALID


def test_stale_revision_rejected_before_dry_run() -> None:
    state = _state()
    plan = _plan(TransformEditProposal("clip-1", opacity_percent=90), revision=69)
    with pytest.raises(PlanContractError) as caught:
        AutoEditPlanVerifier().verify(plan, state, _scope("clip-1"))
    assert caught.value.code is PlanErrorCode.STALE_PLAN


@pytest.mark.parametrize(
    "proposal",
    [
        EffectEditProposal("clip-1", enter_effect="Rise"),
        DurationEditProposal("clip-1", 180),
        SpeedEditProposal("clip-1", 125),
        TransformEditProposal("clip-1", opacity_percent=90),
        TransitionEditProposal("clip-1", "fade_black", 12),
    ],
)
def test_track_lock_rejects_every_w7_family(proposal) -> None:
    state = _state(track_locked=True)
    with pytest.raises(PlanContractError) as caught:
        AutoEditPlanVerifier().verify(_plan(proposal), state, _scope("clip-1"))
    assert caught.value.code is PlanErrorCode.LOCK_CONFLICT


def test_effect_lock_blocks_effects_but_not_general_transform() -> None:
    state = _state(effect_locked=True)
    verifier = AutoEditPlanVerifier()
    with pytest.raises(PlanContractError) as caught:
        verifier.verify(
            _plan(EffectEditProposal("clip-1", enter_effect="Rise")),
            state,
            _scope("clip-1"),
        )
    assert caught.value.code is PlanErrorCode.LOCK_CONFLICT

    verified = verifier.verify(
        _plan(TransformEditProposal("clip-1", opacity_percent=90)),
        state,
        _scope("clip-1"),
    )
    assert verified.command_count == 1


@pytest.mark.parametrize("duration", [59, 241])
def test_duration_dynamic_ratio_policy_rejects_outside_bounds(duration: int) -> None:
    state = _state()
    with pytest.raises(PlanContractError) as caught:
        AutoEditPlanVerifier().verify(
            _plan(DurationEditProposal("clip-2", duration)),
            state,
            _scope("clip-2"),
        )
    assert caught.value.code is PlanErrorCode.SEMANTIC_INVALID


def test_duration_manual_path_rejects_source_media_overrun() -> None:
    state = _state(asset_frames=850)
    with pytest.raises(PlanContractError) as caught:
        AutoEditPlanVerifier().verify(
            _plan(DurationEditProposal("clip-5", 240)),
            state,
            _scope("clip-5"),
        )
    assert caught.value.code is PlanErrorCode.SEMANTIC_INVALID


def test_duration_manual_path_rejects_non_representable_frame_request() -> None:
    state = _state(clip2_speed=150)
    assert state.clip("clip-2").duration_frames == 80
    with pytest.raises(PlanContractError) as caught:
        AutoEditPlanVerifier().verify(
            _plan(DurationEditProposal("clip-2", 49)),
            state,
            _scope("clip-2"),
        )
    assert caught.value.code is PlanErrorCode.SEMANTIC_INVALID


@pytest.mark.parametrize(
    ("field", "value"),
    [("position_x", 961), ("position_x", -961), ("position_y", 541), ("position_y", -541)],
)
def test_transform_canvas_relative_position_policy(field: str, value: int) -> None:
    kwargs = {field: value}
    proposal = TransformEditProposal("clip-1", **kwargs)
    with pytest.raises(PlanContractError) as caught:
        AutoEditPlanVerifier().verify(_plan(proposal), _state(), _scope("clip-1"))
    assert caught.value.code is PlanErrorCode.SEMANTIC_INVALID


def test_transform_translation_preserves_crop_and_sets_uniform_scale() -> None:
    verified = AutoEditPlanVerifier().verify(
        _plan(TransformEditProposal("clip-1", scale_percent=125, position_x=200)),
        _state(),
        _scope("clip-1"),
    )
    command = verified.translated_commands[0]
    assert isinstance(command, SetClipPropertiesCommand)
    video = command.properties.video
    assert video.position_x == 200
    assert video.scale_x_percent == 125
    assert video.scale_y_percent == 125
    assert video.crop_left_percent == 3


def test_effect_translation_preserves_unspecified_fields_and_lock_value() -> None:
    verified = AutoEditPlanVerifier().verify(
        _plan(EffectEditProposal("clip-1", enter_effect="Rise")),
        _state(),
        _scope("clip-1"),
    )
    command = verified.translated_commands[0]
    assert isinstance(command, SetClipPropertiesCommand)
    effects = command.properties.effects
    assert effects.enter_effect == "Rise"
    assert effects.exit_effect == "Drift"
    assert effects.intensity_percent == 80
    assert effects.locked is False


def test_transition_uses_candidate_duration_after_prior_speed_change() -> None:
    state = _state()
    verifier = AutoEditPlanVerifier()
    passing = _plan(
        SpeedEditProposal("clip-3", 200),
        TransitionEditProposal("clip-3", "fade_black", 30),
    )
    verified = verifier.verify(passing, state, _scope("clip-3"))
    assert verified.command_count == 2

    failing = _plan(
        SpeedEditProposal("clip-3", 200),
        TransitionEditProposal("clip-3", "fade_black", 31),
    )
    with pytest.raises(PlanContractError) as caught:
        verifier.verify(failing, state, _scope("clip-3"))
    assert caught.value.code is PlanErrorCode.SEMANTIC_INVALID


def test_later_pacing_cannot_make_earlier_transition_invalid() -> None:
    state = _state()
    plan = _plan(
        TransitionEditProposal("clip-3", "fade_black", 50),
        SpeedEditProposal("clip-3", 200),
    )
    with pytest.raises(PlanContractError) as caught:
        AutoEditPlanVerifier().verify(plan, state, _scope("clip-3"))
    assert caught.value.code is PlanErrorCode.SEMANTIC_INVALID


def test_existing_transition_is_rechecked_when_pacing_changes_candidate_duration() -> None:
    state = _state()
    clip = state.clip("clip-3")
    state = _replace_clip(
        state,
        "clip-3",
        replace(
            clip,
            properties=replace(
                clip.properties,
                transition=TransitionProperties("fade_black", 50),
            ),
        ),
    )
    with pytest.raises(PlanContractError) as caught:
        AutoEditPlanVerifier().verify(
            _plan(SpeedEditProposal("clip-3", 200)),
            state,
            _scope("clip-3"),
        )
    assert caught.value.code is PlanErrorCode.SEMANTIC_INVALID


def test_verify_payload_reuses_strict_w7_parser() -> None:
    state = _state()
    raw = json.dumps(
        {
            "schema_version": 2,
            "base_project_revision": 70,
            "request_id": "REQ-PAYLOAD",
            "summary": "One safe transform.",
            "commands": [
                {
                    "command_type": "set_clip_transform",
                    "target_clip_id": "clip-1",
                    "opacity_percent": 90,
                }
            ],
        }
    )
    verified = AutoEditPlanVerifier().verify_payload(raw, state, _scope("clip-1"))
    assert verified.plan.request_id == "REQ-PAYLOAD"
    assert verified.command_count == 1


def test_verify_response_requires_outer_request_id_correlation() -> None:
    state = _state()
    raw = json.dumps(
        {
            "schema_version": 2,
            "base_project_revision": 70,
            "request_id": "INNER",
            "summary": "One safe transform.",
            "commands": [
                {
                    "command_type": "set_clip_transform",
                    "target_clip_id": "clip-1",
                    "opacity_percent": 90,
                }
            ],
        }
    )
    with pytest.raises(PlanContractError) as caught:
        AutoEditPlanVerifier().verify_response(
            ProviderPlanResponse("OUTER", raw),
            state,
            _scope("clip-1"),
        )
    assert caught.value.code is PlanErrorCode.SEMANTIC_INVALID
