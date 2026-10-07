from __future__ import annotations

from dataclasses import replace

import pytest

from ai_ngerti_geopolitik.application.ai_contracts import (
    EffectEditProposal,
    PlanContractError,
    PlanErrorCode,
)
from ai_ngerti_geopolitik.application.ai_l2_contracts import (
    AutoEditPlan,
    DurationEditProposal,
    SpeedEditProposal,
    TransformEditProposal,
    TransitionEditProposal,
)
from ai_ngerti_geopolitik.application.ai_l2_scope import W7SelectedScope
from ai_ngerti_geopolitik.application.ai_l2_verifier import AutoEditPlanVerifier
from ai_ngerti_geopolitik.application.commands import (
    CommandBus,
    SetClipDurationCommand,
    SetClipPropertiesCommand,
    SetClipSpeedCommand,
)
from ai_ngerti_geopolitik.domain import (
    Asset,
    Clip,
    FrameTime,
    ProjectState,
    Track,
    TransitionProperties,
)
from ai_ngerti_geopolitik.infrastructure.ffmpeg_creative import build_w4_creative_plan
from ai_ngerti_geopolitik.infrastructure.ffmpeg_properties import build_w3_filter_plan


def _state(*, revision: int = 107) -> ProjectState:
    fps = 30
    asset = Asset(
        "asset-w7-007",
        "fixture.mp4",
        "video",
        FrameTime(300, fps),
        1920,
        1080,
        True,
        "7" * 64,
    )
    clips = (
        Clip(
            "clip-1",
            asset.asset_id,
            FrameTime(0, fps),
            FrameTime(0, fps),
            FrameTime(120, fps),
        ),
        Clip(
            "clip-2",
            asset.asset_id,
            FrameTime(120, fps),
            FrameTime(120, fps),
            FrameTime(240, fps),
        ),
    )
    state = replace(
        ProjectState.create("project-w7-007", "W7 transition mixed fixture", fps),
        revision=revision,
        assets=(asset,),
        tracks=(Track("V1", "video", 0, clips=clips),),
    )
    state.validate()
    return state


def _apply_verified(state: ProjectState, verified):
    candidate = state
    for command in verified.translated_commands:
        candidate = command.apply(candidate)
        candidate.validate()
    return candidate


def test_fade_black_transition_uses_canonical_manual_owner_and_render_mapping() -> None:
    state = _state()
    verified = AutoEditPlanVerifier().verify(
        AutoEditPlan(
            2,
            state.revision,
            "REQ-W7-007-TRANSITION",
            "Qualify bounded fade-through-black.",
            (TransitionEditProposal("clip-1", "fade_black", 30),),
        ),
        state,
        W7SelectedScope(("clip-1",)),
    )
    command = verified.translated_commands[0]
    assert isinstance(command, SetClipPropertiesCommand)
    candidate = command.apply(state)
    transition = candidate.clip("clip-1").properties.transition
    assert transition == TransitionProperties("fade_black", 30)
    assert candidate.semantic_hash() == verified.candidate_semantic_hash

    base = build_w3_filter_plan(candidate.clip("clip-1"), state.fps)
    creative = build_w4_creative_plan(
        candidate.clip("clip-1"),
        state.fps,
        base_x=base.overlay_x,
        base_y=base.overlay_y,
    )
    fades = tuple(item for item in creative.post_filters if item.startswith("fade=t="))
    assert len(fades) == 2
    assert all("color=black" in item for item in fades)


def test_none_transition_clears_existing_fade_black() -> None:
    state = _state()
    clip = state.clip("clip-1")
    faded = replace(
        clip,
        properties=replace(
            clip.properties,
            transition=TransitionProperties("fade_black", 30),
        ),
    )
    track = state.track("V1")
    state = replace(
        state,
        tracks=(
            replace(
                track,
                clips=tuple(faded if item.clip_id == "clip-1" else item for item in track.clips),
            ),
        ),
    )
    state.validate()

    verified = AutoEditPlanVerifier().verify(
        AutoEditPlan(
            2,
            state.revision,
            "REQ-W7-007-NONE",
            "Clear transition.",
            (TransitionEditProposal("clip-1", "none", 0),),
        ),
        state,
        W7SelectedScope(("clip-1",)),
    )
    candidate = _apply_verified(state, verified)
    assert candidate.clip("clip-1").properties.transition == TransitionProperties()


def test_transition_bound_uses_candidate_duration_after_prior_speed_change() -> None:
    state = _state()
    scope = W7SelectedScope(("clip-2",))
    passing = AutoEditPlan(
        2,
        state.revision,
        "REQ-W7-007-SEQUENTIAL-PASS",
        "Speed then transition at exact candidate half-duration.",
        (
            SpeedEditProposal("clip-2", 200),
            TransitionEditProposal("clip-2", "fade_black", 30),
        ),
    )
    verified = AutoEditPlanVerifier().verify(passing, state, scope)
    candidate = _apply_verified(state, verified)
    assert candidate.clip("clip-2").duration_frames == 60
    assert candidate.clip("clip-2").properties.transition.duration_frames == 30

    failing = AutoEditPlan(
        2,
        state.revision,
        "REQ-W7-007-SEQUENTIAL-FAIL",
        "Reject transition beyond candidate half-duration.",
        (
            SpeedEditProposal("clip-2", 200),
            TransitionEditProposal("clip-2", "fade_black", 31),
        ),
    )
    with pytest.raises(PlanContractError) as caught:
        AutoEditPlanVerifier().verify(failing, state, scope)
    assert caught.value.code is PlanErrorCode.SEMANTIC_INVALID


def test_mixed_l1_l2_plan_uses_all_canonical_manual_paths_sequentially() -> None:
    state = _state()
    plan = AutoEditPlan(
        2,
        state.revision,
        "REQ-W7-007-MIXED",
        "Mixed L1/L2 qualification.",
        (
            EffectEditProposal(
                "clip-1",
                enter_effect="Rise",
                exit_effect="Fade",
                intensity_percent=110,
            ),
            DurationEditProposal("clip-1", 150),
            TransformEditProposal(
                "clip-1",
                position_x=180,
                position_y=-90,
                scale_percent=125,
                rotation_tenths=100,
                opacity_percent=80,
            ),
            TransitionEditProposal("clip-1", "fade_black", 45),
            SpeedEditProposal("clip-2", 200),
            TransitionEditProposal("clip-2", "fade_black", 30),
        ),
    )
    verified = AutoEditPlanVerifier().verify(
        plan,
        state,
        W7SelectedScope(("clip-1", "clip-2")),
    )
    assert verified.translated_command_types == (
        "SetClipPropertiesCommand",
        "SetClipDurationCommand",
        "SetClipPropertiesCommand",
        "SetClipPropertiesCommand",
        "SetClipSpeedCommand",
        "SetClipPropertiesCommand",
    )
    assert isinstance(verified.translated_commands[0], SetClipPropertiesCommand)
    assert isinstance(verified.translated_commands[1], SetClipDurationCommand)
    assert isinstance(verified.translated_commands[4], SetClipSpeedCommand)

    candidate = _apply_verified(state, verified)
    assert candidate.semantic_hash() == verified.candidate_semantic_hash
    assert candidate.revision == state.revision
    assert candidate.timeline_end_frame == 210

    clip1 = candidate.clip("clip-1")
    clip2 = candidate.clip("clip-2")
    assert clip1.duration_frames == 150
    assert clip1.properties.effects.enter_effect == "Rise"
    assert clip1.properties.effects.exit_effect == "Fade"
    assert clip1.properties.effects.intensity_percent == 110
    assert clip1.properties.video.scale_x_percent == 125
    assert clip1.properties.video.scale_y_percent == 125
    assert clip1.properties.transition == TransitionProperties("fade_black", 45)
    assert clip2.timeline_start.frames == 150
    assert clip2.duration_frames == 60
    assert clip2.properties.speed.rate_percent == 200
    assert clip2.properties.transition == TransitionProperties("fade_black", 30)


def test_mixed_plan_qualification_is_dry_run_without_commandbus_history() -> None:
    state = _state()
    before = state.semantic_json(include_revision=True)
    bus = CommandBus(state)
    verified = AutoEditPlanVerifier().verify(
        AutoEditPlan(
            2,
            state.revision,
            "REQ-W7-007-DRY",
            "Dry-run mixed L1/L2 plan.",
            (
                EffectEditProposal("clip-1", enter_effect="Pan"),
                TransformEditProposal("clip-1", opacity_percent=85),
                TransitionEditProposal("clip-1", "fade_black", 20),
                SpeedEditProposal("clip-2", 150),
            ),
        ),
        state,
        W7SelectedScope(("clip-1", "clip-2")),
    )
    candidate = _apply_verified(state, verified)
    assert candidate.semantic_hash() == verified.candidate_semantic_hash
    assert state.semantic_json(include_revision=True) == before
    assert bus.state.semantic_json(include_revision=True) == before
    assert bus.can_undo is False
    assert bus.can_redo is False
