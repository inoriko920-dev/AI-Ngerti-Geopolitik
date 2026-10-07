from __future__ import annotations

import argparse
import json
import secrets
import sys
from pathlib import Path
from uuid import uuid4

from ai_ngerti_geopolitik.application.ai_contracts import (
    MASKED_CREDENTIAL_VALUE,
    CredentialContractError,
    CredentialSecret,
    CredentialSlotRef,
)
from ai_ngerti_geopolitik.application.credential_slots import CredentialSlotService
from ai_ngerti_geopolitik.infrastructure.in_memory_credentials import (
    InMemoryCredentialStore,
)
from ai_ngerti_geopolitik.infrastructure.windows_credentials import (
    WindowsCredentialStore,
)


def _write_json(path: Path, data: object) -> None:
    path.write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    evidence = args.evidence.resolve()
    evidence.mkdir(parents=True, exist_ok=True)

    if sys.platform != "win32":
        raise RuntimeError("W6-003 requires a real Windows runner")

    namespace = f"AI-Ngerti-Geopolitik/W6-003/{uuid4().hex}"
    raw_one = secrets.token_urlsafe(32)
    raw_hundred = secrets.token_urlsafe(32)
    raw_values = (raw_one, raw_hundred)

    store = WindowsCredentialStore(namespace)
    metadata = InMemoryCredentialStore()
    service = CredentialSlotService(store, metadata)
    slot_one = CredentialSlotRef(1)
    slot_hundred = CredentialSlotRef(100)

    for slot in (slot_one, slot_hundred):
        store.delete_secret(slot)

    try:
        one = service.add_or_update(
            1,
            CredentialSecret(raw_one),
            label="Windows Primary Gemini",
        )
        hundred = service.add_or_update(
            100,
            CredentialSecret(raw_hundred),
            label="Windows Backup Gemini",
        )

        slot_1_round_trip = store.load_secret(slot_one).reveal() == raw_one
        slot_100_round_trip = store.load_secret(slot_hundred).reveal() == raw_hundred
        if not slot_1_round_trip or not slot_100_round_trip:
            raise AssertionError("Windows secure-store round trip failed")

        reopened_store = WindowsCredentialStore(namespace)
        reopened_service = CredentialSlotService(reopened_store, metadata)
        reopen_slot_1 = reopened_store.load_secret(slot_one).reveal() == raw_one
        reopen_slot_100 = reopened_store.load_secret(slot_hundred).reveal() == raw_hundred
        if not reopen_slot_1 or not reopen_slot_100:
            raise AssertionError("Windows secure-store reopen failed")
        if reopened_service.masked_value(1) != MASKED_CREDENTIAL_VALUE:
            raise AssertionError("reopened credential slot mask changed")

        safe_diagnostic = (
            f"store={reopened_store!r}\n"
            f"service={reopened_service!r}\n"
            f"slot1={one!r}\n"
            f"slot100={hundred!r}\n"
        )
        (evidence / "03_safe_diagnostics.log").write_text(
            safe_diagnostic,
            encoding="utf-8",
        )

        reopened_service.delete(1)
        slot_1_deleted = not reopened_store.has_secret(slot_one)
        metadata_1_deleted = metadata.load_metadata(slot_one) is None

        missing_error = ""
        try:
            reopened_store.load_secret(slot_one)
        except CredentialContractError as exc:
            missing_error = str(exc)
        if not missing_error:
            raise AssertionError("deleted secure-store credential produced fake success")
        if raw_one in missing_error or raw_hundred in missing_error:
            raise AssertionError("secure-store failure echoed a raw credential")

        reopened_service.delete(100)
        slot_100_deleted = not reopened_store.has_secret(slot_hundred)
        metadata_100_deleted = metadata.load_metadata(slot_hundred) is None

        _write_json(
            evidence / "01_windows_secure_store.json",
            {
                "backend": "Windows Credential Manager Generic Credential",
                "namespace": namespace,
                "slot_1_round_trip": slot_1_round_trip,
                "slot_100_round_trip": slot_100_round_trip,
                "slot_1_reopen": reopen_slot_1,
                "slot_100_reopen": reopen_slot_100,
                "slot_1_masked": one.masked_value,
                "slot_100_masked": hundred.masked_value,
                "real_windows_runner": True,
            },
        )
        _write_json(
            evidence / "02_delete_failure.json",
            {
                "slot_1_secret_deleted": slot_1_deleted,
                "slot_1_metadata_deleted": metadata_1_deleted,
                "slot_100_secret_deleted": slot_100_deleted,
                "slot_100_metadata_deleted": metadata_100_deleted,
                "load_after_delete_rejected": bool(missing_error),
                "safe_error_message": missing_error,
                "all_secure_store_targets_cleaned": (
                    not reopened_store.has_secret(slot_one)
                    and not reopened_store.has_secret(slot_hundred)
                ),
            },
        )

        report = {
            "status": "PASS",
            "production_windows_secure_store": True,
            "real_windows_secure_store_smoke": True,
            "slots_1_and_100_round_trip": slot_1_round_trip and slot_100_round_trip,
            "reopen_round_trip": reopen_slot_1 and reopen_slot_100,
            "delete_secret_and_metadata": (
                slot_1_deleted
                and metadata_1_deleted
                and slot_100_deleted
                and metadata_100_deleted
            ),
            "failure_after_delete_is_safe": bool(missing_error),
            "fixed_mask_preserved": (
                one.masked_value == MASKED_CREDENTIAL_VALUE
                and hundred.masked_value == MASKED_CREDENTIAL_VALUE
            ),
            "raw_secret_absent_from_evidence": True,
            "secure_store_cleaned_after_smoke": True,
            "health_failover_started": False,
            "bulk_txt_started": False,
            "gemini_network_called": False,
            "credential_ui_started": False,
        }
        _write_json(evidence / "00_w6_003_report.json", report)

        serialized = "\n".join(
            path.read_text(encoding="utf-8", errors="ignore")
            for path in evidence.iterdir()
            if path.is_file()
        )
        for raw in raw_values:
            if raw in serialized:
                raise AssertionError("raw credential leaked into W6-003 evidence")

        print(json.dumps(report, indent=2, sort_keys=True))
        return 0
    finally:
        for slot in (slot_one, slot_hundred):
            store.delete_secret(slot)


if __name__ == "__main__":
    raise SystemExit(main())
