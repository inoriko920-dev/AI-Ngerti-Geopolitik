from __future__ import annotations

from dataclasses import replace

from ai_ngerti_geopolitik.application.ai_l2_contracts import (
    AutoEditPlan,
    DurationEditProposal,
    SpeedEditProposal,
)
from ai_ngerti_geopolitik.application.ai_l2_scope import W7SelectedScope
from ai_ngerti_geopolitik.application.ai_l2_verifier import AutoEditPlanVerifier
from ai_ngerti_geopolitik.application.commands import (
    CommandBus,
    SetClipDurationCommand,
    SetClipSpeedCommand,
)
from ai_ngerti_geopolitik.domain import Asset, Clip, FrameTime, ProjectState, Track


def _state(*, revision: int = 91) -> ProjectState:
    fps = 30
    asset = Asset(
        "asset-w7-005",
        "fixture.mp4",
        "video",
        FrameTime(300, fps),
        1920,
        1080,
        True,
        "5" * 64,
    )
    clips = tuple(
        Clip(
            f"clip-{index + 1}",
            asset.asset_id,
            FrameTime(index * 60, fps),
            FrameTime(index * 60, fps),
            FrameTime((index + 1) * 60, fps),
        )
        for index in range(3)
    )
    state = replace(
        ProjectState.create("project-w7-005", "W7 pacing fixture", fps),
        revision=revision,
        assets=(asset,),
        tracks=(Track("V1", "video", 0, clips=clips),),
    )
    state.validate()
    return state


def _plan(command, *, request_id: str = "REQ-W7-005") -> AutoEditPlan:
    return AutoEditPlan(
        2,
        91,
        request_id,
        "Qualify bounded pacing.",
        (command,),
    )


def _verify(command):
    state = _state()
    verified = AutoEditPlanVerifier().verify(
        _plan(command),
        state,
        W7SelectedScope(("clip-1",)),
    )
    translated = verified.translated_commands[0]
    candidate = translated.apply(state)
    candidate.validate()
    return state, verified, translated, candidate


def test_duration_150_percent_extends_source_and_ripples_following_clips() -> None:
    state, verified, command, candidate = _verify(DurationEditProposal("clip-1", 90))

    assert isinstance(command, SetClipDurationCommand)
    assert command.ripple is True
    assert state.clip("clip-1").duration_frames == 60
    assert candidate.clip("clip-1").duration_frames == 90
    assert candidate.clip("clip-1").source_out.frames == 90
    assert candidate.clip("clip-2").timeline_start.frames == 90
    assert candidate.clip("clip-3").timeline_start.frames == 150
    assert candidate.timeline_end_frame == 210
    assert verified.candidate_semantic_hash == candidate.semantic_hash()
    assert state.timeline_end_frame == 180


def test_duration_50_percent_shrinks_and_ripples_without_touching_speed() -> None:
    state, verified, command, candidate = _verify(DurationEditProposal("clip-1", 30))

    assert isinstance(command, SetClipDurationCommand)
    assert candidate.clip("clip-1").duration_frames == 30
    assert candidate.clip("clip-1").properties.speed.rate_percent == 100
    assert candidate.clip("clip-2").timeline_start.frames == 30
    assert candidate.clip("clip-3").timeline_start.frames == 90
    assert candidate.timeline_end_frame == 150
    assert verified.candidate_semantic_hash == candidate.semantic_hash()
    assert state.semantic_hash() != candidate.semantic_hash()


def test_speed_200_percent_halves_timeline_duration_and_ripples() -> None:
    state, verified, command, candidate = _verify(SpeedEditProposal("clip-1", 200))

    assert isinstance(command, SetClipSpeedCommand)
    assert command.ripple is True
    assert candidate.clip("clip-1").source_out.frames == 60
    assert candidate.clip("clip-1").properties.speed.rate_percent == 200
    assert candidate.clip("clip-1").duration_frames == 30
    assert candidate.clip("clip-2").timeline_start.frames == 30
    assert candidate.clip("clip-3").timeline_start.frames == 90
    assert candidate.timeline_end_frame == 150
    assert verified.candidate_semantic_hash == candidate.semantic_hash()
    assert state.timeline_end_frame == 180


def test_speed_50_percent_doubles_timeline_duration_and_ripples() -> None:
    _state_before, verified, command, candidate = _verify(SpeedEditProposal("clip-1", 50))

    assert isinstance(command, SetClipSpeedCommand)
    assert command.ripple is True
    assert candidate.clip("clip-1").source_out.frames == 60
    assert candidate.clip("clip-1").properties.speed.rate_percent == 50
    assert candidate.clip("clip-1").duration_frames == 120
    assert candidate.clip("clip-2").timeline_start.frames == 120
    assert candidate.clip("clip-3").timeline_start.frames == 180
    assert candidate.timeline_end_frame == 240
    assert verified.candidate_semantic_hash == candidate.semantic_hash()


def test_speed_candidate_maps_timeline_offsets_to_expected_source_frames() -> None:
    state = _state()
    baseline = state.clip("clip-1")
    fast = _verify(SpeedEditProposal("clip-1", 200))[3].clip("clip-1")
    slow = _verify(SpeedEditProposal("clip-1", 50))[3].clip("clip-1")

    assert baseline.source_frame_at_timeline_offset(15) == 15
    assert fast.source_frame_at_timeline_offset(15) == 30
    assert slow.source_frame_at_timeline_offset(15) == 7


def test_pacing_qualification_dry_run_does_not_create_commandbus_history() -> None:
    state = _state()
    before = state.semantic_json(include_revision=True)
    bus = CommandBus(state)

    verified = AutoEditPlanVerifier().verify(
        _plan(DurationEditProposal("clip-1", 90)),
        state,
        W7SelectedScope(("clip-1",)),
    )
    candidate = verified.translated_commands[0].apply(state)

    assert candidate.revision == state.revision
    assert candidate.semantic_hash() == verified.candidate_semantic_hash
    assert state.semantic_json(include_revision=True) == before
    assert bus.state.semantic_json(include_revision=True) == before
    assert bus.can_undo is False
    assert bus.can_redo is False
