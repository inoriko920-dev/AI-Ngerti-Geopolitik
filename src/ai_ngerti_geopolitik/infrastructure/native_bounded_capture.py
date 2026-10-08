"""Bounded private stream capture for a future approved native process runner.

SOL INT-01B/B2-prep only: this module NEVER starts, terminates, or locates a
subprocess, and cannot enable a product export. A future owner-approved runner
may feed data read concurrently from child stdout/stderr into this collector.
"""

from __future__ import annotations

from dataclasses import dataclass
from threading import Lock
from typing import Literal

from ai_ngerti_geopolitik.application.native_process_contract import (
    NativeProcessContractError,
    NativeProcessPolicy,
)

NativeStream = Literal["stdout", "stderr"]


@dataclass(frozen=True, slots=True)
class NativeCaptureMetrics:
    """Safe accounting; never includes bytes, paths, argv, or environment."""

    bytes_seen_stdout: int
    bytes_seen_stderr: int
    overflowed: bool
    sealed: bool


class NativeBoundedCapture:
    """Thread-safe two-pipe buffer with independent strict byte ceilings.

    This collector does NOT drain OS pipes itself. A future runner must read
    BOTH pipes concurrently, pass chunks here, and terminate the child as soon
    as this collector reports an overflow. No stderr content is used in errors.
    """

    __slots__ = (
        "_lock",
        "_max_stdout",
        "_max_stderr",
        "_stdout",
        "_stderr",
        "_seen_stdout",
        "_seen_stderr",
        "_overflowed",
        "_sealed",
    )

    def __init__(self, policy: NativeProcessPolicy) -> None:
        if type(policy) is not NativeProcessPolicy:
            raise NativeProcessContractError("INVALID_NATIVE_PROCESS_POLICY")
        self._lock = Lock()
        self._max_stdout = policy.max_stdout_bytes
        self._max_stderr = policy.max_stderr_bytes
        self._stdout = bytearray()
        self._stderr = bytearray()
        self._seen_stdout = 0
        self._seen_stderr = 0
        self._overflowed = False
        self._sealed = False

    def append(self, stream: NativeStream, chunk: bytes) -> None:
        """Accept one chunk; reject excess WITHOUT copying unbounded input."""
        if stream not in ("stdout", "stderr") or type(stream) is not str:
            raise NativeProcessContractError("INVALID_NATIVE_STREAM")
        if type(chunk) is not bytes:
            raise NativeProcessContractError("INVALID_NATIVE_STREAM_CHUNK")
        with self._lock:
            self._assert_writable()
            if stream == "stdout":
                self._seen_stdout += len(chunk)
                if self._seen_stdout > self._max_stdout:
                    self._overflow()
                self._stdout.extend(chunk)
            else:
                self._seen_stderr += len(chunk)
                if self._seen_stderr > self._max_stderr:
                    self._overflow()
                self._stderr.extend(chunk)

    def metrics(self) -> NativeCaptureMetrics:
        """Return redacted counters safe to expose to the application layer."""
        with self._lock:
            return NativeCaptureMetrics(
                self._seen_stdout,
                self._seen_stderr,
                self._overflowed,
                self._sealed,
            )

    def take_private_buffers(self) -> tuple[bytes, bytes]:
        """Internal-only parser handoff, once, after both readers have finished.

        Never hand these raw bytes to GUI/logs: they may contain full file paths,
        environment values, or other untrusted tool output.
        """
        with self._lock:
            self._assert_writable()
            self._sealed = True
            output = bytes(self._stdout), bytes(self._stderr)
            self._stdout.clear()
            self._stderr.clear()
            return output

    def discard(self) -> None:
        """Revoke further writes and clear all buffered native output."""
        with self._lock:
            self._sealed = True
            self._stdout.clear()
            self._stderr.clear()

    def _overflow(self) -> None:
        self._overflowed = True
        self._stdout.clear()
        self._stderr.clear()
        raise NativeProcessContractError("NATIVE_OUTPUT_TOO_LARGE")

    def _assert_writable(self) -> None:
        if self._overflowed:
            raise NativeProcessContractError("NATIVE_OUTPUT_TOO_LARGE")
        if self._sealed:
            raise NativeProcessContractError("NATIVE_STREAM_CLOSED")
