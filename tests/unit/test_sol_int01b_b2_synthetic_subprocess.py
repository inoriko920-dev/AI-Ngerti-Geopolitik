"""INT-01B/B2: synthetic child processes only; NEVER call external FFmpeg."""

from __future__ import annotations

import subprocess
import sys
import threading
import time

import pytest

from ai_ngerti_geopolitik.application.native_process_contract import (
    NativeProcessPolicy,
    NativeProcessStatus,
)
from ai_ngerti_geopolitik.application.native_toolchain_identity import NativeIssueCode
from ai_ngerti_geopolitik.infrastructure.native_bounded_capture import NativeBoundedCapture
from ai_ngerti_geopolitik.infrastructure.synthetic_process_qualification import (
    SyntheticFixture,
    run_synthetic_fixture,
)


@pytest.mark.parametrize(
    "fixture",
    [
        SyntheticFixture.BURST_STDOUT,
        SyntheticFixture.BURST_STDERR,
        SyntheticFixture.BURST_BOTH,
    ],
)
def test_both_streams_drain_without_deadlock(fixture: SyntheticFixture) -> None:
    result = run_synthetic_fixture(
        fixture,
        NativeProcessPolicy(
            timeout_seconds=8, max_stdout_bytes=1_048_576, max_stderr_bytes=1_048_576
        ),
    )
    assert result.status is NativeProcessStatus.OUTPUT_LIMIT
    assert result.issue is NativeIssueCode.OUTPUT_TOO_LARGE
    assert max(result.bytes_seen_stdout, result.bytes_seen_stderr) > 1_048_576
    assert result.duration_ms < 8_000
    assert not result.product_render_authorized


def test_small_synthetic_process_succeeds_with_no_private_output() -> None:
    result = run_synthetic_fixture(SyntheticFixture.SUCCESS, NativeProcessPolicy())
    assert result.successful
    assert result.exit_code == 0
    assert result.bytes_seen_stdout == 2
    assert result.bytes_seen_stderr == 0
    assert not hasattr(result, "stdout")
    assert not hasattr(result, "stderr")


def test_stalled_child_hits_monotonic_timeout_and_terminates() -> None:
    start = time.monotonic()
    result = run_synthetic_fixture(
        SyntheticFixture.STALL,
        NativeProcessPolicy(timeout_seconds=1, terminate_grace_seconds=0.2),
    )
    assert result.status is NativeProcessStatus.TIMED_OUT
    assert result.issue is NativeIssueCode.PROBE_TIMEOUT
    assert time.monotonic() - start < 5


def test_cancellation_before_launch_and_during_execution() -> None:
    event = threading.Event()
    event.set()
    before = run_synthetic_fixture(
        SyntheticFixture.STALL, NativeProcessPolicy(), cancellation=event
    )
    assert before.status is NativeProcessStatus.CANCELLED
    assert before.duration_ms == 0
    event.clear()
    holder = {}
    thread = threading.Thread(
        target=lambda: holder.setdefault(
            "result",
            run_synthetic_fixture(
                SyntheticFixture.STALL,
                NativeProcessPolicy(timeout_seconds=8, terminate_grace_seconds=0.2),
                cancellation=event,
            ),
        )
    )
    thread.start()
    time.sleep(0.25)
    event.set()
    thread.join(timeout=5)
    assert not thread.is_alive()
    assert holder["result"].status is NativeProcessStatus.CANCELLED


def test_failed_child_stderr_is_redacted_and_exit_preserved() -> None:
    result = run_synthetic_fixture(SyntheticFixture.FAIL_PRIVATE, NativeProcessPolicy())
    assert result.status is NativeProcessStatus.FAILED
    assert result.exit_code == 23
    assert result.issue is NativeIssueCode.QUALIFICATION_FAILED
    assert result.bytes_seen_stderr > 0
    assert "SECRET_TOKEN_DO_NOT_LOG" not in str(result)
    assert "Private" not in repr(result)


def test_invalid_fixture_cannot_run_user_supplied_command() -> None:
    with pytest.raises(ValueError, match="INVALID_SYNTHETIC_FIXTURE_ARGUMENT"):
        run_synthetic_fixture("ffmpeg.exe", NativeProcessPolicy())  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="INVALID_SYNTHETIC_FIXTURE_ARGUMENT"):
        run_synthetic_fixture(SyntheticFixture.SUCCESS, "unbounded")  # type: ignore[arg-type]


def test_invalid_cancellation_is_rejected_before_any_process() -> None:
    with pytest.raises(ValueError, match="INVALID_SYNTHETIC_CANCELLATION"):
        run_synthetic_fixture(
            SyntheticFixture.SUCCESS,
            NativeProcessPolicy(),
            cancellation="not-an-event",  # type: ignore[arg-type]
        )


def test_python_subprocess_really_feeds_both_streams_to_the_shared_bounded_capture(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The three components must interact, not merely coexist in separate files."""
    observed: list[tuple[str, int]] = []
    lock = threading.Lock()
    original = NativeBoundedCapture.append

    def record(self: NativeBoundedCapture, stream: str, chunk: bytes) -> None:
        with lock:
            observed.append((stream, len(chunk)))
        original(self, stream, chunk)  # type: ignore[arg-type]

    monkeypatch.setattr(NativeBoundedCapture, "append", record)
    success = run_synthetic_fixture(SyntheticFixture.SUCCESS, NativeProcessPolicy())
    failure = run_synthetic_fixture(SyntheticFixture.FAIL_PRIVATE, NativeProcessPolicy())
    assert success.successful
    assert failure.status is NativeProcessStatus.FAILED
    assert ("stdout", 2) in observed
    assert any(stream == "stderr" and size > 0 for stream, size in observed)
    assert "SECRET_TOKEN_DO_NOT_LOG" not in str(failure)


@pytest.mark.skipif(sys.platform != "win32", reason="pure Windows argv guard")
def test_invalid_windows_argv_is_rejected_before_synthetic_process_spawn(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    invoked = []

    def forbidden(*args: object, **kwargs: object) -> None:
        invoked.append(True)
        raise AssertionError("UNEXPECTED_SUBPROCESS_LAUNCH")

    monkeypatch.setattr(subprocess, "Popen", forbidden)
    with pytest.raises(ValueError, match="^INVALID_NATIVE_ARGV_LIMIT$"):
        run_synthetic_fixture(
            SyntheticFixture.SUCCESS,
            NativeProcessPolicy(max_argv_items=4),
        )
    assert not invoked
