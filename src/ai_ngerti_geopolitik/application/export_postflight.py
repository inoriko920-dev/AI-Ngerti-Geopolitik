"""SF12-T09 strict postflight contract. No output may become READY unverified."""

from __future__ import annotations

import hashlib
import stat
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Protocol

from ai_ngerti_geopolitik.application.export_request import ExportRequest
from ai_ngerti_geopolitik.application.ports import CancellationToken, ExportResult
from ai_ngerti_geopolitik.domain import ProjectState


class PostflightCode(StrEnum):
    FILE_MISSING_OR_EMPTY = "POSTFLIGHT_FILE_MISSING_OR_EMPTY"
    INVALID_CONTAINER = "POSTFLIGHT_INVALID_CONTAINER"
    STREAM_STRUCTURE = "POSTFLIGHT_STREAM_STRUCTURE"
    CODEC_MISMATCH = "POSTFLIGHT_CODEC_MISMATCH"
    SIZE_MISMATCH = "POSTFLIGHT_SIZE_MISMATCH"
    FPS_MISMATCH = "POSTFLIGHT_FPS_MISMATCH"
    FRAME_COUNT_MISMATCH = "POSTFLIGHT_FRAME_COUNT_MISMATCH"
    DURATION_MISMATCH = "POSTFLIGHT_DURATION_MISMATCH"
    RESULT_MISMATCH = "POSTFLIGHT_RESULT_MISMATCH"
    DECODE_FAILED = "POSTFLIGHT_DECODE_FAILED"
    INSPECTION_FAILED = "POSTFLIGHT_INSPECTION_FAILED"
    STAGING_CHANGED = "POSTFLIGHT_STAGING_CHANGED"


class ExportPostflightError(RuntimeError):
    """Expose only an allowlisted failure code, never a user path or media stderr."""

    def __init__(self, code: PostflightCode) -> None:
        self.code = code
        super().__init__(code.value)


@dataclass(frozen=True, slots=True)
class PostflightReceipt:
    path: Path = field(repr=False)
    sha256: str
    size_bytes: int
    mtime_ns: int
    device: int
    inode: int
    expected_frames: int

    @classmethod
    def capture(cls, path: Path, expected_frames: int) -> PostflightReceipt:
        try:
            details = path.lstat()
            if not stat.S_ISREG(details.st_mode) or details.st_size <= 0:
                raise ValueError("not a regular file")
            digest = hashlib.sha256()
            with path.open("rb") as handle:
                for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                    digest.update(chunk)
            latest = path.lstat()
            if (
                latest.st_size != details.st_size
                or latest.st_mtime_ns != details.st_mtime_ns
                or latest.st_ino != details.st_ino
                or latest.st_dev != details.st_dev
            ):
                raise ValueError("file modified during verification")
            return cls(
                path,
                digest.hexdigest(),
                details.st_size,
                details.st_mtime_ns,
                details.st_dev,
                details.st_ino,
                expected_frames,
            )
        except (OSError, ValueError):
            raise ExportPostflightError(PostflightCode.STAGING_CHANGED) from None

    def still_current(self, stage_path: Path) -> bool:
        try:
            details = stage_path.lstat()
            return (
                stage_path == self.path
                and stat.S_ISREG(details.st_mode)
                and details.st_size == self.size_bytes
                and details.st_mtime_ns == self.mtime_ns
                and details.st_dev == self.device
                and details.st_ino == self.inode
            )
        except (OSError, ValueError):
            return False


class ExportPostflightPort(Protocol):
    def verify(
        self,
        stage_path: Path,
        request: ExportRequest,
        state: ProjectState,
        result: ExportResult,
        cancellation: CancellationToken,
    ) -> PostflightReceipt: ...
