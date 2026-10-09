"""Application CLI for read-only pre-MP4 frame-sequence integrity verification."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository
from ai_ngerti_geopolitik.infrastructure.still_h264_plan import (
    SilentH264PlanError,
    plan_silent_h264_mp4,
)
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
    parser.add_argument(
        "--plan-mp4", metavar="OUTPUT", help="Validasi rencana H.264 tanpa membuat MP4"
    )
    args = parser.parse_args(argv)
    try:
        state = JsonProjectRepository().load(Path(args.project))
        verified = verify_complete_still_sequence(state, Path(args.frames))
        plan = (
            plan_silent_h264_mp4(state, Path(args.frames), Path(args.plan_mp4))
            if args.plan_mp4 is not None
            else None
        )
    except (StillSequenceVerificationError, SilentH264PlanError, OSError, ValueError, RuntimeError):
        print("GAGAL: frame/project tidak lolos verifikasi integritas", file=sys.stderr)
        return 1
    print(
        f"PASS: {verified.frame_count} frame PNG, {verified.fps} FPS, "
        f"{verified.width}x{verified.height}; BELUM MP4, FFmpeg tidak dijalankan."
    )
    if plan is not None:
        print(
            f"DRY RUN PASS: H.264 {plan.duration_numerator}/{plan.duration_denominator} "
            "detik, RGB24; FFmpeg belum dijalankan; tidak ada MP4."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
