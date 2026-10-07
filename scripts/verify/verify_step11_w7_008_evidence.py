from __future__ import annotations

import json
from pathlib import Path


def main() -> int:
    root = Path("artifacts/step11/w7-008/evidence")
    report_path = root / "00_w7_008_report.json"
    if not report_path.is_file() or report_path.stat().st_size <= 0:
        raise SystemExit("missing W7-008 evidence report")

    report = json.loads(report_path.read_text(encoding="utf-8"))
    if report.get("status") != "PASS":
        raise SystemExit("W7-008 evidence status is not PASS")
    if report.get("request_profile") != "L2_AUTO_EDIT":
        raise SystemExit("W7-008 request profile mismatch")
    if report.get("provider_profiles") != ["L2_AUTO_EDIT"]:
        raise SystemExit("W7-008 profile dispatch evidence mismatch")
    if report.get("job_state") != "SUCCESS":
        raise SystemExit("W7-008 shared lifecycle did not succeed")
    if report.get("shared_provider_calls") != 1:
        raise SystemExit("W7-008 provider call count mismatch")
    if report.get("verified_command_count") != 6:
        raise SystemExit("W7-008 command count mismatch")
    if report.get("verified_target_count") != 2:
        raise SystemExit("W7-008 target count mismatch")
    if report.get("verified_scope_count") != 2:
        raise SystemExit("W7-008 scope count mismatch")
    if report.get("candidate_revision") != 28:
        raise SystemExit("W7-008 candidate revision mismatch")

    for key in (
        "provider_off_caller_thread",
        "candidate_hash_present",
        "canonical_state_unchanged",
        "credential_not_in_snapshot",
    ):
        if report.get(key) is not True:
            raise SystemExit(f"W7-008 evidence gate false: {key}")

    for key in (
        "gemini_network_used_in_deterministic_evidence",
        "second_provider_service_created",
        "credential_pool_replaced",
        "runtime_ui_changed",
        "canonical_ai_apply_started",
        "w7_009_started",
    ):
        if report.get(key) is not False:
            raise SystemExit(f"W7-008 crossed later-task boundary: {key}")

    print("W7-008 evidence verification PASS: 1/1 file")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
