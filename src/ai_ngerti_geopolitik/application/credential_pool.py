"""W6-004 credential health, bounded failover and safe bulk TXT import.

This module is provider-agnostic and performs no network requests. Provider outcomes
are reported into the state machine by later adapters. Raw credentials are loaded
only when a bounded session leases one slot for a request/test boundary.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from time import time
from typing import Callable

from ai_ngerti_geopolitik.application.ai_contracts import (
    MAX_CREDENTIAL_SLOTS,
    CredentialContractError,
    CredentialErrorCode,
    CredentialMetadataError,
    CredentialSecret,
    CredentialSlotMetadata,
    CredentialSlotRef,
    ProviderContractError,
    ProviderErrorCode,
)
from ai_ngerti_geopolitik.application.credential_slots import CredentialSlotService
from ai_ngerti_geopolitik.application.ports import CredentialPort


class CredentialHealth(StrEnum):
    UNKNOWN = "UNKNOWN"
    HEALTHY = "HEALTHY"
    INVALID_AUTH = "INVALID_AUTH"
    NETWORK_DEGRADED = "NETWORK_DEGRADED"
    COOLDOWN = "COOLDOWN"


class CredentialTestResult(StrEnum):
    NEVER_TESTED = "NEVER_TESTED"
    PASS = "PASS"
    INVALID_AUTH = "INVALID_AUTH"
    RATE_LIMIT_OR_QUOTA = "RATE_LIMIT_OR_QUOTA"
    NETWORK_TIMEOUT = "NETWORK_TIMEOUT"


@dataclass(frozen=True, slots=True)
class CredentialPoolPolicy:
    max_network_retries_per_slot: int = 1
    max_distinct_slots_per_request: int = 3
    default_cooldown_seconds: float = 60.0
    max_cooldown_seconds: float = 3600.0

    def __post_init__(self) -> None:
        if not 0 <= self.max_network_retries_per_slot <= 3:
            raise ValueError("network retries per slot must be between 0 and 3")
        if not 1 <= self.max_distinct_slots_per_request <= MAX_CREDENTIAL_SLOTS:
            raise ValueError(
                f"distinct slots per request must be between 1 and {MAX_CREDENTIAL_SLOTS}"
            )
        if not 0 < self.default_cooldown_seconds <= self.max_cooldown_seconds:
            raise ValueError("default cooldown must be positive and within the maximum")
        if self.max_cooldown_seconds > 86400:
            raise ValueError("maximum cooldown must not exceed 86400 seconds")


@dataclass(frozen=True, slots=True)
class CredentialHealthSnapshot:
    slot: CredentialSlotRef
    label: str
    enabled: bool
    health: CredentialHealth
    last_result: CredentialTestResult
    cooldown_until_epoch_seconds: float | None
    network_failures: int

    @property
    def slot_id(self) -> int:
        return self.slot.slot_id


@dataclass(frozen=True, slots=True)
class BulkCredentialPreview:
    nonempty_lines: int
    unique_credentials: int
    duplicate_lines: int
    available_slots: int
    can_import: bool


@dataclass(frozen=True, slots=True)
class CredentialLease:
    slot: CredentialSlotRef
    secret: CredentialSecret
    distinct_slot_index: int

    def __repr__(self) -> str:
        return (
            "CredentialLease("
            f"slot_id={self.slot.slot_id}, distinct_slot_index={self.distinct_slot_index}, "
            "secret=**masked**)"
        )


@dataclass(slots=True)
class _RuntimeHealth:
    health: CredentialHealth = CredentialHealth.UNKNOWN
    last_result: CredentialTestResult = CredentialTestResult.NEVER_TESTED
    cooldown_until_epoch_seconds: float | None = None
    network_failures: int = 0


class CredentialPoolService:
    """Non-secret credential health owner plus bounded credential leasing."""

    __slots__ = (
        "_clock",
        "_health",
        "_policy",
        "_provider_cooldown_until",
        "_secrets",
        "_slots",
    )

    def __init__(
        self,
        slots: CredentialSlotService,
        secrets: CredentialPort,
        *,
        policy: CredentialPoolPolicy | None = None,
        clock: Callable[[], float] = time,
    ) -> None:
        self._slots = slots
        self._secrets = secrets
        self._policy = policy or CredentialPoolPolicy()
        self._clock = clock
        self._health: dict[int, _RuntimeHealth] = {}
        self._provider_cooldown_until: float | None = None

    def __repr__(self) -> str:
        snapshots = tuple((item.slot_id, item.health.value) for item in self.snapshots())
        return f"CredentialPoolService(slots={snapshots})"

    @property
    def policy(self) -> CredentialPoolPolicy:
        return self._policy

    def _state(self, slot: CredentialSlotRef) -> _RuntimeHealth:
        return self._health.setdefault(slot.slot_id, _RuntimeHealth())

    def _bounded_cooldown(self, requested_seconds: float | None) -> float:
        seconds = (
            self._policy.default_cooldown_seconds
            if requested_seconds is None
            else requested_seconds
        )
        if seconds <= 0:
            seconds = self._policy.default_cooldown_seconds
        return min(seconds, self._policy.max_cooldown_seconds)

    def _refresh(self) -> None:
        now = self._clock()
        if self._provider_cooldown_until is not None and now >= self._provider_cooldown_until:
            self._provider_cooldown_until = None
        for runtime in self._health.values():
            if (
                runtime.health is CredentialHealth.COOLDOWN
                and runtime.cooldown_until_epoch_seconds is not None
                and now >= runtime.cooldown_until_epoch_seconds
            ):
                runtime.health = CredentialHealth.UNKNOWN
                runtime.cooldown_until_epoch_seconds = None

    def snapshots(self) -> tuple[CredentialHealthSnapshot, ...]:
        self._refresh()
        result: list[CredentialHealthSnapshot] = []
        for metadata in self._slots.list_slots():
            runtime = self._state(metadata.slot)
            result.append(
                CredentialHealthSnapshot(
                    slot=metadata.slot,
                    label=metadata.label,
                    enabled=metadata.enabled,
                    health=runtime.health,
                    last_result=runtime.last_result,
                    cooldown_until_epoch_seconds=runtime.cooldown_until_epoch_seconds,
                    network_failures=runtime.network_failures,
                )
            )
        return tuple(result)

    def snapshot(self, slot_id: int) -> CredentialHealthSnapshot:
        metadata = self._slots.get(slot_id)
        self._refresh()
        runtime = self._state(metadata.slot)
        return CredentialHealthSnapshot(
            slot=metadata.slot,
            label=metadata.label,
            enabled=metadata.enabled,
            health=runtime.health,
            last_result=runtime.last_result,
            cooldown_until_epoch_seconds=runtime.cooldown_until_epoch_seconds,
            network_failures=runtime.network_failures,
        )

    def record_test_result(
        self,
        slot_id: int,
        result: CredentialTestResult,
        *,
        retry_after_seconds: float | None = None,
    ) -> CredentialHealthSnapshot:
        metadata = self._slots.get(slot_id)
        runtime = self._state(metadata.slot)
        runtime.last_result = result

        if result is CredentialTestResult.PASS:
            runtime.health = CredentialHealth.HEALTHY
            runtime.cooldown_until_epoch_seconds = None
            runtime.network_failures = 0
        elif result is CredentialTestResult.INVALID_AUTH:
            runtime.health = CredentialHealth.INVALID_AUTH
            runtime.cooldown_until_epoch_seconds = None
            self._slots.set_enabled(slot_id, False)
        elif result is CredentialTestResult.NETWORK_TIMEOUT:
            runtime.health = CredentialHealth.NETWORK_DEGRADED
            runtime.cooldown_until_epoch_seconds = None
            runtime.network_failures += 1
        elif result is CredentialTestResult.RATE_LIMIT_OR_QUOTA:
            cooldown = self._bounded_cooldown(retry_after_seconds)
            until = self._clock() + cooldown
            runtime.health = CredentialHealth.COOLDOWN
            runtime.cooldown_until_epoch_seconds = until
            self._provider_cooldown_until = max(
                self._provider_cooldown_until or until,
                until,
            )

        return self.snapshot(slot_id)

    def provider_cooldown_remaining_seconds(self) -> float:
        self._refresh()
        if self._provider_cooldown_until is None:
            return 0.0
        return max(0.0, self._provider_cooldown_until - self._clock())

    def _eligible_metadata(
        self,
        excluded_slot_ids: set[int],
    ) -> tuple[CredentialSlotMetadata, ...]:
        self._refresh()
        if self.provider_cooldown_remaining_seconds() > 0:
            raise ProviderContractError(
                ProviderErrorCode.RATE_LIMIT_OR_QUOTA,
                "provider cooldown is active; credential rotation is paused",
            )
        eligible: list[CredentialSlotMetadata] = []
        for metadata in self._slots.list_slots():
            if not metadata.enabled or metadata.slot_id in excluded_slot_ids:
                continue
            runtime = self._state(metadata.slot)
            if runtime.health in {CredentialHealth.INVALID_AUTH, CredentialHealth.COOLDOWN}:
                continue
            eligible.append(metadata)
        return tuple(eligible)

    def start_session(self) -> CredentialFailoverSession:
        return CredentialFailoverSession(self)

    @staticmethod
    def _parse_bulk_text(text: str) -> tuple[tuple[str, ...], int, int]:
        unique: list[str] = []
        seen: set[str] = set()
        nonempty = 0
        duplicates = 0
        for raw_line in text.splitlines():
            value = raw_line.strip()
            if not value:
                continue
            nonempty += 1
            if value in seen:
                duplicates += 1
                continue
            if len(unique) >= MAX_CREDENTIAL_SLOTS:
                raise CredentialMetadataError(
                    "bulk credential TXT supports at most 100 unique credentials"
                )
            CredentialSecret(value)
            seen.add(value)
            unique.append(value)
        return tuple(unique), nonempty, duplicates

    def preview_bulk_text(self, text: str) -> BulkCredentialPreview:
        unique, nonempty, duplicates = self._parse_bulk_text(text)
        occupied = {item.slot_id for item in self._slots.list_slots()}
        available = MAX_CREDENTIAL_SLOTS - len(occupied)
        return BulkCredentialPreview(
            nonempty_lines=nonempty,
            unique_credentials=len(unique),
            duplicate_lines=duplicates,
            available_slots=available,
            can_import=bool(unique) and len(unique) <= available,
        )

    def import_bulk_text(self, text: str) -> tuple[CredentialSlotMetadata, ...]:
        unique, _nonempty, _duplicates = self._parse_bulk_text(text)
        if not unique:
            return ()
        occupied = {item.slot_id for item in self._slots.list_slots()}
        free_slots = [
            slot_id for slot_id in range(1, MAX_CREDENTIAL_SLOTS + 1) if slot_id not in occupied
        ]
        if len(unique) > len(free_slots):
            raise CredentialMetadataError(
                "credential pool has insufficient free slots for bulk import"
            )

        added: list[CredentialSlotMetadata] = []
        try:
            for slot_id, raw_value in zip(free_slots[: len(unique)], unique, strict=True):
                added.append(
                    self._slots.add_or_update(
                        slot_id,
                        CredentialSecret(raw_value),
                    )
                )
        except Exception:
            for metadata in reversed(added):
                self._slots.delete(metadata.slot_id)
            raise
        return tuple(added)


class CredentialFailoverSession:
    """Per-request bounded failover state; never rotates around quota/cooldown."""

    __slots__ = (
        "_closed",
        "_current_slot",
        "_distinct_slots",
        "_network_retries",
        "_pool",
        "_retry_current",
    )

    def __init__(self, pool: CredentialPoolService) -> None:
        self._pool = pool
        self._closed = False
        self._current_slot: CredentialSlotRef | None = None
        self._distinct_slots: list[int] = []
        self._network_retries: dict[int, int] = {}
        self._retry_current = False

    def __repr__(self) -> str:
        return (
            "CredentialFailoverSession("
            f"distinct_slots={tuple(self._distinct_slots)}, closed={self._closed})"
        )

    def _unavailable(self, message: str) -> CredentialContractError:
        self._closed = True
        return CredentialContractError(
            CredentialErrorCode.ALL_SLOTS_UNAVAILABLE,
            message,
        )

    def next_credential(self) -> CredentialLease:
        if self._closed:
            raise CredentialContractError(
                CredentialErrorCode.ALL_SLOTS_UNAVAILABLE,
                "credential session is closed",
            )

        if self._retry_current and self._current_slot is not None:
            self._retry_current = False
            return CredentialLease(
                slot=self._current_slot,
                secret=self._pool._secrets.load_secret(self._current_slot),
                distinct_slot_index=len(self._distinct_slots),
            )

        if len(self._distinct_slots) >= self._pool.policy.max_distinct_slots_per_request:
            raise self._unavailable("credential failover attempt bound reached")

        excluded = set(self._distinct_slots)
        eligible = self._pool._eligible_metadata(excluded)
        if not eligible:
            raise self._unavailable("all configured credential slots are unavailable")

        metadata = eligible[0]
        self._current_slot = metadata.slot
        self._distinct_slots.append(metadata.slot_id)
        return CredentialLease(
            slot=metadata.slot,
            secret=self._pool._secrets.load_secret(metadata.slot),
            distinct_slot_index=len(self._distinct_slots),
        )

    def report_success(self) -> CredentialHealthSnapshot:
        if self._current_slot is None or self._closed:
            raise RuntimeError("credential session has no active slot")
        snapshot = self._pool.record_test_result(
            self._current_slot.slot_id,
            CredentialTestResult.PASS,
        )
        self._closed = True
        return snapshot

    def report_error(
        self,
        code: ProviderErrorCode,
        *,
        retry_after_seconds: float | None = None,
    ) -> CredentialHealthSnapshot:
        if self._current_slot is None or self._closed:
            raise RuntimeError("credential session has no active slot")
        slot_id = self._current_slot.slot_id

        if code is ProviderErrorCode.INVALID_AUTH:
            self._retry_current = False
            snapshot = self._pool.record_test_result(
                slot_id,
                CredentialTestResult.INVALID_AUTH,
            )
            self._current_slot = None
            return snapshot

        if code is ProviderErrorCode.NETWORK_TIMEOUT:
            snapshot = self._pool.record_test_result(
                slot_id,
                CredentialTestResult.NETWORK_TIMEOUT,
            )
            used = self._network_retries.get(slot_id, 0)
            if used < self._pool.policy.max_network_retries_per_slot:
                self._network_retries[slot_id] = used + 1
                self._retry_current = True
            else:
                self._retry_current = False
                self._current_slot = None
            return snapshot

        if code is ProviderErrorCode.RATE_LIMIT_OR_QUOTA:
            self._retry_current = False
            snapshot = self._pool.record_test_result(
                slot_id,
                CredentialTestResult.RATE_LIMIT_OR_QUOTA,
                retry_after_seconds=retry_after_seconds,
            )
            return snapshot

        self._closed = True
        raise ProviderContractError(
            code,
            "provider failure is not eligible for credential failover",
        )
