from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--evidence",
        type=Path,
        required=True,
    )
    args = parser.parse_args()
    root = args.evidence.resolve()

    required = [
        "00_w4_report.json",
        "01_creative_state.json",
        "02_undo_persistence.json",
        "03_preview_export.json",
        "preview_baseline.png",
        "preview_creative.png",
        "w4_creative.angproj",
        "w4_creative_export.mp4",
    ]
    missing = [
        name
        for name in required
        if not (root / name).is_file()
    ]
    if missing:
        raise SystemExit(
            f"missing W4 evidence: {missing}"
        )

    report = json.loads(
        (root / "00_w4_report.json").read_text(
            encoding="utf-8"
        )
    )
    creative = json.loads(
        (root / "01_creative_state.json").read_text(
            encoding="utf-8"
        )
    )
    undo = json.loads(
        (root / "02_undo_persistence.json").read_text(
            encoding="utf-8"
        )
    )
    output = json.loads(
        (root / "03_preview_export.json").read_text(
            encoding="utf-8"
        )
    )

    expected_true = [
        "title_overlay",
        "transition_fade_black",
        "render_backed_effects",
        "unsupported_legacy_hidden",
        "undo_redo",
        "save_reopen",
        "preview_changed",
        "export_valid",
        "export_has_audio",
    ]
    if report.get("status") != "PASS":
        raise SystemExit("W4 report is not PASS")
    for key in expected_true:
        if report.get(key) is not True:
            raise SystemExit(
                f"W4 gate false: {key}"
            )
    if report.get("crossfade_claimed") is not False:
        raise SystemExit(
            "W4 must not claim unsupported crossfade"
        )
    if (
        creative["transition"]["preset"]
        != "fade_black"
    ):
        raise SystemExit(
            "W4 transition evidence is not fade_black"
        )
    if len(
        creative["unsupported_legacy_effects"]
    ) != 12:
        raise SystemExit(
            "W4 unsupported legacy effect map is incomplete"
        )
    if (
        undo.get("undo_restored") is not True
        or undo.get("redo_restored") is not True
    ):
        raise SystemExit(
            "W4 history evidence failed"
        )
    if undo.get("save_reopen_hash_match") is not True:
        raise SystemExit(
            "W4 persistence round-trip failed"
        )
    if output.get("preview_changed") is not True:
        raise SystemExit(
            "preview did not reflect W4 creative state"
        )
    if abs(
        int(output["export_frames"])
        - int(output["canonical_timeline_frames"])
    ) > 3:
        raise SystemExit(
            "W4 export duration is outside tolerance"
        )

    for name in (
        "preview_baseline.png",
        "preview_creative.png",
        "w4_creative_export.mp4",
    ):
        if (root / name).stat().st_size <= 0:
            raise SystemExit(
                f"empty W4 artifact: {name}"
            )

    print(
        f"PASS W4 evidence files: "
        f"{len(required)}/{len(required)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
