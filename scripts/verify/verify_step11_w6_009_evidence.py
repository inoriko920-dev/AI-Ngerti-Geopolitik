from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    root = args.evidence.resolve()

    pairs = {
        "AI_DIRECTOR": ("UI-020", "AI_DIRECTOR_ACTUAL.png"),
        "AI_READY": ("UI-021", "AI_READY_ACTUAL.png"),
        "AI_PLAN": ("UI-022", "AI_PLAN_ACTUAL.png"),
        "AI_APPLIED": ("UI-023", "AI_APPLIED_ACTUAL.png"),
        "AI_PROVIDER_UNAVAILABLE": ("UI-024", "AI_PROVIDER_UNAVAILABLE_ACTUAL.png"),
        "PROVIDER_API_KEYS": ("UI-033", "PROVIDER_API_KEYS_ACTUAL.png"),
    }
    required = [
        "00_w6_009_ui_report.txt",
        "00_w6_009_security_report.txt",
        "00_FROZEN_REFERENCE_CONTACT_SHEET.png",
        *(actual_name for _reference_id, actual_name in pairs.values()),
        *(
            f"{semantic_name}__{reference_id}_REFERENCE_VS_ACTUAL.png"
            for semantic_name, (reference_id, _actual_name) in pairs.items()
        ),
    ]
    missing = [name for name in required if not (root / name).is_file()]
    if missing:
        raise SystemExit(f"missing W6-009 evidence: {missing}")
    for name in required:
        if (root / name).stat().st_size <= 0:
            raise SystemExit(f"empty W6-009 evidence: {name}")

    ui_report = (root / "00_w6_009_ui_report.txt").read_text(encoding="utf-8")
    security = (root / "00_w6_009_security_report.txt").read_text(encoding="utf-8")
    for token in (
        "status=PASS",
        "ai_director=real_widgets",
        "ai_ready=real_widgets",
        "ai_plan=real_widgets",
        "ai_applied=real_widgets",
        "ai_provider_unavailable=real_widgets",
        "provider_api_keys=real_widgets",
        "reference_mapping=AI_DIRECTOR:UI-020,AI_READY:UI-021,AI_PLAN:UI-022,AI_APPLIED:UI-023,AI_PROVIDER_UNAVAILABLE:UI-024,PROVIDER_API_KEYS:UI-033",
        "historical_w6_reference_numbers_corrected=true",
        "l1_only=true",
        "manual_fallback=true",
    ):
        if token not in ui_report:
            raise SystemExit(f"W6-009 UI report token missing: {token}")
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
