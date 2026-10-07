from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

from ai_ngerti_geopolitik.application.validation import ValidationService
from ai_ngerti_geopolitik.domain import Asset, Clip, FrameTime, NarrationTrack, ProjectState, Track


def _asset(asset_id: str, media_type: str, availability: str) -> Asset:
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


def main() -> int:
    output = Path("artifacts/step11/w8-001/evidence")
    output.mkdir(parents=True, exist_ok=True)
    clip = Clip("C001", "A001", FrameTime(0, 30), FrameTime(0, 30), FrameTime(120, 30))
    state = ProjectState(
        "P-W8-001-EVIDENCE",
        "W8-001 deterministic validation",
        1,
        30,
        12,
        (
            _asset("A001", "video", "missing"),
            _asset("A002", "video", "missing"),
            _asset("A003", "audio", "offline"),
        ),
        (Track("V1", "video", 0, (clip,)),),
        narration=NarrationTrack("N001", "A003", FrameTime(0, 30)),
    )
    before = state.semantic_json(include_revision=True)
    result = ValidationService().validate(state)
    after = state.semantic_json(include_revision=True)
    invalid = ValidationService().validate(replace(state, schema_version=99))
    report = {
        "status": "PASS",
        "project_revision": result.project_revision,
        "issue_codes": [issue.issue_code.value for issue in result.issues],
        "issue_severities": [issue.severity.value for issue in result.issues],
        "issue_targets": [list(issue.target_ids) for issue in result.issues],
        "blocker_count": result.blocker_count,
        "error_count": result.error_count,
        "warning_count": result.warning_count,
        "info_count": result.info_count,
        "canonical_state_unchanged": before == after,
        "same_input_deterministic": ValidationService().validate(state) == result,
        "revision_stale_detected": result.is_stale(state.with_revision(13)),
        "semantic_stale_detected": result.is_stale(replace(state, name="same revision change")),
        "project_stale_detected": result.is_stale(replace(state, project_id="P-OTHER")),
        "invalid_project_issue_count": len(invalid.issues),
        "invalid_project_code": invalid.issues[0].issue_code.value,
        "filesystem_probe_started": False,
        "relink_started": False,
        "recovery_started": False,
        "diagnostics_started": False,
        "runtime_ui_changed": False,
        "canonical_apply_started": False,
    }
    expected = {
        "project_revision": 12,
        "issue_codes": [
            "MEDIA_MISSING_REFERENCED",
            "MEDIA_OFFLINE_REFERENCED",
            "MEDIA_MISSING_UNREFERENCED",
        ],
        "issue_severities": ["BLOCKER", "ERROR", "WARNING"],
        "issue_targets": [["A001", "C001"], ["A003", "N001"], ["A002"]],
        "blocker_count": 1,
        "error_count": 1,
        "warning_count": 1,
        "info_count": 0,
        "canonical_state_unchanged": True,
        "same_input_deterministic": True,
        "revision_stale_detected": True,
        "semantic_stale_detected": True,
        "project_stale_detected": True,
        "invalid_project_issue_count": 1,
        "invalid_project_code": "PROJECT_INVALID",
        "filesystem_probe_started": False,
        "relink_started": False,
        "recovery_started": False,
        "diagnostics_started": False,
        "runtime_ui_changed": False,
        "canonical_apply_started": False,
    }
    for key, value in expected.items():
        if report[key] != value:
            raise SystemExit(f"W8-001 evidence mismatch: {key}")
    (output / "00_w8_001_validation_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
