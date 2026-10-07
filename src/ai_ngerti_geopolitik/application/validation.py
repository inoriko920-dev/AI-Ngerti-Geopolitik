"""W8-001 typed, deterministic, non-mutating project validation contracts."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
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
                    f"Project gagal validasi canonical: {exc}. Perbaiki project lalu validasi ulang.",
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
