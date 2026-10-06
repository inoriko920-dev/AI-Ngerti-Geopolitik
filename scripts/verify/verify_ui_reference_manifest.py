from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path

ENTRY = re.compile(
    r"^(?:\|\s*)?(UI-\d{3})(?:\s*\|\s*`?UI-\d{3}\.png`?)?"
    r"\s*\|\s*`?([0-9a-f]{64})`?\s*\|(?:.*\|\s*)?"
    r"APPROVED_FOR_FREEZE(?:\s*\|)?$"
)


def load_manifest(path: Path) -> dict[str, str]:
    entries: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        match = ENTRY.match(raw.strip())
        if not match:
            continue
        ui_id, digest = match.groups()
        if ui_id in entries:
            raise ValueError(f"duplicate manifest id: {ui_id}")
        entries[ui_id] = digest
    return entries


def verify(root: Path) -> list[str]:
    manifest_path = root / "docs/ui_reference/UI_REFERENCE_MANIFEST.md"
    raw_dir = root / "docs/ui_reference/raw"
    entries = load_manifest(manifest_path)
    expected = [f"UI-{index:03d}" for index in range(1, 43)]
    errors: list[str] = []
    if sorted(entries) != expected:
        errors.append(f"manifest ids mismatch: expected 42 exact ids, got {len(entries)}")
    pngs = sorted(raw_dir.glob("UI-*.png"))
    if [p.stem for p in pngs] != expected:
        errors.append(f"raw reference set mismatch: expected 42 exact PNGs, got {len(pngs)}")
    for ui_id in expected:
        path = raw_dir / f"{ui_id}.png"
        if not path.is_file() or ui_id not in entries:
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != entries[ui_id]:
            errors.append(f"SHA-256 mismatch for {ui_id}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    errors = verify(args.root)
    if errors:
        for error in errors:
            print(f"FAIL {error}")
        return 1
    print("PASS UI references 42/42 SHA-256")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
