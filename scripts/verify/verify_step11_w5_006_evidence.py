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
        "00_w5_006_report.json",
        "01_binding.json",
        "02_audio_measurements.json",
        "03_history_persistence.json",
        "narration_440hz.wav",
        "narration_preview.wav",
        "export_baseline.mp4",
        "export_narrated.mp4",
        "export_muted.mp4",
        "export_boosted.mp4",
        "w5_006_narration.angproj",
    ]
    missing = [name for name in required if not (root / name).is_file()]
    if missing:
        raise SystemExit(f"missing W5-006 evidence: {missing}")

    report = json.loads((root / "00_w5_006_report.json").read_text(encoding="utf-8"))
    binding = json.loads((root / "01_binding.json").read_text(encoding="utf-8"))
    audio = json.loads((root / "02_audio_measurements.json").read_text(encoding="utf-8"))
    history = json.loads((root / "03_history_persistence.json").read_text(encoding="utf-8"))

    expected_true = [
        "audio_import_bound",
        "frame_offset_proven",
        "gain_proven",
        "mute_proven",
        "fade_in_proven",
        "preview_audible",
        "export_audible",
        "export_has_audio",
        "undo_redo",
        "save_reopen",
        "source_unchanged",
    ]
    if report.get("status") != "PASS":
        raise SystemExit("W5-006 report is not PASS")
    for key in expected_true:
        if report.get(key) is not True:
            raise SystemExit(f"W5-006 gate false: {key}")
    if report.get("microphone_started") is not False:
        raise SystemExit("W5-006 must not start microphone implementation")
    if binding.get("source_unchanged") is not True:
        raise SystemExit("W5-006 narration source changed")
    if history.get("undo_restored_bound") is not True:
        raise SystemExit("W5-006 Undo evidence failed")
    if history.get("save_reopen_hash_match") is not True:
        raise SystemExit("W5-006 persistence evidence failed")
    if audio["narrated_mid_440_mean_db"] < audio["baseline_mid_440_mean_db"] + 8.0:
        raise SystemExit("W5-006 export narration spectral proof failed")
    if audio["narrated_mid_440_mean_db"] < audio["muted_mid_440_mean_db"] + 8.0:
        raise SystemExit("W5-006 mute spectral proof failed")

    for name in required:
        if (root / name).stat().st_size <= 0:
            raise SystemExit(f"empty W5-006 artifact: {name}")

    print(f"PASS W5-006 evidence files: {len(required)}/{len(required)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
