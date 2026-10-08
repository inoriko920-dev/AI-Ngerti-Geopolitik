"""SOL INT-01A pure contract checks; no native executable is started."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest

from ai_ngerti_geopolitik.application.native_toolchain_identity import (
    NativeCapabilityReport,
    NativeCapabilityStatus,
    NativeExecutableIdentity,
    NativeIdentityError,
    NativeIssueCode,
    NativeQualifiedProfile,
    NativeSource,
    NativeToolchainIdentity,
)


def _binary(tmp_path: Path, executable: str = "ffmpeg.exe") -> NativeExecutableIdentity:
    return NativeExecutableIdentity(
        path=tmp_path / "C Users private" / executable,
        sha256="a" * 64,
        byte_size=321,
        mtime_ns=0,
        version_label="ffmpeg 7.1 libavcodec",
        source=NativeSource.EXPLICIT_USER,
    )


def _pair(tmp_path: Path, **kwargs: object) -> NativeToolchainIdentity:
    arguments: dict[str, object] = {
        "ffmpeg": _binary(tmp_path),
        "ffprobe": _binary(tmp_path, "ffprobe.exe"),
        "encoder_names": ("libx264", "aac"),
        "checked_at_unix_ns": 1,
        "qualification_digest": "b" * 64,
        "qualified_profiles": (NativeQualifiedProfile.H264_AAC_BASELINE,),
    }
    arguments.update(kwargs)
    return NativeToolchainIdentity(**arguments)


def test_immutable_dto_never_authorizes_product_render(tmp_path: Path) -> None:
    executable = _binary(tmp_path)
    pair = _pair(tmp_path)
    report = NativeCapabilityReport(
        NativeCapabilityStatus.QUALIFIED_PILOT_ONLY,
        identity=pair,
    )
    assert executable.kind == "ffmpeg.exe"
    assert pair.has_baseline_claim
    assert not report.can_start_product_render
    assert "C Users private" not in repr(executable)
    assert "C Users private" not in repr(pair)
    assert "C Users private" not in repr(report)
    with pytest.raises(FrozenInstanceError):
        report.status = NativeCapabilityStatus.FAIL_CLOSED  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        executable.byte_size = 0  # type: ignore[misc]


@pytest.mark.parametrize(
    "mutations",
    [
        {"path": Path("relative/ffmpeg.exe")},
        {"path": Path("../ffmpeg.exe")},
        {"path": Path("C:\\not-windows-absolute-if-unix")},
        {"path": Path("/tmp/other.exe")},
        {"sha256": "not-digest"},
        {"sha256": "A" * 64},
        {"sha256": True},
        {"byte_size": 0},
        {"byte_size": -1},
        {"byte_size": True},
        {"mtime_ns": -1},
        {"mtime_ns": False},
        {"version_label": ""},
        {"version_label": "ffmpeg\nsecret"},
        {"version_label": "x" * 97},
        {"source": "explicit_user"},
    ],
)
def test_invalid_executable_identity_fails_closed(
    tmp_path: Path, mutations: dict[str, object]
) -> None:
    with pytest.raises(NativeIdentityError):
        replace(_binary(tmp_path), **mutations)


@pytest.mark.parametrize(
    "mutations",
    [
        {"encoder_names": ["libx264", "aac"]},
        {"encoder_names": ("libx264", "aac", "aac")},
        {"encoder_names": ("malicious_string",)},
        {"encoder_names": (True,)},
        {"checked_at_unix_ns": True},
        {"checked_at_unix_ns": 0},
        {"qualification_digest": "bad"},
        {"qualification_digest": True},
        {"qualified_profiles": ["h264_aac_baseline"]},
        {"qualified_profiles": ("h264_aac_baseline",)},
        {"qualified_profiles": (NativeQualifiedProfile.H264_AAC_BASELINE,) * 2},
        {"qualification_digest": None},
        {"encoder_names": ("aac",)},
    ],
)
def test_invalid_toolchain_claim_is_rejected(tmp_path: Path, mutations: dict[str, object]) -> None:
    with pytest.raises(NativeIdentityError):
        replace(_pair(tmp_path), **mutations)


def test_wrong_pair_and_hevc_qualifications_rejected(tmp_path: Path) -> None:
    with pytest.raises(NativeIdentityError, match="INVALID_NATIVE_TOOLCHAIN_PAIR"):
        _pair(tmp_path, ffprobe=_binary(tmp_path))
    with pytest.raises(NativeIdentityError, match="INVALID_NATIVE_PROFILE_CLAIM"):
        _pair(
            tmp_path,
            qualified_profiles=(NativeQualifiedProfile.H265_AAC_1080P30,),
        )
    valid = _pair(
        tmp_path,
        encoder_names=("libx265", "aac"),
        qualified_profiles=(NativeQualifiedProfile.H265_AAC_1080P30,),
    )
    assert not valid.has_baseline_claim


def test_incomplete_discovery_is_not_pilot_qualification(tmp_path: Path) -> None:
    pair = _pair(tmp_path, qualification_digest=None, qualified_profiles=())
    discovery = NativeCapabilityReport(
        status=NativeCapabilityStatus.DETECTED_UNVERIFIED, identity=pair
    )
    assert not discovery.can_start_product_render
    with pytest.raises(NativeIdentityError, match="NATIVE_QUALIFICATION_NOT_EVIDENCED"):
        NativeCapabilityReport(status=NativeCapabilityStatus.QUALIFIED_PILOT_ONLY, identity=pair)


@pytest.mark.parametrize(
    "status",
    [
        NativeCapabilityStatus.DETECTED_UNVERIFIED,
        NativeCapabilityStatus.QUALIFYING,
        NativeCapabilityStatus.QUALIFIED_PILOT_ONLY,
    ],
)
def test_nonfailed_status_requires_identity(status: NativeCapabilityStatus) -> None:
    with pytest.raises(NativeIdentityError, match="NATIVE_IDENTITY_REQUIRED"):
        NativeCapabilityReport(status=status)


def test_fail_closed_requires_redacted_reason(tmp_path: Path) -> None:
    with pytest.raises(NativeIdentityError, match="NATIVE_FAILURE_REASON_REQUIRED"):
        NativeCapabilityReport(status=NativeCapabilityStatus.FAIL_CLOSED)
    report = NativeCapabilityReport(
        NativeCapabilityStatus.FAIL_CLOSED, issue=NativeIssueCode.PROBE_TIMEOUT
    )
    assert "NATIVE_PROBE_TIMEOUT" in str(report)
    assert not report.can_start_product_render
    with pytest.raises(NativeIdentityError, match="INVALID_NATIVE_ISSUE"):
        replace(report, issue="C:\\Users\\private\\secret.mov")


def test_unknown_status_and_issue_mix_are_rejected(tmp_path: Path) -> None:
    report = NativeCapabilityReport(
        NativeCapabilityStatus.FAIL_CLOSED, issue=NativeIssueCode.NOT_FOUND
    )
    with pytest.raises(NativeIdentityError, match="INVALID_NATIVE_STATUS"):
        replace(report, status="qualified_pilot_only")
    with pytest.raises(NativeIdentityError, match="NATIVE_ISSUE_ONLY_FOR_FAILURE"):
        NativeCapabilityReport(
            NativeCapabilityStatus.DETECTED_UNVERIFIED,
            identity=_pair(tmp_path),
            issue=NativeIssueCode.PATH_UNTRUSTED,
        )


def test_all_native_fail_codes_are_distinct_and_safe() -> None:
    values = [member.value for member in NativeIssueCode]
    assert len(values) == len(set(values))
    assert all(value.startswith("NATIVE_") for value in values)
    assert all("\\" not in value and "/" not in value for value in values)
