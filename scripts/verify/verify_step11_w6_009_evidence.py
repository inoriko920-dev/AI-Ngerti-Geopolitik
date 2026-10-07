from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    root = args.evidence.resolve()

    ids = ("010", "011", "012", "013", "014", "023")
    actual = {
        "010": "UI-010_ACTUAL_AI_DIRECTOR.png",
        "011": "UI-011_ACTUAL_AI_READY.png",
        "012": "UI-012_ACTUAL_AI_PLAN.png",
        "013": "UI-013_ACTUAL_AI_APPLIED.png",
        "014": "UI-014_ACTUAL_PROVIDER_UNAVAILABLE.png",
        "023": "UI-023_ACTUAL_PROVIDER_KEYS.png",
    }
    required = [
        "00_w6_009_ui_report.txt",
        "00_w6_009_security_report.txt",
        "00_FROZEN_REFERENCE_CONTACT_SHEET.png",
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
    for token in (
        "status=PASS",
        "ui_010=ai_director_real_widgets",
        "ui_011=ready_chat_real_widgets",
        "ui_012=plan_approval_real_widgets",
        "ui_013=applied_success_real_widgets",
        "ui_014=provider_unavailable_manual_fallback",
        "ui_023=provider_api_key_manager_real_widgets",
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
