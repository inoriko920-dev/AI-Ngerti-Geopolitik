"""Pure Windows native argv preflight; no executable discovery, I/O, or process launch."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PureWindowsPath

from ai_ngerti_geopolitik.application.native_process_contract import (
    NativeProcessContractError,
    NativeProcessPolicy,
)


@dataclass(frozen=True, slots=True)
class NativeCommandShape:
    """Privacy-safe Windows command-line metrics, not an executable approval."""

    items_including_executable: int
    total_characters: int

    @property
    def product_render_authorized(self) -> bool:
        return False


def _has_unpaired_surrogate(value: str) -> bool:
    return any(0xD800 <= ord(char) <= 0xDFFF for char in value)


def _windows_arg_units(value: str) -> int:
    """Count UTF-16 units after CPython's Windows list2cmdline quoting rules.

    Counts without constructing or retaining the sensitive command line.
    Does not count the separator or final NUL (accounted for by the caller).
    """

    quote = not value or " " in value or "\t" in value
    units = 2 if quote else 0
    backslashes = 0
    for char in value:
        if char == "\\":
            backslashes += 1
        elif char == '"':
            units += 2 * backslashes + 2
            backslashes = 0
        else:
            units += backslashes + (2 if ord(char) > 0xFFFF else 1)
            backslashes = 0
    units += backslashes * (2 if quote else 1)
    return units


def inspect_native_command_shape(
    executable_path: str,
    arguments: tuple[str, ...],
    policy: NativeProcessPolicy,
) -> NativeCommandShape:
    """Validate Windows command shape only, never filesystem trust or identity.

    Limits apply to UTF-16 command-line units after Windows argv quoting,
    including argument separators and the final terminating NUL. The returned
    count excludes that NUL. No raw command data leaves this module.
    """

    if type(policy) is not NativeProcessPolicy:
        raise NativeProcessContractError("INVALID_NATIVE_PROCESS_POLICY")
    if (
        type(executable_path) is not str
        or not executable_path
        or "\x00" in executable_path
        or _has_unpaired_surrogate(executable_path)
        or any(ord(char) < 32 or ord(char) == 127 for char in executable_path)
    ):
        raise NativeProcessContractError("INVALID_NATIVE_EXECUTABLE_PATH")
    if len(executable_path) > policy.max_argv_characters:
        raise NativeProcessContractError("INVALID_NATIVE_ARGV_LIMIT")

    # PureWindowsPath is deterministic even in non-Windows developer test runs.
    candidate = PureWindowsPath(executable_path)
    if (
        not candidate.is_absolute()
        or candidate.drive.startswith("\\\\")
        or ".." in candidate.parts
        or not candidate.name
        or executable_path.endswith(("\\", "/"))
        or any(char in executable_path[2:] for char in '<>:"|?*')
    ):
        raise NativeProcessContractError("INVALID_NATIVE_EXECUTABLE_PATH")
    if type(arguments) is not tuple:
        raise NativeProcessContractError("INVALID_NATIVE_ARGV_TYPE")
    count = len(arguments) + 1
    if count > policy.max_argv_items:
        raise NativeProcessContractError("INVALID_NATIVE_ARGV_LIMIT")

    # Windows CreateProcessW accepts at most 32767 UTF-16 units including NUL.
    # The policy may choose a smaller limit but may not override that ceiling.
    ceiling = min(policy.max_argv_characters, 32_767)
    total = _windows_arg_units(executable_path)
    if total + 1 > ceiling:
        raise NativeProcessContractError("INVALID_NATIVE_ARGV_LIMIT")
    for arg in arguments:
        if type(arg) is not str or "\x00" in arg or _has_unpaired_surrogate(arg):
            raise NativeProcessContractError("INVALID_NATIVE_ARGV_ITEM")
        if len(arg) > ceiling:
            raise NativeProcessContractError("INVALID_NATIVE_ARGV_LIMIT")
        total += 1 + _windows_arg_units(arg)
        if total + 1 > ceiling:
            raise NativeProcessContractError("INVALID_NATIVE_ARGV_LIMIT")

    return NativeCommandShape(count, total)
