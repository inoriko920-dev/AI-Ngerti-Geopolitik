"""W8-002 local real-media integrity inspector behind the application port."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ai_ngerti_geopolitik.application.ports import MediaProbePort
from ai_ngerti_geopolitik.application.validation import (
    MediaIntegrityObservation,
    MediaIntegrityStatus,
)


@dataclass(slots=True)
class LocalMediaIntegrityInspector:
    probe: MediaProbePort

    def inspect(self, path: Path) -> MediaIntegrityObservation:
        try:
            if not path.is_file():
                return MediaIntegrityObservation(MediaIntegrityStatus.MISSING)
            file_size = path.stat().st_size
        except OSError:
            return MediaIntegrityObservation(
                MediaIntegrityStatus.PROBE_FAILED,
                safe_error_code="FILE_STAT_FAILED",
            )

        if file_size == 0:
            return MediaIntegrityObservation(
                MediaIntegrityStatus.ZERO_BYTE,
                file_size=0,
            )

        try:
            result = self.probe.probe(path)
        except (OSError, RuntimeError, ValueError):
            return MediaIntegrityObservation(
                MediaIntegrityStatus.PROBE_FAILED,
                file_size=file_size,
                safe_error_code="MEDIA_PROBE_FAILED",
            )

        return MediaIntegrityObservation(
            MediaIntegrityStatus.OK,
            file_size=result.file_size or file_size,
            media_type=result.media_type,
            fingerprint_sha256=result.fingerprint_sha256,
        )
