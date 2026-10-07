from __future__ import annotations

import asyncio
import json
import threading
import time
from concurrent.futures import CancelledError
from dataclasses import replace
from threading import Event

import pytest
from google.genai import errors, types

from ai_ngerti_geopolitik.application.ai_contracts import (
    AIJobState,
    AIProviderRequest,
    CredentialSecret,
    PlanContractError,
    PlanErrorCode,
    ProviderContractError,
    ProviderErrorCode,
    ProviderPlanResponse,
)
from ai_ngerti_geopolitik.application.ai_jobs import (
    AIPlanJobAccessError,
    AIPlanJobService,
    CancellationFlag,
)
from ai_ngerti_geopolitik.application.ai_plan_verifier import PlanVerifier
from ai_ngerti_geopolitik.application.credential_pool import (
    CredentialPoolPolicy,
    CredentialPoolService,
)
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
from ai_ngerti_geopolitik.infrastructure.gemini_provider import (
    GeminiAIProvider,
    GeminiProviderConfig,
)
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
        error: BaseException | None = None,
    ) -> None:
        self.text = text
        self.delay = delay
        self.error = error
        self.calls: list[dict[str, object]] = []

    async def generate_content(
        self,
        *,
        model: str,
        contents: str,
        config: object,
    ) -> object:
        self.calls.append({"model": model, "contents": contents, "config": config})
        if self.delay:
            await asyncio.sleep(self.delay)
        if self.error is not None:
            raise self.error
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
    def __init__(self, outcomes: list[ProviderPlanResponse | ProviderContractError]) -> None:
        self.outcomes = outcomes
        self.credentials: list[str] = []
        self.thread_ids: list[int] = []

    def request_plan(
        self,
        request: AIProviderRequest,
        credential: CredentialSecret,
        cancellation=None,
    ) -> ProviderPlanResponse:
        del request, cancellation
        self.thread_ids.append(threading.get_ident())
        self.credentials.append(credential.reveal())
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


def _state(*, revision: int = 11) -> ProjectState:
    fps = 30
    asset = Asset(
        "asset-1",
        "fixture.mp4",
        "video",
        FrameTime(300, fps),
        1920,
        1080,
        True,
        "a" * 64,
    )
    clip = Clip(
        "clip-1",
        asset.asset_id,
        FrameTime(0, fps),
        FrameTime(0, fps),
        FrameTime(120, fps),
        properties=replace(
            ClipProperties(),
            effects=EffectProperties("Fade", "Drift", 80, False),
        ),
    )
    state = replace(
        ProjectState.create("project-w6-007", "W6-007", fps),
        revision=revision,
        assets=(asset,),
        tracks=(Track("V1", "video", 0, clips=(clip,)),),
    )
    state.validate()
    return state


def _payload(*, revision: int = 11, request_id: str = "REQ-007") -> str:
    return json.dumps(
        {
            "schema_version": 1,
            "base_project_revision": revision,
            "request_id": request_id,
            "summary": "Use a restrained qualified entrance effect.",
            "commands": [
                {
                    "command_type": "set_clip_effects",
                    "target_clip_id": "clip-1",
                    "enter_effect": "Rise",
                    "intensity_percent": 120,
                }
            ],
        }
    )


def _request(*, revision: int = 11, request_id: str = "REQ-007") -> AIProviderRequest:
    return AIProviderRequest(
        request_id=request_id,
        base_project_revision=revision,
        instruction="Add subtle motion to the selected clip.",
        context_json='{"selected_targets":[{"clip_id":"clip-1"}]}',
    )


def _pool(
    *,
    policy: CredentialPoolPolicy | None = None,
) -> tuple[CredentialPoolService, CredentialSlotService]:
    backend = InMemoryCredentialStore()
    slots = CredentialSlotService(backend, backend)
    pool = CredentialPoolService(slots, backend, policy=policy)
    return pool, slots


def _add(slots: CredentialSlotService, slot_id: int, value: str) -> None:
    slots.add_or_update(slot_id, CredentialSecret(value), label=f"Gemini {slot_id}")


def _wait_terminal(service: AIPlanJobService, job_id: str, timeout: float = 3.0):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        snapshot = service.snapshot(job_id)
        if snapshot.state in {AIJobState.SUCCESS, AIJobState.FAILED, AIJobState.CANCELLED}:
            return snapshot
        time.sleep(0.01)
    raise AssertionError("AI plan job did not reach a terminal state")


def test_official_google_genai_runtime_and_structured_config_are_available() -> None:
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_json_schema={"type": "object"},
    )
    assert config.response_mime_type == "application/json"
    assert errors.APIError is not None


def test_gemini_adapter_uses_async_sdk_json_schema_and_never_prompts_with_credential() -> None:
    raw_value = "runtime-provider-value"
    models = _FakeModels(text=_payload())
    factory = _Factory(models)
    adapter = GeminiAIProvider(client_factory=factory)

    response = adapter.request_plan(_request(), CredentialSecret(raw_value))

    assert response.payload_json == _payload()
    assert factory.keys == [raw_value]
    assert len(models.calls) == 1
    call = models.calls[0]
    assert call["model"] == "gemini-2.5-flash"
    assert raw_value not in str(call["contents"])
    assert raw_value not in repr(call["config"])
    assert isinstance(call["config"], types.GenerateContentConfig)
    assert call["config"].response_mime_type == "application/json"
    assert call["config"].response_json_schema is not None


def test_gemini_adapter_preflight_cancellation_makes_no_sdk_call() -> None:
    models = _FakeModels(text=_payload())
    factory = _Factory(models)
    flag = CancellationFlag()
    flag.cancel()

    with pytest.raises(CancelledError):
        GeminiAIProvider(client_factory=factory).request_plan(
            _request(),
            CredentialSecret("runtime-cancel-value"),
            flag,
        )
    assert factory.keys == []
    assert models.calls == []


def test_gemini_adapter_timeout_is_typed_and_safe() -> None:
    models = _FakeModels(text=_payload(), delay=0.2)
    adapter = GeminiAIProvider(
        GeminiProviderConfig(timeout_seconds=1.0, cancellation_poll_seconds=0.01),
        client_factory=_Factory(models),
    )
    adapter._config = GeminiProviderConfig(  # type: ignore[misc]
        timeout_seconds=1.0,
        cancellation_poll_seconds=0.01,
    )

    original = adapter._config  # type: ignore[attr-defined]
    object.__setattr__(original, "timeout_seconds", 0.02)
    with pytest.raises(ProviderContractError) as caught:
        adapter.request_plan(_request(), CredentialSecret("runtime-timeout-value"))
    assert caught.value.code is ProviderErrorCode.NETWORK_TIMEOUT
    assert "runtime-timeout-value" not in str(caught.value)


@pytest.mark.parametrize(
    ("status_code", "expected"),
    [
        (401, ProviderErrorCode.INVALID_AUTH),
        (403, ProviderErrorCode.INVALID_AUTH),
        (429, ProviderErrorCode.RATE_LIMIT_OR_QUOTA),
        (503, ProviderErrorCode.NETWORK_TIMEOUT),
        (400, ProviderErrorCode.MALFORMED_RESPONSE),
    ],
)
def test_gemini_adapter_maps_official_api_errors_safely(
    status_code: int,
    expected: ProviderErrorCode,
) -> None:
    api_error = errors.ClientError(
        status_code,
        {"message": "provider detail not for UI", "status": "TEST"},
    )
    models = _FakeModels(text=None, error=api_error)
    adapter = GeminiAIProvider(client_factory=_Factory(models))

    with pytest.raises(ProviderContractError) as caught:
        adapter.request_plan(_request(), CredentialSecret("runtime-api-value"))
    assert caught.value.code is expected
    assert "provider detail" not in str(caught.value)


def test_gemini_adapter_rejects_empty_text_response() -> None:
    adapter = GeminiAIProvider(client_factory=_Factory(_FakeModels(text=None)))
    with pytest.raises(ProviderContractError) as caught:
        adapter.request_plan(_request(), CredentialSecret("runtime-empty-value"))
    assert caught.value.code is ProviderErrorCode.MALFORMED_RESPONSE


def test_job_service_runs_off_caller_thread_and_returns_verified_without_mutation() -> None:
    state = _state()
    before = state.semantic_json(include_revision=True)
    pool, slots = _pool()
    raw_value = "runtime-job-value"
    _add(slots, 1, raw_value)
    provider = _SequencedProvider([ProviderPlanResponse("REQ-007", _payload())])
    caller_thread = threading.get_ident()

    with AIPlanJobService(provider, pool, PlanVerifier()) as service:
        queued = service.submit(_request(), state, ("clip-1",), session_id="session-A")
        assert queued.state in {AIJobState.QUEUED, AIJobState.RUNNING}
        terminal = _wait_terminal(service, "REQ-007")
        assert terminal.state is AIJobState.SUCCESS
        verified = service.take_verified("REQ-007", state, session_id="session-A")
        assert verified.command_count == 1
        with pytest.raises(AIPlanJobAccessError, match="already consumed"):
            service.take_verified("REQ-007", state, session_id="session-A")

    assert provider.thread_ids and provider.thread_ids[0] != caller_thread
    assert provider.credentials == [raw_value]
    assert state.semantic_json(include_revision=True) == before
    assert raw_value not in repr(terminal)


def test_job_service_invalid_auth_fails_over_to_next_slot() -> None:
    pool, slots = _pool()
    _add(slots, 1, "runtime-slot-one")
    _add(slots, 2, "runtime-slot-two")
    provider = _SequencedProvider(
        [
            ProviderContractError(ProviderErrorCode.INVALID_AUTH, "invalid auth"),
            ProviderPlanResponse("REQ-007", _payload()),
        ]
    )

    with AIPlanJobService(provider, pool) as service:
        service.submit(_request(), _state(), ("clip-1",), session_id="session-A")
        terminal = _wait_terminal(service, "REQ-007")

    assert terminal.state is AIJobState.SUCCESS
    assert provider.credentials == ["runtime-slot-one", "runtime-slot-two"]
    assert slots.get(1).enabled is False
    assert slots.get(2).enabled is True


def test_job_service_network_timeout_retries_same_slot_before_success() -> None:
    policy = CredentialPoolPolicy(max_network_retries_per_slot=1)
    pool, slots = _pool(policy=policy)
    _add(slots, 1, "runtime-network-value")
    provider = _SequencedProvider(
        [
            ProviderContractError(ProviderErrorCode.NETWORK_TIMEOUT, "timeout"),
            ProviderPlanResponse("REQ-007", _payload()),
        ]
    )

    with AIPlanJobService(provider, pool) as service:
        service.submit(_request(), _state(), ("clip-1",), session_id="session-A")
        terminal = _wait_terminal(service, "REQ-007")

    assert terminal.state is AIJobState.SUCCESS
    assert provider.credentials == ["runtime-network-value", "runtime-network-value"]


def test_job_service_quota_failure_does_not_rotate_credentials() -> None:
    pool, slots = _pool()
    _add(slots, 1, "runtime-quota-one")
    _add(slots, 2, "runtime-quota-two")
    provider = _SequencedProvider(
        [ProviderContractError(ProviderErrorCode.RATE_LIMIT_OR_QUOTA, "quota")]
    )

    with AIPlanJobService(provider, pool) as service:
        service.submit(_request(), _state(), ("clip-1",), session_id="session-A")
        terminal = _wait_terminal(service, "REQ-007")

    assert terminal.state is AIJobState.FAILED
    assert terminal.provider_error is ProviderErrorCode.RATE_LIMIT_OR_QUOTA
    assert provider.credentials == ["runtime-quota-one"]
    assert pool.provider_cooldown_remaining_seconds() > 0
    assert slots.get(2).enabled is True


def test_job_service_cancellation_reaches_cancelled_without_plan_result() -> None:
    pool, slots = _pool()
    _add(slots, 1, "runtime-cancel-job")
    provider = _BlockingProvider()

    with AIPlanJobService(provider, pool) as service:
        service.submit(_request(), _state(), ("clip-1",), session_id="session-A")
        assert provider.started.wait(timeout=1.0)
        assert service.cancel("REQ-007") is True
        terminal = _wait_terminal(service, "REQ-007")
        assert terminal.state is AIJobState.CANCELLED
        with pytest.raises(AIPlanJobAccessError):
            service.take_verified("REQ-007", _state(), session_id="session-A")


def test_job_service_stale_revision_or_session_never_releases_result() -> None:
    pool, slots = _pool()
    _add(slots, 1, "runtime-stale-value")
    provider = _SequencedProvider([ProviderPlanResponse("REQ-007", _payload())])
    state = _state()

    with AIPlanJobService(provider, pool) as service:
        service.submit(_request(), state, ("clip-1",), session_id="session-A")
        assert _wait_terminal(service, "REQ-007").state is AIJobState.SUCCESS
        with pytest.raises(PlanContractError) as stale_revision:
            service.take_verified(
                "REQ-007",
                replace(state, revision=12),
                session_id="session-A",
            )
        assert stale_revision.value.code is PlanErrorCode.STALE_PLAN
        with pytest.raises(PlanContractError) as stale_session:
            service.take_verified("REQ-007", state, session_id="session-B")
        assert stale_session.value.code is PlanErrorCode.STALE_PLAN


def test_job_service_invalid_provider_payload_is_failed_not_applied() -> None:
    pool, slots = _pool()
    _add(slots, 1, "runtime-bad-payload")
    provider = _SequencedProvider(
        [ProviderPlanResponse("REQ-007", '{"schema_version":1}')]
    )
    state = _state()
    before = state.semantic_json(include_revision=True)

    with AIPlanJobService(provider, pool) as service:
        service.submit(_request(), state, ("clip-1",), session_id="session-A")
        terminal = _wait_terminal(service, "REQ-007")

    assert terminal.state is AIJobState.FAILED
    assert terminal.plan_error is PlanErrorCode.SCHEMA_INVALID
    assert state.semantic_json(include_revision=True) == before
