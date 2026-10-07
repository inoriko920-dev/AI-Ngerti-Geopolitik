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
    AIProviderRequest,
    CredentialErrorCode,
    CredentialSecret,
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
        request: AIProviderRequest,
        credential: CredentialSecret,
        cancellation=None,
    ) -> ProviderPlanResponse:
        del request, credential, cancellation
        self.calls += 1
        if isinstance(self.outcome, ProviderContractError):
            raise self.outcome
        return self.outcome


def _state(*, locked: bool = False) -> ProjectState:
    fps = 30
    asset = Asset(
        "asset-closure",
        "fixture.mp4",
        "video",
        FrameTime(300, fps),
        1920,
        1080,
        True,
        "c" * 64,
    )
    clip = Clip(
        "clip-closure",
        asset.asset_id,
        FrameTime(0, fps),
        FrameTime(0, fps),
        FrameTime(120, fps),
        properties=replace(
            ClipProperties(),
            effects=EffectProperties("Fade", "Drift", 80, locked),
        ),
    )
    state = replace(
        ProjectState.create("project-w6-010", "W6-010 closure", fps),
        revision=41,
        assets=(asset,),
        tracks=(Track("V1", "video", 0, clips=(clip,)),),
    )
    state.validate()
    return state


def _payload(
    request_id: str = "REQ-CLOSURE",
    *,
    revision: int = 41,
    enter_effect: str = "Rise",
) -> str:
    return json.dumps(
        {
            "schema_version": 1,
            "base_project_revision": revision,
            "request_id": request_id,
            "summary": "Apply one qualified L1 effect.",
            "commands": [
                {
                    "command_type": "set_clip_effects",
                    "target_clip_id": "clip-closure",
                    "enter_effect": enter_effect,
                    "intensity_percent": 120,
                }
            ],
        }
    )


def _request(
    request_id: str = "REQ-CLOSURE",
    *,
    revision: int = 41,
) -> AIProviderRequest:
    return AIProviderRequest(
        request_id,
        revision,
        "Set the selected clip enter effect to Rise with intensity 120.",
        '{"selected_scope":{"clip_ids":["clip-closure"]}}',
    )


def _pool(
    *values: str,
) -> tuple[CredentialPoolService, CredentialSlotService]:
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
    job_id: str = "REQ-CLOSURE",
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
    raise AssertionError("W6-010 job did not reach a terminal state")


def test_w6_010_valid_chain_is_atomic_and_exact_undo_redo() -> None:
    state = _state()
    bus = CommandBus(state)
    before_hash = bus.state.semantic_hash()
    before_revision = bus.state.revision
    pool, _slots = _pool("runtime-closure-value")
    provider = _Provider(
        ProviderPlanResponse(
            "REQ-CLOSURE",
            _payload(),
        )
    )

    with AIPlanJobService(provider, pool) as jobs:
        jobs.submit(
            _request(),
            bus.state,
            ("clip-closure",),
            session_id="closure-session",
        )
        assert _wait(jobs).state is AIJobState.SUCCESS
        approvals = AIPlanApprovalService(jobs, bus)
        staged = approvals.stage_from_job(
            "REQ-CLOSURE",
            session_id="closure-session",
        )
        assert staged.state is AIApprovalState.PENDING
        approvals.approve(staged.approval_id)
        applied = approvals.apply(staged.approval_id)

    assert applied.state is AIApprovalState.APPLIED
    assert provider.calls == 1
    assert bus.state.revision == before_revision + 1
    assert bus.state.clip("clip-closure").properties.effects.enter_effect == "Rise"
    applied_hash = bus.state.semantic_hash()
    assert applied_hash != before_hash
    assert bus.undo().semantic_hash() == before_hash
    assert bus.redo().semantic_hash() == applied_hash


def test_w6_010_invalid_auth_exhaustion_is_zero_mutation() -> None:
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
            ("clip-closure",),
            session_id="closure-session",
        )
        terminal = _wait(jobs)

    assert terminal.state is AIJobState.FAILED
    assert terminal.credential_error is CredentialErrorCode.ALL_SLOTS_UNAVAILABLE
    assert slots.get(1).enabled is False
    assert state.semantic_json(include_revision=True) == before


def test_w6_010_quota_stops_rotation_and_is_zero_mutation() -> None:
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
            ("clip-closure",),
            session_id="closure-session",
        )
        terminal = _wait(jobs)

    assert terminal.state is AIJobState.FAILED
    assert terminal.provider_error is ProviderErrorCode.RATE_LIMIT_OR_QUOTA
    assert provider.calls == 1
    assert slots.get(2).enabled is True
    assert state.semantic_json(include_revision=True) == before


def test_w6_010_malformed_response_is_zero_mutation() -> None:
    state = _state()
    before = state.semantic_json(include_revision=True)
    pool, _slots = _pool("runtime-malformed")
    provider = _Provider(
        ProviderPlanResponse(
            "REQ-CLOSURE",
            '{"schema_version":1}',
        )
    )

    with AIPlanJobService(provider, pool) as jobs:
        jobs.submit(
            _request(),
            state,
            ("clip-closure",),
            session_id="closure-session",
        )
        terminal = _wait(jobs)

    assert terminal.state is AIJobState.FAILED
    assert terminal.plan_error is PlanErrorCode.SCHEMA_INVALID
    assert state.semantic_json(include_revision=True) == before


def test_w6_010_lock_conflict_is_zero_mutation() -> None:
    state = _state(locked=True)
    before = state.semantic_json(include_revision=True)
    pool, _slots = _pool("runtime-lock")
    provider = _Provider(
        ProviderPlanResponse(
            "REQ-CLOSURE",
            _payload(),
        )
    )

    with AIPlanJobService(provider, pool) as jobs:
        jobs.submit(
            _request(),
            state,
            ("clip-closure",),
            session_id="closure-session",
        )
        terminal = _wait(jobs)

    assert terminal.state is AIJobState.FAILED
    assert terminal.plan_error is PlanErrorCode.LOCK_CONFLICT
    assert state.semantic_json(include_revision=True) == before


def test_w6_010_stale_after_plan_never_applies_ai_batch() -> None:
    state = _state()
    bus = CommandBus(state)
    pool, _slots = _pool("runtime-stale")
    provider = _Provider(
        ProviderPlanResponse(
            "REQ-CLOSURE",
            _payload(),
        )
    )

    with AIPlanJobService(provider, pool) as jobs:
        jobs.submit(
            _request(),
            bus.state,
            ("clip-closure",),
            session_id="closure-session",
        )
        assert _wait(jobs).state is AIJobState.SUCCESS

        clip = bus.state.clip("clip-closure")
        manual = replace(
            clip.properties,
            effects=replace(
                clip.properties.effects,
                intensity_percent=81,
            ),
        )
        bus.execute(
            CommandBatch(
                "MANUAL-W6-010",
                "manual concurrent edit",
                "manual",
                bus.state.revision,
                (SetClipPropertiesCommand("clip-closure", manual),),
            )
        )
        manual_hash = bus.state.semantic_hash()

        approvals = AIPlanApprovalService(jobs, bus)
        with pytest.raises(PlanContractError) as caught:
            approvals.stage_from_job(
                "REQ-CLOSURE",
                session_id="closure-session",
            )

    assert caught.value.code is PlanErrorCode.STALE_PLAN
    assert bus.state.semantic_hash() == manual_hash
    assert bus.can_undo is True
