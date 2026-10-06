from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

STATES = (
    "UI-002",
    "UI-003",
    "UI-010",
    "UI-013",
    "UI-014",
    "UI-027",
    "UI-035",
    "UI-041",
)


def main() -> int:
    from PySide6.QtGui import QImage

    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--actual", type=Path, default=Path("artifacts/step09_actual"))
    args = parser.parse_args()
    root = args.root.resolve()
    actual_dir = (root / args.actual).resolve() if not args.actual.is_absolute() else args.actual
    reference_dir = root / "docs/ui_reference/raw"

    errors: list[str] = []
    for state in STATES:
        actual_path = actual_dir / f"{state}_ACTUAL.png"
        reference_path = reference_dir / f"{state}.png"
        if not actual_path.is_file():
            errors.append(f"missing actual screenshot: {actual_path}")
            continue
        if not reference_path.is_file():
            errors.append(f"missing frozen reference: {reference_path}")
            continue
        actual = QImage(str(actual_path))
        reference = QImage(str(reference_path))
        if actual.isNull():
            errors.append(f"invalid actual image: {actual_path}")
            continue
        if reference.isNull():
            errors.append(f"invalid reference image: {reference_path}")
            continue
        if (actual.width(), actual.height()) != (1920, 1080):
            errors.append(
                f"{state} actual dimensions {actual.width()}x{actual.height()} != 1920x1080"
            )
        if actual_path.stat().st_size < 25_000:
            errors.append(f"{state} actual screenshot unexpectedly small")
        actual_hash = hashlib.sha256(actual_path.read_bytes()).hexdigest()
        reference_hash = hashlib.sha256(reference_path.read_bytes()).hexdigest()
        if actual_hash == reference_hash:
            errors.append(
                f"{state} actual equals frozen PNG byte-for-byte; static-image runtime suspected"
            )

    if errors:
        for error in errors:
            print(f"FAIL {error}")
        return 1
    print(f"PASS representative STEP 09 captures: {len(STATES)}/{len(STATES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
