from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    root = args.evidence.resolve()

    presets = ("fade", "pop", "slide_up", "clean_documentary")
    required = [
        "00_w5_005_report.json",
        "01_animation_matrix.json",
        "02_word_timing_boundary.json",
        "03_history_persistence.json",
        "animation_source.srt",
        "w5_005_animation.angproj",
        "preview_none.png",
        "export_none.mp4",
        "export_none_frame.png",
    ]
    for preset in presets:
        required.extend(
            [
                f"preview_{preset}.png",
                f"export_{preset}.mp4",
                f"export_{preset}_frame.png",
            ]
        )

    missing = [name for name in required if not (root / name).is_file()]
    if missing:
        raise SystemExit(f"missing W5-005 evidence: {missing}")

    report = json.loads((root / "00_w5_005_report.json").read_text(encoding="utf-8"))
    matrix = json.loads((root / "01_animation_matrix.json").read_text(encoding="utf-8"))
    words = json.loads((root / "02_word_timing_boundary.json").read_text(encoding="utf-8"))
    history = json.loads((root / "03_history_persistence.json").read_text(encoding="utf-8"))

    expected_true = [
        "fade_render_backed",
        "pop_render_backed",
        "slide_up_render_backed",
        "clean_documentary_render_backed",
        "all_previews_changed",
        "all_export_frames_changed",
        "unsupported_presets_hidden",
        "word_timing_persisted",
        "undo_redo",
        "save_reopen",
        "source_srt_unchanged",
    ]
    if report.get("status") != "PASS":
        raise SystemExit("W5-005 report is not PASS")
    for key in expected_true:
        if report.get(key) is not True:
            raise SystemExit(f"W5-005 gate false: {key}")
    if report.get("speech_alignment_claimed") is not False:
        raise SystemExit("W5-005 must not claim speech alignment")
    if report.get("asr_used") is not False:
        raise SystemExit("W5-005 must not use ASR")
    if matrix.get("all_previews_changed") is not True:
        raise SystemExit("not every qualified animation changed real preview")
    if matrix.get("all_export_frames_changed") is not True:
        raise SystemExit("not every qualified animation changed exported video")
    if words.get("label") != "NOT speech alignment":
        raise SystemExit("word-timing fallback boundary label missing")
    if words.get("asr_used") is not False or words.get("transcription_used") is not False:
        raise SystemExit("word timing evidence used prohibited ASR/transcription")
    if words.get("speech_alignment_claimed") is not False:
        raise SystemExit("word timing evidence falsely claims speech alignment")
    if history.get("redo_restored") is not True:
        raise SystemExit("W5-005 history evidence failed")
    if history.get("save_reopen_hash_match") is not True:
        raise SystemExit("W5-005 persistence evidence failed")
    if history.get("source_srt_unchanged") is not True:
        raise SystemExit("W5-005 changed source SRT")

    for name in required:
        if (root / name).stat().st_size <= 0:
            raise SystemExit(f"empty W5-005 artifact: {name}")

    print(f"PASS W5-005 evidence files: {len(required)}/{len(required)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
