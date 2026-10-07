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
        "00_w5_007_hardware_report.json",
        "01_microphone_devices.json",
    ]
    missing = [name for name in required if not (root / name).is_file()]
    if missing:
        raise SystemExit(f"missing W5-007 evidence: {missing}")

    report = json.loads(
        (root / "00_w5_007_hardware_report.json").read_text(encoding="utf-8")
    )
    devices = json.loads(
        (root / "01_microphone_devices.json").read_text(encoding="utf-8")
    )
    status = report.get("status")
    if status not in {"PASS", "PASS_WITH_PROVISIONAL_MIC_HARDWARE"}:
        raise SystemExit(f"invalid W5-007 hardware status: {status}")
    if report.get("fake_hardware_claimed") is not False:
        raise SystemExit("W5-007 must never fake microphone hardware evidence")

    device_count = int(devices.get("device_count", -1))
    if status == "PASS":
        if device_count <= 0:
            raise SystemExit("hardware PASS requires a real enumerated microphone")
        if report.get("real_device_available") is not True:
            raise SystemExit("hardware PASS requires real device availability")
        if report.get("hardware_recording_attempted") is not True:
            raise SystemExit("hardware PASS requires a real recording attempt")
        if report.get("hardware_recording_bound") is not True:
            raise SystemExit("hardware PASS requires canonical narration binding")
        recordings = list((root / "recordings").glob("*.wav"))
        if not recordings:
            raise SystemExit("hardware PASS requires captured WAV evidence")
        if not (root / "w5_007_hardware.angproj").is_file():
            raise SystemExit("hardware PASS requires saved project evidence")
    else:
        if device_count != 0:
            raise SystemExit("provisional hardware status requires zero enumerated devices")
        if report.get("real_device_available") is not False:
            raise SystemExit("provisional status must report no real device")
        if report.get("hardware_recording_attempted") is not False:
            raise SystemExit("provisional status must not claim a recording attempt")
        if report.get("hardware_recording_bound") is not False:
            raise SystemExit("provisional status must not claim narration binding")

    for name in required:
        if (root / name).stat().st_size <= 0:
            raise SystemExit(f"empty W5-007 artifact: {name}")

    print(f"PASS W5-007 hardware gate: {status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
