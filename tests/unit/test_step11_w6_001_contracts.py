from __future__ import annotations

from dataclasses import fields

import pytest

from ai_ngerti_geopolitik.application.ai_contracts import (
    EDIT_PLAN_SCHEMA_VERSION,
    L1_RENDER_QUALIFIED_EFFECTS,
    AIJobState,
    AIProviderRequest,
    CredentialContractError,
    CredentialErrorCode,
    CredentialSecret,
    CredentialSlotRef,
    EditPlan,
    EffectEditProposal,
    PlanContractError,
    PlanErrorCode,
    ProviderContractError,
    ProviderErrorCode,
    ProviderPlanResponse,
)
from ai_ngerti_geopolitik.application.ports import AIProviderPort, CredentialPort
from ai_ngerti_geopolitik.domain.properties import SUPPORTED_W4_EFFECTS


class FakeCredentialPort:
    def __init__(self) -> None:
        self.values: dict[int, CredentialSecret] = {}

    def store_secret(self, slot: CredentialSlotRef, secret: CredentialSecret) -> None:
        self.values[slot.slot_id] = secret

    def load_secret(self, slot: CredentialSlotRef) -> CredentialSecret:
        try:
            return self.values[slot.slot_id]
        except KeyError as exc:
            raise CredentialContractError(
                CredentialErrorCode.NO_CREDENTIAL,
                "no credential stored in requested slot",
            ) from exc

    def delete_secret(self, slot: CredentialSlotRef) -> None:
        self.values.pop(slot.slot_id, None)

    def has_secret(self, slot: CredentialSlotRef) -> bool:
        return slot.slot_id in self.values


class FakeProviderPort:
    def request_plan(
        self,
        request: AIProviderRequest,
        credential: CredentialSecret,
        cancellation=None,
    ) -> ProviderPlanResponse:
        del credential, cancellation
        return ProviderPlanResponse(
            request_id=request.request_id,
            payload_json='{"schema_version":1}',
        )


def test_credential_slot_boundary_accepts_only_1_through_100() -> None:
    assert CredentialSlotRef(1).slot_id == 1
    assert CredentialSlotRef(100).slot_id == 100

    for value in (0, 101, -1):
        with pytest.raises(CredentialContractError) as caught:
            CredentialSlotRef(value)
        assert caught.value.code is CredentialErrorCode.INVALID_SLOT


def test_secret_repr_and_str_are_masked_and_reveal_is_explicit() -> None:
    raw = "gemini-test-secret-never-log"
    secret = CredentialSecret(raw)

    assert str(secret) == "**masked**"
    assert repr(secret) == "CredentialSecret(**masked**)"
    assert raw not in str(secret)
    assert raw not in repr(secret)
    assert secret.reveal() == raw


def test_ports_are_provider_agnostic_and_runtime_checkable() -> None:
    credentials = FakeCredentialPort()
    provider = FakeProviderPort()

    assert isinstance(credentials, CredentialPort)
    assert isinstance(provider, AIProviderPort)

    slot = CredentialSlotRef(1)
    secret = CredentialSecret("secret-value")
    credentials.store_secret(slot, secret)
    assert credentials.has_secret(slot)
    assert credentials.load_secret(slot).reveal() == "secret-value"
    credentials.delete_secret(slot)
    assert not credentials.has_secret(slot)


def test_w6_l1_allowlist_is_locked_to_render_qualified_w4_effects() -> None:
    assert L1_RENDER_QUALIFIED_EFFECTS == SUPPORTED_W4_EFFECTS

    for effect in L1_RENDER_QUALIFIED_EFFECTS:
        proposal = EffectEditProposal("C001", enter_effect=effect)
        assert proposal.enter_effect == effect

    with pytest.raises(PlanContractError) as caught:
        EffectEditProposal("C001", enter_effect="Wipe")
    assert caught.value.code is PlanErrorCode.SEMANTIC_INVALID


def test_l1_proposal_cannot_express_lock_title_timeline_or_arbitrary_command() -> None:
    names = {field.name for field in fields(EffectEditProposal)}
    assert names == {
        "target_clip_id",
        "enter_effect",
        "exit_effect",
        "intensity_percent",
        "command_type",
    }
    assert "locked" not in names
    assert "title" not in names
    assert "timeline_start" not in names

    with pytest.raises(PlanContractError) as caught:
        EffectEditProposal(
            "C001",
            enter_effect="Fade",
            command_type="shell_exec",
        )
    assert caught.value.code is PlanErrorCode.SCHEMA_INVALID


def test_effect_proposal_requires_target_change_and_canonical_intensity() -> None:
    with pytest.raises(PlanContractError):
        EffectEditProposal("", enter_effect="Fade")
    with pytest.raises(PlanContractError):
        EffectEditProposal("C001")
    with pytest.raises(PlanContractError):
        EffectEditProposal("C001", intensity_percent=201)

    assert EffectEditProposal("C001", intensity_percent=0).intensity_percent == 0
    assert EffectEditProposal("C001", intensity_percent=200).intensity_percent == 200


def test_edit_plan_schema_is_revision_bound_and_immutable() -> None:
    proposal = EffectEditProposal(
        target_clip_id="C001",
        enter_effect="Rise",
        exit_effect="Fade",
        intensity_percent=120,
    )
    plan = EditPlan(
        schema_version=EDIT_PLAN_SCHEMA_VERSION,
        base_project_revision=7,
        request_id="REQ-001",
        summary="Add a restrained entrance and exit animation.",
        commands=(proposal,),
    )
    assert plan.base_project_revision == 7
    assert plan.commands == (proposal,)

    with pytest.raises(PlanContractError):
        EditPlan(99, 7, "REQ-001", "bad schema", (proposal,))
    with pytest.raises(PlanContractError):
        EditPlan(1, -1, "REQ-001", "bad revision", (proposal,))


def test_provider_request_has_no_credential_or_secret_field() -> None:
    names = {field.name for field in fields(AIProviderRequest)}
    assert names == {
        "request_id",
        "base_project_revision",
        "instruction",
        "context_json",
    }
    assert not {"credential", "api_key", "secret"} & names

    request = AIProviderRequest(
        request_id="REQ-001",
        base_project_revision=3,
        instruction="Plan L1 animation only.",
        context_json='{"clip_id":"C001"}',
    )
    response = FakeProviderPort().request_plan(
        request,
        CredentialSecret("transient-secret"),
    )
    assert response.request_id == request.request_id


def test_typed_error_taxonomy_and_job_lifecycle_are_locked() -> None:
    assert {item.value for item in CredentialErrorCode} == {
        "NO_CREDENTIAL",
        "INVALID_SLOT",
        "ALL_SLOTS_UNAVAILABLE",
    }
    assert {item.value for item in ProviderErrorCode} == {
        "INVALID_AUTH",
        "RATE_LIMIT_OR_QUOTA",
        "NETWORK_TIMEOUT",
        "MALFORMED_RESPONSE",
    }
    assert {item.value for item in PlanErrorCode} == {
        "SCHEMA_INVALID",
        "SEMANTIC_INVALID",
        "STALE_PLAN",
        "LOCK_CONFLICT",
    }
    assert {item.value for item in AIJobState} == {
        "QUEUED",
        "RUNNING",
        "SUCCESS",
        "FAILED",
        "CANCELLED",
    }

    error = ProviderContractError(
        ProviderErrorCode.NETWORK_TIMEOUT,
        "provider request timed out",
    )
    assert error.code is ProviderErrorCode.NETWORK_TIMEOUT
    assert str(error) == "provider request timed out"


def test_provider_response_rejects_empty_payload() -> None:
    with pytest.raises(ProviderContractError) as caught:
        ProviderPlanResponse("REQ-001", " ")
    assert caught.value.code is ProviderErrorCode.MALFORMED_RESPONSE
