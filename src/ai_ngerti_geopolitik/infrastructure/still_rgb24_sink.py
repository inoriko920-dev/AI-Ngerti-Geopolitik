"""Bounded no-FFmpeg RGB24 handoff to a supplied sink.

The sink is an abstract byte consumer, not an FFmpeg process. This worker-only
adapter cannot open files, choose executables, or publish video output. Callers
must discard partial sink output on error, interruption, or cancellation.
"""

from __future__ import annotations

import hashlib
import math
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol

from ai_ngerti_geopolitik.infrastructure.still_h264_plan import SilentH264Plan
from ai_ngerti_geopolitik.infrastructure.still_rgb24_stream import (
    RGB24StreamError,
    iter_rgb24_chunks,
)

_MAX_WRITE_BYTES = 64 * 1024
_MAX_PARTIAL_WRITES = 256
_MAX_FRAMES = 18_000
_MAX_PIXELS = 16_000_000


class RGB24TransferError(RuntimeError):
    """Sink transfer failed; an external sink's partial bytes are not committed."""


class RGB24TransferCancelled(RGB24TransferError):
    """The transfer was cancelled and external partial output must be discarded."""


class RGB24TransferTimeout(RGB24TransferError):
    """The cooperative time budget expired: partial bytes must be discarded."""


class RGB24Sink(Protocol):
    """A synchronous test/worker byte sink; no native process ownership."""

    def write(self, data: bytes) -> int: ...


@dataclass(frozen=True, slots=True)
class RGB24TransferReceipt:
    """Only proves bytes accepted by the sink, not an MP4 or codec."""

    frame_count: int
    fps: int
    width: int
    height: int
    byte_count: int
    stream_sha256: str


def feed_rgb24_to_sink(
    plan: SilentH264Plan,
    sink: RGB24Sink,
    *,
    should_cancel: Callable[[], bool] | None = None,
    on_frame: Callable[[int, int], None] | None = None,
    chunk_rows: int = 32,
    timeout_seconds: float | None = None,
    monotonic: Callable[[], float] = time.monotonic,
) -> RGB24TransferReceipt:
    """Write each packed scanline block through bounded short-write handling.

    Cancellation is cooperative: a blocked sink.write() cannot be interrupted
    by this adapter. Future native subprocess ownership is separately gated.
    """
    if timeout_seconds is not None and (
        isinstance(timeout_seconds, bool)
        or not isinstance(timeout_seconds, (int, float))
        or not math.isfinite(timeout_seconds)
        or not 0 < timeout_seconds <= 86_400
    ):
        raise RGB24TransferError("RGB24 timeout budget is invalid")
    start = monotonic() if timeout_seconds is not None else 0.0
    if timeout_seconds is not None and not math.isfinite(start):
        raise RGB24TransferError("RGB24 monotonic clock is invalid")
    frames = plan.verified_frames
    frame_bytes = plan.rgb24_bytes_per_frame
    if (
        type(frames.frame_count) is not int
        or not 1 <= frames.frame_count <= _MAX_FRAMES
        or type(frame_bytes) is not int
        or frame_bytes != frames.width * frames.height * 3
        or frame_bytes < 1
        or frames.width * frames.height > _MAX_PIXELS
        or frames.fps not in (30, 60)
    ):
        raise RGB24TransferError("invalid RGB24 transfer contract")

    expected = frames.frame_count * frame_bytes
    accepted = 0
    completed = 0
    checksum = hashlib.sha256()

    def check_cancelled() -> None:
        if should_cancel is not None and should_cancel():
            raise RGB24TransferCancelled("RGB24 transfer cancelled")
        if timeout_seconds is not None:
            current = monotonic()
            if not math.isfinite(current) or current < start:
                raise RGB24TransferTimeout("RGB24 monotonic clock is invalid")
            if current - start > timeout_seconds:
                raise RGB24TransferTimeout("RGB24 transfer time budget exceeded")

    try:
        check_cancelled()
        for block in iter_rgb24_chunks(plan, chunk_rows=chunk_rows):
            check_cancelled()
            if not block or accepted + len(block) > expected:
                raise RGB24TransferError("invalid RGB24 stream length")
            offset = 0
            while offset < len(block):
                check_cancelled()
                part = block[offset : offset + _MAX_WRITE_BYTES]
                part_offset = 0
                writes = 0
                while part_offset < len(part):
                    check_cancelled()
                    writes += 1
                    if writes > _MAX_PARTIAL_WRITES:
                        raise RGB24TransferError("RGB24 sink made insufficient progress")
                    piece = part[part_offset:]
                    written = sink.write(piece)
                    check_cancelled()
                    if type(written) is not int or not 0 < written <= len(piece):
                        raise RGB24TransferError("RGB24 sink returned invalid byte count")
                    checksum.update(piece[:written])
                    part_offset += written
                    offset += written
                    accepted += written
                    if accepted % frame_bytes == 0:
                        completed += 1
                        if on_frame is not None:
                            on_frame(completed, frames.frame_count)
                        check_cancelled()
        check_cancelled()
        if accepted != expected or completed != frames.frame_count:
            raise RGB24TransferError("RGB24 stream ended before all frames")
    except RGB24TransferError:
        raise
    except (RGB24StreamError, OSError, ValueError, RuntimeError, TypeError, OverflowError):
        raise RGB24TransferError("RGB24 transfer or sink failed") from None

    return RGB24TransferReceipt(
        frame_count=completed,
        fps=frames.fps,
        width=frames.width,
        height=frames.height,
        byte_count=accepted,
        stream_sha256=checksum.hexdigest(),
    )
