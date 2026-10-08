"""Pure Windows argv shape tests; subprocess.list2cmdline only formats in memory."""

from __future__ import annotations

import subprocess
from dataclasses import FrozenInstanceError

import pytest

from ai_ngerti_geopolitik.application.native_process_contract import (
    NativeProcessContractError,
    NativeProcessPolicy,
)
from ai_ngerti_geopolitik.infrastructure.native_command_preflight import (
    inspect_native_command_shape,
)


def _exe() -> str:
    return "C:\\Program Files\\FFmpeg\\bin\\ffmpeg.exe"


def _expected_units(args: tuple[str, ...]) -> int:
    # CPython's formatter does not execute anything or look up executables.
    return len(subprocess.list2cmdline(list(args)).encode("utf-16-le")) // 2


@pytest.mark.parametrize(
    "args",
    [
        (),
        ("-version",),
        ("-i", "video source.mp4", "-vf", "drawtext=text=你好;PRIVATE & x"),
        ("",),
        ('argument"with"quotes',),
        ("trailing space ",),
        ("double\\\\slash",),
        ('escaped\\"quote',),
        ("emoji_😀_🗺",),
        ("\twith tabs",),
        ("backslashes\\\\ at end \\\\",),
        ("a", "b", ""),
    ],
)
def test_windows_quoting_matches_stdlib_utf16_length(args: tuple[str, ...]) -> None:
    result = inspect_native_command_shape(_exe(), args, NativeProcessPolicy())
    assert result.items_including_executable == 1 + len(args)
    assert result.total_characters == _expected_units((_exe(), *args))
    assert not result.product_render_authorized
    assert not hasattr(result, "argv")
    assert not hasattr(result, "path")


def test_exact_character_cap_counts_quote_separator_and_final_nul() -> None:
    args = ("file with spaces.mp4",)
    command_units = _expected_units((_exe(), *args))
    accepted = NativeProcessPolicy(max_argv_items=2, max_argv_characters=command_units + 1)
    assert inspect_native_command_shape(_exe(), args, accepted).total_characters == command_units

    with pytest.raises(NativeProcessContractError, match="^INVALID_NATIVE_ARGV_LIMIT$"):
        inspect_native_command_shape(
            _exe(),
            args,
            NativeProcessPolicy(max_argv_items=2, max_argv_characters=command_units),
        )


def test_utf16_supplementary_plane_character_takes_two_units() -> None:
    args = ("😀",)
    result = inspect_native_command_shape(_exe(), args, NativeProcessPolicy())
    assert result.total_characters == _expected_units((_exe(), *args))
    assert result.total_characters > len(_exe()) + 1 + len(args)


def test_internal_escaping_may_exceed_unescaped_limit() -> None:
    args = ('x \\\\\\\\"y',)
    quoted = _expected_units((_exe(), *args))
    raw = len(_exe()) + len(args[0])
    assert quoted > raw
    with pytest.raises(NativeProcessContractError, match="^INVALID_NATIVE_ARGV_LIMIT$"):
        inspect_native_command_shape(_exe(), args, NativeProcessPolicy(max_argv_characters=raw + 1))


def test_windows_os_command_line_ceiling_enforced_despite_policy_32768() -> None:
    length = 32_768 - len(_exe()) - 2
    args = ("x" * length,)
    assert _expected_units((_exe(), *args)) + 1 == 32_768
    with pytest.raises(NativeProcessContractError, match="^INVALID_NATIVE_ARGV_LIMIT$"):
        inspect_native_command_shape(_exe(), args, NativeProcessPolicy())


def test_argument_count_cap_enforced() -> None:
    with pytest.raises(NativeProcessContractError, match="^INVALID_NATIVE_ARGV_LIMIT$"):
        inspect_native_command_shape(_exe(), ("A", "B"), NativeProcessPolicy(max_argv_items=2))


def test_private_argument_overflow_never_appears_in_exception() -> None:
    with pytest.raises(NativeProcessContractError) as error:
        inspect_native_command_shape(
            _exe(),
            ("PRIVATE_SECRET" * 1000,),
            NativeProcessPolicy(max_argv_characters=len(_exe()) + 2),
        )
    assert str(error.value) == "INVALID_NATIVE_ARGV_LIMIT"
    assert "PRIVATE_SECRET" not in str(error.value)


@pytest.mark.parametrize(
    "binary",
    [
        "ffmpeg.exe",
        "C:ffmpeg.exe",
        "../ffmpeg.exe",
        "",
        "\x00",
        "bad\npath",
        "\\\\server\\share\\ffmpeg.exe",
        "\\\\?\\C:\\ffmpeg.exe",
        "C:\\tools\\bad.exe:stream",
        "C:\\tools\\foo?.exe",
        "C:\\tools\\",
        "C:\\tools\\..\\other.exe",
        "C:/tools/..\\other.exe",
        0,
        None,
        True,
    ],
)
def test_untrusted_executable_path_rejected(binary: object) -> None:
    with pytest.raises(NativeProcessContractError, match="^INVALID_NATIVE_EXECUTABLE_PATH$"):
        inspect_native_command_shape(binary, (), NativeProcessPolicy())  # type: ignore[arg-type]


@pytest.mark.parametrize("args", [["-version"], "-version", None, False, 7])
def test_wrong_argv_container_rejected(args: object) -> None:
    with pytest.raises(NativeProcessContractError, match="^INVALID_NATIVE_ARGV_TYPE$"):
        inspect_native_command_shape(_exe(), args, NativeProcessPolicy())  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "arg", [False, 2, None, b"private", "\x00", "bad\x00private", "\ud800", "\udfff"]
)
def test_untrusted_arg_rejected_without_echo(arg: object) -> None:
    with pytest.raises(NativeProcessContractError, match="^INVALID_NATIVE_ARGV_ITEM$"):
        inspect_native_command_shape(
            _exe(),
            (arg,),
            NativeProcessPolicy(),  # type: ignore[arg-type]
        )


def test_surrogate_in_executable_path_rejected() -> None:
    with pytest.raises(NativeProcessContractError, match="^INVALID_NATIVE_EXECUTABLE_PATH$"):
        inspect_native_command_shape("C:\\Tools\\\ud800.exe", (), NativeProcessPolicy())


def test_invalid_policy_rejected_before_processing_command() -> None:
    with pytest.raises(NativeProcessContractError, match="^INVALID_NATIVE_PROCESS_POLICY$"):
        inspect_native_command_shape("PRIVATE_PATH", (), None)  # type: ignore[arg-type]


def test_redacted_result_is_immutable() -> None:
    result = inspect_native_command_shape(_exe(), (), NativeProcessPolicy(max_argv_items=1))
    assert result.items_including_executable == 1
    with pytest.raises(FrozenInstanceError):
        result.total_characters = 99  # type: ignore[misc]
    assert "PRIVATE_TOKEN" not in repr(result)
