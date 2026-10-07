from __future__ import annotations

import asyncio
import json
import threading
import time
from concurrent.futures import CancelledError
from dataclasses import replace
from threading import Event

import pytest
from google.genai import types

from ai_ngerti_geopolitik.application.ai_contracts import (
    AIJobState,
    AIProviderRequest,
    AIRequestProfile,
    CredentialSecret,
    L2AIProviderRequest,
    PlanContractError,
    PlanErrorCode,
    ProviderContractError,
    ProviderErrorCode,
    ProviderPlanResponse,
)
from ai_ngerti_geopolitik.application.ai_jobs import (
    AIPlanJobAccessError,
    AIPlanJobService,
)
from ai_ngerti_geopolitik.application.ai_l2_context import L2ContextBuilder
from ai_ngerti_geopolitik.application.ai_l2_scope import W7SelectedScope
from ai_ngerti_geopolitik.application.credential_pool import CredentialPoolService
from ai_ngerti_geopolitik.application.credential_slots import CredentialSlotService
from ai_ngerti_geopolitik.domain import Asset, Clip, FrameTime, ProjectState, Track
from ai_ngerti_geopolitik.infrastructure.gemini_provider import GeminiAIProvider
from ai_ngerti_geopolitik.infrastructure.in_memory_credentials import (
    InMemoryCredentialStore,
)


class _FakeResponse:
    def __init__(self, text: str | None) -> None:
        self.text = text


class _FakeModels:
    def __init__(
        self,
        *,
        text: str | None,
        delay: float = 0.0,
    ) -> None:
        self.text = text
        self.delay = delay
        self.calls: list[dict[str, object]] = []

    async def generate_content(
        self,
        *,
        model: str,
        contents: str,
        config: object,
    ) -> object:
        self.calls.append(
            {
                "model": model,
                "contents": contents,
                "config": config,
            }
        )
        if self.delay:
            await asyncio.sleep(self.delay)
        return _FakeResponse(self.text)


class _FakeAsyncClient:
    def __init__(self, models: _FakeModels) -> None:
        self.models = models

    async def __aenter__(self) -> _FakeAsyncClient:
        return self

    async def __aexit__(
        self,
        exc_type: object,
        exc: object,
        traceback: object,
    ) -> None:
        del exc_type, exc, traceback


class _FakeClient:
    def __init__(self, models: _FakeModels) -> None:
        self.aio = _FakeAsyncClient(models)


class _Factory:
    def __init__(self, models: _FakeModels) -> None:
        self.models = models
        self.keys: list[str] = []

    def __call__(self, api_key: str) -> _FakeClient:
        self.keys.append(api_key)
        return _FakeClient(self.models)


class _SequencedProvider:
    def __init__(
        self,
        outcomes: list[ProviderPlanResponse | ProviderContractError],
    ) -> None:
        self.outcomes = outcomes
        self.credentials: list[str] = []
        self.profiles: list[AIRequestProfile] = []
        self.thread_ids: list[int] = []

    def request_plan(
        self,
        request: AIProviderRequest,
        credential: CredentialSecret,
        cancellation=None,
    ) -> ProviderPlanResponse:
        del cancellation
        self.thread_ids.append(threading.get_ident())
        self.credentials.append(credential.reveal())
        self.profiles.append(request.profile)
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, ProviderContractError):
            raise outcome
        return outcome


class _BlockingProvider:
    def __init__(self) -> None:
        self.started = Event()

    def request_plan(
        self,
        request: AIProviderRequest,
        credential: CredentialSecret,
        cancellation=None,
    ) -> ProviderPlanResponse:
        del request, credential
        self.started.set()
        while cancellation is None or not cancellation.cancelled:
            time.sleep(0.005)
        raise CancelledError("cancelled")


def _state(*, revision: int = 28) -> ProjectState:
    fps = 30
    asset = Asset(
        "asset-w7-008",
        "fixture.mp4",
        "video",
        FrameTime(360, fps),
        1920,
        1080,
        True,
        "8" * 64,
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
        ProjectState.create("project-w7-008", "W7-008", fps),
        revision=revision,
        assets=(asset,),
        tracks=(Track("V1", "video", 0, clips=clips),),
    )
    state.validate()
    return state


def _payload(*, request_id: str = "REQ-W7-008") -> str:
    return json.dumps(
        {
            "schema_version": 2,
            "base_project_revision": 28,
            "request_id": request_id,
            "summary": "Apply bounded Auto Edit L2 changes.",
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


def _request(
    *,
    request_id: str = "REQ-W7-008",
    profile: AIRequestProfile = AIRequestProfile.L2_AUTO_EDIT,
) -> AIProviderRequest:
    state = _state()
    scope = W7SelectedScope(("clip-1", "clip-2"))
    request_type = (
        L2AIProviderRequest
        if profile is AIRequestProfile.L2_AUTO_EDIT
        else AIProviderRequest
    )
    return request_type(
        request_id=request_id,
        base_project_revision=state.revision,
        instruction="Improve pacing and visual motion without structural edits.",
        context_json=L2ContextBuilder().build(state, scope),
    )


def _pool() -> tuple[CredentialPoolService, CredentialSlotService]:
    backend = InMemoryCredentialStore()
    slots = CredentialSlotService(backend, backend)
    return CredentialPoolService(slots, backend), slots


def _add(slots: CredentialSlotService, slot_id: int, value: str) -> None:
    slots.add_or_update(
        slot_id,
        CredentialSecret(value),
        label=f"Gemini {slot_id}",
    )


def _wait_terminal(
    service: AIPlanJobService,
    job_id: str,
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
    raise AssertionError("AI plan job did not reach a terminal state")


def test_l1_provider_request_profile_remains_backward_compatible_default() -> None:
    request = AIProviderRequest(
        "REQ-L1-DEFAULT",
        1,
        "Use subtle animation.",
        '{"selected_targets":[]}',
    )
    assert request.profile is AIRequestProfile.L1_EFFECTS


def test_gemini_l2_profile_uses_schema_v2_without_credential_prompt_leak() -> None:
    raw_value = "runtime-w7-008-key"
    models = _FakeModels(text=_payload())
    factory = _Factory(models)
    adapter = GeminiAIProvider(client_factory=factory)

    response = adapter.request_plan(
        _request(),
        CredentialSecret(raw_value),
    )

    assert response.payload_json == _payload()
    assert factory.keys == [raw_value]
    assert len(models.calls) == 1
    call = models.calls[0]
    assert call["model"] == "gemini-2.5-flash"
    assert raw_value not in str(call["contents"])
    assert raw_value not in repr(call["config"])
    assert "REQUEST_PROFILE:L2_AUTO_EDIT" in str(call["contents"])
    config = call["config"]
    assert isinstance(config, types.GenerateContentConfig)
    assert config.response_mime_type == "application/json"
    assert config.response_json_schema is not None
    assert config.response_json_schema["properties"]["schema_version"]["const"] == 2
    assert "Auto Edit L2" in str(config.system_instruction)


def test_l1_gemini_profile_keeps_schema_v1_and_effect_only_allowlist() -> None:
    models = _FakeModels(
        text=json.dumps(
            {
                "schema_version": 1,
                "base_project_revision": 1,
                "request_id": "REQ-L1",
                "summary": "One effect.",
                "commands": [
                    {
                        "command_type": "set_clip_effects",
                        "target_clip_id": "clip-1",
                        "enter_effect": "Rise",
                    }
                ],
            }
        )
    )
    adapter = GeminiAIProvider(client_factory=_Factory(models))
    adapter.request_plan(
        AIProviderRequest(
            "REQ-L1",
            1,
            "Use a subtle effect.",
            '{"selected_targets":[{"clip_id":"clip-1"}]}',
        ),
        CredentialSecret("runtime-l1-key"),
    )
    config = models.calls[0]["config"]
    assert isinstance(config, types.GenerateContentConfig)
    schema = config.response_json_schema
    assert schema["properties"]["schema_version"]["enum"] == [1]
    commands = schema["properties"]["commands"]["items"]
    assert commands["properties"]["command_type"]["enum"] == ["set_clip_effects"]


def test_shared_job_service_runs_l2_off_thread_and_returns_verified_auto_plan() -> None:
    state = _state()
    before = state.semantic_json(include_revision=True)
    pool, slots = _pool()
    raw_value = "runtime-l2-job-key"
    _add(slots, 1, raw_value)
    provider = _SequencedProvider([ProviderPlanResponse("REQ-W7-008", _payload())])
    caller_thread = threading.get_ident()

    with AIPlanJobService(provider, pool) as service:
        service.submit(
            _request(),
            state,
            ("clip-1", "clip-2"),
            session_id="session-L2",
        )
        terminal = _wait_terminal(service, "REQ-W7-008")
        assert terminal.state is AIJobState.SUCCESS
        verified = service.take_verified_l2(
            "REQ-W7-008",
            state,
            session_id="session-L2",
        )

    assert verified.command_count == 6
    assert verified.target_count == 2
    assert verified.selected_scope_count == 2
    assert verified.candidate_revision == state.revision
    assert verified.translated_command_types == (
        "SetClipPropertiesCommand",
        "SetClipDurationCommand",
        "SetClipPropertiesCommand",
        "SetClipPropertiesCommand",
        "SetClipSpeedCommand",
        "SetClipPropertiesCommand",
    )
    assert provider.thread_ids and provider.thread_ids[0] != caller_thread
    assert provider.credentials == [raw_value]
    assert provider.profiles == [AIRequestProfile.L2_AUTO_EDIT]
    assert state.semantic_json(include_revision=True) == before
    assert raw_value not in repr(terminal)


def test_l2_job_reuses_invalid_auth_failover_without_second_provider_service() -> None:
    pool, slots = _pool()
    _add(slots, 1, "runtime-l2-slot-one")
    _add(slots, 2, "runtime-l2-slot-two")
    provider = _SequencedProvider(
        [
            ProviderContractError(
                ProviderErrorCode.INVALID_AUTH,
                "invalid auth",
            ),
            ProviderPlanResponse("REQ-W7-008", _payload()),
        ]
    )

    with AIPlanJobService(provider, pool) as service:
        service.submit(
            _request(),
            _state(),
            ("clip-1", "clip-2"),
            session_id="session-L2",
        )
        terminal = _wait_terminal(service, "REQ-W7-008")
        assert terminal.state is AIJobState.SUCCESS
        verified = service.take_verified_l2(
            "REQ-W7-008",
            _state(),
            session_id="session-L2",
        )

    assert verified.command_count == 6
    assert provider.credentials == [
        "runtime-l2-slot-one",
        "runtime-l2-slot-two",
    ]
    assert provider.profiles == [
        AIRequestProfile.L2_AUTO_EDIT,
        AIRequestProfile.L2_AUTO_EDIT,
    ]
    assert slots.get(1).enabled is False
    assert slots.get(2).enabled is True


def test_profile_specific_take_boundary_does_not_consume_wrong_result() -> None:
    pool, slots = _pool()
    _add(slots, 1, "runtime-profile-boundary")
    provider = _SequencedProvider([ProviderPlanResponse("REQ-W7-008", _payload())])
    state = _state()

    with AIPlanJobService(provider, pool) as service:
        service.submit(
            _request(),
            state,
            ("clip-1", "clip-2"),
            session_id="session-L2",
        )
        assert _wait_terminal(service, "REQ-W7-008").state is AIJobState.SUCCESS
        with pytest.raises(
            AIPlanJobAccessError,
            match="not an L1",
        ):
            service.take_verified(
                "REQ-W7-008",
                state,
                session_id="session-L2",
            )
        verified = service.take_verified_l2(
            "REQ-W7-008",
            state,
            session_id="session-L2",
        )
        assert verified.command_count == 6


def test_l2_invalid_provider_payload_is_typed_and_never_mutates_state() -> None:
    pool, slots = _pool()
    _add(slots, 1, "runtime-l2-bad-payload")
    provider = _SequencedProvider(
        [
            ProviderPlanResponse(
                "REQ-W7-008",
                '{"schema_version":2}',
            )
        ]
    )
    state = _state()
    before = state.semantic_json(include_revision=True)

    with AIPlanJobService(provider, pool) as service:
        service.submit(
            _request(),
            state,
            ("clip-1", "clip-2"),
            session_id="session-L2",
        )
        terminal = _wait_terminal(service, "REQ-W7-008")

    assert terminal.state is AIJobState.FAILED
    assert terminal.plan_error is PlanErrorCode.SCHEMA_INVALID
    assert state.semantic_json(include_revision=True) == before


def test_l2_job_cancellation_reuses_w6_cancelled_state() -> None:
    pool, slots = _pool()
    _add(slots, 1, "runtime-l2-cancel")
    provider = _BlockingProvider()

    with AIPlanJobService(provider, pool) as service:
        service.submit(
            _request(),
            _state(),
            ("clip-1", "clip-2"),
            session_id="session-L2",
        )
        assert provider.started.wait(timeout=1.0)
        assert service.cancel("REQ-W7-008") is True
        terminal = _wait_terminal(service, "REQ-W7-008")
        assert terminal.state is AIJobState.CANCELLED
        with pytest.raises(AIPlanJobAccessError):
            service.take_verified_l2(
                "REQ-W7-008",
                _state(),
                session_id="session-L2",
            )


def test_l2_stale_session_reuses_existing_stale_plan_gate() -> None:
    pool, slots = _pool()
    _add(slots, 1, "runtime-l2-stale")
    provider = _SequencedProvider([ProviderPlanResponse("REQ-W7-008", _payload())])
    state = _state()

    with AIPlanJobService(provider, pool) as service:
        service.submit(
            _request(),
            state,
            ("clip-1", "clip-2"),
            session_id="session-L2",
        )
        assert _wait_terminal(service, "REQ-W7-008").state is AIJobState.SUCCESS
        with pytest.raises(PlanContractError) as caught:
            service.take_verified_l2(
                "REQ-W7-008",
                state,
                session_id="different-session",
            )
        assert caught.value.code is PlanErrorCode.STALE_PLAN
