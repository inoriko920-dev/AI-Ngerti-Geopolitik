from __future__ import annotations

from dataclasses import replace

from ai_ngerti_geopolitik.application.validation import (
    MediaIntegrityObservation,
    MediaIntegrityStatus,
    RealMediaIntegrityRule,
    ValidationIssueCode,
    ValidationService,
    ValidationSeverity,
)
from ai_ngerti_geopolitik.domain import Asset, Clip, FrameTime, ProjectState, Track


class Inspector:
    def __init__(self, observations: dict[str, MediaIntegrityObservation]) -> None:
        self.observations = observations

    def inspect(self, path):
        return self.observations[path.name]


def _asset(asset_id: str, path_ref: str, fingerprint: str) -> Asset:
    return Asset(
        asset_id,
        path_ref,
        "video",
        FrameTime(120, 30),
        1920,
        1080,
        True,
        fingerprint,
        source_name=path_ref,
        file_size=100,
        sample_rate=48000,
    )


def _state(*assets: Asset) -> ProjectState:
    clip = Clip("C001", assets[0].asset_id, FrameTime(0, 30), FrameTime(0, 30), FrameTime(90, 30))
    return ProjectState(
        "P-W8-002",
        "W8 media integrity",
        1,
        30,
        4,
        assets=assets,
        tracks=(Track("V1", "video", 0, (clip,)),),
    )


def _validate(state: ProjectState, observations: dict[str, MediaIntegrityObservation]):
    return ValidationService((RealMediaIntegrityRule(Inspector(observations)),)).validate(state)


def test_real_missing_referenced_file_is_blocker_without_mutation() -> None:
    asset = _asset("A001", "a.mp4", "a" * 64)
    state = _state(asset)
    before = state.semantic_json(include_revision=True)
    result = _validate(state, {"a.mp4": MediaIntegrityObservation(MediaIntegrityStatus.MISSING)})
    issue = result.issues[0]
    assert issue.issue_code is ValidationIssueCode.MEDIA_FILE_MISSING
    assert issue.severity is ValidationSeverity.BLOCKER
    assert issue.target_ids == ("A001", "C001")
    assert state.semantic_json(include_revision=True) == before


def test_zero_byte_and_probe_failure_are_typed() -> None:
    first = _asset("A001", "zero.mp4", "a" * 64)
    zero = _validate(
        _state(first),
        {"zero.mp4": MediaIntegrityObservation(MediaIntegrityStatus.ZERO_BYTE)},
    )
    assert zero.issues[0].issue_code is ValidationIssueCode.MEDIA_ZERO_BYTE

    broken = _validate(
        _state(replace(first, path_ref="broken.mp4")),
        {
            "broken.mp4": MediaIntegrityObservation(
                MediaIntegrityStatus.PROBE_FAILED,
                file_size=12,
                safe_error_code="MEDIA_PROBE_FAILED",
            )
        },
    )
    assert broken.issues[0].issue_code is ValidationIssueCode.MEDIA_PROBE_FAILED
    assert "MEDIA_PROBE_FAILED" in broken.issues[0].safe_message


def test_type_and_fingerprint_mismatch_are_errors_for_referenced_media() -> None:
    asset = _asset("A001", "a.mp4", "a" * 64)
    result = _validate(
        _state(asset),
        {
            "a.mp4": MediaIntegrityObservation(
                MediaIntegrityStatus.OK,
                file_size=100,
                media_type="image",
                fingerprint_sha256="b" * 64,
            )
        },
    )
    assert [item.issue_code for item in result.issues] == [
        ValidationIssueCode.MEDIA_FINGERPRINT_MISMATCH,
        ValidationIssueCode.MEDIA_TYPE_MISMATCH,
    ]
    assert all(item.severity is ValidationSeverity.ERROR for item in result.issues)


def test_duplicate_fingerprint_is_derived_info_only() -> None:
    first = _asset("A001", "a.mp4", "a" * 64)
    second = _asset("A002", "b.mp4", "a" * 64)
    observations = {
        "a.mp4": MediaIntegrityObservation(
            MediaIntegrityStatus.OK,
            file_size=100,
            media_type="video",
            fingerprint_sha256="a" * 64,
        ),
        "b.mp4": MediaIntegrityObservation(
            MediaIntegrityStatus.OK,
            file_size=100,
            media_type="video",
            fingerprint_sha256="a" * 64,
        ),
    }
    result = _validate(_state(first, second), observations)
    duplicate = next(
        item
        for item in result.issues
        if item.issue_code is ValidationIssueCode.MEDIA_DUPLICATE_FINGERPRINT
    )
    assert duplicate.severity is ValidationSeverity.INFO
    assert duplicate.target_ids == ("A001", "A002")


def test_canonical_missing_does_not_duplicate_physical_missing_issue() -> None:
    asset = replace(_asset("A001", "a.mp4", "a" * 64), availability="missing")
    result = _validate(
        _state(asset),
        {"a.mp4": MediaIntegrityObservation(MediaIntegrityStatus.MISSING)},
    )
    assert [item.issue_code for item in result.issues] == [
        ValidationIssueCode.MEDIA_MISSING_REFERENCED
    ]
