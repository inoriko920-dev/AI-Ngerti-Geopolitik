"""W8-006 explicit startup recovery decisions using the W8-005 validated catalog.

No automatic source overwrite, silent recovery, duplicate project store or UI mutation.
W8-010 owns final main-window/controller wiring; this service owns decisions.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Protocol
from uuid import uuid4

from ai_ngerti_geopolitik.application.autosave_catalog import (
    AutosaveCatalogService,
    AutosaveRecord,
)
from ai_ngerti_geopolitik.application.ports import ProjectRepositoryPort
from ai_ngerti_geopolitik.application.project_session import ProjectSession, UnsavedChangesError
from ai_ngerti_geopolitik.domain import ProjectState


class RecoveryError(RuntimeError):
    """Safe error: no private content or absolute path in message."""


class RecoveryChoice(StrEnum):
    OPEN_SOURCE = "open_source"
    RECOVER_SNAPSHOT = "recover_snapshot"
    IGNORE = "ignore"


@dataclass(frozen=True, slots=True)
class CrashMarker:
    project_id: str
    source_digest: str
    session_id: str
    status: str
    revision: int


class CrashMarkerPort(Protocol):
    def read(self, source: Path, project_id: str) -> CrashMarker | None: ...

    def write(self, source: Path, marker: CrashMarker) -> None: ...


@dataclass(frozen=True, slots=True)
class RecoveryOffer:
    source: Path
    project_id: str
    source_sha256: str
    source_revision: int
    source_semantic_hash: str
    prior_marker: CrashMarker | None
    candidates: tuple[AutosaveRecord, ...]

    @property
    def interrupted(self) -> bool:
        return self.prior_marker is not None and self.prior_marker.status == "unclean"

    @property
    def can_recover(self) -> bool:
        return self.interrupted and bool(self.candidates)


@dataclass(frozen=True, slots=True)
class RecoveryDecision:
    choice: RecoveryChoice
    opened_state: ProjectState | None
    active_marker: CrashMarker | None


def _file_digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(1024 * 1024):
            value.update(block)
    return value.hexdigest()


def _new_marker(source: Path, state: ProjectState) -> CrashMarker:
    return CrashMarker(
        project_id=state.project_id,
        source_digest=hashlib.sha256(str(source.resolve()).encode("utf-8")).hexdigest(),
        session_id=uuid4().hex,
        status="unclean",
        revision=state.revision,
    )


class RecoveryManager:
    def __init__(
        self,
        repository: ProjectRepositoryPort,
        catalog: AutosaveCatalogService,
        markers: CrashMarkerPort,
    ) -> None:
        self.repository = repository
        self.catalog = catalog
        self.markers = markers

    def inspect(self, source: Path) -> RecoveryOffer:
        source = source.resolve()
        if not source.is_file() or source.suffix.lower() != ".angproj":
            raise RecoveryError("source project is missing or invalid")
        try:
            state = self.repository.load(source)
            state.validate()
            marker = self.markers.read(source, state.project_id)
            candidates = self.catalog.inspect(source.parent / ".ang-autosave", state.project_id)
            mtime_ns = source.stat().st_mtime_ns
            recoverable = tuple(
                item
                for item in candidates.recoverable
                if (
                    item.revision > state.revision
                    or (
                        item.revision == state.revision
                        and item.timestamp_ns > mtime_ns
                        and item.semantic_hash != state.semantic_hash()
                    )
                )
            )
            return RecoveryOffer(
                source=source,
                project_id=state.project_id,
                source_sha256=_file_digest(source),
                source_revision=state.revision,
                source_semantic_hash=state.semantic_hash(),
                prior_marker=marker,
                candidates=recoverable if marker is not None and marker.status == "unclean" else (),
            )
        except (OSError, RuntimeError, ValueError) as exc:
            raise RecoveryError("startup recovery inspection failed") from exc

    def decide(
        self,
        offer: RecoveryOffer,
        choice: RecoveryChoice,
        session: ProjectSession,
        *,
        selected_path: Path | None = None,
        discard_unsaved: bool = False,
    ) -> RecoveryDecision:
        if choice is RecoveryChoice.IGNORE:
            # No project state and no marker modification. User may inspect again later.
            return RecoveryDecision(choice, None, None)
        try:
            current = self.inspect(offer.source)
        except RecoveryError as exc:
            raise RecoveryError("recovery offer became invalid; inspect again") from exc
        if (
            current.source_sha256 != offer.source_sha256
            or current.project_id != offer.project_id
            or current.prior_marker != offer.prior_marker
        ):
            raise RecoveryError("recovery offer is stale; inspect again")
        if current.interrupted and not offer.interrupted:
            raise RecoveryError("recovery marker changed during decision")
        restored: ProjectState | None = None
        if choice is RecoveryChoice.RECOVER_SNAPSHOT:
            if not offer.can_recover or selected_path is None:
                raise RecoveryError("a validated recovery snapshot must be selected")
            if not current.can_recover:
                raise RecoveryError("selected recovery snapshot is stale or invalid")
            target = selected_path.resolve()
            candidate = next((x for x in offer.candidates if x.path == target), None)
            fresh = next((x for x in current.candidates if x.path == target), None)
            if (
                candidate is None
                or fresh is None
                or candidate.file_sha256 != fresh.file_sha256
                or candidate.semantic_hash != fresh.semantic_hash
                or candidate.revision != fresh.revision
            ):
                raise RecoveryError("selected recovery snapshot is stale or invalid")
            # Source is still read-only. ProjectSession exclusively owns working state.
            restored = session.recover_snapshot(
                offer.source, target, discard_unsaved=discard_unsaved
            )
        elif choice is RecoveryChoice.OPEN_SOURCE:
            restored = session.open_project(offer.source, discard_unsaved=discard_unsaved)
        else:
            raise RecoveryError("unsupported recovery decision")

        assert restored is not None
        active_marker = _new_marker(offer.source, restored)
        try:
            self.markers.write(offer.source, active_marker)
        except (OSError, RuntimeError, ValueError) as exc:
            raise RecoveryError("unable to begin crash-safe session marker") from exc
        return RecoveryDecision(choice, restored, active_marker)

    def close_clean(
        self,
        session: ProjectSession,
        source: Path,
        active_marker: CrashMarker,
        *,
        discard_unsaved: bool = False,
    ) -> None:
        if session.current_path != source.resolve():
            raise RecoveryError("active session does not match recovery source")
        current = self.markers.read(source, active_marker.project_id)
        if current != active_marker or active_marker.status != "unclean":
            raise RecoveryError("active session marker mismatch")
        # Enforce the unsaved-work guard BEFORE writing a clean marker.
        # A rejected marker write must never destroy the still-active session.
        if session.dirty and not discard_unsaved:
            raise UnsavedChangesError("project has unsaved changes")
        self.markers.write(
            source,
            CrashMarker(
                project_id=active_marker.project_id,
                source_digest=active_marker.source_digest,
                session_id=active_marker.session_id,
                status="clean",
                revision=active_marker.revision,
            ),
        )
        # With a validated clean (or explicitly discarded) session, closing
        # is an in-memory operation; no more fallible disk writes follow it.
        try:
            session.close(discard_unsaved=discard_unsaved)
        except (OSError, RuntimeError, ValueError):
            # Defensive rollback for an unexpected close failure. The ordinary
            # Qt path is single-threaded and cannot change dirty state here.
            self.markers.write(source, active_marker)
            raise
