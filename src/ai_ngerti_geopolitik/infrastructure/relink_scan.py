"""W8-004 deterministic, bounded, symlink-safe local media directory iterator."""

from __future__ import annotations

import os
from collections.abc import Iterator
from pathlib import Path

from ai_ngerti_geopolitik.application.relink_scan import ScanCancel

_MEDIA_SUFFIXES = frozenset(
    {
        ".mp4",
        ".mov",
        ".mkv",
        ".avi",
        ".webm",
        ".mp3",
        ".wav",
        ".m4a",
        ".flac",
        ".png",
        ".jpg",
        ".jpeg",
        ".webp",
        ".bmp",
        ".tif",
        ".tiff",
    }
)


class LocalRelinkDirectoryScanner:
    """Only walks an explicitly selected root; never follows symlinked directories."""

    def paths(
        self, root: Path, *, cancellation: ScanCancel, max_files: int, max_depth: int
    ) -> Iterator[Path]:
        root = root.resolve()
        if not root.is_dir():
            raise OSError("scan root unavailable")
        count = 0
        for base, directories, filenames in os.walk(root, topdown=True, followlinks=False):
            if cancellation.cancelled:
                return
            current = Path(base)
            depth = len(current.relative_to(root).parts)
            directories[:] = sorted(
                directory
                for directory in directories
                if depth < max_depth and not (current / directory).is_symlink()
            )
            for filename in sorted(filenames):
                if cancellation.cancelled or count >= max_files:
                    return
                candidate = current / filename
                if candidate.suffix.lower() not in _MEDIA_SUFFIXES or candidate.is_symlink():
                    continue
                if not candidate.is_file():
                    continue
                resolved = candidate.resolve()
                if not resolved.is_relative_to(root):
                    continue
                count += 1
                yield resolved
