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
        "00_w6_010_report.json",
        "01_render_proof.json",
        "02_live_qualification.json",
        "preview_baseline.png",
        "preview_ai_applied.png",
    ]
    missing = [name for name in required if not (root / name).is_file()]
    if missing:
        raise SystemExit(f"missing W6-010 evidence: {missing}")
    for name in required:
        if (root / name).stat().st_size <= 0:
            raise SystemExit(f"empty W6-010 evidence: {name}")

    report = json.loads((root / "00_w6_010_report.json").read_text(encoding="utf-8"))
    render = json.loads((root / "01_render_proof.json").read_text(encoding="utf-8"))
    live = json.loads((root / "02_live_qualification.json").read_text(encoding="utf-8"))

    expected_true = (
        "render_effect_visible",
        "one_revision_apply",
        "undo_exact",
        "redo_exact",
    )
    if report.get("status") != "PASS":
        raise SystemExit("W6-010 deterministic closure is not PASS")
    for key in expected_true:
        if report.get(key) is not True:
            raise SystemExit(f"W6-010 deterministic gate false: {key}")
    if report.get("selected_effect") != "Rise":
        raise SystemExit("W6-010 deterministic effect is not Rise")
    if report.get("selected_intensity_percent") != 120:
        raise SystemExit("W6-010 deterministic intensity is not 120")
    if render.get("different") is not True:
        raise SystemExit("W6-010 render proof did not change")
    if render.get("baseline_sha256") == render.get("ai_applied_sha256"):
        raise SystemExit("W6-010 render hashes are identical")

    live_status = live.get("status")
    if live_status == "PASS":
        for key in (
            "credential_available",
            "request_attempted",
            "official_adapter_used",
            "windows_secure_store_used",
            "canonical_apply",
            "one_revision_apply",
            "undo_exact",
            "redo_exact",
        ):
            if live.get(key) is not True:
                raise SystemExit(f"W6-010 live gate false: {key}")
        if live.get("raw_credential_in_evidence") is not False:
            raise SystemExit("W6-010 live evidence reports a credential leak")
        print("PASS W6-010 closure: FULL_LIVE_GEMINI")
        return 0

    if live_status == "PROVISIONAL_NO_CREDENTIAL":
        if live.get("credential_available") is not False:
            raise SystemExit("provisional live report has inconsistent credential state")
        if live.get("request_attempted") is not False:
            raise SystemExit("provisional live report must not fake a request")
        if live.get("raw_credential_in_evidence") is not False:
            raise SystemExit("provisional live report reports a credential leak")
        print("PASS W6-010 closure: PASS_WITH_PROVISIONAL_LIVE_GEMINI")
        return 0

    raise SystemExit(f"W6-010 live qualification failed: {live_status}")


if __name__ == "__main__":
    raise SystemExit(main())
