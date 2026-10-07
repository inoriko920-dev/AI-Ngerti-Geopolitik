from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    root = args.evidence.resolve()

    required = [
        "00_w5_008_ui_report.txt",
        "UI-017_ACTUAL_SUBTITLE_TEXT.png",
        "UI-018_ACTUAL_NARRATION.png",
        "UI-033_ACTUAL_SUBTITLE_STYLE.png",
        "UI-034_ACTUAL_SUBTITLE_ANIMATION.png",
        "UI-035_ACTUAL_WORD_TIMING_BOUNDARY.png",
        "UI-036_ACTUAL_WORD_TIMING_ACK.png",
        "UI-017_REFERENCE_VS_ACTUAL.png",
        "UI-018_REFERENCE_VS_ACTUAL.png",
        "UI-033_REFERENCE_VS_ACTUAL.png",
        "UI-034_REFERENCE_VS_ACTUAL.png",
        "UI-035_REFERENCE_VS_ACTUAL.png",
        "UI-036_REFERENCE_VS_ACTUAL.png",
        "WIN-001_ACTUAL_NARRATION_RECORDING.png",
    ]
    missing = [name for name in required if not (root / name).is_file()]
    if missing:
        raise SystemExit(f"missing W5-008 evidence: {missing}")

    report = (root / "00_w5_008_ui_report.txt").read_text(encoding="utf-8")
    for token in (
        "status=PASS",
        "unsupported_controls=hidden_or_disabled",
        "microphone_hardware_claim=provisional",
    ):
        if token not in report:
            raise SystemExit(f"W5-008 report token missing: {token}")

    for name in required:
        if (root / name).stat().st_size <= 0:
            raise SystemExit(f"empty W5-008 evidence: {name}")

    print(f"PASS W5-008 evidence files: {len(required)}/{len(required)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
