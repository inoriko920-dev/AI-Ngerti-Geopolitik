from __future__ import annotations

import argparse
import json
from pathlib import Path


REQUIRED = (
    "00_environment.json",
    "01_input_media_sha256.txt",
    "01_fixture_provenance.txt",
    "02_ffprobe_input.json",
    "03_pre_edit_snapshot.json",
    "04_post_split_snapshot.json",
    "05_post_trim_snapshot.json",
    "06_undo_redo_hashes.txt",
    "07_preview_boundary.txt",
    "08_saved_project.angproj",
    "09_roundtrip_diff.txt",
    "10_export_settings.json",
    "11_exported_output.mp4",
    "12_ffprobe_output.json",
    "12_export_sha256.txt",
    "13_negative_paths.txt",
    "14_timings.json",
    "15_test_report.json",
    "screenshots/preview_frame_149.png",
    "screenshots/preview_frame_151.png",
)


def load_json(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"expected JSON object: {path}")
    return data


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--expected-sha", required=True)
    args = parser.parse_args()

    root = args.evidence.resolve()
    errors: list[str] = []
    for relative in REQUIRED:
        path = root / relative
        if not path.is_file() or path.stat().st_size == 0:
            errors.append(f"missing/empty evidence: {relative}")

    if errors:
        for error in errors:
            print(f"FAIL {error}")
        return 1

    environment = load_json(root / "00_environment.json")
    report = load_json(root / "15_test_report.json")
    output_probe = load_json(root / "12_ffprobe_output.json")

    if environment.get("git_sha") != args.expected_sha:
        errors.append("environment git SHA does not match workflow SHA")
    if report.get("git_sha") != args.expected_sha:
        errors.append("report git SHA does not match workflow SHA")
    if report.get("status") != "PASS":
        errors.append("E2E report status is not PASS")
    if int(report.get("duration_frames", 0)) != 210:
        errors.append("export duration frame count is not canonical 210")
    if int(report.get("negative_paths", 0)) < 5:
        errors.append("negative path coverage is incomplete")

    streams = output_probe.get("streams")
    if not isinstance(streams, list):
        errors.append("output probe streams missing")
    else:
        video = next(
            (
                stream
                for stream in streams
                if isinstance(stream, dict) and stream.get("codec_type") == "video"
            ),
            None,
        )
        audio = next(
            (
                stream
                for stream in streams
                if isinstance(stream, dict) and stream.get("codec_type") == "audio"
            ),
            None,
        )
        if not isinstance(video, dict):
            errors.append("output video stream missing")
        else:
            if video.get("codec_name") != "h264":
                errors.append("output codec is not H.264")
            if int(video.get("width", 0)) != 1920 or int(video.get("height", 0)) != 1080:
                errors.append("output dimensions are not 1920x1080")
            if video.get("avg_frame_rate") != "30/1":
                errors.append("output frame rate is not 30 fps")
        if not isinstance(audio, dict) or audio.get("codec_name") != "aac":
            errors.append("output AAC audio stream missing")

    project = load_json(root / "08_saved_project.angproj")
    if project.get("schema_version") != 1:
        errors.append("saved .angproj schema_version is not 1")

    negative = (root / "13_negative_paths.txt").read_text(encoding="utf-8")
    for marker in (
        "missing-media: PASS",
        "invalid-split-atomic: PASS",
        "corrupt-project: PASS",
        "cancel-export-cleanup: PASS",
        "invalid-project-extension: PASS",
    ):
        if marker not in negative:
            errors.append(f"negative-path marker missing: {marker}")

    if (root / "cancelled_output.mp4").exists():
        errors.append("cancelled export left a false final artifact")
    if (root / "cancelled_output.partial.mp4").exists():
        errors.append("cancelled export left a partial artifact")

    if errors:
        for error in errors:
            print(f"FAIL {error}")
        return 1
    print(f"PASS STEP 10 evidence set: {len(REQUIRED)}/{len(REQUIRED)} required files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
