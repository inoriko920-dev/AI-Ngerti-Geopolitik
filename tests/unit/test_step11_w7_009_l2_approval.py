from __future__ import annotations

import json
import time
from dataclasses import replace

import pytest

from ai_ngerti_geopolitik.application.ai_approval import (
    AIApprovalError,
    AIApprovalState,
    AIPlanApprovalService,
)
from ai_ngerti_geopolitik.application.ai_contracts import (
    AIJobState,
    CredentialSecret,
    L2AIProviderRequest,
    PlanContractError,
    PlanErrorCode,
    ProviderPlanResponse,
)
from ai_ngerti_geopolitik.application.ai_jobs import AIPlanJobService
from ai_ngerti_geopolitik.application.commands import CommandBus
from ai_ngerti_geopolitik.application.credential_pool import CredentialPoolService
from ai_ngerti_geopolitik.application.credential_slots import CredentialSlotService
from ai_ngerti_geopolitik.domain import (
    Asset,
    Clip,
    ClipProperties,
    EffectProperties,
    FrameTime,
    ProjectState,
    Track,
)
from ai_ngerti_geopolitik.infrastructure.in_memory_credentials import (
    InMemoryCredentialStore,
)


class _Provider:
    def request_plan(self, request, credential, cancellation=None):
        del credential, cancellation
        return ProviderPlanResponse(
            request.request_id,
            _payload(request.request_id, request.base_project_revision),
        )


def _state(*, revision: int = 31) -> ProjectState:
    fps = 30
    asset = Asset(
        "asset-w7-009",
        "fixture.mp4",
        "video",
        FrameTime(360, fps),
        1920,
        1080,
        True,
        "9" * 64,
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
        ),
    )
    state = replace(
        ProjectState.create("project-w7-009", "W7-009", fps),
        revision=revision,
        assets=(asset,),
        tracks=(Track("V1", "video", 0, clips=clips),),
    )
    state.validate()
    return state


def _payload(request_id: str = "REQ-W7-009", revision: int = 31) -> str:
    return json.dumps(
        {
            "schema_version": 2,
            "base_project_revision": revision,
            "request_id": request_id,
            "summary": "Apply one reviewed mixed Auto Edit L2 transaction.",
            "commands": [
                {
                    "command_type": "set_clip_effects",
                    "target_clip_id": "clip-1",
                    "enter_effect": "Rise",
                    "intensity_percent": 110,
                },
                {
                    "command_type": "set_clip_duration",
                    "target_clip_id": "clip-1",
                    "duration_frames": 150,
                },
                {
                    "command_type": "set_clip_transform",
                    "target_clip_id": "clip-1",
                    "scale_percent": 125,
                    "opacity_percent": 85,
                },
                {
                    "command_type": "set_clip_transition",
                    "target_clip_id": "clip-1",
                    "preset": "fade_black",
                    "duration_frames": 45,
                },
                {
                    "command_type": "set_clip_speed",
                    "target_clip_id": "clip-2",
                    "rate_percent": 200,
                },
                {
                    "command_type": "set_clip_transition",
                    "target_clip_id": "clip-2",
                    "preset": "fade_black",
                    "duration_frames": 30,
                },
            ],
        }
    )


def _request(request_id: str = "REQ-W7-009", revision: int = 31) -> L2AIProviderRequest:
    return L2AIProviderRequest(
        request_id=request_id,
        base_project_revision=revision,
        instruction="Apply bounded pacing and visual changes.",
        context_json='{"selected_scope":{"clip_ids":["clip-1","clip-2"]}}',
    )


def _jobs_and_bus() -> tuple[AIPlanJobService, CommandBus]:
    backend = InMemoryCredentialStore()
    slots = CredentialSlotService(backend, backend)
    slots.add_or_update(
        1,
        CredentialSecret("runtime-w7-009-approval"),
        label="Gemini 1",
    )
    pool = CredentialPoolService(slots, backend)
    return AIPlanJobService(_Provider(), pool), CommandBus(_state())


def _wait(service: AIPlanJobService, job_id: str = "REQ-W7-009") -> None:
    deadline = time.monotonic() + 3.0
    while time.monotonic() < deadline:
        state = service.snapshot(job_id).state
        if state in {AIJobState.SUCCESS, AIJobState.FAILED, AIJobState.CANCELLED}:
            assert state is AIJobState.SUCCESS
            return
        time.sleep(0.01)
    raise AssertionError("W7-009 AI job did not complete")


def _stage(
    jobs: AIPlanJobService,
    bus: CommandBus,
    request_id: str = "REQ-W7-009",
) -> tuple[AIPlanApprovalService, str]:
    jobs.submit(
        _request(request_id, bus.state.revision),
        bus.state,
        ("clip-1", "clip-2"),
        session_id="session-L2",
    )
    _wait(jobs, request_id)
    approvals = AIPlanApprovalService(jobs, bus)
    snapshot = approvals.stage_from_job_l2(
        request_id,
        session_id="session-L2",
    )
    assert snapshot.state is AIApprovalState.PENDING
    return approvals, snapshot.approval_id


def test_l2_staging_builds_bounded_before_after_diff_without_mutation() -> None:
    jobs, bus = _jobs_and_bus()
    before = bus.state.semantic_json(include_revision=True)
    try:
        approvals, approval_id = _stage(jobs, bus)
        diffs = approvals.diff_entries(approval_id)
        lines = approvals.diff_texts(approval_id)

        assert len(diffs) == 6
        assert len(lines) == 6
        assert all(len(line) <= 280 for line in lines)
        assert "effects[enter=Fade, intensity=80%]" in lines[0]
        assert "effects[enter=Rise, intensity=110%]" in lines[0]
        assert "duration=120f" in lines[1] and "duration=150f" in lines[1]
        assert "scale=100%" in lines[2] and "scale=125%" in lines[2]
        assert "transition=none/0f" in lines[3]
        assert "transition=fade_black/45f" in lines[3]
        assert "speed=100%, duration=120f" in lines[4]
        assert "speed=200%, duration=60f" in lines[4]
        assert bus.state.semantic_json(include_revision=True) == before
        assert bus.can_undo is False
    finally:
        jobs.shutdown()


def test_l2_apply_requires_explicit_approval_and_reject_cancel_create_no_history() -> None:
    jobs, bus = _jobs_and_bus()
    before = bus.state.semantic_json(include_revision=True)
    try:
        approvals, approval_id = _stage(jobs, bus)
        with pytest.raises(AIApprovalError, match="explicit approval"):
            approvals.apply(approval_id)
        approvals.reject(approval_id)
        assert bus.state.semantic_json(include_revision=True) == before
        assert bus.can_undo is False
    finally:
        jobs.shutdown()

    jobs, bus = _jobs_and_bus()
    before = bus.state.semantic_json(include_revision=True)
    try:
        approvals, approval_id = _stage(jobs, bus)
        approvals.approve(approval_id)
        approvals.cancel(approval_id)
        assert bus.state.semantic_json(include_revision=True) == before
        assert bus.can_undo is False
    finally:
        jobs.shutdown()


def test_l2_approved_mixed_plan_is_one_atomic_batch_with_one_undo_redo() -> None:
    jobs, bus = _jobs_and_bus()
    before_hash = bus.state.semantic_hash()
    before_revision = bus.state.revision
    try:
        approvals, approval_id = _stage(jobs, bus)
        approvals.approve(approval_id)
        applied = approvals.apply(approval_id)

        assert applied.state is AIApprovalState.APPLIED
        assert applied.batch_id == "AI-BATCH:REQ-W7-009"
        assert applied.applied_revision == before_revision + 1
        assert bus.state.revision == before_revision + 1
        assert bus.state.timeline_end_frame == 210

        clip1 = bus.state.clip("clip-1")
        clip2 = bus.state.clip("clip-2")
        assert clip1.duration_frames == 150
        assert clip1.properties.effects.enter_effect == "Rise"
        assert clip1.properties.effects.intensity_percent == 110
        assert clip1.properties.video.scale_x_percent == 125
        assert clip1.properties.video.scale_y_percent == 125
        assert clip1.properties.video.opacity_percent == 85
        assert clip1.properties.transition.preset == "fade_black"
        assert clip1.properties.transition.duration_frames == 45
        assert clip2.timeline_start.frames == 150
        assert clip2.duration_frames == 60
        assert clip2.properties.speed.rate_percent == 200
        assert clip2.properties.transition.duration_frames == 30

        applied_hash = bus.state.semantic_hash()
        assert applied_hash != before_hash
        assert bus.can_undo is True

        undone = bus.undo()
        assert undone.semantic_hash() == before_hash
        assert bus.can_undo is False
        assert bus.can_redo is True

        redone = bus.redo()
        assert redone.semantic_hash() == applied_hash
        assert bus.can_redo is False
    finally:
        jobs.shutdown()


def test_l2_duplicate_apply_is_rejected_without_second_history_entry() -> None:
    jobs, bus = _jobs_and_bus()
    try:
        approvals, approval_id = _stage(jobs, bus)
        approvals.approve(approval_id)
        approvals.apply(approval_id)
        revision_after_first = bus.state.revision

        with pytest.raises(AIApprovalError, match="explicit approval"):
            approvals.apply(approval_id)
        assert bus.state.revision == revision_after_first
        bus.undo()
        assert bus.can_undo is False
    finally:
        jobs.shutdown()


def test_l2_same_revision_semantic_replacement_is_stale_before_apply() -> None:
    jobs, bus = _jobs_and_bus()
    try:
        approvals, approval_id = _stage(jobs, bus)
        approvals.approve(approval_id)

        current = bus.state
        clip = current.clip("clip-1")
        changed_clip = replace(
            clip,
            properties=replace(
                clip.properties,
                effects=replace(clip.properties.effects, intensity_percent=81),
            ),
        )
        track = current.track("V1")
        replacement = replace(
            current,
            tracks=(
                replace(
                    track,
                    clips=tuple(
                        changed_clip if item.clip_id == "clip-1" else item
                        for item in track.clips
                    ),
                ),
            ),
        )
        replacement.validate()
        assert replacement.revision == current.revision
        bus.replace_loaded_state(replacement)

        with pytest.raises(PlanContractError) as caught:
            approvals.apply(approval_id)
        assert caught.value.code is PlanErrorCode.STALE_PLAN
        assert bus.state.semantic_hash() == replacement.semantic_hash()
        assert bus.can_undo is False
    finally:
        jobs.shutdown()
