from __future__ import annotations

import pytest

from ai_ngerti_geopolitik.application.ai_contracts import (
    CredentialContractError,
    CredentialErrorCode,
    CredentialMetadataError,
    CredentialSecret,
    ProviderContractError,
    ProviderErrorCode,
)
from ai_ngerti_geopolitik.application.credential_pool import (
    CredentialHealth,
    CredentialPoolPolicy,
    CredentialPoolService,
    CredentialTestResult,
)
from ai_ngerti_geopolitik.application.credential_slots import CredentialSlotService
from ai_ngerti_geopolitik.infrastructure.in_memory_credentials import (
    InMemoryCredentialStore,
)


class FakeClock:
    def __init__(self, value: float = 1000.0) -> None:
        self.value = value

    def __call__(self) -> float:
        return self.value

    def advance(self, seconds: float) -> None:
        self.value += seconds


def _pool(
    *,
    policy: CredentialPoolPolicy | None = None,
    clock: FakeClock | None = None,
) -> tuple[CredentialPoolService, CredentialSlotService, InMemoryCredentialStore, FakeClock]:
    backend = InMemoryCredentialStore()
    slots = CredentialSlotService(backend, backend)
    fake_clock = clock or FakeClock()
    pool = CredentialPoolService(
        slots,
        backend,
        policy=policy,
        clock=fake_clock,
    )
    return pool, slots, backend, fake_clock


def _add(slots: CredentialSlotService, slot_id: int, raw: str) -> None:
    slots.add_or_update(
        slot_id,
        CredentialSecret(raw),
        label=f"Gemini {slot_id}",
    )


def test_health_snapshots_are_non_secret_and_success_resets_transient_failures() -> None:
    pool, slots, _backend, _clock = _pool()
    raw = "runtime-health-secret"
    _add(slots, 1, raw)

    before = pool.snapshot(1)
    assert before.health is CredentialHealth.UNKNOWN
    assert before.last_result is CredentialTestResult.NEVER_TESTED

    degraded = pool.record_test_result(1, CredentialTestResult.NETWORK_TIMEOUT)
    assert degraded.health is CredentialHealth.NETWORK_DEGRADED
    assert degraded.network_failures == 1

    healthy = pool.record_test_result(1, CredentialTestResult.PASS)
    assert healthy.health is CredentialHealth.HEALTHY
    assert healthy.network_failures == 0
    assert raw not in repr(pool)
    assert raw not in repr(healthy)


def test_invalid_auth_disables_only_affected_slot_and_allows_legal_failover() -> None:
    pool, slots, _backend, _clock = _pool()
    raw_one = "runtime-invalid-auth-one"
    raw_two = "runtime-invalid-auth-two"
    _add(slots, 1, raw_one)
    _add(slots, 2, raw_two)

    session = pool.start_session()
    first = session.next_credential()
    assert first.slot.slot_id == 1
    assert first.secret.reveal() == raw_one

    invalid = session.report_error(ProviderErrorCode.INVALID_AUTH)
    assert invalid.health is CredentialHealth.INVALID_AUTH
    assert slots.get(1).enabled is False
    assert slots.get(2).enabled is True

    second = session.next_credential()
    assert second.slot.slot_id == 2
    assert second.secret.reveal() == raw_two
    success = session.report_success()
    assert success.health is CredentialHealth.HEALTHY


def test_network_timeout_retries_same_slot_once_then_fails_over() -> None:
    policy = CredentialPoolPolicy(
        max_network_retries_per_slot=1,
        max_distinct_slots_per_request=3,
    )
    pool, slots, _backend, _clock = _pool(policy=policy)
    _add(slots, 1, "runtime-network-one")
    _add(slots, 2, "runtime-network-two")

    session = pool.start_session()
    first = session.next_credential()
    assert first.slot.slot_id == 1

    session.report_error(ProviderErrorCode.NETWORK_TIMEOUT)
    retry = session.next_credential()
    assert retry.slot.slot_id == 1

    session.report_error(ProviderErrorCode.NETWORK_TIMEOUT)
    fallback = session.next_credential()
    assert fallback.slot.slot_id == 2
    assert pool.snapshot(1).network_failures == 2


def test_rate_limit_sets_bounded_provider_cooldown_and_does_not_rotate_immediately() -> None:
    clock = FakeClock()
    policy = CredentialPoolPolicy(
        default_cooldown_seconds=30,
        max_cooldown_seconds=120,
    )
    pool, slots, _backend, _ = _pool(policy=policy, clock=clock)
    _add(slots, 1, "runtime-quota-one")
    _add(slots, 2, "runtime-quota-two")

    session = pool.start_session()
    assert session.next_credential().slot.slot_id == 1
    cooled = session.report_error(
        ProviderErrorCode.RATE_LIMIT_OR_QUOTA,
        retry_after_seconds=999,
    )
    assert cooled.health is CredentialHealth.COOLDOWN
    assert pool.provider_cooldown_remaining_seconds() == 120

    with pytest.raises(ProviderContractError) as caught:
        session.next_credential()
    assert caught.value.code is ProviderErrorCode.RATE_LIMIT_OR_QUOTA

    clock.advance(121)
    resumed = pool.start_session().next_credential()
    assert resumed.slot.slot_id in {1, 2}
    assert pool.provider_cooldown_remaining_seconds() == 0


def test_all_slots_unavailable_is_typed_and_safe() -> None:
    pool, slots, _backend, _clock = _pool()
    raw = "runtime-all-unavailable-secret"
    _add(slots, 1, raw)
    slots.set_enabled(1, False)

    with pytest.raises(CredentialContractError) as caught:
        pool.start_session().next_credential()
    assert caught.value.code is CredentialErrorCode.ALL_SLOTS_UNAVAILABLE
    assert raw not in str(caught.value)


def test_distinct_slot_attempt_bound_stops_unbounded_rotation() -> None:
    policy = CredentialPoolPolicy(
        max_network_retries_per_slot=0,
        max_distinct_slots_per_request=2,
    )
    pool, slots, _backend, _clock = _pool(policy=policy)
    for slot_id in (1, 2, 3):
        _add(slots, slot_id, f"runtime-bound-{slot_id}")

    session = pool.start_session()
    assert session.next_credential().slot.slot_id == 1
    session.report_error(ProviderErrorCode.NETWORK_TIMEOUT)
    assert session.next_credential().slot.slot_id == 2
    session.report_error(ProviderErrorCode.NETWORK_TIMEOUT)

    with pytest.raises(CredentialContractError) as caught:
        session.next_credential()
    assert caught.value.code is CredentialErrorCode.ALL_SLOTS_UNAVAILABLE
    assert slots.get(3).enabled is True


def test_non_credential_provider_failure_is_not_rotated() -> None:
    pool, slots, _backend, _clock = _pool()
    _add(slots, 1, "runtime-malformed-one")
    _add(slots, 2, "runtime-malformed-two")
    session = pool.start_session()
    assert session.next_credential().slot.slot_id == 1

    with pytest.raises(ProviderContractError) as caught:
        session.report_error(ProviderErrorCode.MALFORMED_RESPONSE)
    assert caught.value.code is ProviderErrorCode.MALFORMED_RESPONSE

    with pytest.raises(CredentialContractError):
        session.next_credential()


def test_bulk_txt_preview_trim_dedupe_import_and_no_plaintext_repr() -> None:
    pool, slots, backend, _clock = _pool()
    raw_one = "runtime-bulk-one"
    raw_two = "runtime-bulk-two"
    text = f"  {raw_one}  \n\n{raw_two}\n{raw_one}\n"

    preview = pool.preview_bulk_text(text)
    assert preview.nonempty_lines == 3
    assert preview.unique_credentials == 2
    assert preview.duplicate_lines == 1
    assert preview.available_slots == 100
    assert preview.can_import is True
    assert raw_one not in repr(preview)
    assert raw_two not in repr(pool)

    imported = pool.import_bulk_text(text)
    assert [item.slot_id for item in imported] == [1, 2]
    assert len(slots.list_slots()) == 2
    assert backend.load_secret(imported[0].slot).reveal() == raw_one
    assert backend.load_secret(imported[1].slot).reveal() == raw_two
    assert raw_one not in repr(imported)
    assert raw_two not in repr(pool)


def test_bulk_txt_rejects_more_than_100_unique_without_mutation() -> None:
    pool, slots, _backend, _clock = _pool()
    text = "\n".join(f"runtime-overflow-{index}" for index in range(101))

    with pytest.raises(CredentialMetadataError, match="at most 100"):
        pool.preview_bulk_text(text)
    with pytest.raises(CredentialMetadataError, match="at most 100"):
        pool.import_bulk_text(text)
    assert slots.list_slots() == ()


def test_bulk_txt_capacity_preflight_prevents_partial_import() -> None:
    pool, slots, _backend, _clock = _pool()
    for slot_id in range(1, 100):
        _add(slots, slot_id, f"runtime-existing-{slot_id}")

    with pytest.raises(CredentialMetadataError, match="insufficient free slots"):
        pool.import_bulk_text("runtime-new-one\nruntime-new-two\n")

    assert len(slots.list_slots()) == 99
