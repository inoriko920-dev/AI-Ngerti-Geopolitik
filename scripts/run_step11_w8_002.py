from __future__ import annotations

import argparse
import json
import shutil
from dataclasses import replace
from pathlib import Path

from ai_ngerti_geopolitik.application.media_import import build_asset_from_probe
from ai_ngerti_geopolitik.application.validation import (
    RealMediaIntegrityRule,
    ValidationIssueCode,
    ValidationService,
)
from ai_ngerti_geopolitik.domain import Clip, FrameTime, ProjectState, Track
from ai_ngerti_geopolitik.infrastructure.ffmpeg_slice import FfprobeMediaProbe
from ai_ngerti_geopolitik.infrastructure.media_integrity import LocalMediaIntegrityInspector
from ai_ngerti_geopolitik.presentation.validation_center import project_validation_center


def _state(asset, *, revision: int = 20) -> ProjectState:
    clip = Clip(
        "C001",
        asset.asset_id,
        FrameTime(0, 30),
        FrameTime(0, 30),
        FrameTime(min(90, asset.duration.frames), 30),
    )
    return ProjectState(
        "P-W8-002-EVIDENCE",
        "W8-002 real media",
        1,
        30,
        revision,
        assets=(asset,),
        tracks=(Track("V1", "video", 0, (clip,)),),
    )


def _validate(state: ProjectState, inspector: LocalMediaIntegrityInspector):
    return ValidationService((RealMediaIntegrityRule(inspector),)).validate(state)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    evidence = args.evidence.resolve()
    evidence.mkdir(parents=True, exist_ok=True)

    probe = FfprobeMediaProbe()
    inspector = LocalMediaIntegrityInspector(probe)
    base = ProjectState.create("P-TEMP", "temp", 30)
    probe_result = probe.probe(args.video.resolve())
    asset = build_asset_from_probe(base, probe_result, "A001")
    clean_state = _state(asset)
    clean = _validate(clean_state, inspector)

    missing_asset = replace(asset, path_ref=str(evidence / "missing.mp4"))
    missing = _validate(_state(missing_asset), inspector)

    zero_path = evidence / "zero.mp4"
    zero_path.write_bytes(b"")
    zero = _validate(_state(replace(asset, path_ref=str(zero_path))), inspector)

    broken_path = evidence / "broken.mp4"
    broken_path.write_bytes(b"not-a-media-container")
    broken = _validate(_state(replace(asset, path_ref=str(broken_path))), inspector)

    duplicate_path = evidence / "duplicate.mp4"
    shutil.copy2(args.video.resolve(), duplicate_path)
    duplicate_probe = probe.probe(duplicate_path)
    duplicate_asset = build_asset_from_probe(base, duplicate_probe, "A002")
    duplicate_state = replace(
        clean_state,
        assets=(asset, duplicate_asset),
    )
    duplicate = _validate(duplicate_state, inspector)

    missing_projection = project_validation_center(missing, _state(missing_asset))
    stale_projection = project_validation_center(missing, _state(missing_asset, revision=21))

    report = {
        "status": "PASS",
        "clean_issue_count": len(clean.issues),
        "missing_codes": [item.issue_code.value for item in missing.issues],
        "missing_blocker": missing.has_blocker,
        "zero_codes": [item.issue_code.value for item in zero.issues],
        "broken_codes": [item.issue_code.value for item in broken.issues],
        "duplicate_codes": [item.issue_code.value for item in duplicate.issues],
        "duplicate_targets": [
            list(item.target_ids)
            for item in duplicate.issues
            if item.issue_code is ValidationIssueCode.MEDIA_DUPLICATE_FINGERPRINT
        ],
        "fixture_fingerprint": probe_result.fingerprint_sha256,
        "duplicate_fingerprint": duplicate_probe.fingerprint_sha256,
        "projection_total": missing_projection.total_count,
        "projection_media_count": dict(missing_projection.tab_counts)["Media"],
        "projection_stale_initial": missing_projection.stale,
        "projection_stale_after_revision": stale_projection.stale,
        "canonical_state_unchanged": clean_state.semantic_hash() == _state(asset).semantic_hash(),
        "relink_started": False,
        "recovery_started": False,
        "diagnostics_started": False,
        "ui_redesign_started": False,
    }
    expected = {
        "clean_issue_count": 0,
        "missing_codes": ["MEDIA_FILE_MISSING"],
        "missing_blocker": True,
        "zero_codes": ["MEDIA_ZERO_BYTE"],
        "broken_codes": ["MEDIA_PROBE_FAILED"],
        "duplicate_codes": ["MEDIA_DUPLICATE_FINGERPRINT"],
        "duplicate_targets": [["A001", "A002"]],
        "projection_total": 1,
        "projection_media_count": 1,
        "projection_stale_initial": False,
        "projection_stale_after_revision": True,
        "canonical_state_unchanged": True,
        "relink_started": False,
        "recovery_started": False,
        "diagnostics_started": False,
        "ui_redesign_started": False,
    }
    if report["fixture_fingerprint"] != report["duplicate_fingerprint"]:
        raise SystemExit("W8-002 duplicate real-media fingerprint mismatch")
    for key, value in expected.items():
        if report[key] != value:
            raise SystemExit(f"W8-002 evidence mismatch: {key}")

    (evidence / "00_w8_002_real_media_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
