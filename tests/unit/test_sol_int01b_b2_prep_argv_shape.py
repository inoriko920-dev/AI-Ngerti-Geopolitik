"""B2 argv preflight negative tests; never launch subprocesses."""

from __future__ import annotations

import sys
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from ai_ngerti_geopolitik.application.native_process_contract import (
    NativeProcessContractError,
    NativeProcessPolicy,
)
from ai_ngerti_geopolitik.infrastructure.native_command_preflight import (
    inspect_native_command_shape,
)


def _exe() -> str:
    return str(Path(sys.executable).absolute())


def test_unicode_spaces_and_metacharacters_are_not_shell_parsed() -> None:
    args = ("-i", "video source.mp4", "-vf", "drawtext=text=你好;PRIVATE & x")
    result = inspect_native_command_shape(_exe(), args, NativeProcessPolicy())
    assert result.items_including_executable == 5
    assert result.total_characters == len(_exe()) + sum(len(arg) for arg in args)
    assert not result.product_render_authorized
    assert not hasattr(result, "argv")
    assert not hasattr(result, "path")


def test_exact_character_cap_includes_executable() -> None:
    policy = NativeProcessPolicy(max_argv_items=2, max_argv_characters=len(_exe()) + 1)
    result = inspect_native_command_shape(_exe(), ("é",), policy)
    assert result.total_characters == len(_exe()) + 1


def test_arg_count_cap_rejects_extra_item() -> None:
    with pytest.raises(NativeProcessContractError, match="^INVALID_NATIVE_ARGV_LIMIT$"):
        inspect_native_command_shape(_exe(), ("A", "B"), NativeProcessPolicy(max_argv_items=2))


def test_length_cap_does_not_echo_secrets() -> None:
    with pytest.raises(NativeProcessContractError) as caught:
        inspect_native_command_shape(
            _exe(),
            ("SECRET_PATH" * 1000,),
            NativeProcessPolicy(max_argv_characters=len(_exe()) + 1),
        )
    assert str(caught.value) == "INVALID_NATIVE_ARGV_LIMIT"


@pytest.mark.parametrize(
    "path",
    ["ffmpeg.exe", "C:ffmpeg.exe", "../ffmpeg.exe", "", "\x00", "bad\npath", 0, None, True],
)
def test_bad_executable_path_rejected(path: object) -> None:
    with pytest.raises(NativeProcessContractError, match="^INVALID_NATIVE_EXECUTABLE_PATH$"):
        inspect_native_command_shape(path, (), NativeProcessPolicy())  # type: ignore[arg-type]


def test_parent_directory_traversal_rejected() -> None:
    exe = Path(_exe())
    with pytest.raises(NativeProcessContractError, match="^INVALID_NATIVE_EXECUTABLE_PATH$"):
        inspect_native_command_shape(str(exe.parent / ".." / exe.name), (), NativeProcessPolicy())


@pytest.mark.parametrize("args", [["-version"], "-version", None, False, 7])
def test_non_tuple_args_rejected(args: object) -> None:
    with pytest.raises(NativeProcessContractError, match="^INVALID_NATIVE_ARGV_TYPE$"):
        inspect_native_command_shape(_exe(), args, NativeProcessPolicy())  # type: ignore[arg-type]


@pytest.mark.parametrize("arg", [False, 2, None, b"secret", "\x00", "abc\x00secret"])
def test_wrong_arg_type_or_nul_rejected(arg: object) -> None:
    with pytest.raises(NativeProcessContractError, match="^INVALID_NATIVE_ARGV_ITEM$"):
        inspect_native_command_shape(
            _exe(),
            (arg,),
            NativeProcessPolicy(),  # type: ignore[arg-type]
        )


def test_wrong_policy_rejected_without_inspecting_command() -> None:
    with pytest.raises(NativeProcessContractError, match="^INVALID_NATIVE_PROCESS_POLICY$"):
        inspect_native_command_shape("PRIVATE_PATH", (), None)  # type: ignore[arg-type]


def test_single_binary_accepted_and_redacted_result_frozen() -> None:
    result = inspect_native_command_shape(_exe(), (), NativeProcessPolicy(max_argv_items=1))
    assert result.items_including_executable == 1
    with pytest.raises(FrozenInstanceError):
        result.total_characters = 99  # type: ignore[misc]
    assert "PRIVATE_TOKEN" not in repr(result)
