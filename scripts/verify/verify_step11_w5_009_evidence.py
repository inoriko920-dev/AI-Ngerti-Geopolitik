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
        "00_w5_009_report.json",
        "01_subtitle_edit_style.json",
        "02_animation_matrix.json",
        "03_narration_sync.json",
        "04_persistence_output.json",
        "source_original.srt",
        "source_original.edited.srt",
        "narration_440hz.wav",
        "preview_edited_before_cue.png",
        "preview_edited_inside_cue.png",
        "preview_styled.png",
        "preview_narration.wav",
        "preview_fade.png",
        "preview_pop.png",
        "preview_slide_up.png",
        "preview_clean_documentary.png",
        "export_fade.mp4",
        "export_pop.mp4",
        "export_slide_up.mp4",
        "export_clean_documentary.mp4",
        "export_fade_frame.png",
        "export_pop_frame.png",
        "export_slide_up_frame.png",
        "export_clean_documentary_frame.png",
        "w5_009_combined.angproj",
        "preview_reopened.png",
    ]
    missing = [name for name in required if not (root / name).is_file()]
    if missing:
        raise SystemExit(f"missing W5-009 evidence: {missing}")

    report = _load(root / "00_w5_009_report.json")
    subtitle = _load(root / "01_subtitle_edit_style.json")
    animation = _load(root / "02_animation_matrix.json")
    narration = _load(root / "03_narration_sync.json")
    persistence = _load(root / "04_persistence_output.json")

    expected_true = (
        "source_srt_unchanged",
        "edited_text_timing_persisted",
        "subtitle_timing_preview_proven",
        "style_visible",
        "all_enabled_animations_preview_rendered",
        "all_enabled_animations_export_rendered",
        "narration_preview_audible",
        "narration_frame_sync_proven",
        "subtitle_narration_coexist_same_export",
        "output_valid",
        "duration_within_tolerance",
        "save_reopen",
        "narration_source_unchanged",
    )
    if report.get("status") != "PASS":
        raise SystemExit("W5-009 report is not PASS")
    for key in expected_true:
        if report.get(key) is not True:
            raise SystemExit(f"W5-009 gate false: {key}")
    if report.get("microphone_hardware_qualifier") != "PROVISIONAL":
        raise SystemExit("W5-009 must preserve provisional microphone hardware status")
    if report.get("asr_used") is not False:
        raise SystemExit("W5-009 must not use ASR")
    if report.get("speech_alignment_claimed") is not False:
        raise SystemExit("W5-009 must not claim speech alignment")

    if subtitle.get("source_srt_unchanged") is not True:
        raise SystemExit("source SRT changed")
    if subtitle.get("style_preview_changed") is not True:
        raise SystemExit("subtitle style visual proof failed")
    if subtitle.get("before_cue_matches_baseline") is not True:
        raise SystemExit("subtitle appeared before edited IN frame")
    if subtitle.get("inside_cue_differs_from_baseline") is not True:
        raise SystemExit("subtitle is missing inside edited cue")

    if animation.get("presets") != [
        "Fade",
        "Pop",
        "Slide Up",
        "Clean Documentary",
    ]:
        raise SystemExit("qualified animation matrix is incomplete")
    if animation.get("all_previews_changed") is not True:
        raise SystemExit("animation preview matrix failed")
    if animation.get("all_export_frames_changed") is not True:
        raise SystemExit("animation export matrix failed")

    if narration.get("source_unchanged") is not True:
        raise SystemExit("narration source changed")
    if narration.get("offset_proven") is not True:
        raise SystemExit("narration frame offset proof failed")
    if narration.get("audible_over_baseline") is not True:
        raise SystemExit("narration audible-over-baseline proof failed")

    if persistence.get("save_reopen_hash_match") is not True:
        raise SystemExit("combined save/reopen proof failed")
    if persistence.get("subtitle_and_narration_present") is not True:
        raise SystemExit("combined project lost subtitle or narration")
    if persistence.get("duration_within_tolerance") is not True:
        raise SystemExit("combined export duration is outside tolerance")
    if persistence.get("has_audio") is not True:
        raise SystemExit("combined export lost audio")

    for name in required:
        if (root / name).stat().st_size <= 0:
            raise SystemExit(f"empty W5-009 evidence: {name}")

    print(f"PASS W5-009 evidence files: {len(required)}/{len(required)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
