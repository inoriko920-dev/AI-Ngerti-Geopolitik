from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    root = args.evidence.resolve()

    required = [
        "00_w7_007_transition_mixed_report.json",
        "01_transition_qualification.json",
        "02_mixed_plan_qualification.json",
        "preview_transition_baseline_frame1.png",
        "preview_transition_fade_black_frame1.png",
        "preview_mixed_frame15.png",
        "transition_fade_black_export.mp4",
        "mixed_plan_export.mp4",
    ]
    missing = [name for name in required if not (root / name).is_file()]
    if missing:
        raise SystemExit(f"missing W7-007 evidence: {missing}")
    if any((root / name).stat().st_size <= 0 for name in required):
        raise SystemExit("W7-007 evidence contains an empty file")

    report = json.loads(
        (root / "00_w7_007_transition_mixed_report.json").read_text(
            encoding="utf-8"
        )
    )
    transition = json.loads(
        (root / "01_transition_qualification.json").read_text(encoding="utf-8")
    )
    mixed = json.loads(
        (root / "02_mixed_plan_qualification.json").read_text(encoding="utf-8")
    )

    if report.get("status") != "PASS":
        raise SystemExit("W7-007 report is not PASS")

    for key in (
        "transition_manual_owner_reused",
        "transition_filter_fade_black",
        "transition_real_preview",
        "transition_real_export",
        "transition_export_audio",
        "transition_none_clear",
        "mixed_l1_l2_plan",
        "mixed_candidate_hash_matches_verifier",
        "mixed_candidate_revision_unchanged",
        "mixed_real_export",
        "mixed_export_audio",
        "canonical_state_unchanged",
        "command_bus_history_unchanged",
        "source_media_unchanged",
    ):
        if report.get(key) is not True:
            raise SystemExit(f"W7-007 gate false: {key}")

    for key in (
        "provider_profile_changed",
        "runtime_ui_changed",
        "canonical_ai_apply_started",
        "w7_008_provider_lifecycle_started",
    ):
        if report.get(key) is not False:
            raise SystemExit(f"W7-007 crossed later-task boundary: {key}")

    if transition.get("translated_command") != "SetClipPropertiesCommand":
        raise SystemExit("transition did not reuse SetClipPropertiesCommand")
    if transition.get("preset") != "fade_black":
        raise SystemExit("transition preset evidence mismatch")
    if transition.get("duration_frames") != 30:
        raise SystemExit("transition duration evidence mismatch")
    if transition.get("candidate_hash_matches_verifier") is not True:
        raise SystemExit("transition candidate hash mismatch")
    if transition.get("none_clear_verified") is not True:
        raise SystemExit("none transition clear evidence mismatch")
    if sum(
        1
        for item in transition.get("post_filters", [])
        if isinstance(item, str)
        and item.startswith("fade=t=")
        and "color=black" in item
    ) != 2:
        raise SystemExit("transition real render mapping evidence mismatch")

    expected_types = [
        "SetClipPropertiesCommand",
        "SetClipDurationCommand",
        "SetClipPropertiesCommand",
        "SetClipPropertiesCommand",
        "SetClipSpeedCommand",
        "SetClipPropertiesCommand",
    ]
    if mixed.get("translated_command_types") != expected_types:
        raise SystemExit("mixed plan canonical command sequence mismatch")
    if mixed.get("command_count") != 6 or mixed.get("target_count") != 2:
        raise SystemExit("mixed plan cardinality evidence mismatch")
    if mixed.get("candidate_hash_matches_verifier") is not True:
        raise SystemExit("mixed plan candidate hash mismatch")
    if mixed.get("candidate_revision_unchanged") is not True:
        raise SystemExit("mixed plan dry-run revision changed")
    if mixed.get("timeline_end_frames") != 210:
        raise SystemExit("mixed plan timeline result mismatch")
    if mixed["clip_1"]["duration_frames"] != 150:
        raise SystemExit("mixed C001 duration mismatch")
    if mixed["clip_1"]["transition_duration_frames"] != 45:
        raise SystemExit("mixed C001 transition mismatch")
    if mixed["clip_2"]["timeline_start"] != 150:
        raise SystemExit("mixed C002 ripple start mismatch")
    if mixed["clip_2"]["duration_frames"] != 60:
        raise SystemExit("mixed C002 speed duration mismatch")
    if mixed["clip_2"]["transition_duration_frames"] != 30:
        raise SystemExit("mixed C002 transition mismatch")

    print(f"W7-007 evidence verification PASS: {len(required)}/{len(required)} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
