"""W8-002 frozen UI-041 projection for canonical validation results."""

from __future__ import annotations

from dataclasses import dataclass

from ai_ngerti_geopolitik.application.validation import (
    ValidationAction,
    ValidationResult,
    ValidationScope,
    ValidationSeverity,
)
from ai_ngerti_geopolitik.domain import ProjectState


@dataclass(frozen=True, slots=True)
class ValidationIssueProjection:
    severity_text: str
    title: str
    description: str
    action_label: str
    action_code: str
    issue_code: str
    category: str
    target_ids: tuple[str, ...]
    can_act: bool


@dataclass(frozen=True, slots=True)
class ValidationCenterProjection:
    project_revision: int
    stale: bool
    error_count: int
    warning_count: int
    issues: tuple[ValidationIssueProjection, ...]

    @property
    def total_count(self) -> int:
        return len(self.issues)

    @property
    def summary_title(self) -> str:
        if self.stale:
            return "Hasil validasi sudah usang"
        return f"{self.error_count} Error, {self.warning_count} Peringatan"

    @property
    def summary_detail(self) -> str:
        if self.stale:
            return "Project berubah setelah validasi. Jalankan Validasi Ulang."
        return f"Ditemukan {self.total_count} masalah dalam project ini"

    @property
    def tab_counts(self) -> tuple[tuple[str, int], ...]:
        categories = ("Project", "Media", "Scene", "AI", "Render")
        counts = {name: 0 for name in categories}
        for issue in self.issues:
            counts[issue.category] += 1
        return (
            ("Semua", self.total_count),
            *((name, counts[name]) for name in categories),
        )


_ACTION_LABELS = {
    ValidationAction.REVALIDATE: "Validasi Ulang",
    ValidationAction.RELINK_MEDIA: "Relink",
    ValidationAction.OPEN_SUBTITLE: "Buka Subtitle",
    ValidationAction.OPEN_NARRATION: "Buka Narasi",
    ValidationAction.NONE: "",
}


def _category(scope: ValidationScope) -> str:
    if scope in {ValidationScope.PROJECT, ValidationScope.RUNTIME}:
        return "Project"
    if scope is ValidationScope.MEDIA:
        return "Media"
    if scope in {
        ValidationScope.TIMELINE_SCENE,
        ValidationScope.SUBTITLE,
        ValidationScope.NARRATION,
    }:
        return "Scene"
    if scope is ValidationScope.AI:
        return "AI"
    return "Render"


def _severity_text(severity: ValidationSeverity) -> str:
    if severity is ValidationSeverity.WARNING:
        return "PERINGATAN"
    return severity.value


def project_validation_center(
    result: ValidationResult,
    current_state: ProjectState,
) -> ValidationCenterProjection:
    stale = result.is_stale(current_state)
    issues = tuple(
        ValidationIssueProjection(
            severity_text=_severity_text(issue.severity),
            title=issue.safe_title,
            description=issue.safe_message,
            action_label=_ACTION_LABELS[issue.remediation_action],
            action_code=issue.remediation_action.value,
            issue_code=issue.issue_code.value,
            category=_category(issue.scope),
            target_ids=issue.target_ids,
            can_act=not stale and issue.remediation_action is not ValidationAction.NONE,
        )
        for issue in result.issues
    )
    return ValidationCenterProjection(
        project_revision=result.project_revision,
        stale=stale,
        error_count=result.blocker_count + result.error_count,
        warning_count=result.warning_count + result.info_count,
        issues=issues,
    )
