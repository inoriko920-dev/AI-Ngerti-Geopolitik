"""Pure plan for a future silent RGB24 -> H.264/MP4 encoder, with no execution.

Only a separate owner-approved Pilot A may choose an FFmpeg executable,
start a child process, stream images, inspect the resulting file, or publish it.
The prepared argv suffix is NOT a claim that an encoder or codec is available.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ai_ngerti_geopolitik.domain import ProjectState
from ai_ngerti_geopolitik.infrastructure.still_sequence_verification import (
    VerifiedStillSequence,
    verify_complete_still_sequence,
)

_MAX_FRAME_PIXELS = 16_000_000
_FORBIDDEN_WIN_NAME_CHARS = frozenset('<>:"/\\|?*')
_WIN_RESERVED = frozenset(
    {"CON", "PRN", "AUX", "NUL"}
    | {f"COM{i}" for i in range(1, 10)}
    | {f"LPT{i}" for i in range(1, 10)}
)


class SilentH264PlanError(RuntimeError):
    """One safe error category for an output that must not be rendered."""


@dataclass(frozen=True, slots=True)
class SilentH264Plan:
    """Non-executable proposal: frame order and exact rawvideo encoder contract."""

    verified_frames: VerifiedStillSequence
    destination: Path
    rgb24_bytes_per_frame: int
    ffmpeg_argument_suffix: tuple[str, ...]

    @property
    def duration_numerator(self) -> int:
        return self.verified_frames.frame_count

    @property
    def duration_denominator(self) -> int:
        return self.verified_frames.fps


def _validate_output_path(output: Path, root: Path) -> None:
    if not output.is_absolute() or output.suffix.lower() != ".mp4":
        raise ValueError("output must be an absolute MP4 path")
    name = output.name
    stem = output.stem
    if (
        not stem
        or stem.startswith(".")
        or name != name.rstrip(" .")
        or any(char in _FORBIDDEN_WIN_NAME_CHARS or ord(char) < 32 for char in name)
        or stem.split(".")[0].upper() in _WIN_RESERVED
    ):
        raise ValueError("output filename is invalid")
    if output.exists() or output.is_symlink():
        raise ValueError("output already exists")
    parent = output.parent
    if not parent.is_dir():
        raise ValueError("output directory is unavailable")
    if any(part.is_symlink() or part.is_junction() for part in (parent, *parent.parents)):
        raise ValueError("linked output directory is not qualified")
    frames_path = root.resolve(strict=True)
    output_parent = parent.resolve(strict=True)
    if output_parent == frames_path or output_parent.is_relative_to(frames_path):
        raise ValueError("output must stay outside source frame folder")


def plan_silent_h264_mp4(
    state: ProjectState, frames_root: Path, destination: Path
) -> SilentH264Plan:
    """Verify input + output for a silent plan, but do not launch or write anything.

    The next separately approved runner must revalidate every input immediately
    before reading it, decode frames in this order to packed RGB24, enforce
    duration/frame-count postflight, and keep the output staged until PASS.
    """
    try:
        _validate_output_path(destination, frames_root)
        verified = verify_complete_still_sequence(state, frames_root)
        width, height = verified.width, verified.height
        if (
            verified.fps not in (30, 60)
            or width < 2
            or height < 2
            or width % 2 != 0
            or height % 2 != 0
            or width * height > _MAX_FRAME_PIXELS
        ):
            raise ValueError("rawvideo/YUV420p resolution or FPS is not qualified")
        if len(verified.frame_files) != verified.frame_count:
            raise ValueError("verified image count differs")
        # The actual source PNGs have not been opened by an encoder. The
        # consumer must decode each PNG as packed RGB24 in exact sequence.
        argv = (
            "-hide_banner",
            "-nostdin",
            "-loglevel",
            "error",
            "-n",
            "-f",
            "rawvideo",
            "-pixel_format",
            "rgb24",
            "-video_size",
            f"{width}x{height}",
            "-framerate",
            str(verified.fps),
            "-i",
            "pipe:0",
            "-map",
            "0:v:0",
            "-an",
            "-sn",
            "-dn",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-frames:v",
            str(verified.frame_count),
            "-movflags",
            "+faststart",
            "-f",
            "mp4",
            str(destination),
        )
        return SilentH264Plan(
            verified_frames=verified,
            destination=destination,
            rgb24_bytes_per_frame=width * height * 3,
            ffmpeg_argument_suffix=argv,
        )
    except (OSError, ValueError, RuntimeError, UnicodeError):
        raise SilentH264PlanError(
            "silent MP4 plan blocked by frame, resolution or output preflight"
        ) from None
