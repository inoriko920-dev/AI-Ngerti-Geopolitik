"""INT-01B/B2 preparation: isolated, Python-fixture-only subprocess qualification.

This is NOT an FFmpeg runner. It cannot run arbitrary executables, files or
commands, is not imported by application bootstrap, and never enables render.
It uses the B1 bounded contracts to demonstrate concurrent pipe draining,
deadline/cancellation and privacy-safe results with controlled child Python.
Actual FFmpeg, Windows child trees and production adapters require later gates.
"""

from __future__ import annotations

import subprocess
import sys
import threading
import time
from contextlib import suppress
from dataclasses import dataclass
from enum import StrEnum
from typing import IO

from ai_ngerti_geopolitik.application.native_process_contract import (
    NativeProcessContractError,
    NativeProcessOutcome,
    NativeProcessPolicy,
    NativeProcessStatus,
)
from ai_ngerti_geopolitik.application.native_toolchain_identity import NativeIssueCode
from ai_ngerti_geopolitik.infrastructure.native_bounded_capture import (
    NativeBoundedCapture,
    NativeStream,
)
from ai_ngerti_geopolitik.infrastructure.native_command_preflight import (
    inspect_native_command_shape,
)


class SyntheticFixture(StrEnum):
    SUCCESS = "success"
    BURST_STDOUT = "burst_stdout"
    BURST_STDERR = "burst_stderr"
    BURST_BOTH = "burst_both"
    STALL = "stall"
    FAIL_PRIVATE = "fail_private"


# Owned test program, not caller-controlled command text, binary or media path.
_FIXTURE = """
import sys
import time
mode = sys.argv[1]
if mode == 'success':
    sys.stdout.buffer.write(b'OK')
elif mode in ('burst_stdout', 'burst_stderr', 'burst_both'):
    for i in range(160):
        if mode != 'burst_stderr':
            sys.stdout.buffer.write(b'X' * 8192)
            sys.stdout.buffer.flush()
        if mode != 'burst_stdout':
            sys.stderr.buffer.write(b'Y' * 8192)
            sys.stderr.buffer.flush()
elif mode == 'stall':
    time.sleep(30)
elif mode == 'fail_private':
    sys.stderr.write('C:\\\\Users\\\\Private\\\\API_KEY=SECRET_TOKEN_DO_NOT_LOG')
    sys.exit(23)
else:
    sys.exit(5)
"""


@dataclass(slots=True)
class _PipeCounter:
    """Feed concurrent synthetic pipe readers into the existing bounded collector."""

    stream: IO[bytes]
    capture: NativeBoundedCapture
    channel: NativeStream
    exceeded: bool = False
    read_failed: bool = False

    def drain(self) -> None:
        try:
            while data := self.stream.read(16_384):
                try:
                    self.capture.append(self.channel, data)
                except NativeProcessContractError:
                    # Fail closed: the collector also clears private bytes on overflow.
                    self.exceeded = True
                    return
            self.capture.finish_stream(self.channel)
        except (OSError, ValueError, NativeProcessContractError):
            # A closed or broken reader must never produce a successful result.
            self.read_failed = True


def _outcome(
    status: NativeProcessStatus,
    duration_ms: int,
    stdout: int,
    stderr: int,
    exit_code: int | None = None,
) -> NativeProcessOutcome:
    issue = {
        NativeProcessStatus.SUCCESS: None,
        NativeProcessStatus.FAILED: NativeIssueCode.QUALIFICATION_FAILED,
        NativeProcessStatus.TIMED_OUT: NativeIssueCode.PROBE_TIMEOUT,
        NativeProcessStatus.CANCELLED: NativeIssueCode.PROCESS_CANCELLED,
        NativeProcessStatus.OUTPUT_LIMIT: NativeIssueCode.OUTPUT_TOO_LARGE,
        NativeProcessStatus.START_FAILED: NativeIssueCode.PROBE_INTERNAL_ERROR,
    }[status]
    return NativeProcessOutcome(
        status=status,
        exit_code=exit_code,
        duration_ms=max(0, duration_ms),
        bytes_seen_stdout=stdout,
        bytes_seen_stderr=stderr,
        issue=issue,
    )


def _terminate_owned(process: subprocess.Popen[bytes], grace_seconds: float) -> None:
    if process.poll() is not None:
        return
    try:
        process.terminate()
        process.wait(timeout=grace_seconds)
    except subprocess.TimeoutExpired:
        process.kill()
        with suppress(subprocess.TimeoutExpired):
            process.wait(timeout=2)
    except OSError:
        if process.poll() is None:
            with suppress(OSError):
                process.kill()


def run_synthetic_fixture(
    fixture: SyntheticFixture,
    policy: NativeProcessPolicy,
    *,
    cancellation: threading.Event | None = None,
) -> NativeProcessOutcome:
    """Exercise a bounded subprocess using only this module's fixed Python fixture.

    Never takes a caller-specified executable, argv, script or FFmpeg path.
    This demonstration does not implement Windows process-tree cleanup (B3).
    """

    if type(fixture) is not SyntheticFixture or type(policy) is not NativeProcessPolicy:
        raise ValueError("INVALID_SYNTHETIC_FIXTURE_ARGUMENT")
    if cancellation is not None and not isinstance(cancellation, threading.Event):
        raise ValueError("INVALID_SYNTHETIC_CANCELLATION")
    if cancellation is not None and cancellation.is_set():
        return _outcome(NativeProcessStatus.CANCELLED, 0, 0, 0)

    # The shared Windows command-shape guard is exercised by this fixed fixture.
    # It only validates syntax; it is NOT trust, identity or FFmpeg authorization.
    if sys.platform == "win32":
        inspect_native_command_shape(
            sys.executable, ("-I", "-c", _FIXTURE, fixture.value), policy
        )

    start = time.monotonic()
    try:
        process = subprocess.Popen(
            [sys.executable, "-I", "-c", _FIXTURE, fixture.value],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
        )
    except OSError:
        return _outcome(
            NativeProcessStatus.START_FAILED,
            int((time.monotonic() - start) * 1000),
            0,
            0,
        )

    assert process.stdout is not None and process.stderr is not None
    capture = NativeBoundedCapture(policy)
    out = _PipeCounter(process.stdout, capture, "stdout")
    err = _PipeCounter(process.stderr, capture, "stderr")
    readers = [
        threading.Thread(target=out.drain, daemon=True),
        threading.Thread(target=err.drain, daemon=True),
    ]
    status: NativeProcessStatus | None = None
    try:
        for reader in readers:
            reader.start()
        while True:
            if cancellation is not None and cancellation.is_set():
                status = NativeProcessStatus.CANCELLED
                break
            if out.exceeded or err.exceeded or out.read_failed or err.read_failed:
                status = NativeProcessStatus.OUTPUT_LIMIT
                break
            if time.monotonic() - start >= policy.timeout_seconds:
                status = NativeProcessStatus.TIMED_OUT
                break
            if process.poll() is not None:
                break
            time.sleep(policy.poll_interval_ms / 1000)
    finally:
        if status is not None or process.poll() is None:
            _terminate_owned(process, policy.terminate_grace_seconds)
        for reader in readers:
            reader.join(timeout=policy.terminate_grace_seconds + 2)
        for stream in (process.stdout, process.stderr):
            stream.close()

    # Collect metadata only after both readers have joined. Never return or log
    # the private bytes, including the known synthetic credential in stderr.
    metrics = capture.metrics()
    capture.discard()
    stdout_count = metrics.bytes_seen_stdout
    stderr_count = metrics.bytes_seen_stderr

    elapsed = int((time.monotonic() - start) * 1000)
    # Reader data can continue to arrive after the child has exited.
    if status is None and (
        metrics.overflowed or out.exceeded or err.exceeded or out.read_failed or err.read_failed
    ):
        status = NativeProcessStatus.OUTPUT_LIMIT
    if status is None and cancellation is not None and cancellation.is_set():
        status = NativeProcessStatus.CANCELLED
    if status is not None:
        return _outcome(status, elapsed, stdout_count, stderr_count)
    if process.returncode == 0:
        return _outcome(NativeProcessStatus.SUCCESS, elapsed, stdout_count, stderr_count, 0)
    if process.returncode is None:
        return _outcome(NativeProcessStatus.TIMED_OUT, elapsed, stdout_count, stderr_count)
    return _outcome(NativeProcessStatus.FAILED, elapsed, stdout_count, stderr_count, process.returncode)
