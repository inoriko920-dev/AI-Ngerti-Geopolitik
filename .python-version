from __future__ import annotations

from dataclasses import replace

from ai_ngerti_geopolitik.application.ai_l2_contracts import AutoEditPlan, TransformEditProposal
from ai_ngerti_geopolitik.application.ai_l2_scope import W7SelectedScope
from ai_ngerti_geopolitik.application.ai_l2_verifier import AutoEditPlanVerifier
from ai_ngerti_geopolitik.application.commands import CommandBus, SetClipPropertiesCommand
from ai_ngerti_geopolitik.domain import (
    Asset,
    Clip,
    ClipProperties,
    FrameTime,
    ProjectState,
    Track,
    VideoProperties,
)


def _state(*, revision: int = 106) -> ProjectState:
    fps = 30
    asset = Asset(
        "asset-w7-006",
        "fixture.mp4",
        "video",
        FrameTime(300, fps),
        1920,
        1080,
        True,
        "6" * 64,
    )
    properties = replace(
        ClipProperties(),
        video=VideoProperties(
            position_x=10,
            position_y=-5,
            scale_x_percent=100,
            scale_y_percent=100,
            rotation_tenths=0,
            opacity_percent=100,
            crop_left_percent=3,
            crop_top_percent=2,
        ),
    )
    clip = Clip(
        "clip-1",
        asset.asset_id,
        FrameTime(0, fps),
        FrameTime(0, fps),
        FrameTime(90, fps),
        properties=properties,
    )
    state = replace(
        ProjectState.create("project-w7-006", "W7 transform fixture", fps),
        revision=revision,
        assets=(asset,),
        tracks=(Track("V1", "video", 0, clips=(clip,)),),
    )
    state.validate()
    return state


def _verify(proposal: TransformEditProposal):
    state = _state()
    plan = AutoEditPlan(
        2,
        state.revision,
        "REQ-W7-006",
        "Qualify bounded transform.",
        (proposal,),
    )
    verified = AutoEditPlanVerifier().verify(
        plan,
        state,
        W7SelectedScope(("clip-1",)),
    )
    command = verified.translated_commands[0]
    candidate = command.apply(state)
    candidate.validate()
    return state, verified, command, candidate


def test_transform_all_fields_use_canonical_set_clip_properties_command() -> None:
    state, verified, command, candidate = _verify(
        TransformEditProposal(
            "clip-1",
            position_x=240,
            position_y=-120,
            scale_percent=125,
            rotation_tenths=100,
            opacity_percent=80,
        )
    )
    assert isinstance(command, SetClipPropertiesCommand)
    video = candidate.clip("clip-1").properties.video
    assert (video.position_x, video.position_y) == (240, -120)
    assert (video.scale_x_percent, video.scale_y_percent) == (125, 125)
    assert video.rotation_tenths == 100
    assert video.opacity_percent == 80
    assert verified.candidate_semantic_hash == candidate.semantic_hash()
    assert candidate.revision == state.revision


def test_transform_preserves_crop_and_unspecified_fields() -> None:
    _state_before, _verified, _command, candidate = _verify(
        TransformEditProposal("clip-1", position_x=200)
    )
    video = candidate.clip("clip-1").properties.video
    assert video.position_x == 200
    assert video.position_y == -5
    assert video.scale_x_percent == 100
    assert video.scale_y_percent == 100
    assert video.rotation_tenths == 0
    assert video.opacity_percent == 100
    assert video.crop_left_percent == 3
    assert video.crop_top_percent == 2


def test_uniform_scale_translates_to_equal_xy_scale() -> None:
    _state_before, _verified, _command, candidate = _verify(
        TransformEditProposal("clip-1", scale_percent=150)
    )
    video = candidate.clip("clip-1").properties.video
    assert video.scale_x_percent == 150
    assert video.scale_y_percent == 150


def test_transform_policy_edge_values_are_accepted() -> None:
    _state_before, verified, _command, candidate = _verify(
        TransformEditProposal(
            "clip-1",
            position_x=960,
            position_y=-540,
            scale_percent=200,
            rotation_tenths=-150,
            opacity_percent=60,
        )
    )
    assert verified.command_count == 1
    video = candidate.clip("clip-1").properties.video
    assert (video.position_x, video.position_y) == (960, -540)
    assert video.scale_x_percent == 200
    assert video.rotation_tenths == -150
    assert video.opacity_percent == 60


def test_transform_qualification_is_dry_run_without_commandbus_history() -> None:
    state = _state()
    before = state.semantic_json(include_revision=True)
    bus = CommandBus(state)
    verified = AutoEditPlanVerifier().verify(
        AutoEditPlan(
            2,
            state.revision,
            "REQ-W7-006-DRY",
            "Dry-run transform only.",
            (TransformEditProposal("clip-1", opacity_percent=75),),
        ),
        state,
        W7SelectedScope(("clip-1",)),
    )
    candidate = verified.translated_commands[0].apply(state)
    assert candidate.semantic_hash() == verified.candidate_semantic_hash
    assert state.semantic_json(include_revision=True) == before
    assert bus.state.semantic_json(include_revision=True) == before
    assert bus.can_undo is False
    assert bus.can_redo is False
