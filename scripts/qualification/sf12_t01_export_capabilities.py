"""Emit Boolean toolchain inventory, not a claim of render qualification."""

from __future__ import annotations

import json
from dataclasses import asdict

from ai_ngerti_geopolitik.infrastructure.export_capability_probe import (
    detect_export_toolchain,
)


def main() -> int:
    print(json.dumps(asdict(detect_export_toolchain()), sort_keys=True))
    print("EXPORT_PIPELINE_NOT_YET_CONNECTED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
