from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    root = args.evidence.resolve()

    required = (
        "00_w7_010_report.json",
        "01_review_and_apply.json",
        "02_real_media.json",
        "03_persistence_undo_redo.json",
        "preview_baseline.png",
        "preview_ai_applied.png",
        "preview_reopened.png",
        "w7_010_mixed_export.mp4",
        "w7_010_applied.angproj",
    )
    for name in required:
        path = root / name
        if not path.is_file() or path.stat().st_size <= 0:
            raise SystemExit(f"missing W7-010 evidence: {name}")

    report = json.loads((root / "00_w7_010_report.json").read_text(encoding="utf-8"))
    review = json.loads((root / "01_review_and_apply.json").read_text(encoding="utf-8"))
    media = json.loads((root / "02_real_media.json").read_text(encoding="utf-8"))
    persistence = json.loads((root / "03_persistence_undo_redo.json").read_text(encoding="utf-8"))

    if report.get("status") != "PASS":
        raise SystemExit("W7-010 report status is not PASS")
    if report.get("review_diff_count") != 6 or len(review.get("diffs", [])) != 6:
        raise SystemExit("W7-010 review diff count mismatch")
    if report.get("real_pacing_timeline_frames") != 210:
        raise SystemExit("W7-010 timeline result mismatch")
    if abs(int(report.get("real_export_frames", 0)) - 210) > 3:
        raise SystemExit("W7-010 export timing mismatch")

    for key in (
        "mixed_l1_l2_plan",
        "review_diffs_bounded",
        "canonical_unchanged_before_approval",
        "one_revision_apply",
        "applied_revision_recorded",
        "real_preview_changed",
        "real_export_audio",
        "effect_applied",
        "transform_applied",
        "fade_black_applied",
        "save_reopen_hash_exact",
        "save_reopen_render_exact",
        "undo_exact",
        "redo_exact",
        "source_media_unchanged",
    ):
        if report.get(key) is not True:
            raise SystemExit(f"W7-010 closure gate false: {key}")

    if report.get("live_gemini_network_claimed") is not False:
        raise SystemExit("W7-010 made an unsupported live Gemini claim")
    if report.get("later_wave_started") is not False:
        raise SystemExit("W7-010 crossed the later-wave boundary")

    if review.get("batch_id") != "AI-BATCH:REQ-W7-010-REAL":
        raise SystemExit("W7-010 batch id mismatch")
    if not all(
        isinstance(item, str) and "→" in item and len(item) <= 280 for item in review["diffs"]
    ):
        raise SystemExit("W7-010 diff evidence is not bounded before/after text")

    if media.get("baseline_preview_sha256") == media.get("applied_preview_sha256"):
        raise SystemExit("W7-010 applied real preview equals baseline")
    if media.get("applied_preview_sha256") != media.get("reopened_preview_sha256"):
        raise SystemExit("W7-010 reopened preview differs from applied preview")
    if media.get("source_before_sha256") != media.get("source_after_sha256"):
        raise SystemExit("W7-010 source media changed")
    if media.get("export_sha256") != _sha256(root / "w7_010_mixed_export.mp4"):
        raise SystemExit("W7-010 export digest mismatch")

    if persistence.get("saved_semantic_hash") != persistence.get("reopened_semantic_hash"):
        raise SystemExit("W7-010 save/reopen semantic hash mismatch")
    if persistence.get("undo_semantic_hash") != persistence.get("baseline_semantic_hash"):
        raise SystemExit("W7-010 Undo semantic hash mismatch")
    if persistence.get("redo_semantic_hash") != persistence.get("saved_semantic_hash"):
        raise SystemExit("W7-010 Redo semantic hash mismatch")
    if persistence.get("project_file_sha256") != _sha256(root / "w7_010_applied.angproj"):
        raise SystemExit("W7-010 project-file digest mismatch")

    print("W7-010 closure evidence verification PASS: 9/9 files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
