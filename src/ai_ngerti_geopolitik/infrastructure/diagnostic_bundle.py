"""Deterministic, bounded, atomic ZIP diagnostic writer; never reads project files."""

from __future__ import annotations

import io
from contextlib import suppress
import os
import tempfile
import zipfile
from pathlib import Path
from threading import Event

from ai_ngerti_geopolitik.application.diagnostics import DiagnosticError, DiagnosticErrorCode


class LocalDiagnosticZipWriter:
    MAX_ZIP_BYTES = 128 * 1024

    def write_bundle(self, target: Path, *, manifest: bytes, events: bytes, cancel: Event) -> None:
        if target.suffix.lower() != ".zip" or target.is_symlink():
            raise DiagnosticError(DiagnosticErrorCode.INVALID_INPUT)
        if target.exists():
            raise DiagnosticError(DiagnosticErrorCode.OUTPUT_EXISTS)
        if cancel.is_set():
            raise DiagnosticError(DiagnosticErrorCode.CANCELLED)
        if len(events) + len(manifest) > self.MAX_ZIP_BYTES:
            raise DiagnosticError(DiagnosticErrorCode.SIZE_LIMIT)
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as bundle:
            for name, contents in (("manifest.json", manifest), ("events.json", events)):
                meta = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                meta.compress_type = zipfile.ZIP_DEFLATED
                meta.create_system = 3
                meta.external_attr = 0o600 << 16
                bundle.writestr(meta, contents)
        payload = buf.getvalue()
        if len(payload) > self.MAX_ZIP_BYTES:
            raise DiagnosticError(DiagnosticErrorCode.SIZE_LIMIT)
        temporary: Path | None = None
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                "wb", dir=target.parent, prefix=".ang-diagnostics-", suffix=".tmp", delete=False
            ) as handle:
                temporary = Path(handle.name)
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            if cancel.is_set():
                raise DiagnosticError(DiagnosticErrorCode.CANCELLED)
            # Race-safe no-overwrite creation; no existing file is replaced.
            try:
                os.link(temporary, target)
            except FileExistsError as exc:
                raise DiagnosticError(DiagnosticErrorCode.OUTPUT_EXISTS) from exc
        except DiagnosticError:
            raise
        except OSError as exc:
            raise DiagnosticError(DiagnosticErrorCode.OUTPUT_UNAVAILABLE) from exc
        finally:
            if temporary is not None:
                with suppress(OSError):
                    # Only this owned temp is pruned; never the project source.
                    temporary.unlink(missing_ok=True)
