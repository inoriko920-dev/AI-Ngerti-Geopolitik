"""SOL INT-01A: immutable, privacy-safe identity contract for external media tools.

This module performs NO disk reads, executable discovery, probing or launching.
Its fields are untrusted *claims* until infrastructure independently validates
them in later INT-01 tasks. It NEVER enables the product render button.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path


class NativeIdentityError(ValueError):
    """Typed, privacy-safe failures with no native paths or subprocess text."""


class NativeSource(StrEnum):
    EXPLICIT_USER = "explicit_user"
    PATH_CANDIDATE = "path_candidate"


class NativeCapabilityStatus(StrEnum):
    FAIL_CLOSED = "fail_closed"
    DETECTED_UNVERIFIED = "detected_unverified"
    QUALIFYING = "qualifying"
    QUALIFIED_PILOT_ONLY = "qualified_pilot_only"
    REVALIDATION_REQUIRED = "revalidation_required"


class NativeIssueCode(StrEnum):
    NOT_FOUND = "NATIVE_NOT_FOUND"
    PATH_UNTRUSTED = "NATIVE_PATH_UNTRUSTED"
    PAIR_MISMATCH = "NATIVE_PAIR_MISMATCH"
    VERSION_REJECTED = "NATIVE_VERSION_REJECTED"
    PROBE_TIMEOUT = "NATIVE_PROBE_TIMEOUT"
    OUTPUT_TOO_LARGE = "NATIVE_OUTPUT_TOO_LARGE"
    ENCODER_MISSING = "NATIVE_ENCODER_MISSING"
    QUALIFICATION_FAILED = "NATIVE_QUALIFICATION_FAILED"
    FINGERPRINT_CHANGED = "NATIVE_FINGERPRINT_CHANGED"
    PROCESS_CANCELLED = "NATIVE_PROCESS_CANCELLED"
    PROBE_INTERNAL_ERROR = "NATIVE_PROBE_INTERNAL_ERROR"


class NativeQualifiedProfile(StrEnum):
    H264_AAC_BASELINE = "h264_aac_baseline"
    H265_AAC_1080P30 = "h265_aac_1080p30"


_DIGEST = re.compile(r"[0-9a-f]{64}\Z")
_SAFE_VERSION = re.compile(r"[\x20-\x7e]{1,96}\Z")


def _is_digest(value: object) -> bool:
    return type(value) is str and _DIGEST.fullmatch(value) is not None


def _valid_path(path: object, name: str) -> bool:
    return (
        isinstance(path, Path)
        and path.is_absolute()
        and path.name.lower() == name
        and ".." not in path.parts
        and all(ord(char) >= 32 and ord(char) != 127 for char in str(path))
    )


@dataclass(frozen=True, slots=True)
class NativeExecutableIdentity:
    """Untrusted snapshot claim; path is intentionally excluded from repr."""

    path: Path = field(repr=False)
    sha256: str
    byte_size: int
    mtime_ns: int
    version_label: str
    source: NativeSource

    def __post_init__(self) -> None:
        if not (_valid_path(self.path, "ffmpeg.exe") or _valid_path(self.path, "ffprobe.exe")):
            raise NativeIdentityError("INVALID_NATIVE_EXECUTABLE_PATH")
        if not _is_digest(self.sha256):
            raise NativeIdentityError("INVALID_NATIVE_FINGERPRINT")
        if type(self.byte_size) is not int or self.byte_size <= 0:
            raise NativeIdentityError("INVALID_NATIVE_FILE_STAMP")
        if type(self.mtime_ns) is not int or self.mtime_ns < 0:
            raise NativeIdentityError("INVALID_NATIVE_FILE_STAMP")
        if (
            type(self.version_label) is not str
            or _SAFE_VERSION.fullmatch(self.version_label) is None
        ):
            raise NativeIdentityError("INVALID_NATIVE_VERSION_LABEL")
        if type(self.source) is not NativeSource:
            raise NativeIdentityError("INVALID_NATIVE_SOURCE")

    @property
    def kind(self) -> str:
        return self.path.name.lower()


@dataclass(frozen=True, slots=True)
class NativeToolchainIdentity:
    """A matched candidate pair, never a credential or trust approval."""

    ffmpeg: NativeExecutableIdentity = field(repr=False)
    ffprobe: NativeExecutableIdentity = field(repr=False)
    encoder_names: tuple[str, ...]
    checked_at_unix_ns: int
    qualification_digest: str | None = None
    qualified_profiles: tuple[NativeQualifiedProfile, ...] = ()

    def __post_init__(self) -> None:
        if (
            type(self.ffmpeg) is not NativeExecutableIdentity
            or type(self.ffprobe) is not NativeExecutableIdentity
            or self.ffmpeg.kind != "ffmpeg.exe"
            or self.ffprobe.kind != "ffprobe.exe"
            or self.ffmpeg.path == self.ffprobe.path
        ):
            raise NativeIdentityError("INVALID_NATIVE_TOOLCHAIN_PAIR")
        if type(self.checked_at_unix_ns) is not int or self.checked_at_unix_ns <= 0:
            raise NativeIdentityError("INVALID_NATIVE_CHECK_TIME")
        if (
            type(self.encoder_names) is not tuple
            or len(self.encoder_names) > 16
            or any(
                type(name) is not str or name not in {"libx264", "libx265", "aac"}
                for name in self.encoder_names
            )
            or len(set(self.encoder_names)) != len(self.encoder_names)
        ):
            raise NativeIdentityError("INVALID_NATIVE_ENCODER_CLAIM")
        if self.qualification_digest is not None and not _is_digest(self.qualification_digest):
            raise NativeIdentityError("INVALID_NATIVE_QUALIFICATION_DIGEST")
        if (
            type(self.qualified_profiles) is not tuple
            or any(
                type(profile) is not NativeQualifiedProfile for profile in self.qualified_profiles
            )
            or len(set(self.qualified_profiles)) != len(self.qualified_profiles)
            or (self.qualified_profiles and self.qualification_digest is None)
        ):
            raise NativeIdentityError("INVALID_NATIVE_PROFILE_CLAIM")
        if (
            NativeQualifiedProfile.H264_AAC_BASELINE in self.qualified_profiles
            and not {"libx264", "aac"}.issubset(self.encoder_names)
        ) or (
            NativeQualifiedProfile.H265_AAC_1080P30 in self.qualified_profiles
            and not {"libx265", "aac"}.issubset(self.encoder_names)
        ):
            raise NativeIdentityError("INVALID_NATIVE_PROFILE_CLAIM")

    @property
    def has_baseline_claim(self) -> bool:
        return NativeQualifiedProfile.H264_AAC_BASELINE in self.qualified_profiles


@dataclass(frozen=True, slots=True)
class NativeCapabilityReport:
    """An application snapshot; not a product capability authorization."""

    status: NativeCapabilityStatus
    identity: NativeToolchainIdentity | None = field(default=None, repr=False)
    issue: NativeIssueCode | None = None

    def __post_init__(self) -> None:
        if type(self.status) is not NativeCapabilityStatus:
            raise NativeIdentityError("INVALID_NATIVE_STATUS")
        if self.identity is not None and type(self.identity) is not NativeToolchainIdentity:
            raise NativeIdentityError("INVALID_NATIVE_REPORT_IDENTITY")
        if self.issue is not None and type(self.issue) is not NativeIssueCode:
            raise NativeIdentityError("INVALID_NATIVE_ISSUE")
        if self.status is NativeCapabilityStatus.FAIL_CLOSED:
            if self.issue is None:
                raise NativeIdentityError("NATIVE_FAILURE_REASON_REQUIRED")
        elif self.issue is not None:
            raise NativeIdentityError("NATIVE_ISSUE_ONLY_FOR_FAILURE")
        if (
            self.status
            in {
                NativeCapabilityStatus.QUALIFYING,
                NativeCapabilityStatus.DETECTED_UNVERIFIED,
                NativeCapabilityStatus.QUALIFIED_PILOT_ONLY,
            }
            and self.identity is None
        ):
            raise NativeIdentityError("NATIVE_IDENTITY_REQUIRED")
        if self.status is NativeCapabilityStatus.QUALIFIED_PILOT_ONLY and (
            self.identity is None or not self.identity.qualified_profiles
        ):
            raise NativeIdentityError("NATIVE_QUALIFICATION_NOT_EVIDENCED")

    @property
    def can_start_product_render(self) -> bool:
        """Never becomes True just because the native identity DTO is constructed."""
        return False
