from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    root = args.evidence.resolve()

    previews = [
        "preview_style_baseline.png",
        "preview_font_family.png",
        "preview_font_size.png",
        "preview_fill_color.png",
        "preview_outline.png",
        "preview_shadow.png",
        "preview_background.png",
        "preview_alignment.png",
        "preview_margin_v.png",
        "preview_style_final.png",
    ]
    required = [
        "00_w5_004_report.json",
        "01_style_state.json",
        "02_style_preview_matrix.json",
        "03_history_persistence.json",
        "04_export.json",
        "style_source.srt",
        "w5_004_style.angproj",
        "w5_004_style_export.mp4",
        *previews,
    ]
    missing = [name for name in required if not (root / name).is_file()]
    if missing:
        raise SystemExit(f"missing W5-004 evidence: {missing}")

    report = json.loads((root / "00_w5_004_report.json").read_text(encoding="utf-8"))
    matrix = json.loads((root / "02_style_preview_matrix.json").read_text(encoding="utf-8"))
    history = json.loads((root / "03_history_persistence.json").read_text(encoding="utf-8"))
    export = json.loads((root / "04_export.json").read_text(encoding="utf-8"))

    expected_true = [
        "font_family",
        "font_size",
        "fill_color",
        "outline",
        "shadow",
        "background_box_opacity",
        "alignment",
        "safe_vertical_margin",
        "undo_redo",
        "save_reopen",
        "preview_matrix_changed",
        "export_valid",
        "export_has_audio",
        "source_srt_unchanged",
    ]
    if report.get("status") != "PASS":
        raise SystemExit("W5-004 report is not PASS")
    for key in expected_true:
        if report.get(key) is not True:
            raise SystemExit(f"W5-004 gate false: {key}")
    if report.get("subtitle_animation_enabled") is not False:
        raise SystemExit("W5-004 must not enable subtitle animation")
    if matrix.get("all_variants_changed") is not True:
        raise SystemExit("not every W5-004 style property changed real preview")
    if history.get("undo_restored") is not True:
        raise SystemExit("W5-004 Undo evidence failed")
    if history.get("redo_restored") is not True:
        raise SystemExit("W5-004 Redo evidence failed")
    if history.get("save_reopen_hash_match") is not True:
        raise SystemExit("W5-004 persistence evidence failed")
    if export.get("source_srt_unchanged") is not True:
        raise SystemExit("W5-004 changed source SRT")
    if abs(int(export["export_frames"]) - int(export["canonical_timeline_frames"])) > 3:
        raise SystemExit("W5-004 export duration outside tolerance")

    for name in required:
        if (root / name).stat().st_size <= 0:
            raise SystemExit(f"empty W5-004 artifact: {name}")

    print(f"PASS W5-004 evidence files: {len(required)}/{len(required)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
