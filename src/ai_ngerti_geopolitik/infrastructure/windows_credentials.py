"""Windows Credential Manager secure-store adapter for W6-003.

Raw secrets remain behind CredentialPort. This module uses the native Windows
Generic Credential API and never persists secret values in project state or
plain-text application files.
"""

from __future__ import annotations

import ctypes
import sys
from typing import Any, Protocol

from ctypes import wintypes

from ai_ngerti_geopolitik.application.ai_contracts import (
    CredentialContractError,
    CredentialErrorCode,
    CredentialSecret,
    CredentialSlotRef,
)

_CRED_TYPE_GENERIC = 1
_CRED_PERSIST_LOCAL_MACHINE = 2
_ERROR_NOT_FOUND = 1168
_MAX_CREDENTIAL_BLOB_BYTES = 2560


class WindowsCredentialStoreError(RuntimeError):
    """Safe secure-store failure that never embeds the credential value."""


class WindowsCredentialApiError(RuntimeError):
    """Native API failure carrying only operation + Windows error code."""

    def __init__(self, operation: str, error_code: int) -> None:
        self.operation = operation
        self.error_code = error_code
        super().__init__(
            f"Windows credential API {operation} failed with error {error_code}"
        )


class _CredentialApi(Protocol):
    def write(self, target: str, payload: bytes) -> None: ...

    def read(self, target: str) -> bytes: ...

    def delete(self, target: str) -> None: ...


class _CredentialW(ctypes.Structure):
    _fields_ = [
        ("Flags", wintypes.DWORD),
        ("Type", wintypes.DWORD),
        ("TargetName", wintypes.LPWSTR),
        ("Comment", wintypes.LPWSTR),
        ("LastWritten", wintypes.FILETIME),
        ("CredentialBlobSize", wintypes.DWORD),
        ("CredentialBlob", ctypes.POINTER(ctypes.c_ubyte)),
        ("Persist", wintypes.DWORD),
        ("AttributeCount", wintypes.DWORD),
        ("Attributes", ctypes.c_void_p),
        ("TargetAlias", wintypes.LPWSTR),
        ("UserName", wintypes.LPWSTR),
    ]


class _NativeWindowsCredentialApi:
    __slots__ = ("_cred_delete", "_cred_free", "_cred_read", "_cred_write")

    def __init__(self) -> None:
        if sys.platform != "win32":
            raise WindowsCredentialStoreError(
                "Windows Credential Manager is unavailable on this platform"
            )
        win_dll = getattr(ctypes, "WinDLL", None)
        if win_dll is None:
            raise WindowsCredentialStoreError(
                "Windows Credential Manager API loader is unavailable"
            )
        advapi: Any = win_dll("Advapi32.dll", use_last_error=True)

        self._cred_write = advapi.CredWriteW
        self._cred_write.argtypes = [ctypes.POINTER(_CredentialW), wintypes.DWORD]
        self._cred_write.restype = wintypes.BOOL

        self._cred_read = advapi.CredReadW
        self._cred_read.argtypes = [
            wintypes.LPCWSTR,
            wintypes.DWORD,
            wintypes.DWORD,
            ctypes.POINTER(ctypes.POINTER(_CredentialW)),
        ]
        self._cred_read.restype = wintypes.BOOL

        self._cred_delete = advapi.CredDeleteW
        self._cred_delete.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD]
        self._cred_delete.restype = wintypes.BOOL

        self._cred_free = advapi.CredFree
        self._cred_free.argtypes = [ctypes.c_void_p]
        self._cred_free.restype = None

    @staticmethod
    def _raise(operation: str) -> None:
        raise WindowsCredentialApiError(operation, ctypes.get_last_error())

    def write(self, target: str, payload: bytes) -> None:
        if len(payload) > _MAX_CREDENTIAL_BLOB_BYTES:
            raise WindowsCredentialStoreError(
                "credential secret exceeds Windows secure-store size limit"
            )
        blob = (ctypes.c_ubyte * len(payload)).from_buffer_copy(payload)
        credential = _CredentialW()
        credential.Flags = 0
        credential.Type = _CRED_TYPE_GENERIC
        credential.TargetName = target
        credential.Comment = None
        credential.CredentialBlobSize = len(payload)
        credential.CredentialBlob = ctypes.cast(
            blob,
            ctypes.POINTER(ctypes.c_ubyte),
        )
        credential.Persist = _CRED_PERSIST_LOCAL_MACHINE
        credential.AttributeCount = 0
        credential.Attributes = None
        credential.TargetAlias = None
        credential.UserName = "AI-Ngerti-Geopolitik"
        try:
            if not self._cred_write(ctypes.byref(credential), 0):
                self._raise("write")
        finally:
            if payload:
                ctypes.memset(ctypes.addressof(blob), 0, len(payload))

    def read(self, target: str) -> bytes:
        pointer = ctypes.POINTER(_CredentialW)()
        if not self._cred_read(
            target,
            _CRED_TYPE_GENERIC,
            0,
            ctypes.byref(pointer),
        ):
            self._raise("read")
        try:
            credential = pointer.contents
            if credential.CredentialBlobSize == 0:
                return b""
            return ctypes.string_at(
                credential.CredentialBlob,
                credential.CredentialBlobSize,
            )
        finally:
            self._cred_free(pointer)

    def delete(self, target: str) -> None:
        if not self._cred_delete(target, _CRED_TYPE_GENERIC, 0):
            self._raise("delete")


class WindowsCredentialStore:
    """Production Windows Generic Credential implementation of CredentialPort."""

    __slots__ = ("_api", "_namespace")

    def __init__(
        self,
        namespace: str = "AI-Ngerti-Geopolitik/Gemini",
        *,
        api: _CredentialApi | None = None,
    ) -> None:
        normalized = namespace.strip().rstrip("/")
        if not normalized:
            raise WindowsCredentialStoreError(
                "Windows credential namespace cannot be empty"
            )
        if len(normalized) > 180:
            raise WindowsCredentialStoreError(
                "Windows credential namespace is too long"
            )
        if any(character in normalized for character in "\r\n\t"):
            raise WindowsCredentialStoreError(
                "Windows credential namespace contains invalid whitespace"
            )
        self._namespace = normalized
        self._api = api if api is not None else _NativeWindowsCredentialApi()

    def __repr__(self) -> str:
        return f"WindowsCredentialStore(namespace={self._namespace!r})"

    def _target(self, slot: CredentialSlotRef) -> str:
        return f"{self._namespace}/slot/{slot.slot_id:03d}"

    @staticmethod
    def _safe_failure(operation: str, error: WindowsCredentialApiError) -> None:
        raise WindowsCredentialStoreError(
            f"Windows secure credential store {operation} failed "
            f"(error {error.error_code})"
        ) from error

    def store_secret(
        self,
        slot: CredentialSlotRef,
        secret: CredentialSecret,
    ) -> None:
        payload = secret.reveal().encode("utf-8")
        try:
            self._api.write(self._target(slot), payload)
        except WindowsCredentialApiError as exc:
            self._safe_failure("write", exc)

    def load_secret(self, slot: CredentialSlotRef) -> CredentialSecret:
        try:
            payload = self._api.read(self._target(slot))
        except WindowsCredentialApiError as exc:
            if exc.error_code == _ERROR_NOT_FOUND:
                raise CredentialContractError(
                    CredentialErrorCode.NO_CREDENTIAL,
                    "credential slot is not configured",
                ) from exc
            self._safe_failure("read", exc)
        try:
            value = payload.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise WindowsCredentialStoreError(
                "Windows secure credential store returned invalid credential data"
            ) from exc
        return CredentialSecret(value)

    def delete_secret(self, slot: CredentialSlotRef) -> None:
        try:
            self._api.delete(self._target(slot))
        except WindowsCredentialApiError as exc:
            if exc.error_code == _ERROR_NOT_FOUND:
                return
            self._safe_failure("delete", exc)

    def has_secret(self, slot: CredentialSlotRef) -> bool:
        try:
            self._api.read(self._target(slot))
        except WindowsCredentialApiError as exc:
            if exc.error_code == _ERROR_NOT_FOUND:
                return False
            self._safe_failure("read", exc)
        return True
