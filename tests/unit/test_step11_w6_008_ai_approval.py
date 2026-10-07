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
    AIProviderRequest,
    CredentialSecret,
    PlanContractError,
    PlanErrorCode,
    ProviderPlanResponse,
)
from ai_ngerti_geopolitik.application.ai_jobs import AIPlanJobService
from ai_ngerti_geopolitik.application.commands import (
    CommandBatch,
    CommandBus,
    SetClipPropertiesCommand,
)
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
    def request_plan(
        self,
        request: AIProviderRequest,
        credential: CredentialSecret,
        cancellation=None,
    ) -> ProviderPlanResponse:
        del credential, cancellation
        return ProviderPlanResponse(
            request.request_id,
            _payload(request.request_id, request.base_project_revision),
        )


def _state() -> ProjectState:
    fps = 30
    asset = Asset(
        "asset-1",
        "fixture.mp4",
        "video",
        FrameTime(600, fps),
        1920,
        1080,
        True,
        "a" * 64,
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
                effects=EffectProperties("Pop", "Fade", 90, False),
            ),
        ),
    )
    state = replace(
        ProjectState.create("project-w6-008", "Approval fixture", fps),
        revision=14,
        assets=(asset,),
        tracks=(Track("V1", "video", 0, clips=clips),),
    )
    state.validate()
    return state


def _payload(request_id: str = "REQ-008", revision: int = 14) -> str:
    return json.dumps(
        {
            "schema_version": 1,
            "base_project_revision": revision,
            "request_id": request_id,
            "summary": "Apply two restrained L1 effect changes.",
            "commands": [
                {
                    "command_type": "set_clip_effects",
                    "target_clip_id": "clip-1",
                    "enter_effect": "Rise",
                },
                {
                    "command_type": "set_clip_effects",
                    "target_clip_id": "clip-2",
                    "exit_effect": "Tumble",
                    "intensity_percent": 115,
                },
            ],
        }
    )


def _request(request_id: str = "REQ-008", revision: int = 14) -> AIProviderRequest:
    return AIProviderRequest(
        request_id,
        revision,
        "Use restrained L1 motion.",
        '{"selected_scope":{"clip_ids":["clip-1","clip-2"]}}',
    )


def _jobs_and_bus() -> tuple[AIPlanJobService, CommandBus]:
    backend = InMemoryCredentialStore()
    slots = CredentialSlotService(backend, backend)
    slots.add_or_update(1, CredentialSecret("runtime-approval-value"), label="Gemini 1")
    pool = CredentialPoolService(slots, backend)
    return AIPlanJobService(_Provider(), pool), CommandBus(_state())


def _wait(service: AIPlanJobService, job_id: str = "REQ-008") -> None:
    deadline = time.monotonic() + 3.0
    while time.monotonic() < deadline:
        state = service.snapshot(job_id).state
        if state in {AIJobState.SUCCESS, AIJobState.FAILED, AIJobState.CANCELLED}:
            assert state is AIJobState.SUCCESS
            return
        time.sleep(0.01)
    raise AssertionError("AI job did not complete")


def _stage(service: AIPlanJobService, bus: CommandBus) -> AIPlanApprovalService:
    service.submit(
        _request(),
        bus.state,
        ("clip-1", "clip-2"),
        session_id="session-A",
    )
    _wait(service)
    approvals = AIPlanApprovalService(service, bus)
    snapshot = approvals.stage_from_job("REQ-008", session_id="session-A")
    assert snapshot.state is AIApprovalState.PENDING
    return approvals


def test_staging_verified_job_is_non_mutating_and_one_consume_only() -> None:
    jobs, bus = _jobs_and_bus()
    before = bus.state.semantic_json(include_revision=True)
    try:
        approvals = _stage(jobs, bus)
        assert approvals.snapshot("AI-APPROVAL:REQ-008").command_count == 2
        assert bus.state.semantic_json(include_revision=True) == before
        with pytest.raises(AIApprovalError, match="already staged"):
            approvals.stage_from_job("REQ-008", session_id="session-A")
    finally:
        jobs.shutdown()


def test_apply_without_explicit_approval_is_rejected_without_mutation() -> None:
    jobs, bus = _jobs_and_bus()
    before = bus.state.semantic_json(include_revision=True)
    try:
        approvals = _stage(jobs, bus)
        with pytest.raises(AIApprovalError, match="explicit approval"):
            approvals.apply("AI-APPROVAL:REQ-008")
        assert bus.state.semantic_json(include_revision=True) == before
        assert bus.can_undo is False
    finally:
        jobs.shutdown()


def test_reject_is_terminal_and_zero_mutation() -> None:
    jobs, bus = _jobs_and_bus()
    before = bus.state.semantic_json(include_revision=True)
    try:
        approvals = _stage(jobs, bus)
        rejected = approvals.reject("AI-APPROVAL:REQ-008")
        assert rejected.state is AIApprovalState.REJECTED
        with pytest.raises(AIApprovalError):
            approvals.apply("AI-APPROVAL:REQ-008")
        assert bus.state.semantic_json(include_revision=True) == before
        assert bus.can_undo is False
    finally:
        jobs.shutdown()


def test_cancel_after_approval_is_terminal_and_zero_mutation() -> None:
    jobs, bus = _jobs_and_bus()
    before = bus.state.semantic_json(include_revision=True)
    try:
        approvals = _stage(jobs, bus)
        approvals.approve("AI-APPROVAL:REQ-008")
        cancelled = approvals.cancel("AI-APPROVAL:REQ-008")
        assert cancelled.state is AIApprovalState.CANCELLED
        with pytest.raises(AIApprovalError):
            approvals.apply("AI-APPROVAL:REQ-008")
        assert bus.state.semantic_json(include_revision=True) == before
        assert bus.can_undo is False
    finally:
        jobs.shutdown()


def test_approved_plan_is_one_atomic_batch_with_exact_undo_redo_semantics() -> None:
    jobs, bus = _jobs_and_bus()
    before_hash = bus.state.semantic_hash()
    before_revision = bus.state.revision
    try:
        approvals = _stage(jobs, bus)
        approved = approvals.approve("AI-APPROVAL:REQ-008")
        assert approved.state is AIApprovalState.APPROVED
        applied = approvals.apply("AI-APPROVAL:REQ-008")

        assert applied.state is AIApprovalState.APPLIED
        assert applied.batch_id == "AI-BATCH:REQ-008"
        assert applied.applied_revision == before_revision + 1
        assert bus.state.clip("clip-1").properties.effects.enter_effect == "Rise"
        assert bus.state.clip("clip-1").properties.effects.exit_effect == "Drift"
        assert bus.state.clip("clip-2").properties.effects.exit_effect == "Tumble"
        assert bus.state.clip("clip-2").properties.effects.intensity_percent == 115
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


def test_duplicate_apply_is_rejected_without_second_history_entry() -> None:
    jobs, bus = _jobs_and_bus()
    try:
        approvals = _stage(jobs, bus)
        approvals.approve("AI-APPROVAL:REQ-008")
        approvals.apply("AI-APPROVAL:REQ-008")
        revision_after_first = bus.state.revision

        with pytest.raises(AIApprovalError, match="explicit approval"):
            approvals.apply("AI-APPROVAL:REQ-008")
        assert bus.state.revision == revision_after_first

        bus.undo()
        assert bus.can_undo is False
    finally:
        jobs.shutdown()


def test_revision_change_after_approval_is_stale_and_does_not_apply_ai_batch() -> None:
    jobs, bus = _jobs_and_bus()
    try:
        approvals = _stage(jobs, bus)
        approvals.approve("AI-APPROVAL:REQ-008")

        clip = bus.state.clip("clip-1")
        changed = replace(
            clip.properties,
            effects=replace(clip.properties.effects, intensity_percent=81),
        )
        bus.execute(
            CommandBatch(
                "MANUAL-1",
                "manual effect",
                "manual",
                bus.state.revision,
                (SetClipPropertiesCommand("clip-1", changed),),
            )
        )
        manual_hash = bus.state.semantic_hash()
        manual_revision = bus.state.revision

        with pytest.raises(PlanContractError) as caught:
            approvals.apply("AI-APPROVAL:REQ-008")
        assert caught.value.code is PlanErrorCode.STALE_PLAN
        assert bus.state.semantic_hash() == manual_hash
        assert bus.state.revision == manual_revision
    finally:
        jobs.shutdown()


def test_same_revision_semantic_replacement_is_also_stale() -> None:
    jobs, bus = _jobs_and_bus()
    try:
        approvals = _stage(jobs, bus)
        approvals.approve("AI-APPROVAL:REQ-008")
        current = bus.state
        clip = current.clip("clip-1")
        changed_clip = replace(
            clip,
            properties=replace(
                clip.properties,
                effects=replace(clip.properties.effects, intensity_percent=82),
            ),
        )
        track = current.track("V1")
        replacement = replace(
            current,
            tracks=(
                replace(
                    track,
                    clips=tuple(
                        changed_clip if item.clip_id == "clip-1" else item for item in track.clips
                    ),
                ),
            ),
        )
        replacement.validate()
        assert replacement.revision == current.revision
        bus.replace_loaded_state(replacement)

        with pytest.raises(PlanContractError) as caught:
            approvals.apply("AI-APPROVAL:REQ-008")
        assert caught.value.code is PlanErrorCode.STALE_PLAN
        assert bus.state.semantic_hash() == replacement.semantic_hash()
    finally:
        jobs.shutdown()


def test_plan_translation_preserves_unspecified_fields_across_sequential_commands() -> None:
    jobs, bus = _jobs_and_bus()
    try:
        jobs.submit(
            _request("REQ-SEQ"),
            bus.state,
            ("clip-1", "clip-2"),
            session_id="session-A",
        )
        _wait(jobs, "REQ-SEQ")
        approvals = AIPlanApprovalService(jobs, bus)
        staged = approvals.stage_from_job("REQ-SEQ", session_id="session-A")
        approvals.approve(staged.approval_id)
        approvals.apply(staged.approval_id)

        first = bus.state.clip("clip-1").properties.effects
        assert first.enter_effect == "Rise"
        assert first.exit_effect == "Drift"
        assert first.intensity_percent == 80
    finally:
        jobs.shutdown()
