"""Bounded CPU-only scanline RGB24 frames from verified still PNG sequences.

This module never launches FFmpeg, writes MP4s, or creates output files.
Each PNG is rehashed before its pixels are decoded and yielded.
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterator
from pathlib import Path

from PySide6.QtCore import QBuffer, QByteArray, QIODevice
from PySide6.QtGui import QImage, QImageReader

from ai_ngerti_geopolitik.infrastructure.still_h264_plan import SilentH264Plan

_MAX_PNG_BYTES = 128 * 1024 * 1024
_MAX_PIXELS = 16_000_000
_MAX_DIMENSION = 8192
_MAX_ROWS = 64


class RGB24StreamError(RuntimeError):
    """Fail-closed error that never includes a user's private paths."""


def _read_frame(path: Path, checksum: str, expected_bytes: int) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise ValueError("missing or linked PNG")
    before = path.stat()
    if not 0 < before.st_size == expected_bytes <= _MAX_PNG_BYTES:
        raise ValueError("PNG size not qualified")
    with path.open("rb") as handle:
        data = handle.read(_MAX_PNG_BYTES + 1)
    after = path.stat()
    if (
        len(data) != expected_bytes
        or hashlib.sha256(data).hexdigest() != checksum
        or (
            before.st_size,
            before.st_mtime_ns,
            before.st_ctime_ns,
        )
        != (
            after.st_size,
            after.st_mtime_ns,
            after.st_ctime_ns,
        )
    ):
        raise ValueError("PNG changed after verification")
    return data


def _decode_rgb(data: bytes, width: int, height: int) -> QImage:
    buffer = QBuffer()
    buffer.setData(QByteArray(data))
    if not buffer.open(QIODevice.OpenModeFlag.ReadOnly):
        raise ValueError("PNG buffer unavailable")
    try:
        reader = QImageReader(buffer)
        reader.setAutoTransform(False)
        dimensions = reader.size()
        if not dimensions.isValid() or dimensions.width() != width or dimensions.height() != height:
            raise ValueError("PNG dimensions changed")
        decoded = reader.read()
        if decoded.isNull() or decoded.width() != width or decoded.height() != height:
            raise ValueError("PNG could not be decoded")
        rgb = decoded.convertToFormat(QImage.Format.Format_RGB888)
        if rgb.isNull() or rgb.sizeInBytes() < width * height * 3:
            raise ValueError("RGB888 conversion failed")
        return rgb
    finally:
        buffer.close()


def iter_rgb24_chunks(plan: SilentH264Plan, *, chunk_rows: int = 32) -> Iterator[bytes]:
    """Yield packed RGB24 whole-row chunks in exact timeline order.

    No file writes or subprocesses. A future, separately authorized encoder
    must provide its own cancellation, revalidation and safe MP4 postflight.
    """
    if type(chunk_rows) is not int or not 1 <= chunk_rows <= _MAX_ROWS:
        raise RGB24StreamError("invalid RGB24 chunk row count")
    frames = plan.verified_frames
    width, height = frames.width, frames.height
    if (
        type(width) is not int
        or type(height) is not int
        or width < 2
        or height < 2
        or width > _MAX_DIMENSION
        or height > _MAX_DIMENSION
        or width % 2 != 0
        or height % 2 != 0
        or width * height > _MAX_PIXELS
        or frames.fps not in (30, 60)
        or type(frames.frame_count) is not int
        or frames.frame_count < 1
        or plan.rgb24_bytes_per_frame != width * height * 3
        or len(frames.frame_files) != frames.frame_count
        or len(frames.frame_sha256) != frames.frame_count
        or len(frames.frame_bytes) != frames.frame_count
    ):
        raise RGB24StreamError("RGB24 plan is unsupported")

    for frame_number, path in enumerate(frames.frame_files):
        try:
            if path.name != f"frame_{frame_number:06d}.png":
                raise ValueError("frame numbering changed")
            data = _read_frame(
                path, frames.frame_sha256[frame_number], frames.frame_bytes[frame_number]
            )
            rgb = _decode_rgb(data, width, height)
            stride = rgb.bytesPerLine()
            row_bytes = width * 3
            if stride < row_bytes or rgb.sizeInBytes() < stride * height:
                raise ValueError("RGB24 stride not qualified")
            pixels = rgb.constBits()
            for top in range(0, height, chunk_rows):
                end = min(height, top + chunk_rows)
                chunk = b"".join(
                    bytes(pixels[row * stride : row * stride + row_bytes])
                    for row in range(top, end)
                )
                if len(chunk) != (end - top) * row_bytes:
                    raise ValueError("short RGB24 scanline block")
                yield chunk
        except (OSError, ValueError, RuntimeError, TypeError, OverflowError):
            raise RGB24StreamError("RGB24 frame stream integrity check failed") from None
