"""Standalone read-only pre-MP4 frame-sequence gate. Never runs FFmpeg."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository
from ai_ngerti_geopolitik.infrastructure.still_sequence_verification import (
    StillSequenceVerificationError,
    verify_complete_still_sequence,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Periksa semua frame PNG sebelum integrasi MP4 (tanpa encode)."
    )
    parser.add_argument("--project", required=True, help="Proyek .angproj yang tersimpan")
    parser.add_argument("--frames", required=True, help="Folder hasil frames-all")
    args = parser.parse_args(argv)
    try:
        state = JsonProjectRepository().load(Path(args.project))
        verified = verify_complete_still_sequence(state, Path(args.frames))
    except (StillSequenceVerificationError, OSError, ValueError, RuntimeError):
        print("GAGAL: frame/project tidak lolos verifikasi integritas", file=sys.stderr)
        return 1
    print(
        f"PASS: {verified.frame_count} frame PNG, {verified.fps} FPS, "
        f"{verified.width}x{verified.height}; BELUM MP4, FFmpeg tidak dijalankan."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
