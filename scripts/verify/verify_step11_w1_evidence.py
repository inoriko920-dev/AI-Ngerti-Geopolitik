from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED = (
    "00_w1_report.json",
    "01_canonical.angproj",
    "02_save_as.angproj",
    "02_save_as.angproj.bak",
    "03_media_inventory.json",
    "04_media_bin_query.json",
    "05_project_settings.json",
    "06_missing_media_snapshot.json",
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
            errors.append(f"missing/empty W1 evidence: {relative}")

    autosaves = sorted((root / ".ang-autosave").glob("*.angproj"))
    if len(autosaves) != 1:
        errors.append(f"expected exactly one autosave snapshot, got {len(autosaves)}")

    if errors:
        for error in errors:
            print(f"FAIL {error}")
        return 1

    report = load_json(root / "00_w1_report.json")
    inventory = load_json(root / "03_media_inventory.json")
    media_bin = load_json(root / "04_media_bin_query.json")
    settings = load_json(root / "05_project_settings.json")
    missing = load_json(root / "06_missing_media_snapshot.json")

    if not isinstance(report, dict) or report.get("status") != "PASS":
        errors.append("W1 report status is not PASS")
    if isinstance(report, dict):
        if report.get("asset_ids") != ["A001", "A002", "A003"]:
            errors.append("stable W1 asset IDs are not A001/A002/A003")
        if report.get("media_types") != ["video", "audio", "image"]:
            errors.append("video/audio/image import evidence is incomplete")
        for marker in (
            "backup_previous_state",
            "autosave_did_not_overwrite_canonical",
            "missing_media_preserved_clip",
        ):
            if report.get(marker) is not True:
                errors.append(f"W1 report marker false: {marker}")
        if report.get("dirty_close_guard") != "PASS":
            errors.append("dirty close guard did not PASS")

    if not isinstance(inventory, list) or len(inventory) != 3:
        errors.append("media inventory must contain exactly three assets")
    if not isinstance(media_bin, dict):
        errors.append("media-bin evidence missing")
    else:
        if media_bin.get("selected") != ["A002"]:
            errors.append("media-bin stable selection is not A002")
        if media_bin.get("audio_query") != ["A002"]:
            errors.append("media-bin audio filter failed")
        if media_bin.get("image_query") != ["A003"]:
            errors.append("media-bin text query failed")

    expected_settings = {"width": 1280, "height": 720, "fps": 30, "aspect_ratio": "16:9"}
    if settings != expected_settings:
        errors.append(f"project settings mismatch: {settings!r}")

    if not isinstance(missing, dict):
        errors.append("missing-media evidence missing")
    else:
        if missing.get("snapshot_availability") != "missing":
            errors.append("autosave did not preserve missing state")
        if missing.get("canonical_availability") != "online":
            errors.append("autosave appears to have overwritten canonical project")
        if missing.get("clip_asset_id") != "A001" or missing.get("clip_count") != 1:
            errors.append("missing media silently changed/deleted the clip")

    if errors:
        for error in errors:
            print(f"FAIL {error}")
        return 1
    print(f"PASS STEP 11 W1 evidence: {len(REQUIRED)} required files + 1 autosave")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
