"""Pure native command shape validation. No subprocess, binary discovery or UI."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ai_ngerti_geopolitik.application.native_process_contract import (
    NativeProcessContractError,
    NativeProcessPolicy,
)


@dataclass(frozen=True, slots=True)
class NativeCommandShape:
    """Only safe counters; no command, path, or environment contents."""

    items_including_executable: int
    total_characters: int

    @property
    def product_render_authorized(self) -> bool:
        return False


def inspect_native_command_shape(
    executable_path: str,
    arguments: tuple[str, ...],
    policy: NativeProcessPolicy,
) -> NativeCommandShape:
    """Lexical argv check only; does not prove binary identity or permission."""

    if type(policy) is not NativeProcessPolicy:
        raise NativeProcessContractError("INVALID_NATIVE_PROCESS_POLICY")
    if (
        type(executable_path) is not str
        or not executable_path
        or "\x00" in executable_path
        or any(ord(char) < 32 or ord(char) == 127 for char in executable_path)
    ):
        raise NativeProcessContractError("INVALID_NATIVE_EXECUTABLE_PATH")
    if len(executable_path) > policy.max_argv_characters:
        raise NativeProcessContractError("INVALID_NATIVE_ARGV_LIMIT")
    path = Path(executable_path)
    if not path.is_absolute() or ".." in path.parts or not path.name:
        raise NativeProcessContractError("INVALID_NATIVE_EXECUTABLE_PATH")
    if type(arguments) is not tuple:
        raise NativeProcessContractError("INVALID_NATIVE_ARGV_TYPE")
    count = len(arguments) + 1
    if count > policy.max_argv_items:
        raise NativeProcessContractError("INVALID_NATIVE_ARGV_LIMIT")
    total = len(executable_path)
    for arg in arguments:
        if type(arg) is not str or "\x00" in arg:
            raise NativeProcessContractError("INVALID_NATIVE_ARGV_ITEM")
        total += len(arg)
        if total > policy.max_argv_characters:
            raise NativeProcessContractError("INVALID_NATIVE_ARGV_LIMIT")
    return NativeCommandShape(count, total)
