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
        "00_w6_003_report.json",
        "01_windows_secure_store.json",
        "02_delete_failure.json",
        "03_safe_diagnostics.log",
    ]
    missing = [name for name in required if not (root / name).is_file()]
    if missing:
        raise SystemExit(f"missing W6-003 evidence: {missing}")

    report = _load(root / "00_w6_003_report.json")
    secure = _load(root / "01_windows_secure_store.json")
    deletion = _load(root / "02_delete_failure.json")

    if report.get("status") != "PASS":
        raise SystemExit("W6-003 report is not PASS")

    for key in (
        "production_windows_secure_store",
        "real_windows_secure_store_smoke",
        "slots_1_and_100_round_trip",
        "reopen_round_trip",
        "delete_secret_and_metadata",
        "failure_after_delete_is_safe",
        "fixed_mask_preserved",
        "raw_secret_absent_from_evidence",
        "secure_store_cleaned_after_smoke",
    ):
        if report.get(key) is not True:
            raise SystemExit(f"W6-003 gate false: {key}")

    for key in (
        "health_failover_started",
        "bulk_txt_started",
        "gemini_network_called",
        "credential_ui_started",
    ):
        if report.get(key) is not False:
            raise SystemExit(f"W6-003 scope violation: {key}")

    if secure.get("backend") != "Windows Credential Manager Generic Credential":
        raise SystemExit("W6-003 did not qualify the Windows Generic Credential backend")
    for key in (
        "slot_1_round_trip",
        "slot_100_round_trip",
        "slot_1_reopen",
        "slot_100_reopen",
        "real_windows_runner",
    ):
        if secure.get(key) is not True:
            raise SystemExit(f"W6-003 secure-store proof failed: {key}")

    for key in (
        "slot_1_secret_deleted",
        "slot_1_metadata_deleted",
        "slot_100_secret_deleted",
        "slot_100_metadata_deleted",
        "load_after_delete_rejected",
        "all_secure_store_targets_cleaned",
    ):
        if deletion.get(key) is not True:
            raise SystemExit(f"W6-003 delete/failure proof failed: {key}")

    diagnostic = (root / "03_safe_diagnostics.log").read_text(encoding="utf-8")
    if "CredentialSecret(" in diagnostic:
        raise SystemExit("safe diagnostics exposed credential wrapper internals")

    for name in required:
        if (root / name).stat().st_size <= 0:
            raise SystemExit(f"empty W6-003 evidence: {name}")

    print(f"PASS W6-003 evidence files: {len(required)}/{len(required)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
