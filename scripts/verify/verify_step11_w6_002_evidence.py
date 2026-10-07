from __future__ import annotations

import argparse
import json
from pathlib import Path


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    root = args.evidence.resolve()

    required = [
        "00_w6_002_report.json",
        "01_slots.json",
        "02_no_secret_persistence.json",
        "03_safe_diagnostics.log",
        "w6_002_project.angproj",
    ]
    missing = [name for name in required if not (root / name).is_file()]
    if missing:
        raise SystemExit(f"missing W6-002 evidence: {missing}")

    report = _load(root / "00_w6_002_report.json")
    slots = _load(root / "01_slots.json")
    safety = _load(root / "02_no_secret_persistence.json")

    if report.get("status") != "PASS":
        raise SystemExit("W6-002 report is not PASS")

    expected_true = (
        "slots_1_and_100_supported",
        "slots_0_and_101_rejected",
        "add_update_delete",
        "enable_disable_metadata_only",
        "fixed_mask_only",
        "in_memory_reopen",
        "secret_and_metadata_delete_consistent",
        "raw_secret_absent_from_project_persistence_diagnostics",
        "label_secret_rejected",
        "project_state_unchanged_by_credentials",
    )
    for key in expected_true:
        if report.get(key) is not True:
            raise SystemExit(f"W6-002 gate false: {key}")

    for key in (
        "production_secure_store_started",
        "gemini_network_called",
        "health_failover_started",
        "credential_ui_started",
    ):
        if report.get(key) is not False:
            raise SystemExit(f"W6-002 scope violation: {key}")

    if slots.get("slot_100_disabled") is not True:
        raise SystemExit("slot 100 disable metadata proof failed")
    if slots.get("label_secret_rejected") is not True:
        raise SystemExit("secret-in-label rejection proof failed")
    if slots.get("delete_secret_removed") is not True:
        raise SystemExit("secret delete proof failed")
    if slots.get("delete_metadata_removed") is not True:
        raise SystemExit("metadata delete proof failed")

    for key, value in safety.items():
        if value is not True:
            raise SystemExit(f"W6-002 secret-safety gate false: {key}")

    diagnostic = (root / "03_safe_diagnostics.log").read_text(encoding="utf-8")
    if "**masked**" in diagnostic:
        raise SystemExit("legacy object mask appeared instead of fixed slot mask")
    if "CredentialSecret(" in diagnostic:
        raise SystemExit("safe diagnostics exposed secret wrapper internals")

    for name in required:
        if (root / name).stat().st_size <= 0:
            raise SystemExit(f"empty W6-002 evidence: {name}")

    print(f"PASS W6-002 evidence files: {len(required)}/{len(required)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
