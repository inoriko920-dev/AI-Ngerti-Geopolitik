"""Local output preflight; never overwrite media or the user's existing MP4.

The bounded writable probe touches only a random temporary file inside the
selected directory, then deletes it. Do not call from the Qt GUI thread.
"""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from ai_ngerti_geopolitik.application.export_preflight import (
    ExportPreflightCode,
    OutputTargetInspection,
)


class LocalExportOutputInspector:
    def inspect(
        self,
        output_path: Path,
        protected_paths: tuple[Path, ...],
        min_free_bytes: int,
    ) -> OutputTargetInspection:
        try:
            parent = output_path.parent
            if not parent.is_dir():
                return OutputTargetInspection(ExportPreflightCode.OUTPUT_PARENT_INVALID)
            if output_path.is_symlink():
                return OutputTargetInspection(ExportPreflightCode.OUTPUT_EXISTS)
            target = output_path.resolve(strict=False)
            if target in {source.resolve(strict=False) for source in protected_paths}:
                return OutputTargetInspection(ExportPreflightCode.OUTPUT_COLLISION)
            if output_path.exists():
                return OutputTargetInspection(ExportPreflightCode.OUTPUT_EXISTS)
            if shutil.disk_usage(parent).free < min_free_bytes:
                return OutputTargetInspection(ExportPreflightCode.INSUFFICIENT_DISK)
            with tempfile.NamedTemporaryFile(prefix=".ang-preflight-", suffix=".tmp", dir=parent):
                pass
        except (OSError, ValueError):
            return OutputTargetInspection(ExportPreflightCode.OUTPUT_NOT_WRITABLE)
        return OutputTargetInspection()
