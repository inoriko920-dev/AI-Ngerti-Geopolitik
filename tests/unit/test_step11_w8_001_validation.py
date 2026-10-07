from __future__ import annotations

from dataclasses import replace

import pytest

from ai_ngerti_geopolitik.application.validation import (
    ValidationAction,
    ValidationIssue,
    ValidationIssueCode,
    ValidationResult,
    ValidationScope,
    ValidationService,
    ValidationSeverity,
)
from ai_ngerti_geopolitik.domain import Asset, Clip, FrameTime, NarrationTrack, ProjectState, Track


def _asset(asset_id: str, media_type: str, availability: str = "online") -> Asset:
    visual = media_type != "audio"
    return Asset(
        asset_id,
        f"{asset_id}.{'wav' if media_type == 'audio' else 'mp4'}",
        media_type,
        FrameTime(180, 30),
        1280 if visual else 0,
        720 if visual else 0,
        media_type == "audio",
        asset_id[-1].lower() * 64,
        file_size=100,
        sample_rate=48000 if media_type == "audio" else 0,
        availability=availability,
    )


def _state() -> ProjectState:
    clip = Clip("C001", "A001", FrameTime(0, 30), FrameTime(0, 30), FrameTime(120, 30))
    return ProjectState(
        project_id="P-W8-001",
        name="W8 validation",
        schema_version=1,
        fps=30,
        revision=8,
        assets=(
            _asset("A001", "video", "missing"),
            _asset("A002", "video", "missing"),
            _asset("A003", "audio", "offline"),
        ),
        tracks=(Track("V1", "video", 0, (clip,)),),
        narration=NarrationTrack("N001", "A003", FrameTime(0, 30)),
    )


def test_validation_contract_is_typed_frozen_and_safe() -> None:
    issue = ValidationIssue(
        ValidationIssueCode.MEDIA_MISSING_REFERENCED,
        ValidationSeverity.BLOCKER,
        ValidationScope.MEDIA,
        "Media A001 missing",
        "A001 dipakai oleh C001. Relink media sebelum melanjutkan.",
        ("A001", "C001"),
        ValidationAction.RELINK_MEDIA,
        8,
    )
    assert issue.target_ids == ("A001", "C001")
    with pytest.raises(ValueError):
        replace(issue, safe_title="")
    with pytest.raises(ValueError):
        replace(issue, safe_message="bad\nmessage")
    with pytest.raises(ValueError):
        replace(issue, target_ids=("A001", "A001"))


def test_baseline_validation_is_deterministic_and_non_mutating() -> None:
    state = _state()
    before = state.semantic_json(include_revision=True)
    first = ValidationService().validate(state)
    second = ValidationService().validate(state)
    assert state.semantic_json(include_revision=True) == before
    assert first == second
    assert first.project_revision == 8
    assert first.project_semantic_hash == state.semantic_hash()
    assert [issue.severity for issue in first.issues] == [
        ValidationSeverity.BLOCKER,
        ValidationSeverity.ERROR,
        ValidationSeverity.WARNING,
    ]
    assert (first.blocker_count, first.error_count, first.warning_count, first.info_count) == (
        1,
        1,
        1,
        0,
    )
    assert first.has_blocker


def test_missing_referenced_media_is_blocker_with_exact_ids() -> None:
    issue = ValidationService().validate(_state()).issues[0]
    assert issue.issue_code is ValidationIssueCode.MEDIA_MISSING_REFERENCED
    assert issue.scope is ValidationScope.MEDIA
    assert issue.target_ids == ("A001", "C001")
    assert issue.remediation_action is ValidationAction.RELINK_MEDIA
    assert "A001" in issue.safe_message and "C001" in issue.safe_message


def test_offline_referenced_narration_is_error_not_project_mutation() -> None:
    state = _state()
    before = state.semantic_hash()
    result = ValidationService().validate(state)
    issue = next(
        item
        for item in result.issues
        if item.issue_code is ValidationIssueCode.MEDIA_OFFLINE_REFERENCED
    )
    assert issue.severity is ValidationSeverity.ERROR
    assert issue.target_ids == ("A003", "N001")
    assert state.semantic_hash() == before


def test_missing_unreferenced_media_is_warning() -> None:
    result = ValidationService().validate(_state())
    issue = next(
        item
        for item in result.issues
        if item.issue_code is ValidationIssueCode.MEDIA_MISSING_UNREFERENCED
    )
    assert issue.severity is ValidationSeverity.WARNING
    assert issue.target_ids == ("A002",)


def test_offline_unreferenced_media_is_info() -> None:
    state = ProjectState.create("P-INFO", "Info").with_revision(2)
    state = replace(state, assets=(_asset("A004", "video", "offline"),))
    result = ValidationService().validate(state)
    assert result.info_count == 1
    assert result.issues[0].issue_code is ValidationIssueCode.MEDIA_OFFLINE_UNREFERENCED


def test_structurally_invalid_project_short_circuits_to_one_project_blocker() -> None:
    result = ValidationService().validate(replace(_state(), schema_version=99))
    assert len(result.issues) == 1
    assert result.issues[0].issue_code is ValidationIssueCode.PROJECT_INVALID
    assert result.issues[0].scope is ValidationScope.PROJECT
    assert result.issues[0].severity is ValidationSeverity.BLOCKER
    assert result.issues[0].remediation_action is ValidationAction.REVALIDATE


def test_result_stale_gate_detects_revision_project_and_same_revision_semantic_change() -> None:
    state = _state()
    result = ValidationService().validate(state)
    assert result.is_stale(state) is False
    assert result.is_stale(state.with_revision(9)) is True
    assert result.is_stale(replace(state, project_id="P-OTHER")) is True
    assert result.is_stale(replace(state, name="Changed without revision")) is True


def test_result_rejects_issue_from_different_revision() -> None:
    issue = ValidationIssue(
        ValidationIssueCode.MEDIA_MISSING_UNREFERENCED,
        ValidationSeverity.WARNING,
        ValidationScope.MEDIA,
        "Media A001 missing",
        "A001 belum tersedia. Relink media ini bila diperlukan.",
        ("A001",),
        ValidationAction.RELINK_MEDIA,
        1,
    )
    with pytest.raises(ValueError):
        ValidationResult("P1", 2, "a" * 64, (issue,))
