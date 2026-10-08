"""SOL INT-01B/B1 value-object tests; NEVER launch a child process."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace

import pytest

from ai_ngerti_geopolitik.application.native_process_contract import (
    NativeProcessContractError,
    NativeProcessOutcome,
    NativeProcessPolicy,
    NativeProcessStatus,
)
from ai_ngerti_geopolitik.application.native_toolchain_identity import NativeIssueCode


def _success() -> NativeProcessOutcome:
    return NativeProcessOutcome(
        status=NativeProcessStatus.SUCCESS,
        exit_code=0,
        duration_ms=456,
        bytes_seen_stdout=1_024,
        bytes_seen_stderr=2,
    )


def test_policy_is_immutable_bounded_and_does_not_authorize_render() -> None:
    policy = NativeProcessPolicy()
    assert (policy.timeout_seconds, policy.max_stdout_bytes, policy.poll_interval_ms) == (
        8.0,
        1_048_576,
        50,
    )
    assert not policy.product_render_authorized
    with pytest.raises(FrozenInstanceError):
        policy.max_stdout_bytes = 2_000_000  # type: ignore[misc]


@pytest.mark.parametrize(
    ("updates", "error"),
    [
        ({"timeout_seconds": 0.0}, "INVALID_NATIVE_TIMEOUT"),
        ({"timeout_seconds": 1_801}, "INVALID_NATIVE_TIMEOUT"),
        ({"timeout_seconds": float("inf")}, "INVALID_NATIVE_TIMEOUT"),
        ({"timeout_seconds": float("nan")}, "INVALID_NATIVE_TIMEOUT"),
        ({"timeout_seconds": 10**1000}, "INVALID_NATIVE_TIMEOUT"),
        ({"timeout_seconds": -(10**1000)}, "INVALID_NATIVE_TIMEOUT"),
        ({"timeout_seconds": True}, "INVALID_NATIVE_TIMEOUT"),
        ({"timeout_seconds": "8"}, "INVALID_NATIVE_TIMEOUT"),
        ({"max_stdout_bytes": 0}, "INVALID_NATIVE_OUTPUT_CAP"),
        ({"max_stdout_bytes": 1_048_577}, "INVALID_NATIVE_OUTPUT_CAP"),
        ({"max_stderr_bytes": -1}, "INVALID_NATIVE_OUTPUT_CAP"),
        ({"max_stderr_bytes": True}, "INVALID_NATIVE_OUTPUT_CAP"),
        ({"poll_interval_ms": 9}, "INVALID_NATIVE_POLL_INTERVAL"),
        ({"poll_interval_ms": 101}, "INVALID_NATIVE_POLL_INTERVAL"),
        ({"poll_interval_ms": 50.5}, "INVALID_NATIVE_POLL_INTERVAL"),
        ({"terminate_grace_seconds": 0}, "INVALID_NATIVE_TERMINATION_GRACE"),
        ({"terminate_grace_seconds": 5.1}, "INVALID_NATIVE_TERMINATION_GRACE"),
        ({"terminate_grace_seconds": float("nan")}, "INVALID_NATIVE_TERMINATION_GRACE"),
        ({"terminate_grace_seconds": 10**1000}, "INVALID_NATIVE_TERMINATION_GRACE"),
        ({"max_argv_items": 129}, "INVALID_NATIVE_ARGV_LIMIT"),
        ({"max_argv_items": False}, "INVALID_NATIVE_ARGV_LIMIT"),
        ({"max_argv_characters": 0}, "INVALID_NATIVE_ARGV_LIMIT"),
        ({"max_argv_characters": 32_769}, "INVALID_NATIVE_ARGV_LIMIT"),
    ],
)
def test_policy_rejects_invalid_bound_without_echoing_value(
    updates: dict[str, object], error: str
) -> None:
    with pytest.raises(NativeProcessContractError, match=f"^{error}$"):
        replace(NativeProcessPolicy(), **updates)


def test_valid_policy_limits_and_finite_fractional_values() -> None:
    policy = NativeProcessPolicy(
        timeout_seconds=1,
        max_stdout_bytes=1,
        max_stderr_bytes=1,
        poll_interval_ms=100,
        terminate_grace_seconds=0.1,
        max_argv_items=1,
        max_argv_characters=1,
    )
    assert policy.max_stdout_bytes == 1
    assert not policy.product_render_authorized


def test_success_has_bounded_counters_and_no_stdout_or_stderr() -> None:
    result = _success()
    assert result.successful
    assert not result.product_render_authorized
    assert result.issue is None
    assert not hasattr(result, "stderr")
    assert not hasattr(result, "stdout")
    with pytest.raises(FrozenInstanceError):
        result.duration_ms = 99  # type: ignore[misc]


@pytest.mark.parametrize(
    ("status", "issue", "exit_code"),
    [
        (NativeProcessStatus.FAILED, NativeIssueCode.QUALIFICATION_FAILED, 1),
        (NativeProcessStatus.TIMED_OUT, NativeIssueCode.PROBE_TIMEOUT, None),
        (NativeProcessStatus.CANCELLED, NativeIssueCode.PROCESS_CANCELLED, -1),
        (NativeProcessStatus.OUTPUT_LIMIT, NativeIssueCode.OUTPUT_TOO_LARGE, None),
        (NativeProcessStatus.START_FAILED, NativeIssueCode.PROBE_INTERNAL_ERROR, None),
    ],
)
def test_typed_failure_codes_cannot_be_silently_marked_success(
    status: NativeProcessStatus, issue: NativeIssueCode, exit_code: int | None
) -> None:
    result = replace(_success(), status=status, issue=issue, exit_code=exit_code)
    assert not result.successful
    assert not result.product_render_authorized
    assert result.issue is issue


@pytest.mark.parametrize(
    ("updates", "error"),
    [
        ({"status": "SUCCESS"}, "INVALID_NATIVE_PROCESS_STATUS"),
        ({"status": True}, "INVALID_NATIVE_PROCESS_STATUS"),
        ({"exit_code": None}, "INVALID_NATIVE_PROCESS_SUCCESS"),
        ({"exit_code": 1}, "INVALID_NATIVE_PROCESS_SUCCESS"),
        ({"exit_code": True}, "INVALID_NATIVE_EXIT_CODE"),
        ({"exit_code": 2**31}, "INVALID_NATIVE_EXIT_CODE"),
        ({"issue": NativeIssueCode.PROBE_TIMEOUT}, "INVALID_NATIVE_PROCESS_SUCCESS"),
        ({"issue": "SECRET_C_USERS"}, "INVALID_NATIVE_PROCESS_ISSUE"),
        ({"duration_ms": -1}, "INVALID_NATIVE_PROCESS_COUNTER"),
        ({"duration_ms": float("nan")}, "INVALID_NATIVE_PROCESS_COUNTER"),
        ({"duration_ms": 10**1000}, "INVALID_NATIVE_PROCESS_COUNTER"),
        ({"bytes_seen_stdout": -1}, "INVALID_NATIVE_PROCESS_COUNTER"),
        ({"bytes_seen_stderr": True}, "INVALID_NATIVE_PROCESS_COUNTER"),
        ({"bytes_seen_stderr": 2**63}, "INVALID_NATIVE_PROCESS_COUNTER"),
        (
            {"status": NativeProcessStatus.CANCELLED, "issue": None},
            "INVALID_NATIVE_PROCESS_FAILURE",
        ),
        (
            {"status": NativeProcessStatus.OUTPUT_LIMIT, "issue": NativeIssueCode.PROBE_TIMEOUT},
            "INVALID_NATIVE_PROCESS_FAILURE",
        ),
        (
            {
                "status": NativeProcessStatus.FAILED,
                "issue": NativeIssueCode.QUALIFICATION_FAILED,
                "exit_code": 0,
            },
            "INVALID_NATIVE_PROCESS_EXIT_CODE",
        ),
        (
            {
                "status": NativeProcessStatus.START_FAILED,
                "issue": NativeIssueCode.PROBE_INTERNAL_ERROR,
                "exit_code": 13,
            },
            "INVALID_NATIVE_PROCESS_EXIT_CODE",
        ),
    ],
)
def test_outcome_rejects_inconsistent_or_private_error_values(
    updates: dict[str, object], error: str
) -> None:
    with pytest.raises(NativeProcessContractError, match=f"^{error}$"):
        replace(_success(), **updates)


def test_no_success_or_failure_outcome_contains_untrusted_native_data() -> None:
    failure = NativeProcessOutcome(
        status=NativeProcessStatus.TIMED_OUT,
        exit_code=None,
        duration_ms=1_000,
        bytes_seen_stdout=45,
        bytes_seen_stderr=999,
        issue=NativeIssueCode.PROBE_TIMEOUT,
    )
    for result in (_success(), failure):
        assert "C:\\Users" not in repr(result)
        assert "TOKEN_SYNTHETIC_SECRET" not in str(result)
        assert not result.product_render_authorized
