"""Owner-approved Pilot A audio / simple burned subtitle postflight.

Restricted to one fingerprint-pinned PCM WAV narration and plain static
ASCII text cues. Never assumes unsupported media fidelity.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import tempfile
from collections.abc import Callable
from pathlib import Path

from ai_ngerti_geopolitik.domain import ProjectState
from ai_ngerti_geopolitik.infrastructure.ffmpeg_narration import build_narration_render_plan
from ai_ngerti_geopolitik.infrastructure.ffmpeg_subtitles import build_subtitle_export_plan
from ai_ngerti_geopolitik.infrastructure.pilot_a_still_mp4 import (
    PilotAError,
    PilotAResult,
    sha256_executable,
)

_TEXT_ALLOWED = re.compile(r"[A-Za-z0-9 .!?-]{1,120}\Z")


def _narration_source(state: ProjectState) -> Path | None:
    narration = state.narration
    if narration is None:
        return None
    asset = state.asset(narration.asset_id)
    source = Path(asset.path_ref)
    if (
        asset.media_type != "audio"
        or source.suffix.lower() != ".wav"
        or source.is_symlink()
        or not source.is_absolute()
        or not source.is_file()
        or not 0 < source.stat().st_size <= 128 * 1024 * 1024
        or source.stat().st_size != asset.file_size
        or asset.sample_rate not in (16000, 24000, 44100, 48000)
    ):
        raise PilotAError("narration source unavailable or unsupported")
    digest = hashlib.sha256()
    with source.open("rb") as stream:
        while block := stream.read(1024 * 1024):
            digest.update(block)
    if digest.hexdigest() != asset.fingerprint_sha256:
        raise PilotAError("narration source integrity changed")
    return source


def _subtitles(state: ProjectState, enabled: bool) -> str | None:
    sub = state.subtitle
    if not enabled:
        if sub is not None and sub.enabled:
            raise PilotAError("enabled subtitle cannot be silently omitted")
        return None
    if (
        sub is None
        or not sub.enabled
        or len(sub.cues) > 10
        or sub.animation.preset != "none"
        or sub.style.font_family != "Arial"
        or any(_TEXT_ALLOWED.fullmatch(cue.text) is None for cue in sub.cues)
    ):
        raise PilotAError("complex or missing subtitle unsupported for native Pilot A")
    filters = build_subtitle_export_plan(state).filters
    if not filters or len(filters) != len(sub.cues):
        raise PilotAError("subtitle filter construction failed")
    return ",".join(filters)


def compose_narration_subtitle_pilot_a(
    silent: PilotAResult,
    state: ProjectState,
    output: Path,
    *,
    ffmpeg_path: Path,
    ffmpeg_sha256: str,
    ffprobe_path: Path,
    ffprobe_sha256: str,
    include_subtitles: bool,
    should_cancel: Callable[[], bool] | None = None,
) -> PilotAResult:
    """Compose verified final MP4 after the visual-only encoder, never overwrite."""
    try:
        if (
            ffmpeg_path.is_symlink()
            or ffprobe_path.is_symlink()
            or sha256_executable(ffmpeg_path) != ffmpeg_sha256
            or sha256_executable(ffprobe_path) != ffprobe_sha256
            or not output.is_absolute()
            or output.exists()
            or output.is_symlink()
            or silent.path == output
            or not silent.path.is_file()
        ):
            raise PilotAError("native postcompose input invalid")
        narration = _narration_source(state)
        subtitles = _subtitles(state, include_subtitles)
        if narration is None and subtitles is None:
            raise PilotAError("no secondary track required")
        if should_cancel is not None and should_cancel():
            raise PilotAError("postcompose cancelled")
        duration = state.timeline_end_frame / state.fps
        with tempfile.TemporaryDirectory(prefix=".ang-av-", dir=output.parent) as folder:
            staged = Path(folder) / "av.mp4"
            args = [
                str(ffmpeg_path),
                "-nostdin",
                "-hide_banner",
                "-v",
                "error",
                "-xerror",
                "-i",
                str(silent.path),
            ]
            if narration is not None:
                args.extend(("-i", str(narration)))
            if subtitles is not None:
                args.extend(("-vf", subtitles))
            args.extend(("-map", "0:v:0"))
            if narration is None:
                args.extend(("-an",))
            else:
                audio_plan = build_narration_render_plan(state)
                if audio_plan is None:
                    raise PilotAError("narration plan is missing")
                audio_filter = ",".join(
                    (
                        *audio_plan.filters,
                        "apad",
                        f"atrim=end={duration:.6f}",
                    )
                )
                args.extend(("-map", "1:a:0", "-af", audio_filter))
            if subtitles is None:
                args.extend(("-c:v", "copy"))
            else:
                args.extend(
                    ("-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p")
                )
            if narration is not None:
                args.extend(("-c:a", "aac", "-b:a", "128k", "-ar", "48000", "-ac", "2"))
            args.extend(
                ("-t", f"{duration:.6f}", "-movflags", "+faststart", "-f", "mp4", "-y", str(staged))
            )
            finished = subprocess.run(
                args,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                shell=False,
                timeout=120,
                check=False,
            )
            if finished.returncode != 0 or not staged.is_file() or staged.stat().st_size <= 0:
                raise PilotAError("native audiovisual compose failed")
            with tempfile.TemporaryFile() as manifest:
                verified = subprocess.run(
                    [
                        str(ffprobe_path),
                        "-v",
                        "error",
                        "-count_frames",
                        "-show_entries",
                        "stream=codec_type,codec_name,pix_fmt,width,height,nb_read_frames,avg_frame_rate",
                        "-show_entries",
                        "format=duration",
                        "-of",
                        "json",
                        str(staged),
                    ],
                    stdin=subprocess.DEVNULL,
                    stdout=manifest,
                    stderr=subprocess.DEVNULL,
                    shell=False,
                    timeout=20,
                    check=False,
                )
                if verified.returncode != 0 or manifest.tell() > 65536:
                    raise PilotAError("audiovisual postflight failed")
                manifest.seek(0)
                parsed = json.loads(manifest.read(65536).decode("utf-8"))
            streams = parsed["streams"]
            videos = [stream for stream in streams if stream.get("codec_type") == "video"]
            audios = [stream for stream in streams if stream.get("codec_type") == "audio"]
            if (
                len(videos) != 1
                or videos[0].get("codec_name") != "h264"
                or videos[0].get("pix_fmt") != "yuv420p"
                or int(videos[0]["width"]) != silent.width
                or int(videos[0]["height"]) != silent.height
                or int(videos[0]["nb_read_frames"]) != silent.frame_count
                or len(audios) != (1 if narration is not None else 0)
                or (audios and audios[0].get("codec_name") != "aac")
                or abs(float(parsed["format"]["duration"]) - duration) > 1 / state.fps
            ):
                raise PilotAError("audiovisual stream mismatch")
            decoded = subprocess.run(
                [
                    str(ffmpeg_path),
                    "-nostdin",
                    "-v",
                    "error",
                    "-xerror",
                    "-i",
                    str(staged),
                    "-f",
                    "null",
                    "-",
                ],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                shell=False,
                timeout=40,
                check=False,
            )
            if decoded.returncode != 0:
                raise PilotAError("audiovisual full decode failed")
            if should_cancel is not None and should_cancel():
                raise PilotAError("postcompose cancelled before publish")
            digest = hashlib.sha256()
            with staged.open("rb") as content:
                while chunk := content.read(1024 * 1024):
                    digest.update(chunk)
            # Exclusive publish: an existing output cannot be overwritten.
            os.link(staged, output)
            return PilotAResult(
                path=output,
                sha256=digest.hexdigest(),
                file_bytes=output.stat().st_size,
                frame_count=silent.frame_count,
                fps=silent.fps,
                width=silent.width,
                height=silent.height,
                duration_seconds=duration,
                rgb24_sha256=silent.rgb24_sha256,
            )
    except (
        OSError,
        ValueError,
        TypeError,
        RuntimeError,
        KeyError,
        OverflowError,
        subprocess.TimeoutExpired,
    ):
        raise PilotAError("native audiovisual Pilot A failed without publishing output") from None
