from __future__ import annotations

import logging
from io import StringIO
from pathlib import Path

import pytest

from ai_ngerti_geopolitik.application.ai_contracts import (
    MASKED_CREDENTIAL_VALUE,
    CredentialContractError,
    CredentialErrorCode,
    CredentialMetadataError,
    CredentialSecret,
    CredentialSlotRef,
)
from ai_ngerti_geopolitik.application.credential_slots import CredentialSlotService
from ai_ngerti_geopolitik.application.ports import CredentialMetadataPort, CredentialPort
from ai_ngerti_geopolitik.domain import ProjectState
from ai_ngerti_geopolitik.infrastructure.in_memory_credentials import (
    InMemoryCredentialStore,
)
from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository


def _service() -> tuple[CredentialSlotService, InMemoryCredentialStore]:
    backend = InMemoryCredentialStore()
    return CredentialSlotService(backend, backend), backend


def test_slots_1_and_100_add_list_and_mask_without_raw_exposure() -> None:
    service, backend = _service()
    raw_one = "runtime-only-slot-one-value"
    raw_hundred = "runtime-only-slot-hundred-value"

    one = service.add_or_update(
        1,
        CredentialSecret(raw_one),
        label="Primary Gemini",
    )
    hundred = service.add_or_update(
        100,
        CredentialSecret(raw_hundred),
        label="Backup Gemini",
    )

    assert [item.slot_id for item in service.list_slots()] == [1, 100]
    assert one.masked_value == MASKED_CREDENTIAL_VALUE
    assert hundred.masked_value == MASKED_CREDENTIAL_VALUE
    assert service.masked_value(1) == MASKED_CREDENTIAL_VALUE
    assert raw_one not in repr(one)
    assert raw_hundred not in repr(hundred)
    assert raw_one not in repr(service)
    assert raw_hundred not in repr(backend)
    assert isinstance(backend, CredentialPort)
    assert isinstance(backend, CredentialMetadataPort)


def test_invalid_slots_are_rejected_before_storage() -> None:
    service, backend = _service()
    for slot_id in (0, 101, -1):
        with pytest.raises(CredentialContractError) as caught:
            service.add_or_update(slot_id, CredentialSecret("runtime-value"))
        assert caught.value.code is CredentialErrorCode.INVALID_SLOT

    assert service.list_slots() == ()
    assert repr(backend) == "InMemoryCredentialStore(slots=())"


def test_update_replaces_secret_preserves_enabled_and_updates_label() -> None:
    service, backend = _service()
    old_raw = "runtime-old-credential-value"
    new_raw = "runtime-new-credential-value"

    service.add_or_update(1, CredentialSecret(old_raw), label="Initial")
    service.set_enabled(1, False)
    updated = service.add_or_update(
        1,
        CredentialSecret(new_raw),
        label="Updated Label",
    )

    assert updated.label == "Updated Label"
    assert updated.enabled is False
    assert backend.load_secret(CredentialSlotRef(1)).reveal() == new_raw
    assert old_raw not in repr(service)
    assert new_raw not in repr(service)


def test_enable_disable_changes_metadata_only() -> None:
    service, backend = _service()
    raw = "runtime-toggle-credential-value"
    service.add_or_update(1, CredentialSecret(raw), label="Toggle Slot")
    before = backend.load_secret(CredentialSlotRef(1)).reveal()

    disabled = service.set_enabled(1, False)
    enabled = service.set_enabled(1, True)

    assert disabled.enabled is False
    assert enabled.enabled is True
    assert backend.load_secret(CredentialSlotRef(1)).reveal() == before


def test_delete_removes_secret_and_metadata_consistently() -> None:
    service, backend = _service()
    service.add_or_update(
        100,
        CredentialSecret("runtime-delete-credential-value"),
        label="Delete Me",
    )

    service.delete(100)

    slot = CredentialSlotRef(100)
    assert not backend.has_secret(slot)
    assert backend.load_metadata(slot) is None
    assert service.list_slots() == ()
    with pytest.raises(CredentialContractError) as caught:
        service.get(100)
    assert caught.value.code is CredentialErrorCode.NO_CREDENTIAL


def test_label_cannot_contain_raw_credential_and_failure_is_non_mutating() -> None:
    service, backend = _service()
    raw = "runtime-label-safety-value"

    with pytest.raises(CredentialMetadataError):
        service.add_or_update(
            1,
            CredentialSecret(raw),
            label=f"Do not persist {raw}",
        )

    assert service.list_slots() == ()
    assert not backend.has_secret(CredentialSlotRef(1))


def test_service_reopen_over_same_backend_retains_only_safe_metadata() -> None:
    service, backend = _service()
    raw = "runtime-reopen-credential-value"
    service.add_or_update(1, CredentialSecret(raw), label="Persistent Fake Slot")
    service.set_enabled(1, False)

    reopened = CredentialSlotService(backend, backend)
    item = reopened.get(1)

    assert item.label == "Persistent Fake Slot"
    assert item.enabled is False
    assert item.masked_value == MASKED_CREDENTIAL_VALUE
    assert raw not in repr(reopened)
    assert raw not in repr(item)


def test_project_persistence_and_safe_diagnostics_never_include_raw_secret(
    tmp_path: Path,
) -> None:
    service, backend = _service()
    raw = "runtime-persistence-credential-value"
    item = service.add_or_update(1, CredentialSecret(raw), label="Safe Slot")

    project = ProjectState.create("P-W6-002", "Credential separation")
    project_path = tmp_path / "credential-separation.angproj"
    JsonProjectRepository().save(project, project_path)

    stream = StringIO()
    handler = logging.StreamHandler(stream)
    logger = logging.getLogger("w6-002-safe-diagnostic")
    logger.handlers = [handler]
    logger.setLevel(logging.INFO)
    logger.propagate = False
    logger.info("slot=%r service=%r backend=%r", item, service, backend)
    handler.flush()

    persisted = project_path.read_text(encoding="utf-8")
    diagnostic = stream.getvalue()
    assert raw not in project.semantic_json(include_revision=True)
    assert raw not in persisted
    assert raw not in diagnostic
    assert MASKED_CREDENTIAL_VALUE in repr(item)


def test_missing_slot_errors_are_safe_and_do_not_echo_other_credentials() -> None:
    service, _backend = _service()
    raw = "runtime-safe-error-credential-value"
    service.add_or_update(1, CredentialSecret(raw), label="Primary")

    with pytest.raises(CredentialContractError) as caught:
        service.get(2)

    assert caught.value.code is CredentialErrorCode.NO_CREDENTIAL
    assert raw not in str(caught.value)
