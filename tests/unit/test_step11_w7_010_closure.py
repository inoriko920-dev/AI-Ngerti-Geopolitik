from __future__ import annotations

import json
import time
from dataclasses import replace

import pytest

from ai_ngerti_geopolitik.application.ai_approval import (
    AIApprovalState,
    AIPlanApprovalService,
)
from ai_ngerti_geopolitik.application.ai_contracts import (
    AIJobState,
    CredentialErrorCode,
    CredentialSecret,
    L2AIProviderRequest,
    PlanContractError,
    PlanErrorCode,
    ProviderContractError,
    ProviderErrorCode,
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
    def __init__(
        self,
        outcome: ProviderPlanResponse | ProviderContractError,
    ) -> None:
        self.outcome = outcome
        self.calls = 0

    def request_plan(
        self,
        request,
        credential: CredentialSecret,
        cancellation=None,
    ) -> ProviderPlanResponse:
        del request, credential, cancellation
        self.calls += 1
        if isinstance(self.outcome, ProviderContractError):
            raise self.outcome
        return self.outcome


def _state(*, track_locked: bool = False) -> ProjectState:
    fps = 30
    asset = Asset(
        "asset-w7-010",
        "fixture.mp4",
        "video",
        FrameTime(360, fps),
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
        ProjectState.create("project-w7-010", "W7-010 closure", fps),
        revision=51,
        assets=(asset,),
        tracks=(Track("V1", "video", 0, locked=track_locked, clips=clips),),
    )
    state.validate()
    return state


def _payload(
    request_id: str = "REQ-W7-010",
    *,
    revision: int = 51,
    commands: list[dict[str, object]] | None = None,
) -> str:
    if commands is None:
        commands = [
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
        ]
    return json.dumps(
        {
            "schema_version": 2,
            "base_project_revision": revision,
            "request_id": request_id,
            "summary": "Final bounded W7 mixed-plan closure.",
            "commands": commands,
        }
    )


def _request(
    request_id: str = "REQ-W7-010",
    *,
    revision: int = 51,
) -> L2AIProviderRequest:
    return L2AIProviderRequest(
        request_id=request_id,
        base_project_revision=revision,
        instruction="Apply the final bounded mixed L2 plan.",
        context_json='{"selected_scope":{"clip_ids":["clip-1","clip-2"]}}',
    )


def _pool(*values: str) -> tuple[CredentialPoolService, CredentialSlotService]:
    backend = InMemoryCredentialStore()
    slots = CredentialSlotService(backend, backend)
    for slot_id, value in enumerate(values, start=1):
        slots.add_or_update(
            slot_id,
            CredentialSecret(value),
            label=f"Gemini {slot_id}",
        )
    return CredentialPoolService(slots, backend), slots


def _wait(
    service: AIPlanJobService,
    job_id: str = "REQ-W7-010",
    timeout: float = 3.0,
):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        snapshot = service.snapshot(job_id)
        if snapshot.state in {
            AIJobState.SUCCESS,
            AIJobState.FAILED,
            AIJobState.CANCELLED,
        }:
            return snapshot
        time.sleep(0.01)
    raise AssertionError("W7-010 job did not reach a terminal state")


def _run(
    state: ProjectState,
    response: ProviderPlanResponse,
    *,
    allowed_targets: tuple[str, ...] = ("clip-1", "clip-2"),
) -> tuple[AIPlanJobService, CommandBus, _Provider]:
    bus = CommandBus(state)
    pool, _slots = _pool("runtime-w7-010")
    provider = _Provider(response)
    jobs = AIPlanJobService(provider, pool)
    jobs.submit(
        _request(response.request_id, revision=state.revision),
        bus.state,
        allowed_targets,
        session_id="w7-010-session",
    )
    return jobs, bus, provider


def test_w7_010_valid_chain_is_one_atomic_l2_transaction() -> None:
    response = ProviderPlanResponse("REQ-W7-010", _payload())
    jobs, bus, provider = _run(_state(), response)
    before_hash = bus.state.semantic_hash()
    before_revision = bus.state.revision
    try:
        assert _wait(jobs).state is AIJobState.SUCCESS
        approvals = AIPlanApprovalService(jobs, bus)
        staged = approvals.stage_from_job_l2(
            "REQ-W7-010",
            session_id="w7-010-session",
        )
        assert staged.state is AIApprovalState.PENDING
        assert len(approvals.diff_entries(staged.approval_id)) == 6
        approvals.approve(staged.approval_id)
        applied = approvals.apply(staged.approval_id)

        assert applied.state is AIApprovalState.APPLIED
        assert provider.calls == 1
        assert bus.state.revision == before_revision + 1
        assert bus.state.timeline_end_frame == 210
        applied_hash = bus.state.semantic_hash()
        assert applied_hash != before_hash
        assert bus.undo().semantic_hash() == before_hash
        assert bus.redo().semantic_hash() == applied_hash
    finally:
        jobs.shutdown()


def test_w7_010_invalid_schema_is_zero_mutation() -> None:
    state = _state()
    before = state.semantic_json(include_revision=True)
    response = ProviderPlanResponse(
        "REQ-W7-010",
        '{"schema_version":2,"request_id":"REQ-W7-010"}',
    )
    jobs, _bus, _provider = _run(state, response)
    try:
        terminal = _wait(jobs)
        assert terminal.state is AIJobState.FAILED
        assert terminal.plan_error is PlanErrorCode.SCHEMA_INVALID
        assert state.semantic_json(include_revision=True) == before
    finally:
        jobs.shutdown()


def test_w7_010_out_of_range_transform_is_zero_mutation() -> None:
    state = _state()
    before = state.semantic_json(include_revision=True)
    response = ProviderPlanResponse(
        "REQ-W7-010",
        _payload(
            commands=[
                {
                    "command_type": "set_clip_transform",
                    "target_clip_id": "clip-1",
                    "position_x": 2000,
                }
            ]
        ),
    )
    jobs, _bus, _provider = _run(state, response)
    try:
        terminal = _wait(jobs)
        assert terminal.state is AIJobState.FAILED
        assert terminal.plan_error is PlanErrorCode.SEMANTIC_INVALID
        assert state.semantic_json(include_revision=True) == before
    finally:
        jobs.shutdown()


def test_w7_010_out_of_scope_target_is_zero_mutation() -> None:
    state = _state()
    before = state.semantic_json(include_revision=True)
    response = ProviderPlanResponse(
        "REQ-W7-010",
        _payload(
            commands=[
                {
                    "command_type": "set_clip_effects",
                    "target_clip_id": "clip-2",
                    "enter_effect": "Rise",
                }
            ]
        ),
    )
    jobs, _bus, _provider = _run(
        state,
        response,
        allowed_targets=("clip-1",),
    )
    try:
        terminal = _wait(jobs)
        assert terminal.state is AIJobState.FAILED
        assert terminal.plan_error is PlanErrorCode.SEMANTIC_INVALID
        assert state.semantic_json(include_revision=True) == before
    finally:
        jobs.shutdown()


def test_w7_010_locked_target_is_zero_mutation() -> None:
    state = _state(track_locked=True)
    before = state.semantic_json(include_revision=True)
    response = ProviderPlanResponse(
        "REQ-W7-010",
        _payload(
            commands=[
                {
                    "command_type": "set_clip_transform",
                    "target_clip_id": "clip-1",
                    "scale_percent": 125,
                }
            ]
        ),
    )
    jobs, _bus, _provider = _run(state, response)
    try:
        terminal = _wait(jobs)
        assert terminal.state is AIJobState.FAILED
        assert terminal.plan_error is PlanErrorCode.LOCK_CONFLICT
        assert state.semantic_json(include_revision=True) == before
    finally:
        jobs.shutdown()


def test_w7_010_stale_after_provider_success_never_applies_ai_batch() -> None:
    response = ProviderPlanResponse("REQ-W7-010", _payload())
    jobs, bus, _provider = _run(_state(), response)
    try:
        assert _wait(jobs).state is AIJobState.SUCCESS

        clip = bus.state.clip("clip-1")
        changed = replace(
            clip.properties,
            effects=replace(clip.properties.effects, intensity_percent=81),
        )
        bus.execute(
            CommandBatch(
                "MANUAL-W7-010",
                "manual concurrent edit",
                "manual",
                bus.state.revision,
                (SetClipPropertiesCommand("clip-1", changed),),
            )
        )
        manual_hash = bus.state.semantic_hash()
        manual_revision = bus.state.revision

        approvals = AIPlanApprovalService(jobs, bus)
        with pytest.raises(PlanContractError) as caught:
            approvals.stage_from_job_l2(
                "REQ-W7-010",
                session_id="w7-010-session",
            )

        assert caught.value.code is PlanErrorCode.STALE_PLAN
        assert bus.state.semantic_hash() == manual_hash
        assert bus.state.revision == manual_revision
        assert bus.can_undo is True
    finally:
        jobs.shutdown()


def test_w7_010_quota_provider_failure_stops_rotation_and_is_zero_mutation() -> None:
    state = _state()
    before = state.semantic_json(include_revision=True)
    pool, slots = _pool("runtime-quota-one", "runtime-quota-two")
    provider = _Provider(
        ProviderContractError(
            ProviderErrorCode.RATE_LIMIT_OR_QUOTA,
            "quota",
        )
    )

    with AIPlanJobService(provider, pool) as jobs:
        jobs.submit(
            _request(),
            state,
            ("clip-1", "clip-2"),
            session_id="w7-010-session",
        )
        terminal = _wait(jobs)

    assert terminal.state is AIJobState.FAILED
    assert terminal.provider_error is ProviderErrorCode.RATE_LIMIT_OR_QUOTA
    assert provider.calls == 1
    assert slots.get(2).enabled is True
    assert state.semantic_json(include_revision=True) == before


def test_w7_010_invalid_auth_exhaustion_is_zero_mutation() -> None:
    state = _state()
    before = state.semantic_json(include_revision=True)
    pool, slots = _pool("runtime-invalid-auth")
    provider = _Provider(
        ProviderContractError(
            ProviderErrorCode.INVALID_AUTH,
            "invalid auth",
        )
    )

    with AIPlanJobService(provider, pool) as jobs:
        jobs.submit(
            _request(),
            state,
            ("clip-1", "clip-2"),
            session_id="w7-010-session",
        )
        terminal = _wait(jobs)

    assert terminal.state is AIJobState.FAILED
    assert terminal.credential_error is CredentialErrorCode.ALL_SLOTS_UNAVAILABLE
    assert slots.get(1).enabled is False
    assert state.semantic_json(include_revision=True) == before
