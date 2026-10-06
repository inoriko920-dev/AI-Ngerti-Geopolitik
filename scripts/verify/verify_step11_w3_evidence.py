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
        "00_w3_report.json",
        "01_properties.json",
        "02_undo_persistence.json",
        "03_preview_export.json",
        "preview_baseline.png",
        "preview_properties.png",
        "w3_properties.angproj",
        "w3_properties_export.mp4",
    ]
    missing = [name for name in required if not (root / name).is_file()]
    if missing:
        raise SystemExit(f"missing W3 evidence: {missing}")

    report = json.loads((root / "00_w3_report.json").read_text(encoding="utf-8"))
    undo = json.loads((root / "02_undo_persistence.json").read_text(encoding="utf-8"))
    output = json.loads((root / "03_preview_export.json").read_text(encoding="utf-8"))

    expected_true = [
        "video_properties",
        "crop_composition",
        "audio_properties",
        "color_properties",
        "speed_duration_recompute",
        "undo_redo",
        "save_reopen",
        "preview_changed",
        "export_valid",
        "export_has_audio",
    ]
    if report.get("status") != "PASS":
        raise SystemExit("W3 report is not PASS")
    for key in expected_true:
        if report.get(key) is not True:
            raise SystemExit(f"W3 gate false: {key}")
    if report.get("reverse_supported") is not False:
        raise SystemExit("Reverse must remain explicitly disabled in W3")
    if undo.get("undo_restored") is not True or undo.get("redo_restored") is not True:
        raise SystemExit("cross-property history evidence failed")
    if undo.get("save_reopen_hash_match") is not True:
        raise SystemExit("W3 persistence round-trip failed")
    if output.get("preview_changed") is not True:
        raise SystemExit("preview did not reflect W3 properties")
    if abs(int(output["export_frames"]) - int(output["canonical_timeline_frames"])) > 3:
        raise SystemExit("W3 export duration is outside tolerance")

    for name in ("preview_baseline.png", "preview_properties.png", "w3_properties_export.mp4"):
        if (root / name).stat().st_size <= 0:
            raise SystemExit(f"empty W3 artifact: {name}")

    print(f"PASS W3 evidence files: {len(required)}/{len(required)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
