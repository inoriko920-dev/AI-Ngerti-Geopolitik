from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED = (
    "00_w2_report.json",
    "01_timeline.json",
    "02_interaction.json",
    "03_preview_export.json",
    "04_semantics.json",
    "05_stress.json",
    "w2_multitrack_semantics.angproj",
    "w2_timeline.angproj",
    "w2_edited_timeline.mp4",
)


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    root = args.evidence.resolve()
    errors: list[str] = []

    for relative in REQUIRED:
        path = root / relative
        if not path.is_file() or path.stat().st_size == 0:
            errors.append(f"missing/empty W2 evidence: {relative}")

    preview_files = sorted((root / "preview").glob("*.png"))
    if len(preview_files) < 2:
        errors.append("W2 must contain at least two real preview frame captures")

    if errors:
        for error in errors:
            print(f"FAIL {error}")
        return 1

    report = load_json(root / "00_w2_report.json")
    timeline = load_json(root / "01_timeline.json")
    interaction = load_json(root / "02_interaction.json")

    if not isinstance(report, dict) or report.get("status") != "PASS":
        errors.append("W2 report status is not PASS")
    elif not all(
        report.get(key) is True
        for key in (
            "selection_valid",
            "snap_pass",
            "edit_auto_paused",
            "save_reopen_hash_match",
            "preview_files_valid",
            "export_valid",
        )
    ):
        errors.append("one or more W2 report acceptance markers are false")

    if not isinstance(timeline, dict):
        errors.append("W2 timeline evidence missing")
    else:
        clip_ids = timeline.get("clip_ids")
        if clip_ids != ["C003", "C004", "C001", "C002"]:
            errors.append(f"W2 canonical clip order mismatch: {clip_ids!r}")
        starts = timeline.get("starts")
        if not isinstance(starts, list) or not starts or starts[0] != 0:
            errors.append("W2 timeline does not start at frame zero")
        if isinstance(starts, list) and starts != sorted(starts):
            errors.append("W2 timeline starts are not monotonic")
        marker = timeline.get("marker")
        if not isinstance(marker, dict) or marker.get("id") != "M001":
            errors.append("W2 persisted marker evidence missing")


    semantics = load_json(root / "04_semantics.json")
    if not isinstance(semantics, dict) or semantics.get("status") != "PASS":
        errors.append("W2 complete semantics report is not PASS")
    else:
        if semantics.get("track_ids") != ["V2", "V1"]:
            errors.append(f"W2 track ordering evidence mismatch: {semantics.get('track_ids')!r}")
        if semantics.get("v2_name") != "B-roll":
            errors.append("W2 track rename evidence missing")
        if semantics.get("v2_muted") is not True or semantics.get("v2_visible") is not False:
            errors.append("W2 track mute/visibility evidence missing")
        if semantics.get("c003_track") != "V2":
            errors.append("W2 stable cross-track clip identity evidence missing")
        if semantics.get("all_mutations_undo_redo_checked") is not True:
            errors.append("W2 undo/redo coverage marker missing")
        if semantics.get("save_reopen_hash_match") is not True:
            errors.append("W2 multitrack save/reopen mismatch")

    stress = load_json(root / "05_stress.json")
    if not isinstance(stress, dict) or stress.get("status") != "PASS":
        errors.append("W2 stress budget did not pass")
    else:
        if int(stress.get("total_clips", 0)) < 1000:
            errors.append("W2 stress fixture must cover at least 1000 clips")
        if float(stress.get("elapsed_ms", 1e12)) > float(stress.get("budget_ms", 0)):
            errors.append("W2 stress elapsed time exceeds budget")

    if not isinstance(interaction, dict):
        errors.append("W2 interaction evidence missing")
    else:
        if interaction.get("snap_pass") is not True:
            errors.append("W2 snap evidence is not PASS")
        if interaction.get("edit_auto_paused") is not True:
            errors.append("W2 edit-during-playback policy not proven")
        if interaction.get("follow_suspended_after_manual_scroll") is not True:
            errors.append("W2 follow suspension behavior not proven")
        in_frame = interaction.get("selection_in")
        out_frame = interaction.get("selection_out")
        if not isinstance(in_frame, int) or not isinstance(out_frame, int) or in_frame >= out_frame:
            errors.append("W2 IN/OUT evidence invalid")

    if errors:
        for error in errors:
            print(f"FAIL {error}")
        return 1
    print(f"PASS STEP 11 W2 evidence: {len(REQUIRED)} required files + previews")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
