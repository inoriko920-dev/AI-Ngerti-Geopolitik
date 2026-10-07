from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED_TRUE = (
    "revision_preserved",
    "stable_target_id_present",
    "lock_state_present",
    "media_aspect_present",
    "neighbor_summary_bounded",
    "allowlist_exact",
    "unsupported_effects_absent",
    "fixed_command_allowlist",
    "untrusted_text_policy",
    "filesystem_path_absent",
    "source_name_absent",
    "credential_absent",
    "private_content_absent",
    "project_not_mutated",
)

REQUIRED_FALSE = (
    "gemini_network_called",
    "plan_verifier_started",
    "credential_ui_started",
    "ai_plan_apply_started",
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    evidence = args.evidence.resolve()

    report_path = evidence / "00_w6_005_report.json"
    shape_path = evidence / "01_context_shape.json"
    if not report_path.is_file() or not shape_path.is_file():
        raise SystemExit("W6-005 evidence files are incomplete")

    report = json.loads(report_path.read_text(encoding="utf-8"))
    shape = json.loads(shape_path.read_text(encoding="utf-8"))

    checks: list[tuple[str, bool]] = [
        ("status", report.get("status") == "PASS"),
        ("schema", report.get("schema_version") == 1),
        ("shape-target-count", shape.get("target_count") == 1),
        ("shape-target-id", shape.get("target_clip_id") == "evidence-clip-2"),
        ("shape-effective-lock", shape.get("effective_locked") is True),
    ]
    checks.extend((key, report.get(key) is True) for key in REQUIRED_TRUE)
    checks.extend((key, report.get(key) is False) for key in REQUIRED_FALSE)

    failed = [name for name, passed in checks if not passed]
    if failed:
        raise SystemExit("W6-005 evidence verification failed: " + ", ".join(failed))

    print(f"W6-005 evidence verification PASS: {len(checks)}/{len(checks)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
