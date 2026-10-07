"""Canonical W6 AI and credential contracts.

This module contains application-layer DTOs and typed errors only. It deliberately
contains no Gemini client, secure-store, Qt, filesystem enumeration or project
mutation implementation.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Final

EDIT_PLAN_SCHEMA_VERSION: Final = 1
MAX_CREDENTIAL_SLOTS: Final = 100
MASKED_CREDENTIAL_VALUE: Final = "••••••••"

L1_RENDER_QUALIFIED_EFFECTS: Final = (
    "None",
    "Fade",
    "Pop",
    "Breathe",
    "Stomp",
    "Tumble",
    "Tectonic",
    "Rise",
    "Pan",
    "Drift",
)


class CredentialErrorCode(StrEnum):
    NO_CREDENTIAL = "NO_CREDENTIAL"
    INVALID_SLOT = "INVALID_SLOT"
    ALL_SLOTS_UNAVAILABLE = "ALL_SLOTS_UNAVAILABLE"


class ProviderErrorCode(StrEnum):
    INVALID_AUTH = "INVALID_AUTH"
    RATE_LIMIT_OR_QUOTA = "RATE_LIMIT_OR_QUOTA"
    NETWORK_TIMEOUT = "NETWORK_TIMEOUT"
    MALFORMED_RESPONSE = "MALFORMED_RESPONSE"


class PlanErrorCode(StrEnum):
    SCHEMA_INVALID = "SCHEMA_INVALID"
    SEMANTIC_INVALID = "SEMANTIC_INVALID"
    STALE_PLAN = "STALE_PLAN"
    LOCK_CONFLICT = "LOCK_CONFLICT"


class AIJobState(StrEnum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class AIRequestProfile(StrEnum):
    """Provider request profile; L1 remains the backward-compatible default."""

    L1_EFFECTS = "L1_EFFECTS"
    L2_AUTO_EDIT = "L2_AUTO_EDIT"


class CredentialContractError(RuntimeError):
    def __init__(self, code: CredentialErrorCode, safe_message: str) -> None:
        self.code = code
        self.safe_message = safe_message.strip() or code.value
        super().__init__(self.safe_message)


class CredentialMetadataError(ValueError):
    """Safe validation failure for non-secret credential-slot metadata."""

    def __init__(self, safe_message: str) -> None:
        self.safe_message = safe_message.strip() or "invalid credential metadata"
        super().__init__(self.safe_message)


class ProviderContractError(RuntimeError):
    def __init__(self, code: ProviderErrorCode, safe_message: str) -> None:
        self.code = code
        self.safe_message = safe_message.strip() or code.value
        super().__init__(self.safe_message)


class PlanContractError(ValueError):
    def __init__(self, code: PlanErrorCode, safe_message: str) -> None:
        self.code = code
        self.safe_message = safe_message.strip() or code.value
        super().__init__(self.safe_message)


class CredentialSecret:
    """Transient raw credential wrapper with masked string representations."""

    __slots__ = ("__value",)

    def __init__(self, value: str) -> None:
        normalized = value.strip()
        if not normalized:
            raise CredentialContractError(
                CredentialErrorCode.NO_CREDENTIAL,
                "credential secret cannot be empty",
            )
        self.__value = normalized

    def reveal(self) -> str:
        """Explicitly reveal the secret for a secure-store/provider boundary."""
        return self.__value

    def __repr__(self) -> str:
        return "CredentialSecret(**masked**)"

    def __str__(self) -> str:
        return "**masked**"


@dataclass(frozen=True, slots=True)
class CredentialSlotRef:
    slot_id: int

    def __post_init__(self) -> None:
        if not 1 <= self.slot_id <= MAX_CREDENTIAL_SLOTS:
            raise CredentialContractError(
                CredentialErrorCode.INVALID_SLOT,
                f"credential slot must be between 1 and {MAX_CREDENTIAL_SLOTS}",
            )


@dataclass(frozen=True, slots=True)
class CredentialSlotMetadata:
    """Non-secret logical-slot metadata safe for presentation/persistence."""

    slot: CredentialSlotRef
    label: str
    enabled: bool = True

    def __post_init__(self) -> None:
        normalized = self.label.strip()
        if not normalized:
            raise CredentialMetadataError("credential slot label cannot be empty")
        if len(normalized) > 80:
            raise CredentialMetadataError("credential slot label must not exceed 80 characters")
        if any(character in normalized for character in "\r\n\t"):
            raise CredentialMetadataError("credential slot label cannot contain control whitespace")
        object.__setattr__(self, "label", normalized)

    @property
    def slot_id(self) -> int:
        return self.slot.slot_id

    @property
    def masked_value(self) -> str:
        return MASKED_CREDENTIAL_VALUE

    def __repr__(self) -> str:
        return (
            "CredentialSlotMetadata("
            f"slot_id={self.slot_id}, label={self.label!r}, "
            f"enabled={self.enabled}, masked_value={MASKED_CREDENTIAL_VALUE!r})"
        )


@dataclass(frozen=True, slots=True)
class EffectEditProposal:
    """Only W6 L1 command shape. It cannot express lock/title/timeline mutation."""

    target_clip_id: str
    enter_effect: str | None = None
    exit_effect: str | None = None
    intensity_percent: int | None = None
    command_type: str = "set_clip_effects"

    def __post_init__(self) -> None:
        if self.command_type != "set_clip_effects":
            raise PlanContractError(
                PlanErrorCode.SCHEMA_INVALID,
                f"unsupported L1 command type: {self.command_type}",
            )
        if not self.target_clip_id.strip():
            raise PlanContractError(
                PlanErrorCode.SCHEMA_INVALID,
                "L1 effect proposal requires a stable target clip id",
            )
        if (
            self.enter_effect is None
            and self.exit_effect is None
            and self.intensity_percent is None
        ):
            raise PlanContractError(
                PlanErrorCode.SCHEMA_INVALID,
                "L1 effect proposal must change at least one effect field",
            )
        for name, value in (
            ("enter_effect", self.enter_effect),
            ("exit_effect", self.exit_effect),
        ):
            if value is not None and value not in L1_RENDER_QUALIFIED_EFFECTS:
                raise PlanContractError(
                    PlanErrorCode.SEMANTIC_INVALID,
                    f"{name} is not render-qualified for W6 L1: {value}",
                )
        if self.intensity_percent is not None and not 0 <= self.intensity_percent <= 200:
            raise PlanContractError(
                PlanErrorCode.SEMANTIC_INVALID,
                "effect intensity must be between 0 and 200",
            )


@dataclass(frozen=True, slots=True)
class EditPlan:
    schema_version: int
    base_project_revision: int
    request_id: str
    summary: str
    commands: tuple[EffectEditProposal, ...]

    def __post_init__(self) -> None:
        if self.schema_version != EDIT_PLAN_SCHEMA_VERSION:
            raise PlanContractError(
                PlanErrorCode.SCHEMA_INVALID,
                f"unsupported EditPlan schema version: {self.schema_version}",
            )
        if self.base_project_revision < 0:
            raise PlanContractError(
                PlanErrorCode.SCHEMA_INVALID,
                "base project revision must be non-negative",
            )
        if not self.request_id.strip():
            raise PlanContractError(
                PlanErrorCode.SCHEMA_INVALID,
                "EditPlan request id is required",
            )
        if not self.summary.strip():
            raise PlanContractError(
                PlanErrorCode.SCHEMA_INVALID,
                "EditPlan summary is required",
            )


@dataclass(frozen=True, slots=True)
class AIProviderRequest:
    """Sanitized provider request. Credential is deliberately not a field."""

    request_id: str
    base_project_revision: int
    instruction: str
    context_json: str

    def __post_init__(self) -> None:
        if not self.request_id.strip():
            raise PlanContractError(
                PlanErrorCode.SCHEMA_INVALID,
                "provider request id is required",
            )
        if self.base_project_revision < 0:
            raise PlanContractError(
                PlanErrorCode.SCHEMA_INVALID,
                "provider base project revision must be non-negative",
            )
        if not self.instruction.strip():
            raise PlanContractError(
                PlanErrorCode.SCHEMA_INVALID,
                "provider instruction is required",
            )
        if not self.context_json.strip():
            raise PlanContractError(
                PlanErrorCode.SCHEMA_INVALID,
                "provider context is required",
            )

    @property
    def profile(self) -> AIRequestProfile:
        return AIRequestProfile.L1_EFFECTS


@dataclass(frozen=True, slots=True)
class L2AIProviderRequest(AIProviderRequest):
    """W7 L2 provider request preserving the frozen W6 request field contract."""

    @property
    def profile(self) -> AIRequestProfile:
        return AIRequestProfile.L2_AUTO_EDIT


@dataclass(frozen=True, slots=True)
class ProviderPlanResponse:
    request_id: str
    payload_json: str

    def __post_init__(self) -> None:
        if not self.request_id.strip():
            raise ProviderContractError(
                ProviderErrorCode.MALFORMED_RESPONSE,
                "provider response request id is required",
            )
        if not self.payload_json.strip():
            raise ProviderContractError(
                ProviderErrorCode.MALFORMED_RESPONSE,
                "provider response payload is empty",
            )
