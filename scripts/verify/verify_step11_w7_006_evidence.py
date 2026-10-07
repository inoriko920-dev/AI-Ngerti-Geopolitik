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
        "00_w7_006_transform_report.json",
        "01_transform_qualification.json",
        "preview_baseline_frame30.png",
        "preview_transform_position_frame30.png",
        "preview_transform_scale_frame30.png",
        "preview_transform_rotation_frame30.png",
        "preview_transform_opacity_frame30.png",
        "preview_transform_composite_frame30.png",
        "transform_composite_90f.mp4",
    ]
    missing = [name for name in required if not (root / name).is_file()]
    if missing:
        raise SystemExit(f"missing W7-006 evidence: {missing}")
    if any((root / name).stat().st_size <= 0 for name in required):
        raise SystemExit("W7-006 evidence contains an empty file")

    report = json.loads((root / "00_w7_006_transform_report.json").read_text(encoding="utf-8"))
    detail = json.loads((root / "01_transform_qualification.json").read_text(encoding="utf-8"))

    if report.get("status") != "PASS":
        raise SystemExit("W7-006 report is not PASS")

    for key in (
        "position_real_preview",
        "scale_real_preview",
        "rotation_real_preview",
        "opacity_real_preview",
        "all_previews_distinct",
        "composite_real_export",
        "composite_export_audio",
        "candidate_hashes_match_verifier",
        "canonical_state_unchanged",
        "command_bus_history_unchanged",
        "source_media_unchanged",
    ):
        if report.get(key) is not True:
            raise SystemExit(f"W7-006 gate false: {key}")

    for key in (
        "provider_profile_changed",
        "runtime_ui_changed",
        "canonical_ai_apply_started",
        "w7_007_transition_mixed_started",
    ):
        if report.get(key) is not False:
            raise SystemExit(f"W7-006 crossed later-task boundary: {key}")

    if (
        detail["position"]["position_x"],
        detail["position"]["position_y"],
    ) != (240, -120):
        raise SystemExit("position evidence mismatch")

    if (
        detail["scale"]["scale_x_percent"],
        detail["scale"]["scale_y_percent"],
    ) != (135, 135):
        raise SystemExit("uniform scale evidence mismatch")

    if detail["rotation"]["rotation_tenths"] != 120:
        raise SystemExit("rotation evidence mismatch")
    if detail["opacity"]["opacity_percent"] != 70:
        raise SystemExit("opacity evidence mismatch")

    for item in detail.values():
        if item.get("translated_command") != "SetClipPropertiesCommand":
            raise SystemExit("transform did not use canonical manual command")
        if item.get("candidate_hash_matches_verifier") is not True:
            raise SystemExit("transform candidate hash diverged from verifier proof")

    print(f"W7-006 evidence verification PASS: {len(required)}/{len(required)} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
