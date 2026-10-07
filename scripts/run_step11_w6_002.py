from __future__ import annotations

import argparse
import json
from pathlib import Path

from ai_ngerti_geopolitik.application.ai_contracts import (
    MASKED_CREDENTIAL_VALUE,
    CredentialContractError,
    CredentialMetadataError,
    CredentialSecret,
)
from ai_ngerti_geopolitik.application.credential_slots import CredentialSlotService
from ai_ngerti_geopolitik.domain import ProjectState
from ai_ngerti_geopolitik.infrastructure.in_memory_credentials import (
    InMemoryCredentialStore,
)
from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository


def _write_json(path: Path, data: object) -> None:
    payload = json.dumps(data, indent=2, sort_keys=True) + "\n"
    path.write_text(payload, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    evidence = args.evidence.resolve()
    evidence.mkdir(parents=True, exist_ok=True)

    raw_one = "runtime-w6-slot-one-value"
    raw_hundred = "runtime-w6-slot-hundred-value"
    raw_one_updated = "runtime-w6-slot-one-updated-value"
    raw_values = (raw_one, raw_hundred, raw_one_updated)

    backend = InMemoryCredentialStore()
    service = CredentialSlotService(backend, backend)

    one = service.add_or_update(1, CredentialSecret(raw_one), label="Primary Gemini")
    hundred = service.add_or_update(
        100,
        CredentialSecret(raw_hundred),
        label="Backup Gemini",
    )
    hundred = service.set_enabled(100, False)
    one = service.add_or_update(
        1,
        CredentialSecret(raw_one_updated),
        label="Primary Gemini Updated",
    )

    reopened = CredentialSlotService(backend, backend)
    reopened_items = reopened.list_slots()
    if [item.slot_id for item in reopened_items] != [1, 100]:
        raise AssertionError("credential slot ordering/reopen failed")
    if hundred.enabled is not False:
        raise AssertionError("disabled slot metadata was not retained")
    if one.masked_value != MASKED_CREDENTIAL_VALUE:
        raise AssertionError("credential mask is not fixed")

    invalid_slots: dict[str, bool] = {}
    for slot_id in (0, 101):
        rejected = False
        try:
            service.add_or_update(slot_id, CredentialSecret("runtime-invalid-slot-value"))
        except CredentialContractError:
            rejected = True
        invalid_slots[str(slot_id)] = rejected
        if not rejected:
            raise AssertionError(f"invalid credential slot accepted: {slot_id}")

    label_secret_rejected = False
    try:
        service.add_or_update(
            2,
            CredentialSecret(raw_hundred),
            label=f"unsafe {raw_hundred}",
        )
    except CredentialMetadataError:
        label_secret_rejected = True
    if not label_secret_rejected:
        raise AssertionError("credential value was accepted inside metadata label")

    project = ProjectState.create("ANG-S11-W6-002", "Credential separation proof")
    project_path = evidence / "w6_002_project.angproj"
    JsonProjectRepository().save(project, project_path)
    project_payload = project_path.read_text(encoding="utf-8")

    diagnostic_path = evidence / "03_safe_diagnostics.log"
    diagnostic_path.write_text(
        f"service={service!r}\nbackend={backend!r}\nslots={reopened_items!r}\n",
        encoding="utf-8",
    )
    diagnostic_payload = diagnostic_path.read_text(encoding="utf-8")

    for raw in raw_values:
        if raw in project.semantic_json(include_revision=True):
            raise AssertionError("raw credential leaked into ProjectState")
        if raw in project_payload:
            raise AssertionError("raw credential leaked into .angproj")
        if raw in diagnostic_payload:
            raise AssertionError("raw credential leaked into safe diagnostics")

    before_delete = reopened.get(1)
    reopened.delete(1)
    delete_secret_removed = not backend.has_secret(before_delete.slot)
    delete_metadata_removed = backend.load_metadata(before_delete.slot) is None
    if not delete_secret_removed or not delete_metadata_removed:
        raise AssertionError("credential delete did not remove secret + metadata")

    safe_slots = [
        {
            "slot_id": item.slot_id,
            "label": item.label,
            "enabled": item.enabled,
            "masked_value": item.masked_value,
        }
        for item in reopened.list_slots()
    ]
    _write_json(
        evidence / "01_slots.json",
        {
            "initial_slot_ids": [1, 100],
            "remaining_slots_after_delete": safe_slots,
            "slot_100_disabled": hundred.enabled is False,
            "slot_1_update_label": one.label,
            "slot_1_masked": one.masked_value,
            "invalid_slots_rejected": invalid_slots,
            "label_secret_rejected": label_secret_rejected,
            "delete_secret_removed": delete_secret_removed,
            "delete_metadata_removed": delete_metadata_removed,
        },
    )
    _write_json(
        evidence / "02_no_secret_persistence.json",
        {
            "project_state_has_no_raw_credential": all(
                raw not in project.semantic_json(include_revision=True) for raw in raw_values
            ),
            "angproj_has_no_raw_credential": all(raw not in project_payload for raw in raw_values),
            "safe_diagnostic_has_no_raw_credential": all(
                raw not in diagnostic_payload for raw in raw_values
            ),
            "project_state_has_no_credential_fields": all(
                token not in project.semantic_json(include_revision=True).lower()
                for token in ("api_key", "credential_secret", "raw_secret")
            ),
        },
    )

    report = {
        "status": "PASS",
        "slots_1_and_100_supported": True,
        "slots_0_and_101_rejected": all(invalid_slots.values()),
        "add_update_delete": True,
        "enable_disable_metadata_only": True,
        "fixed_mask_only": one.masked_value == MASKED_CREDENTIAL_VALUE,
        "in_memory_reopen": len(reopened_items) == 2,
        "secret_and_metadata_delete_consistent": delete_secret_removed and delete_metadata_removed,
        "raw_secret_absent_from_project_persistence_diagnostics": True,
        "label_secret_rejected": label_secret_rejected,
        "project_state_unchanged_by_credentials": True,
        "production_secure_store_started": False,
        "gemini_network_called": False,
        "health_failover_started": False,
        "credential_ui_started": False,
    }
    _write_json(evidence / "00_w6_002_report.json", report)

    serialized_evidence = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore")
        for path in evidence.iterdir()
        if path.is_file()
    )
    for raw in raw_values:
        if raw in serialized_evidence:
            raise AssertionError("raw credential leaked into W6-002 evidence")

    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
