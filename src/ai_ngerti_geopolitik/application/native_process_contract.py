"""SOL INT-01B/B1: pure, bounded subprocess policy and privacy-safe result contracts.

No subprocess is created here. Neither native toolchain qualification nor
product render controls are authorized by constructing these value objects.
Only future INT-01B/B2 infrastructure may implement process execution, after
the externally supplied FFmpeg Pilot A receives explicit owner approval.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum

from ai_ngerti_geopolitik.application.native_toolchain_identity import NativeIssueCode


class NativeProcessContractError(ValueError):
    """A fixed-code contract failure; never includes paths, argv or tool output."""


class NativeProcessStatus(StrEnum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    TIMED_OUT = "TIMED_OUT"
    CANCELLED = "CANCELLED"
    OUTPUT_LIMIT = "OUTPUT_LIMIT"
    START_FAILED = "START_FAILED"


_STATUS_ISSUE = {
    NativeProcessStatus.FAILED: NativeIssueCode.QUALIFICATION_FAILED,
    NativeProcessStatus.TIMED_OUT: NativeIssueCode.PROBE_TIMEOUT,
    NativeProcessStatus.CANCELLED: NativeIssueCode.PROCESS_CANCELLED,
    NativeProcessStatus.OUTPUT_LIMIT: NativeIssueCode.OUTPUT_TOO_LARGE,
    NativeProcessStatus.START_FAILED: NativeIssueCode.PROBE_INTERNAL_ERROR,
}


def _seconds_between(value: object, low: float, high: float) -> bool:
    return type(value) in (int, float) and math.isfinite(value) and low <= value <= high


def _bounded_int(value: object, low: int, high: int) -> bool:
    return type(value) is int and low <= value <= high


@dataclass(frozen=True, slots=True)
class NativeProcessPolicy:
    """HARD upper bounds for an eventual native runner; no execution behavior."""

    timeout_seconds: float = 8.0
    max_stdout_bytes: int = 1_048_576
    max_stderr_bytes: int = 1_048_576
    poll_interval_ms: int = 50
    terminate_grace_seconds: float = 2.0
    max_argv_items: int = 128
    max_argv_characters: int = 32_768

    def __post_init__(self) -> None:
        if not _seconds_between(self.timeout_seconds, 1.0, 1_800.0):
            raise NativeProcessContractError("INVALID_NATIVE_TIMEOUT")
        if not (
            _bounded_int(self.max_stdout_bytes, 1, 1_048_576)
            and _bounded_int(self.max_stderr_bytes, 1, 1_048_576)
        ):
            raise NativeProcessContractError("INVALID_NATIVE_OUTPUT_CAP")
        if not _bounded_int(self.poll_interval_ms, 10, 100):
            raise NativeProcessContractError("INVALID_NATIVE_POLL_INTERVAL")
        if not _seconds_between(self.terminate_grace_seconds, 0.1, 5.0):
            raise NativeProcessContractError("INVALID_NATIVE_TERMINATION_GRACE")
        if not (
            _bounded_int(self.max_argv_items, 1, 128)
            and _bounded_int(self.max_argv_characters, 1, 32_768)
        ):
            raise NativeProcessContractError("INVALID_NATIVE_ARGV_LIMIT")

    @property
    def product_render_authorized(self) -> bool:
        """Even a valid subprocess policy cannot enable any Qt render control."""
        return False


@dataclass(frozen=True, slots=True)
class NativeProcessOutcome:
    """Public-safe accounting only; NEVER carries stdout, stderr or command."""

    status: NativeProcessStatus
    exit_code: int | None
    duration_ms: int
    bytes_seen_stdout: int
    bytes_seen_stderr: int
    issue: NativeIssueCode | None = None

    def __post_init__(self) -> None:
        if type(self.status) is not NativeProcessStatus:
            raise NativeProcessContractError("INVALID_NATIVE_PROCESS_STATUS")
        if self.exit_code is not None and not _bounded_int(self.exit_code, -(2**31), 2**31 - 1):
            raise NativeProcessContractError("INVALID_NATIVE_EXIT_CODE")
        if not (
            _bounded_int(self.duration_ms, 0, 2**63 - 1)
            and _bounded_int(self.bytes_seen_stdout, 0, 2**63 - 1)
            and _bounded_int(self.bytes_seen_stderr, 0, 2**63 - 1)
        ):
            raise NativeProcessContractError("INVALID_NATIVE_PROCESS_COUNTER")
        if self.issue is not None and type(self.issue) is not NativeIssueCode:
            raise NativeProcessContractError("INVALID_NATIVE_PROCESS_ISSUE")
        if self.status is NativeProcessStatus.SUCCESS:
            if self.exit_code != 0 or self.issue is not None:
                raise NativeProcessContractError("INVALID_NATIVE_PROCESS_SUCCESS")
        elif self.issue is not _STATUS_ISSUE[self.status]:
            raise NativeProcessContractError("INVALID_NATIVE_PROCESS_FAILURE")
        elif self.status is NativeProcessStatus.FAILED and (
            self.exit_code is None or self.exit_code == 0
        ):
            raise NativeProcessContractError("INVALID_NATIVE_PROCESS_EXIT_CODE")
        elif self.status is NativeProcessStatus.START_FAILED and self.exit_code is not None:
            raise NativeProcessContractError("INVALID_NATIVE_PROCESS_EXIT_CODE")

    @property
    def successful(self) -> bool:
        return self.status is NativeProcessStatus.SUCCESS

    @property
    def product_render_authorized(self) -> bool:
        """A process result is not proof of a verified user export."""
        return False
