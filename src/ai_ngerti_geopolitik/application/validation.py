"""W8-001 typed, deterministic, non-mutating project validation contracts."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Protocol

from ai_ngerti_geopolitik.domain import DomainValidationError, ProjectState


class ValidationSeverity(StrEnum):
    BLOCKER = "BLOCKER"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


class ValidationScope(StrEnum):
    PROJECT = "PROJECT"
    MEDIA = "MEDIA"
    TIMELINE_SCENE = "TIMELINE_SCENE"
    SUBTITLE = "SUBTITLE"
    NARRATION = "NARRATION"
    AI = "AI"
    RENDER = "RENDER"
    RUNTIME = "RUNTIME"


class ValidationAction(StrEnum):
    REVALIDATE = "REVALIDATE"
    RELINK_MEDIA = "RELINK_MEDIA"
    OPEN_SUBTITLE = "OPEN_SUBTITLE"
    OPEN_NARRATION = "OPEN_NARRATION"
    NONE = "NONE"


class ValidationIssueCode(StrEnum):
    PROJECT_INVALID = "PROJECT_INVALID"
    MEDIA_MISSING_REFERENCED = "MEDIA_MISSING_REFERENCED"
    MEDIA_MISSING_UNREFERENCED = "MEDIA_MISSING_UNREFERENCED"
    MEDIA_OFFLINE_REFERENCED = "MEDIA_OFFLINE_REFERENCED"
    MEDIA_OFFLINE_UNREFERENCED = "MEDIA_OFFLINE_UNREFERENCED"
    MEDIA_FILE_MISSING = "MEDIA_FILE_MISSING"
    MEDIA_ZERO_BYTE = "MEDIA_ZERO_BYTE"
    MEDIA_PROBE_FAILED = "MEDIA_PROBE_FAILED"
    MEDIA_TYPE_MISMATCH = "MEDIA_TYPE_MISMATCH"
    MEDIA_FINGERPRINT_MISMATCH = "MEDIA_FINGERPRINT_MISMATCH"
    MEDIA_DUPLICATE_FINGERPRINT = "MEDIA_DUPLICATE_FINGERPRINT"


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    issue_code: ValidationIssueCode
    severity: ValidationSeverity
    scope: ValidationScope
    safe_title: str
    safe_message: str
    target_ids: tuple[str, ...]
    remediation_action: ValidationAction
    project_revision: int

    def __post_init__(self) -> None:
        title = self.safe_title.strip()
        message = self.safe_message.strip()
        if not title:
            raise ValueError("validation issue title is required")
        if not message:
            raise ValueError("validation issue message is required")
        if len(title) > 120:
            raise ValueError("validation issue title must not exceed 120 characters")
        if len(message) > 500:
            raise ValueError("validation issue message must not exceed 500 characters")
        if any(character in title for character in "\r\n\t"):
            raise ValueError("validation issue title cannot contain control whitespace")
        if any(character in message for character in "\r\n\t"):
            raise ValueError("validation issue message cannot contain control whitespace")
        if self.project_revision < 0:
            raise ValueError("validation issue revision must be non-negative")
        normalized_targets = tuple(
            dict.fromkeys(item.strip() for item in self.target_ids if item.strip())
        )
        if normalized_targets != self.target_ids:
            raise ValueError("validation issue targets must be non-empty, unique and normalized")
        object.__setattr__(self, "safe_title", title)
        object.__setattr__(self, "safe_message", message)


@dataclass(frozen=True, slots=True)
class ValidationResult:
    project_id: str
    project_revision: int
    project_semantic_hash: str
    issues: tuple[ValidationIssue, ...]

    def __post_init__(self) -> None:
        if not self.project_id.strip():
            raise ValueError("validation result project id is required")
        if self.project_revision < 0:
            raise ValueError("validation result revision must be non-negative")
        if len(self.project_semantic_hash) != 64:
            raise ValueError("validation result semantic hash must be SHA-256")
        if any(issue.project_revision != self.project_revision for issue in self.issues):
            raise ValueError("validation issue revision must match result revision")

    @property
    def has_blocker(self) -> bool:
        return any(issue.severity is ValidationSeverity.BLOCKER for issue in self.issues)

    @property
    def blocker_count(self) -> int:
        return sum(issue.severity is ValidationSeverity.BLOCKER for issue in self.issues)

    @property
    def error_count(self) -> int:
        return sum(issue.severity is ValidationSeverity.ERROR for issue in self.issues)

    @property
    def warning_count(self) -> int:
        return sum(issue.severity is ValidationSeverity.WARNING for issue in self.issues)

    @property
    def info_count(self) -> int:
        return sum(issue.severity is ValidationSeverity.INFO for issue in self.issues)

    def is_stale(self, state: ProjectState) -> bool:
        return (
            state.project_id != self.project_id
            or state.revision != self.project_revision
            or state.semantic_hash() != self.project_semantic_hash
        )


class ValidationRule(Protocol):
    def evaluate(self, state: ProjectState) -> tuple[ValidationIssue, ...]: ...


@dataclass(frozen=True, slots=True)
class CanonicalStateRule:
    """Expose ProjectState.validate() failures as one safe project blocker."""

    def evaluate(self, state: ProjectState) -> tuple[ValidationIssue, ...]:
        try:
            state.validate()
        except DomainValidationError as exc:
            return (
                ValidationIssue(
                    ValidationIssueCode.PROJECT_INVALID,
                    ValidationSeverity.BLOCKER,
                    ValidationScope.PROJECT,
                    "Project tidak valid",
                    (
                        f"Project gagal validasi canonical: {exc}. "
                        "Perbaiki project lalu validasi ulang."
                    ),
                    (state.project_id,),
                    ValidationAction.REVALIDATE,
                    state.revision,
                ),
            )
        return ()


@dataclass(frozen=True, slots=True)
class MediaAvailabilityRule:
    """Project-only availability checks; no filesystem probing belongs in W8-001."""

    def evaluate(self, state: ProjectState) -> tuple[ValidationIssue, ...]:
        references: dict[str, list[str]] = {}
        for track in state.tracks:
            for clip in track.clips:
                references.setdefault(clip.asset_id, []).append(clip.clip_id)
        if state.narration is not None:
            references.setdefault(state.narration.asset_id, []).append(state.narration.narration_id)

        issues: list[ValidationIssue] = []
        for asset in sorted(state.assets, key=lambda item: item.asset_id):
            if asset.availability == "online":
                continue
            targets = (asset.asset_id, *sorted(references.get(asset.asset_id, ())))
            referenced = len(targets) > 1
            if asset.availability == "missing":
                issue_code = (
                    ValidationIssueCode.MEDIA_MISSING_REFERENCED
                    if referenced
                    else ValidationIssueCode.MEDIA_MISSING_UNREFERENCED
                )
                severity = ValidationSeverity.BLOCKER if referenced else ValidationSeverity.WARNING
                message = (
                    f"{asset.asset_id} tidak ditemukan dan dipakai oleh "
                    f"{', '.join(targets[1:])}. Relink media ini sebelum melanjutkan."
                    if referenced
                    else f"{asset.asset_id} tidak ditemukan tetapi belum dipakai timeline/narasi. "
                    "Relink media ini bila ingin digunakan."
                )
            else:
                issue_code = (
                    ValidationIssueCode.MEDIA_OFFLINE_REFERENCED
                    if referenced
                    else ValidationIssueCode.MEDIA_OFFLINE_UNREFERENCED
                )
                severity = ValidationSeverity.ERROR if referenced else ValidationSeverity.INFO
                message = (
                    f"{asset.asset_id} berstatus offline dan dipakai oleh "
                    f"{', '.join(targets[1:])}. Relink atau aktifkan media sebelum action terkait."
                    if referenced
                    else f"{asset.asset_id} berstatus offline dan belum dipakai timeline/narasi."
                )
            issues.append(
                ValidationIssue(
                    issue_code,
                    severity,
                    ValidationScope.MEDIA,
                    f"Media {asset.asset_id} {asset.availability}",
                    message,
                    targets,
                    ValidationAction.RELINK_MEDIA,
                    state.revision,
                )
            )
        return tuple(issues)



class MediaIntegrityStatus(StrEnum):
    OK = "OK"
    MISSING = "MISSING"
    ZERO_BYTE = "ZERO_BYTE"
    PROBE_FAILED = "PROBE_FAILED"


@dataclass(frozen=True, slots=True)
class MediaIntegrityObservation:
    status: MediaIntegrityStatus
    file_size: int = 0
    media_type: str | None = None
    fingerprint_sha256: str | None = None
    safe_error_code: str = ""

    def __post_init__(self) -> None:
        if self.file_size < 0:
            raise ValueError("media integrity file size must be non-negative")
        if self.status is MediaIntegrityStatus.OK:
            if self.media_type not in {"video", "audio", "image"}:
                raise ValueError("OK media integrity observation requires a media type")
            if self.fingerprint_sha256 is None or len(self.fingerprint_sha256) != 64:
                raise ValueError("OK media integrity observation requires SHA-256 fingerprint")
        error_code = self.safe_error_code.strip()
        if len(error_code) > 80:
            raise ValueError("media integrity error code must not exceed 80 characters")
        if any(character in error_code for character in "\r\n\t"):
            raise ValueError("media integrity error code cannot contain control whitespace")
        object.__setattr__(self, "safe_error_code", error_code)


class MediaIntegrityInspectorPort(Protocol):
    def inspect(self, path: Path) -> MediaIntegrityObservation: ...


@dataclass(frozen=True, slots=True)
class RealMediaIntegrityRule:
    inspector: MediaIntegrityInspectorPort

    @staticmethod
    def _references(state: ProjectState) -> dict[str, tuple[str, ...]]:
        references: dict[str, list[str]] = {}
        for track in state.tracks:
            for clip in track.clips:
                references.setdefault(clip.asset_id, []).append(clip.clip_id)
        if state.narration is not None:
            references.setdefault(state.narration.asset_id, []).append(state.narration.narration_id)
        return {
            asset_id: tuple(sorted(items))
            for asset_id, items in references.items()
        }

    @staticmethod
    def _severity(referenced: bool, *, hard: bool) -> ValidationSeverity:
        if referenced:
            return ValidationSeverity.BLOCKER if hard else ValidationSeverity.ERROR
        return ValidationSeverity.WARNING

    def evaluate(self, state: ProjectState) -> tuple[ValidationIssue, ...]:
        references = self._references(state)
        issues: list[ValidationIssue] = []
        fingerprints: dict[str, list[str]] = {}

        for asset in sorted(state.assets, key=lambda item: item.asset_id):
            observation = self.inspector.inspect(Path(asset.path_ref))
            target_refs = references.get(asset.asset_id, ())
            targets = (asset.asset_id, *target_refs)
            referenced = bool(target_refs)

            if observation.status is MediaIntegrityStatus.MISSING:
                if asset.availability != "missing":
                    issues.append(
                        ValidationIssue(
                            ValidationIssueCode.MEDIA_FILE_MISSING,
                            self._severity(referenced, hard=True),
                            ValidationScope.MEDIA,
                            f"Media {asset.asset_id} tidak ditemukan",
                            (
                                f"{asset.asset_id} tidak ada pada lokasi sumber saat validasi real-media. "
                                "Relink media sebelum operasi yang memerlukannya."
                            ),
                            targets,
                            ValidationAction.RELINK_MEDIA,
                            state.revision,
                        )
                    )
                continue

            if observation.status is MediaIntegrityStatus.ZERO_BYTE:
                issues.append(
                    ValidationIssue(
                        ValidationIssueCode.MEDIA_ZERO_BYTE,
                        self._severity(referenced, hard=True),
                        ValidationScope.MEDIA,
                        f"Media {asset.asset_id} kosong",
                        (
                            f"{asset.asset_id} berukuran 0 byte dan tidak dapat dipakai. "
                            "Relink ke file media yang valid."
                        ),
                        targets,
                        ValidationAction.RELINK_MEDIA,
                        state.revision,
                    )
                )
                continue

            if observation.status is MediaIntegrityStatus.PROBE_FAILED:
                issues.append(
                    ValidationIssue(
                        ValidationIssueCode.MEDIA_PROBE_FAILED,
                        self._severity(referenced, hard=True),
                        ValidationScope.MEDIA,
                        f"Media {asset.asset_id} gagal dibaca",
                        (
                            f"{asset.asset_id} tidak lolos pemeriksaan media "
                            f"({observation.safe_error_code or 'PROBE_FAILED'}). "
                            "Relink atau ganti dengan media yang dapat dibaca."
                        ),
                        targets,
                        ValidationAction.RELINK_MEDIA,
                        state.revision,
                    )
                )
                continue

            assert observation.fingerprint_sha256 is not None
            assert observation.media_type is not None
            fingerprints.setdefault(observation.fingerprint_sha256, []).append(asset.asset_id)

            if observation.media_type != asset.media_type:
                issues.append(
                    ValidationIssue(
                        ValidationIssueCode.MEDIA_TYPE_MISMATCH,
                        self._severity(referenced, hard=False),
                        ValidationScope.MEDIA,
                        f"Tipe media {asset.asset_id} berubah",
                        (
                            f"{asset.asset_id} tercatat sebagai {asset.media_type} tetapi file saat ini "
                            f"terbaca sebagai {observation.media_type}. Verifikasi atau relink media."
                        ),
                        targets,
                        ValidationAction.RELINK_MEDIA,
                        state.revision,
                    )
                )
            if observation.fingerprint_sha256 != asset.fingerprint_sha256:
                issues.append(
                    ValidationIssue(
                        ValidationIssueCode.MEDIA_FINGERPRINT_MISMATCH,
                        self._severity(referenced, hard=False),
                        ValidationScope.MEDIA,
                        f"Identitas media {asset.asset_id} berubah",
                        (
                            f"SHA-256 file {asset.asset_id} berbeda dari fingerprint project. "
                            "Verifikasi sumber atau relink media."
                        ),
                        targets,
                        ValidationAction.RELINK_MEDIA,
                        state.revision,
                    )
                )

        for fingerprint, asset_ids in sorted(fingerprints.items()):
            if len(asset_ids) < 2:
                continue
            targets = tuple(sorted(asset_ids))
            issues.append(
                ValidationIssue(
                    ValidationIssueCode.MEDIA_DUPLICATE_FINGERPRINT,
                    ValidationSeverity.INFO,
                    ValidationScope.MEDIA,
                    "Media duplikat terdeteksi",
                    (
                        f"{', '.join(targets)} memiliki fingerprint file yang sama. "
                        "Ini hanya informasi kesehatan media dan tidak mengubah project."
                    ),
                    targets,
                    ValidationAction.NONE,
                    state.revision,
                )
            )

        return tuple(issues)


_SEVERITY_ORDER = {
    ValidationSeverity.BLOCKER: 0,
    ValidationSeverity.ERROR: 1,
    ValidationSeverity.WARNING: 2,
    ValidationSeverity.INFO: 3,
}


class ValidationService:
    """Deterministic non-mutating validation projection for one canonical revision."""

    def __init__(self, extra_rules: tuple[ValidationRule, ...] = ()) -> None:
        self._rules: tuple[ValidationRule, ...] = (
            CanonicalStateRule(),
            MediaAvailabilityRule(),
            *extra_rules,
        )

    def validate(self, state: ProjectState) -> ValidationResult:
        semantic_before = state.semantic_json(include_revision=True)
        canonical_issues = self._rules[0].evaluate(state)
        if canonical_issues:
            issues = canonical_issues
        else:
            collected: list[ValidationIssue] = []
            for rule in self._rules[1:]:
                collected.extend(rule.evaluate(state))
            issues = tuple(
                sorted(
                    collected,
                    key=lambda issue: (
                        _SEVERITY_ORDER[issue.severity],
                        issue.scope.value,
                        issue.issue_code.value,
                        issue.target_ids,
                    ),
                )
            )
        if state.semantic_json(include_revision=True) != semantic_before:
            raise RuntimeError("validation rules must not mutate canonical ProjectState")
        return ValidationResult(
            project_id=state.project_id,
            project_revision=state.revision,
            project_semantic_hash=state.semantic_hash(),
            issues=issues,
        )
