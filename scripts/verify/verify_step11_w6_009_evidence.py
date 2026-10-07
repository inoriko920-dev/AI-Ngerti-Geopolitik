from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    root = args.evidence.resolve()

    ids = ("010", "021", "022", "023", "024", "033")
    actual = {
        "010": "UI-010_ACTUAL_EDITOR_AI_ENTRY.png",
        "021": "UI-021_ACTUAL_AI_READY.png",
        "022": "UI-022_ACTUAL_AI_PLAN.png",
        "023": "UI-023_ACTUAL_AI_APPLIED.png",
        "024": "UI-024_ACTUAL_PROVIDER_UNAVAILABLE.png",
        "033": "UI-033_ACTUAL_PROVIDER_KEYS.png",
    }
    required = [
        "00_w6_009_ui_report.txt",
        "00_w6_009_security_report.txt",
        "00_w6_009_reference_mapping_report.txt",
        "00_FROZEN_REFERENCE_CONTACT_SHEET.png",
        "W6-AI-DIRECTOR_ACTUAL.png",
        *actual.values(),
        *(f"UI-{ui_id}_REFERENCE_VS_ACTUAL.png" for ui_id in ids),
    ]
    missing = [name for name in required if not (root / name).is_file()]
    if missing:
        raise SystemExit(f"missing W6-009 evidence: {missing}")
    for name in required:
        if (root / name).stat().st_size <= 0:
            raise SystemExit(f"empty W6-009 evidence: {name}")

    ui_report = (root / "00_w6_009_ui_report.txt").read_text(encoding="utf-8")
    security = (root / "00_w6_009_security_report.txt").read_text(encoding="utf-8")
    mapping = (root / "00_w6_009_reference_mapping_report.txt").read_text(
        encoding="utf-8"
    )
    for token in (
        "status=PASS",
        "ui_010=baseline_editor_ai_entry",
        "ui_021=ready_chat_real_widgets",
        "ui_022=plan_approval_real_widgets",
        "ui_023=applied_success_real_widgets",
        "ui_024=provider_unavailable_manual_fallback",
        "ui_033=provider_api_key_manager_real_widgets",
        "ai_director=real_widgets_actual_only_no_dedicated_frozen_raster",
        "l1_only=true",
        "manual_fallback=true",
    ):
        if token not in ui_report:
            raise SystemExit(f"W6-009 UI report token missing: {token}")
    for token in (
        "status=PASS",
        "authority=actual_frozen_raster_visual",
        "planning_id_title_conflict=true",
        "gap_ux_001_applied=true",
        "ui_021=ai_ready_chat",
        "ui_022=ai_plan_approval",
        "ui_023=ai_applied_success",
        "ui_024=provider_unavailable",
        "ui_033=provider_api_key_manager",
        "ai_director_dedicated_frozen_raster=none_found",
        "raw_frozen_png_modified=0",
    ):
        if token not in mapping:
            raise SystemExit(f"W6-009 mapping report token missing: {token}")
    for token in (
        "status=PASS",
        "saved_credentials_display=masked_only",
        "raw_saved_credentials_in_ui=0",
        "unsupported_l1_effects_selectable=0",
        "screenshot_as_runtime=0",
        "live_gemini_used=0",
        "quota_circumvention_claim=0",
    ):
        if token not in security:
            raise SystemExit(f"W6-009 security report token missing: {token}")

    print(f"PASS W6-009 evidence files: {len(required)}/{len(required)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
