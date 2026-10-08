"""Approved Pilot A: bounded real FFmpeg H264 encoding of verified image-only frames.

Owner authorized external FFmpeg/FFprobe on a development branch only.
No UI Export, merge, audio/subtitle support or portable distribution.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import shutil
import subprocess
import tempfile
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

from ai_ngerti_geopolitik.infrastructure.still_h264_plan import SilentH264Plan
from ai_ngerti_geopolitik.infrastructure.still_rgb24_sink import (
    RGB24TransferReceipt,
    feed_rgb24_to_sink,
)


class PilotAError(RuntimeError):
    """Path-free native pilot error."""


@dataclass(frozen=True, slots=True)
class PilotAResult:
    path: Path
    sha256: str
    file_bytes: int
    frame_count: int
    fps: int
    width: int
    height: int
    duration_seconds: float
    rgb24_sha256: str


def sha256_executable(path: Path) -> str:
    try:
        if (
            path.is_symlink()
            or not path.is_file()
            or not 0 < path.stat().st_size < 512 * 1024 * 1024
        ):
            raise ValueError("invalid binary")
        checksum = hashlib.sha256()
        with path.open("rb") as handle:
            while block := handle.read(1024 * 1024):
                checksum.update(block)
        return checksum.hexdigest()
    except (OSError, ValueError):
        raise PilotAError("native binary verification failed") from None


def _pinned(path: Path, digest: str, basename: str) -> Path:
    try:
        if (
            not path.is_absolute()
            or path.name.lower() not in {basename, basename + ".exe"}
            or path.resolve(strict=True) != path
            or type(digest) is not str
            or len(digest) != 64
            or any(char not in "0123456789abcdef" for char in digest)
            or sha256_executable(path) != digest
        ):
            raise ValueError("binary identity mismatch")
        return path
    except (OSError, ValueError, PilotAError):
        raise PilotAError("native binary identity mismatch") from None


def _encode(
    plan: SilentH264Plan,
    ffmpeg: Path,
    staging: Path,
    timeout: float,
    should_cancel: Callable[[], bool] | None,
) -> RGB24TransferReceipt:
    try:
        child = subprocess.Popen(
            [str(ffmpeg), *plan.ffmpeg_argument_suffix[:-1], str(staging)],
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            shell=False,
        )
    except OSError:
        raise PilotAError("native encoding process could not start") from None
    finished = threading.Event()
    receipt: list[RGB24TransferReceipt] = []
    failure: list[str] = []

    def producer() -> None:
        assert child.stdin is not None
        try:
            receipt.append(
                feed_rgb24_to_sink(
                    plan,
                    child.stdin,
                    should_cancel=should_cancel,
                    timeout_seconds=timeout,
                )
            )
        except (OSError, ValueError, RuntimeError, TypeError) as error:
            failure.append(type(error).__name__)
        finally:
            try:
                child.stdin.close()
            except OSError:
                pass
            finished.set()

    writer = threading.Thread(target=producer, daemon=True, name="ang-pilot-a-rgb24")
    writer.start()
    started = time.monotonic()
    try:
        while True:
            if should_cancel is not None and should_cancel():
                raise PilotAError("native encode cancelled")
            if time.monotonic() - started >= timeout:
                raise PilotAError("native encoder deadline exceeded")
            code = child.poll()
            if finished.is_set() and code is not None:
                break
            if failure:
                raise PilotAError("RGB24 producer failed")
            if code is not None and not finished.wait(0.5):
                raise PilotAError("native encoder exited before RGB24 completion")
            time.sleep(0.03)
        writer.join(timeout=2)
        if writer.is_alive() or failure or child.returncode != 0 or len(receipt) != 1:
            raise PilotAError("native encoding incomplete")
        return receipt[0]
    except (OSError, RuntimeError, ValueError, TypeError):
        raise PilotAError("native encoding failed or cancelled") from None
    finally:
        if child.poll() is None:
            child.kill()
        try:
            child.wait(timeout=3)
        except subprocess.TimeoutExpired:
            child.kill()
        writer.join(timeout=3)


def _postflight(mp4: Path, ffmpeg: Path, ffprobe: Path, plan: SilentH264Plan) -> float:
    with tempfile.TemporaryFile() as metadata:
        try:
            probe = subprocess.run(
                [
                    str(ffprobe),
                    "-v",
                    "error",
                    "-count_frames",
                    "-show_entries",
                    "stream=codec_type,codec_name,pix_fmt,width,height,nb_read_frames,avg_frame_rate",
                    "-show_entries",
                    "format=duration",
                    "-of",
                    "json",
                    str(mp4),
                ],
                stdin=subprocess.DEVNULL,
                stdout=metadata,
                stderr=subprocess.DEVNULL,
                timeout=20,
                shell=False,
                check=False,
            )
            if probe.returncode != 0 or metadata.tell() > 128 * 1024:
                raise ValueError("probe failed")
            metadata.seek(0)
            info = json.loads(metadata.read(128 * 1024).decode("utf-8"))
            streams = info["streams"]
            if not isinstance(streams, list) or len(streams) != 1:
                raise ValueError("unexpected tracks")
            video = streams[0]
            expected = plan.verified_frames
            if (
                video.get("codec_type") != "video"
                or video.get("codec_name") != "h264"
                or video.get("pix_fmt") != "yuv420p"
                or int(video["width"]) != expected.width
                or int(video["height"]) != expected.height
                or int(video["nb_read_frames"]) != expected.frame_count
                or Fraction(str(video["avg_frame_rate"])) != expected.fps
            ):
                raise ValueError("wrong video properties")
            duration = float(info["format"]["duration"])
            if (
                not math.isfinite(duration)
                or abs(duration - expected.frame_count / expected.fps) > 1 / expected.fps
            ):
                raise ValueError("duration mismatch")
            decoded = subprocess.run(
                [
                    str(ffmpeg),
                    "-nostdin",
                    "-v",
                    "error",
                    "-xerror",
                    "-i",
                    str(mp4),
                    "-map",
                    "0:v:0",
                    "-an",
                    "-f",
                    "null",
                    "-",
                ],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=30,
                shell=False,
                check=False,
            )
            if decoded.returncode != 0:
                raise ValueError("decoded video failed")
            return duration
        except (
            OSError,
            ValueError,
            KeyError,
            TypeError,
            RuntimeError,
            subprocess.TimeoutExpired,
            ZeroDivisionError,
        ):
            raise PilotAError("native MP4 postflight failed") from None


def export_silent_h264_pilot_a(
    plan: SilentH264Plan,
    *,
    ffmpeg_path: Path,
    ffmpeg_sha256: str,
    ffprobe_path: Path,
    ffprobe_sha256: str,
    timeout_seconds: float = 60,
    should_cancel: Callable[[], bool] | None = None,
) -> PilotAResult:
    """Write a verified MP4 via FFmpeg with no overwrite of existing output."""
    if (
        isinstance(timeout_seconds, bool)
        or not isinstance(timeout_seconds, (float, int))
        or not math.isfinite(timeout_seconds)
        or not 1 <= timeout_seconds <= 3600
    ):
        raise PilotAError("invalid encoder deadline")
    output = plan.destination
    if (
        not output.is_absolute()
        or output.suffix.lower() != ".mp4"
        or output.exists()
        or output.is_symlink()
        or not output.parent.is_dir()
        or any(p.is_symlink() or p.is_junction() for p in (output.parent, *output.parent.parents))
    ):
        raise PilotAError("invalid MP4 output destination")
    if should_cancel is not None and should_cancel():
        raise PilotAError("native export cancelled before launch")
    ffmpeg = _pinned(ffmpeg_path, ffmpeg_sha256, "ffmpeg")
    ffprobe = _pinned(ffprobe_path, ffprobe_sha256, "ffprobe")
    stage_dir: Path | None = None
    try:
        stage_dir = Path(tempfile.mkdtemp(prefix=".ang-pilot-", dir=output.parent))
        staged = stage_dir / "video.mp4"
        receipt = _encode(plan, ffmpeg, staged, timeout_seconds, should_cancel)
        if (
            staged.is_symlink()
            or not staged.is_file()
            or not 0 < staged.stat().st_size < 2 * 1024 * 1024 * 1024
        ):
            raise PilotAError("native encoder produced no qualified MP4")
        duration = _postflight(staged, ffmpeg, ffprobe, plan)
        if should_cancel is not None and should_cancel():
            raise PilotAError("native export cancelled before publish")
        sha256 = hashlib.sha256()
        with staged.open("rb") as reader:
            while block := reader.read(1024 * 1024):
                sha256.update(block)
        size = staged.stat().st_size
        # Exclusive atomic create: os.rename could overwrite on POSIX.
        os.link(staged, output)
        return PilotAResult(
            path=output,
            sha256=sha256.hexdigest(),
            file_bytes=size,
            frame_count=receipt.frame_count,
            fps=receipt.fps,
            width=receipt.width,
            height=receipt.height,
            duration_seconds=duration,
            rgb24_sha256=receipt.stream_sha256,
        )
    except (OSError, ValueError, RuntimeError, TypeError, OverflowError):
        raise PilotAError("native pilot failed; no MP4 published") from None
    finally:
        if stage_dir is not None:
            shutil.rmtree(stage_dir, ignore_errors=True)
