"""Bounded FFmpeg encoder inventory; run off the GUI thread or in CI."""

from __future__ import annotations

import shutil
import subprocess
from collections.abc import Callable

from ai_ngerti_geopolitik.application.export_capabilities import ExportToolchain

Runner = Callable[[tuple[str, ...]], tuple[int, str] | None]


def _run(command: tuple[str, ...]) -> tuple[int, str] | None:
    try:
        result = subprocess.run(command, capture_output=True, check=False, text=True, timeout=8)
    except (OSError, subprocess.TimeoutExpired, UnicodeError):
        return None
    return result.returncode, result.stdout


def _encoder_exists(output: str, flag: str, encoder: str) -> bool:
    return any(
        len(parts) >= 2 and len(parts[0]) >= 6 and parts[0][0] == flag and parts[1] == encoder
        for parts in (line.split() for line in output.splitlines())
    )


def detect_export_toolchain(
    *,
    ffmpeg_binary: str | None = None,
    ffprobe_binary: str | None = None,
    runner: Runner = _run,
) -> ExportToolchain:
    ffmpeg = ffmpeg_binary or shutil.which("ffmpeg")
    ffprobe = ffprobe_binary or shutil.which("ffprobe")
    if not ffmpeg or not ffprobe:
        return ExportToolchain(ffmpeg_found=bool(ffmpeg), ffprobe_found=bool(ffprobe))
    version = runner((ffprobe, "-version"))
    encoders = runner((ffmpeg, "-hide_banner", "-encoders"))
    probe_ok = version is not None and version[0] == 0
    ffmpeg_ok = encoders is not None and encoders[0] == 0
    output = encoders[1] if ffmpeg_ok and encoders is not None else ""
    return ExportToolchain(
        ffmpeg_found=ffmpeg_ok,
        ffprobe_found=probe_ok,
        h264_encoder_found=_encoder_exists(output, "V", "libx264"),
        h265_encoder_found=_encoder_exists(output, "V", "libx265"),
        aac_encoder_found=_encoder_exists(output, "A", "aac"),
    )
