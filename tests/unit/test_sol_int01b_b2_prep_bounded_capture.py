"""B2-prep tests for a pure bounded collector; never start a process."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import FrozenInstanceError

import pytest

from ai_ngerti_geopolitik.application.native_process_contract import (
    NativeProcessContractError,
    NativeProcessPolicy,
)
from ai_ngerti_geopolitik.infrastructure.native_bounded_capture import NativeBoundedCapture


def _capture(*, stdout: int = 8, stderr: int = 8) -> NativeBoundedCapture:
    return NativeBoundedCapture(
        NativeProcessPolicy(max_stdout_bytes=stdout, max_stderr_bytes=stderr)
    )


def test_separate_stream_caps_and_private_one_time_handoff() -> None:
    capture = _capture()
    capture.append("stdout", b"12345678")
    capture.append("stderr", b"ABCDEFGH")
    metrics = capture.metrics()
    assert (metrics.bytes_seen_stdout, metrics.bytes_seen_stderr) == (8, 8)
    assert not metrics.overflowed and not metrics.sealed
    capture.finish_stream("stdout")
    capture.finish_stream("stderr")
    assert capture.take_private_buffers() == (b"12345678", b"ABCDEFGH")
    assert capture.metrics().sealed
    with pytest.raises(NativeProcessContractError, match="^NATIVE_STREAM_CLOSED$"):
        capture.take_private_buffers()
    with pytest.raises(NativeProcessContractError, match="^NATIVE_STREAM_CLOSED$"):
        capture.append("stdout", b"?")


@pytest.mark.parametrize("exceeded", ["stdout", "stderr"])
def test_one_byte_overflow_fails_closed_and_clears_other_stream(exceeded: str) -> None:
    capture = _capture()
    capture.append("stdout", b"A")
    capture.append("stderr", b"B")
    with pytest.raises(NativeProcessContractError, match="^NATIVE_OUTPUT_TOO_LARGE$"):
        capture.append(exceeded, b"X" * 8)
    state = capture.metrics()
    assert state.overflowed
    assert "secret" not in repr(state)
    with pytest.raises(NativeProcessContractError, match="^NATIVE_OUTPUT_TOO_LARGE$"):
        capture.take_private_buffers()
    with pytest.raises(NativeProcessContractError, match="^NATIVE_OUTPUT_TOO_LARGE$"):
        capture.append("stderr", b"retry")


def test_huge_chunk_rejected_without_echo_and_without_retaining_data() -> None:
    capture = _capture(stdout=1)
    secret = b"C:\\Users\\Hidden\\secret_token"
    with pytest.raises(NativeProcessContractError) as caught:
        capture.append("stdout", secret * 4096)
    assert str(caught.value) == "NATIVE_OUTPUT_TOO_LARGE"
    assert "Hidden" not in repr(capture)
    assert "secret_token" not in repr(capture.metrics())
    assert capture.metrics().bytes_seen_stdout == len(secret) * 4096
    capture.discard()
    assert capture.metrics().sealed


@pytest.mark.parametrize(
    ("stream", "chunk", "reason"),
    [
        ("stdin", b"x", "INVALID_NATIVE_STREAM"),
        (None, b"x", "INVALID_NATIVE_STREAM"),
        (3, b"x", "INVALID_NATIVE_STREAM"),
        ("stdout", "private path", "INVALID_NATIVE_STREAM_CHUNK"),
        ("stderr", bytearray(b"secret"), "INVALID_NATIVE_STREAM_CHUNK"),
        ("stderr", None, "INVALID_NATIVE_STREAM_CHUNK"),
    ],
)
def test_invalid_untrusted_inputs_fail_without_echo(
    stream: object, chunk: object, reason: str
) -> None:
    collector = _capture()
    with pytest.raises(NativeProcessContractError, match=f"^{reason}$"):
        collector.append(stream, chunk)  # type: ignore[arg-type]
    assert collector.metrics().bytes_seen_stdout == 0


def test_zero_length_chunk_does_not_change_accounting() -> None:
    capture = _capture(stdout=1, stderr=1)
    capture.append("stdout", b"")
    capture.append("stderr", b"")
    assert capture.metrics().bytes_seen_stdout == 0
    capture.finish_stream("stdout")
    capture.finish_stream("stderr")
    assert capture.take_private_buffers() == (b"", b"")


def test_discard_clears_raw_bytes_and_blocks_reuse() -> None:
    capture = _capture()
    capture.append("stderr", b"PRIVATE")
    capture.discard()
    assert capture.metrics().sealed
    with pytest.raises(NativeProcessContractError, match="^NATIVE_STREAM_CLOSED$"):
        capture.append("stdout", b"new")
    with pytest.raises(NativeProcessContractError, match="^NATIVE_STREAM_CLOSED$"):
        capture.take_private_buffers()


def test_parallel_reader_threads_keep_stream_counts_and_exact_data() -> None:
    capture = _capture(stdout=8192, stderr=8192)

    def write(stream: str, payload: bytes) -> None:
        for _ in range(64):
            capture.append(stream, payload)  # type: ignore[arg-type]

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [
            pool.submit(write, "stdout", b"a" * 64),
            pool.submit(write, "stderr", b"z" * 64),
        ]
        for future in futures:
            future.result(timeout=3)

    assert capture.metrics().bytes_seen_stdout == 4096
    assert capture.metrics().bytes_seen_stderr == 4096
    capture.finish_stream("stdout")
    capture.finish_stream("stderr")
    assert capture.take_private_buffers() == (b"a" * 4096, b"z" * 4096)


def test_metrics_are_immutable_public_safe_values() -> None:
    stats = _capture().metrics()
    with pytest.raises(FrozenInstanceError):
        stats.overflowed = True  # type: ignore[misc]
    assert not hasattr(stats, "stdout")
    assert not hasattr(stats, "stderr")
    assert not hasattr(stats, "argv")


def test_wrong_policy_type_rejected() -> None:
    with pytest.raises(NativeProcessContractError, match="^INVALID_NATIVE_PROCESS_POLICY$"):
        NativeBoundedCapture(None)  # type: ignore[arg-type]

def test_handoff_requires_both_readers_finished_without_losing_partial_data() -> None:
    capture = _capture()
    capture.append("stdout", b"A")
    with pytest.raises(NativeProcessContractError, match="^NATIVE_STREAM_INCOMPLETE$"):
        capture.take_private_buffers()
    assert not capture.metrics().sealed
    capture.finish_stream("stdout")
    with pytest.raises(NativeProcessContractError, match="^NATIVE_STREAM_INCOMPLETE$"):
        capture.take_private_buffers()
    with pytest.raises(NativeProcessContractError, match="^NATIVE_STREAM_CLOSED$"):
        capture.append("stdout", b"late")
    capture.append("stderr", b"B")
    capture.finish_stream("stderr")
    assert capture.take_private_buffers() == (b"A", b"B")


def test_finished_stream_cannot_finish_twice_and_rejects_invalid_stream() -> None:
    capture = _capture()
    for wrong in (None, 0, [], "stdin", False):
        with pytest.raises(NativeProcessContractError, match="^INVALID_NATIVE_STREAM$"):
            capture.finish_stream(wrong)  # type: ignore[arg-type]
    capture.finish_stream("stderr")
    with pytest.raises(NativeProcessContractError, match="^NATIVE_STREAM_CLOSED$"):
        capture.finish_stream("stderr")
    capture.finish_stream("stdout")
    assert capture.take_private_buffers() == (b"", b"")


def test_discard_and_overflow_prohibit_stream_finalization() -> None:
    discarded = _capture()
    discarded.discard()
    with pytest.raises(NativeProcessContractError, match="^NATIVE_STREAM_CLOSED$"):
        discarded.finish_stream("stdout")

    overflowed = _capture(stdout=1)
    with pytest.raises(NativeProcessContractError, match="^NATIVE_OUTPUT_TOO_LARGE$"):
        overflowed.append("stdout", b"too big")
    with pytest.raises(NativeProcessContractError, match="^NATIVE_OUTPUT_TOO_LARGE$"):
        overflowed.finish_stream("stdout")
