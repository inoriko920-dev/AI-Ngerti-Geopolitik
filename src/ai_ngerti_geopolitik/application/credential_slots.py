"""W6-002 logical credential-slot orchestration.

Raw credential values stay behind CredentialPort. This service exposes only
non-secret metadata and a constant masked marker.
"""

from __future__ import annotations

from dataclasses import replace

from ai_ngerti_geopolitik.application.ai_contracts import (
    MASKED_CREDENTIAL_VALUE,
    CredentialContractError,
    CredentialErrorCode,
    CredentialMetadataError,
    CredentialSecret,
    CredentialSlotMetadata,
    CredentialSlotRef,
)
from ai_ngerti_geopolitik.application.ports import CredentialMetadataPort, CredentialPort


class CredentialSlotService:
    """Coordinates secure secrets with non-secret logical-slot metadata."""

    __slots__ = ("_metadata", "_secrets")

    def __init__(
        self,
        secrets: CredentialPort,
        metadata: CredentialMetadataPort,
    ) -> None:
        self._secrets = secrets
        self._metadata = metadata

    def __repr__(self) -> str:
        slots = tuple(item.slot_id for item in self.list_slots())
        return f"CredentialSlotService(slots={slots})"

    @staticmethod
    def _default_label(slot: CredentialSlotRef) -> str:
        return f"Gemini Slot {slot.slot_id:03d}"

    @staticmethod
    def _validate_label_does_not_contain_secret(
        label: str,
        secret: CredentialSecret,
    ) -> None:
        raw = secret.reveal()
        if raw and raw in label:
            raise CredentialMetadataError(
                "credential slot label cannot contain the credential value"
            )

    def add_or_update(
        self,
        slot_id: int,
        secret: CredentialSecret,
        *,
        label: str | None = None,
    ) -> CredentialSlotMetadata:
        slot = CredentialSlotRef(slot_id)
        previous_metadata = self._metadata.load_metadata(slot)
        had_secret = self._secrets.has_secret(slot)
        previous_secret = self._secrets.load_secret(slot) if had_secret else None

        effective_label = (
            label
            if label is not None
            else (
                previous_metadata.label
                if previous_metadata is not None
                else self._default_label(slot)
            )
        )
        enabled = previous_metadata.enabled if previous_metadata is not None else True
        candidate = CredentialSlotMetadata(slot=slot, label=effective_label, enabled=enabled)
        self._validate_label_does_not_contain_secret(candidate.label, secret)

        try:
            self._secrets.store_secret(slot, secret)
            self._metadata.save_metadata(candidate)
        except Exception:
            if previous_secret is not None:
                self._secrets.store_secret(slot, previous_secret)
            else:
                self._secrets.delete_secret(slot)
            if previous_metadata is not None:
                self._metadata.save_metadata(previous_metadata)
            else:
                self._metadata.delete_metadata(slot)
            raise
        return candidate

    def get(self, slot_id: int) -> CredentialSlotMetadata:
        slot = CredentialSlotRef(slot_id)
        metadata = self._metadata.load_metadata(slot)
        if metadata is None or not self._secrets.has_secret(slot):
            raise CredentialContractError(
                CredentialErrorCode.NO_CREDENTIAL,
                "credential slot is not configured",
            )
        return metadata

    def list_slots(self) -> tuple[CredentialSlotMetadata, ...]:
        return tuple(
            metadata
            for metadata in sorted(
                self._metadata.list_metadata(),
                key=lambda item: item.slot_id,
            )
            if self._secrets.has_secret(metadata.slot)
        )

    def masked_value(self, slot_id: int) -> str:
        self.get(slot_id)
        return MASKED_CREDENTIAL_VALUE

    def set_enabled(self, slot_id: int, enabled: bool) -> CredentialSlotMetadata:
        current = self.get(slot_id)
        updated = replace(current, enabled=enabled)
        self._metadata.save_metadata(updated)
        return updated

    def delete(self, slot_id: int) -> None:
        slot = CredentialSlotRef(slot_id)
        previous_metadata = self._metadata.load_metadata(slot)
        had_secret = self._secrets.has_secret(slot)
        if previous_metadata is None and not had_secret:
            raise CredentialContractError(
                CredentialErrorCode.NO_CREDENTIAL,
                "credential slot is not configured",
            )
        previous_secret = self._secrets.load_secret(slot) if had_secret else None
        try:
            self._secrets.delete_secret(slot)
            self._metadata.delete_metadata(slot)
        except Exception:
            if previous_secret is not None:
                self._secrets.store_secret(slot, previous_secret)
            if previous_metadata is not None:
                self._metadata.save_metadata(previous_metadata)
            raise
