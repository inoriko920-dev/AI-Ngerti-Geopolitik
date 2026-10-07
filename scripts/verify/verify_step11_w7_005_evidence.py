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
        "00_w7_005_pacing_report.json",
        "01_duration_qualification.json",
        "02_speed_qualification.json",
        "03_baseline_and_boundaries.json",
        "preview_baseline_frame15.png",
        "preview_speed_200_frame15.png",
        "preview_speed_50_frame15.png",
        "baseline_180f.mp4",
        "duration_150pct_210f.mp4",
        "speed_200pct_150f.mp4",
        "speed_50pct_240f.mp4",
    ]
    missing = [name for name in required if not (root / name).is_file()]
    if missing:
        raise SystemExit(f"missing W7-005 evidence: {missing}")
    for name in required:
        if (root / name).stat().st_size <= 0:
            raise SystemExit(f"empty W7-005 evidence: {name}")

    report = json.loads(
        (root / "00_w7_005_pacing_report.json").read_text(encoding="utf-8")
    )
    duration = json.loads(
        (root / "01_duration_qualification.json").read_text(encoding="utf-8")
    )
    speed = json.loads(
        (root / "02_speed_qualification.json").read_text(encoding="utf-8")
    )
    boundaries = json.loads(
        (root / "03_baseline_and_boundaries.json").read_text(encoding="utf-8")
    )

    true_checks = [
        "duration_real_timing",
        "duration_ripple",
        "speed_200_real_timing",
        "speed_50_real_timing",
        "speed_ripple",
        "speed_source_mapping",
        "speed_previews_distinct",
        "all_exports_have_audio",
        "candidate_hashes_match_verifier",
        "application_owned_ripple",
        "canonical_state_unchanged",
        "command_bus_history_unchanged",
        "source_media_unchanged",
    ]
    if report.get("status") != "PASS":
        raise SystemExit("W7-005 report is not PASS")
    for key in true_checks:
        if report.get(key) is not True:
            raise SystemExit(f"W7-005 gate false: {key}")

    for key in (
        "provider_profile_changed",
        "runtime_ui_changed",
        "canonical_ai_apply_started",
        "w7_006_transform_qualification_started",
    ):
        if report.get(key) is not False:
            raise SystemExit(f"W7-005 crossed later-task boundary: {key}")

    if duration.get("translated_command") != "SetClipDurationCommand":
        raise SystemExit("duration did not use canonical manual command")
    if duration.get("application_owned_ripple") is not True:
        raise SystemExit("duration ripple is not application-owned")
    if duration.get("qualified_duration_frames") != 90:
        raise SystemExit("duration qualification did not reach 90 frames")
    if duration.get("later_clip_starts") != [90, 150]:
        raise SystemExit("duration ripple evidence mismatch")
    if duration.get("candidate_hash_matches_verifier") is not True:
        raise SystemExit("duration candidate hash diverged from verifier proof")

    if speed.get("baseline_source_frame_at_offset_15") != 15:
        raise SystemExit("baseline source-frame mapping mismatch")
    if speed["speed_200"].get("duration_frames") != 30:
        raise SystemExit("200 percent speed duration mismatch")
    if speed["speed_200"].get("source_frame_at_offset_15") != 30:
        raise SystemExit("200 percent speed source-frame mapping mismatch")
    if speed["speed_50"].get("duration_frames") != 120:
        raise SystemExit("50 percent speed duration mismatch")
    if speed["speed_50"].get("source_frame_at_offset_15") != 7:
        raise SystemExit("50 percent speed source-frame mapping mismatch")
    if speed.get("all_previews_distinct") is not True:
        raise SystemExit("speed real previews are not distinct")

    if boundaries.get("canonical_state_unchanged") is not True:
        raise SystemExit("canonical state changed during qualification")
    if boundaries.get("command_bus_history_unchanged") is not True:
        raise SystemExit("CommandBus history changed during qualification")
    if boundaries.get("source_media_unchanged") is not True:
        raise SystemExit("source media changed during qualification")

    print(f"W7-005 evidence verification PASS: {len(required)}/{len(required)} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
