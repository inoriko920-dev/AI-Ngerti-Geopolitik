from __future__ import annotations

import sys

import pytest

from ai_ngerti_geopolitik.application.ai_contracts import (
    CredentialContractError,
    CredentialErrorCode,
    CredentialSecret,
    CredentialSlotRef,
)
from ai_ngerti_geopolitik.application.ports import CredentialPort
from ai_ngerti_geopolitik.infrastructure.windows_credentials import (
    WindowsCredentialApiError,
    WindowsCredentialStore,
    WindowsCredentialStoreError,
)


class FakeCredentialApi:
    def __init__(self) -> None:
        self.values: dict[str, bytes] = {}

    def write(self, target: str, payload: bytes) -> None:
        self.values[target] = bytes(payload)

    def read(self, target: str) -> bytes:
        try:
            return self.values[target]
        except KeyError as exc:
            raise WindowsCredentialApiError("read", 1168) from exc

    def delete(self, target: str) -> None:
        if target not in self.values:
            raise WindowsCredentialApiError("delete", 1168)
        del self.values[target]


class FailingCredentialApi(FakeCredentialApi):
    def __init__(self, operation: str) -> None:
        super().__init__()
        self.operation = operation

    def write(self, target: str, payload: bytes) -> None:
        if self.operation == "write":
            raise WindowsCredentialApiError("write", 5)
        super().write(target, payload)

    def read(self, target: str) -> bytes:
        if self.operation == "read":
            raise WindowsCredentialApiError("read", 5)
        return super().read(target)

    def delete(self, target: str) -> None:
        if self.operation == "delete":
            raise WindowsCredentialApiError("delete", 5)
        super().delete(target)


def test_slot_1_and_100_round_trip_and_reopen_over_same_secure_backend() -> None:
    api = FakeCredentialApi()
    first = WindowsCredentialStore("ANG/W6-003", api=api)
    raw_one = "unit-slot-one-secret"
    raw_hundred = "unit-slot-hundred-secret"

    first.store_secret(CredentialSlotRef(1), CredentialSecret(raw_one))
    first.store_secret(CredentialSlotRef(100), CredentialSecret(raw_hundred))

    reopened = WindowsCredentialStore("ANG/W6-003", api=api)
    assert reopened.load_secret(CredentialSlotRef(1)).reveal() == raw_one
    assert reopened.load_secret(CredentialSlotRef(100)).reveal() == raw_hundred
    assert reopened.has_secret(CredentialSlotRef(1))
    assert reopened.has_secret(CredentialSlotRef(100))
    assert isinstance(reopened, CredentialPort)
    assert raw_one not in repr(reopened)
    assert raw_hundred not in repr(reopened)


def test_delete_is_idempotent_and_missing_load_is_typed_no_credential() -> None:
    api = FakeCredentialApi()
    store = WindowsCredentialStore("ANG/W6-003", api=api)
    slot = CredentialSlotRef(1)
    store.store_secret(slot, CredentialSecret("unit-delete-secret"))

    store.delete_secret(slot)
    store.delete_secret(slot)

    assert not store.has_secret(slot)
    with pytest.raises(CredentialContractError) as caught:
        store.load_secret(slot)
    assert caught.value.code is CredentialErrorCode.NO_CREDENTIAL


@pytest.mark.parametrize("operation", ["write", "read", "delete"])
def test_native_backend_failures_are_safe_and_never_echo_secret(operation: str) -> None:
    raw = "unit-never-echo-this-secret"
    store = WindowsCredentialStore(
        "ANG/W6-003",
        api=FailingCredentialApi(operation),
    )
    slot = CredentialSlotRef(1)

    with pytest.raises(WindowsCredentialStoreError) as caught:
        if operation == "write":
            store.store_secret(slot, CredentialSecret(raw))
        elif operation == "read":
            store.load_secret(slot)
        else:
            store.delete_secret(slot)

    assert raw not in str(caught.value)
    assert raw not in repr(store)
    assert "error 5" in str(caught.value)


def test_invalid_slots_are_rejected_before_targeting_windows_store() -> None:
    api = FakeCredentialApi()
    store = WindowsCredentialStore("ANG/W6-003", api=api)

    for slot_id in (0, 101):
        with pytest.raises(CredentialContractError) as caught:
            store.has_secret(CredentialSlotRef(slot_id))
        assert caught.value.code is CredentialErrorCode.INVALID_SLOT

    assert api.values == {}


def test_default_native_store_is_windows_only() -> None:
    if sys.platform == "win32":
        store = WindowsCredentialStore("ANG/W6-003-native-constructor")
        assert isinstance(store, CredentialPort)
    else:
        with pytest.raises(WindowsCredentialStoreError, match="unavailable"):
            WindowsCredentialStore("ANG/W6-003-native-constructor")
