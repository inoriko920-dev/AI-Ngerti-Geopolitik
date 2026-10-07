"""Deterministic W6-002 in-memory credential backend.

Qualification/test fake only. This is not the production Windows secure-store
adapter; that belongs to W6-003.
"""

from __future__ import annotations

from ai_ngerti_geopolitik.application.ai_contracts import (
    CredentialContractError,
    CredentialErrorCode,
    CredentialSecret,
    CredentialSlotMetadata,
    CredentialSlotRef,
)


class InMemoryCredentialStore:
    __slots__ = ("_metadata", "_secrets")

    def __init__(self) -> None:
        self._secrets: dict[int, CredentialSecret] = {}
        self._metadata: dict[int, CredentialSlotMetadata] = {}

    def __repr__(self) -> str:
        return f"InMemoryCredentialStore(slots={tuple(sorted(self._secrets))})"

    def store_secret(
        self,
        slot: CredentialSlotRef,
        secret: CredentialSecret,
    ) -> None:
        self._secrets[slot.slot_id] = CredentialSecret(secret.reveal())

    def load_secret(self, slot: CredentialSlotRef) -> CredentialSecret:
        try:
            secret = self._secrets[slot.slot_id]
        except KeyError as exc:
            raise CredentialContractError(
                CredentialErrorCode.NO_CREDENTIAL,
                "credential slot is not configured",
            ) from exc
        return CredentialSecret(secret.reveal())

    def delete_secret(self, slot: CredentialSlotRef) -> None:
        self._secrets.pop(slot.slot_id, None)

    def has_secret(self, slot: CredentialSlotRef) -> bool:
        return slot.slot_id in self._secrets

    def save_metadata(self, metadata: CredentialSlotMetadata) -> None:
        self._metadata[metadata.slot_id] = metadata

    def load_metadata(
        self,
        slot: CredentialSlotRef,
    ) -> CredentialSlotMetadata | None:
        return self._metadata.get(slot.slot_id)

    def delete_metadata(self, slot: CredentialSlotRef) -> None:
        self._metadata.pop(slot.slot_id, None)

    def list_metadata(self) -> tuple[CredentialSlotMetadata, ...]:
        return tuple(self._metadata[key] for key in sorted(self._metadata))
