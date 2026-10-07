from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    evidence = args.evidence.resolve()

    report_path = evidence / "00_w6_006_report.json"
    shape_path = evidence / "01_verified_plan_shape.json"
    if not report_path.is_file() or not shape_path.is_file():
        raise SystemExit("W6-006 evidence files are incomplete")

    report = json.loads(report_path.read_text(encoding="utf-8"))
    shape = json.loads(shape_path.read_text(encoding="utf-8"))

    checks = [
        ("status", report.get("status") == "PASS"),
        ("strict-valid-plan", report.get("strict_valid_plan") is True),
        ("candidate-changed", report.get("candidate_changed") is True),
        (
            "candidate-revision-preserved",
            report.get("candidate_revision_preserved") is True,
        ),
        ("canonical-state-unchanged", report.get("canonical_state_unchanged") is True),
        (
            "unknown-root-schema",
            report.get("unknown_root_code") == report.get("expected_schema_code"),
        ),
        (
            "unknown-command-schema",
            report.get("unknown_command_code") == report.get("expected_schema_code"),
        ),
        (
            "unknown-target-semantic",
            report.get("unknown_target_code") == report.get("expected_semantic_code"),
        ),
        (
            "unsupported-effect-semantic",
            report.get("unsupported_effect_code") == report.get("expected_semantic_code"),
        ),
        (
            "range-semantic",
            report.get("range_code") == report.get("expected_semantic_code"),
        ),
        ("lock-conflict", report.get("lock_code") == report.get("expected_lock_code")),
        ("stale-plan", report.get("stale_code") == report.get("expected_stale_code")),
        (
            "request-mismatch-semantic",
            report.get("request_mismatch_code") == report.get("expected_semantic_code"),
        ),
        ("no-gemini", report.get("gemini_network_called") is False),
        ("no-command-bus-apply", report.get("command_bus_apply_started") is False),
        ("no-approval-ui", report.get("approval_ui_started") is False),
        ("no-w6-ui", report.get("w6_ui_started") is False),
        ("shape-request", shape.get("request_id") == "REQ-EVIDENCE-006"),
        ("shape-revision", shape.get("base_project_revision") == 31),
        ("shape-command-count", shape.get("command_count") == 1),
        ("shape-candidate-revision", shape.get("candidate_revision") == 31),
        ("shape-command-type", shape.get("command_type") == "set_clip_effects"),
        ("shape-target", shape.get("target_clip_id") == "clip-open"),
        (
            "shape-hash",
            isinstance(shape.get("candidate_semantic_hash"), str)
            and len(shape["candidate_semantic_hash"]) == 64,
        ),
    ]

    failed = [name for name, passed in checks if not passed]
    if failed:
        raise SystemExit("W6-006 evidence verification failed: " + ", ".join(failed))

    print(f"W6-006 evidence verification PASS: {len(checks)}/{len(checks)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
