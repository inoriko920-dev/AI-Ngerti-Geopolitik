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
        "00_w5_010_report.json",
        "01_history.json",
        "02_failure_paths.json",
        "03_backward_compat.json",
        "04_source_safety.json",
        "valid_source.srt",
        "malformed.srt",
        "valid_narration.wav",
        "corrupt_narration.wav",
    ]
    missing = [name for name in required if not (root / name).is_file()]
    if missing:
        raise SystemExit(f"missing W5-010 evidence: {missing}")

    report = _load(root / "00_w5_010_report.json")
    history = _load(root / "01_history.json")
    failures = _load(root / "02_failure_paths.json")
    compat = _load(root / "03_backward_compat.json")
    safety = _load(root / "04_source_safety.json")

    if report.get("status") != "PASS_WITH_PROVISIONAL_MIC_HARDWARE":
        raise SystemExit("W5-010 must preserve the provisional microphone qualifier")

    expected_true = (
        "subtitle_narration_undo_redo",
        "pre_w5_w4_safe_defaults",
        "malformed_srt_rejected_without_mutation",
        "dirty_working_copy_guard",
        "missing_narration_rejected_without_mutation",
        "corrupt_narration_rejected_without_mutation",
        "missing_bound_narration_no_fake_preview",
        "failed_recording_preserves_existing_narration",
        "source_srt_unchanged",
        "narration_source_unchanged",
    )
    for key in expected_true:
        if report.get(key) is not True:
            raise SystemExit(f"W5-010 gate false: {key}")

    if report.get("microphone_hardware_qualifier") != "PROVISIONAL":
        raise SystemExit("microphone hardware qualifier changed unexpectedly")
    if report.get("fake_hardware_claimed") is not False:
        raise SystemExit("W5-010 may not fake hardware qualification")
    if report.get("asr_used") is not False:
        raise SystemExit("W5-010 may not use ASR")
    if report.get("speech_alignment_claimed") is not False:
        raise SystemExit("W5-010 may not claim speech alignment")

    if history.get("undo_redo_restored") is not True:
        raise SystemExit("W5 history closure failed")
    if failures.get("state_unchanged_after_failures") is not True:
        raise SystemExit("failure path mutated canonical project state")
    if failures.get("fake_preview_created") is not False:
        raise SystemExit("failure path created fake narration preview")
    if compat.get("subtitle_default_none") is not True:
        raise SystemExit("pre-W5 subtitle default is unsafe")
    if compat.get("narration_default_none") is not True:
        raise SystemExit("pre-W5 narration default is unsafe")
    if safety.get("source_srt_unchanged") is not True:
        raise SystemExit("source SRT changed during closure")
    if safety.get("narration_source_unchanged") is not True:
        raise SystemExit("narration source changed during closure")
    if safety.get("existing_narration_preserved_after_recording_failure") is not True:
        raise SystemExit("failed recording clobbered existing narration")

    for name in required:
        if (root / name).stat().st_size <= 0:
            raise SystemExit(f"empty W5-010 evidence: {name}")

    print(f"PASS W5-010 evidence files: {len(required)}/{len(required)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
