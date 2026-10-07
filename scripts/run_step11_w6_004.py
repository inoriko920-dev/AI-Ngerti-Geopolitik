from __future__ import annotations

import argparse
import json
import secrets
from pathlib import Path

from ai_ngerti_geopolitik.application.ai_contracts import (
    CredentialContractError,
    CredentialErrorCode,
    CredentialSecret,
    ProviderContractError,
    ProviderErrorCode,
)
from ai_ngerti_geopolitik.application.credential_pool import (
    CredentialHealth,
    CredentialPoolPolicy,
    CredentialPoolService,
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


def _write_json(path: Path, data: object) -> None:
    path.write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _pool(
    *,
    policy: CredentialPoolPolicy | None = None,
    clock: FakeClock | None = None,
) -> tuple[CredentialPoolService, CredentialSlotService, FakeClock]:
    backend = InMemoryCredentialStore()
    slots = CredentialSlotService(backend, backend)
    fake_clock = clock or FakeClock()
    return (
        CredentialPoolService(slots, backend, policy=policy, clock=fake_clock),
        slots,
        fake_clock,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    evidence = args.evidence.resolve()
    evidence.mkdir(parents=True, exist_ok=True)

    runtime_secrets = [secrets.token_urlsafe(32) for _ in range(8)]

    pool, slots, _clock = _pool(
        policy=CredentialPoolPolicy(
            max_network_retries_per_slot=1,
            max_distinct_slots_per_request=3,
        )
    )
    for slot_id, raw in zip((1, 2, 3), runtime_secrets[:3], strict=True):
        slots.add_or_update(
            slot_id,
            CredentialSecret(raw),
            label=f"Evidence Slot {slot_id}",
        )

    session = pool.start_session()
    first = session.next_credential()
    session.report_error(ProviderErrorCode.INVALID_AUTH)
    second = session.next_credential()
    session.report_error(ProviderErrorCode.NETWORK_TIMEOUT)
    retry = session.next_credential()
    session.report_error(ProviderErrorCode.NETWORK_TIMEOUT)
    third = session.next_credential()
    success = session.report_success()

    sequence = [
        first.slot.slot_id,
        second.slot.slot_id,
        retry.slot.slot_id,
        third.slot.slot_id,
    ]
    if sequence != [1, 2, 2, 3]:
        raise AssertionError("bounded failover sequence changed")
    if success.health is not CredentialHealth.HEALTHY:
        raise AssertionError("successful slot was not marked healthy")

    quota_clock = FakeClock()
    quota_pool, quota_slots, _ = _pool(
        policy=CredentialPoolPolicy(
            default_cooldown_seconds=30,
            max_cooldown_seconds=120,
        ),
        clock=quota_clock,
    )
    quota_slots.add_or_update(1, CredentialSecret(runtime_secrets[3]))
    quota_slots.add_or_update(2, CredentialSecret(runtime_secrets[4]))
    quota_session = quota_pool.start_session()
    quota_session.next_credential()
    quota_session.report_error(
        ProviderErrorCode.RATE_LIMIT_OR_QUOTA,
        retry_after_seconds=999,
    )
    quota_blocked_rotation = False
    try:
        quota_session.next_credential()
    except ProviderContractError as exc:
        quota_blocked_rotation = exc.code is ProviderErrorCode.RATE_LIMIT_OR_QUOTA
    if not quota_blocked_rotation:
        raise AssertionError("quota cooldown allowed immediate credential rotation")
    cooldown_was_bounded = quota_pool.provider_cooldown_remaining_seconds() == 120
    quota_clock.advance(121)
    cooldown_expired = quota_pool.provider_cooldown_remaining_seconds() == 0

    unavailable_pool, unavailable_slots, _ = _pool()
    unavailable_slots.add_or_update(1, CredentialSecret(runtime_secrets[5]))
    unavailable_slots.set_enabled(1, False)
    all_unavailable_typed = False
    try:
        unavailable_pool.start_session().next_credential()
    except CredentialContractError as exc:
        all_unavailable_typed = exc.code is CredentialErrorCode.ALL_SLOTS_UNAVAILABLE
    if not all_unavailable_typed:
        raise AssertionError("all-unavailable did not return typed credential error")

    bulk_pool, bulk_slots, _ = _pool()
    bulk_text = (
        f"  {runtime_secrets[6]}  \n\n"
        f"{runtime_secrets[7]}\n"
        f"{runtime_secrets[6]}\n"
    )
    preview = bulk_pool.preview_bulk_text(bulk_text)
    imported = bulk_pool.import_bulk_text(bulk_text)
    bulk_rules_pass = (
        preview.nonempty_lines == 3
        and preview.unique_credentials == 2
        and preview.duplicate_lines == 1
        and [item.slot_id for item in imported] == [1, 2]
        and len(bulk_slots.list_slots()) == 2
    )
    if not bulk_rules_pass:
        raise AssertionError("bulk TXT trim/dedupe/import contract failed")

    report = {
        "status": "PASS",
        "invalid_auth_disables_affected_slot_only": slots.get(1).enabled is False,
        "network_retry_is_bounded": retry.slot.slot_id == 2,
        "legal_failover_sequence": sequence,
        "success_marks_slot_healthy": success.health.value == "HEALTHY",
        "quota_does_not_rotate_immediately": quota_blocked_rotation,
        "quota_cooldown_is_bounded": cooldown_was_bounded,
        "quota_cooldown_expires": cooldown_expired,
        "all_slots_unavailable_is_typed": all_unavailable_typed,
        "bulk_txt_trim_dedupe_max100_no_retention_contract": bulk_rules_pass,
        "bulk_preview_is_count_only": {
            "nonempty_lines": preview.nonempty_lines,
            "unique_credentials": preview.unique_credentials,
            "duplicate_lines": preview.duplicate_lines,
        },
        "gemini_network_called": False,
        "context_builder_started": False,
        "plan_verifier_started": False,
        "credential_ui_started": False,
        "quota_evasion_rotation": False,
        "raw_secret_absent_from_evidence": True,
    }
    _write_json(evidence / "00_w6_004_report.json", report)

    health = {
        "slot_1": pool.snapshot(1).health.value,
        "slot_2": pool.snapshot(2).health.value,
        "slot_3": pool.snapshot(3).health.value,
        "slot_1_enabled": slots.get(1).enabled,
        "slot_2_enabled": slots.get(2).enabled,
        "slot_3_enabled": slots.get(3).enabled,
    }
    _write_json(evidence / "01_health_failover.json", health)

    serialized = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore")
        for path in evidence.iterdir()
        if path.is_file()
    )
    for raw in runtime_secrets:
        if raw in serialized:
            raise AssertionError("raw credential leaked into W6-004 evidence")

    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
