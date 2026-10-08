"""Atomic local crash marker storage; project source and .bak are never written."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path

from ai_ngerti_geopolitik.application.recovery import CrashMarker, RecoveryError


class FileCrashMarkerStore:
    """One marker per (project ID, resolved source); fail closed on malformed files."""

    def _path(self, source: Path, project_id: str) -> Path:
        if not project_id or "/" in project_id or "\\" in project_id or project_id in {".", ".."}:
            raise RecoveryError("invalid project identity in crash marker")
        source = source.resolve()
        digest = hashlib.sha256(str(source).encode("utf-8")).hexdigest()
        return source.parent / ".ang-autosave" / f"{digest}.session.json"

    def read(self, source: Path, project_id: str) -> CrashMarker | None:
        path = self._path(source, project_id)
        if path.is_symlink():
            raise RecoveryError("unsafe crash marker link")
        if not path.exists():
            return None
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(raw, dict) or raw.get("schema") != 1:
                raise ValueError("invalid crash marker schema")
            marker = CrashMarker(
                project_id=str(raw["project_id"]),
                source_digest=str(raw["source_digest"]),
                session_id=str(raw["session_id"]),
                status=str(raw["status"]),
                revision=int(raw["revision"]),
            )
            expected = hashlib.sha256(str(source.resolve()).encode("utf-8")).hexdigest()
            if (
                marker.project_id != project_id
                or marker.source_digest != expected
                or marker.status not in {"clean", "unclean"}
                or not marker.session_id
                or marker.revision < 0
            ):
                raise ValueError("corrupt crash marker")
            return marker
        except (OSError, ValueError, KeyError, TypeError) as exc:
            raise RecoveryError("crash marker invalid or unreadable") from exc

    def write(self, source: Path, marker: CrashMarker) -> None:
        path = self._path(source, marker.project_id)
        expected = hashlib.sha256(str(source.resolve()).encode("utf-8")).hexdigest()
        if marker.source_digest != expected or marker.status not in {"clean", "unclean"}:
            raise RecoveryError("invalid crash marker payload")
        if path.is_symlink() or path.parent.is_symlink():
            raise RecoveryError("unsafe crash marker destination")
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema": 1,
            "project_id": marker.project_id,
            "source_digest": marker.source_digest,
            "session_id": marker.session_id,
            "status": marker.status,
            "revision": marker.revision,
        }
        temporary: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=path.parent,
                prefix=".crash-marker.",
                suffix=".tmp",
                delete=False,
            ) as handle:
                json.dump(payload, handle, sort_keys=True)
                handle.flush()
                os.fsync(handle.fileno())
                temporary = Path(handle.name)
            os.replace(temporary, path)
            temporary = None
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
