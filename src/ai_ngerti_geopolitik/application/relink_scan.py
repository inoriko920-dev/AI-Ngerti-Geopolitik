"""W8-004 bounded background relink discovery and explicit atomic approval.

Discovery never touches canonical ProjectState or CommandBus history. Only user-selected,
re-probed, fingerprint-exact candidates may be committed by one CommandBatch.
"""

from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from threading import Event, Lock
from typing import Iterator, Protocol
from uuid import uuid4

from ai_ngerti_geopolitik.application.commands import CommandBatch, CommandError, RelinkAssetCommand
from ai_ngerti_geopolitik.application.media_import import CommandSession, build_asset_from_probe
from ai_ngerti_geopolitik.application.ports import MediaProbePort
from ai_ngerti_geopolitik.application.relink import RelinkService, _metadata_compatible
from ai_ngerti_geopolitik.domain import Asset, ProjectState


class ScanState(StrEnum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"
    STALE = "STALE"


class RelinkScanError(RuntimeError):
    """Safe W8-004 error: filesystem paths and raw media errors are not logged."""


class ScanCancel:
    __slots__ = ("_event",)

    def __init__(self) -> None:
        self._event = Event()

    @property
    def cancelled(self) -> bool:
        return self._event.is_set()

    def cancel(self) -> None:
        self._event.set()


class RelinkDirectoryPort(Protocol):
    def paths(
        self, root: Path, *, cancellation: ScanCancel, max_files: int, max_depth: int
    ) -> Iterator[Path]: ...


@dataclass(frozen=True, slots=True)
class RelinkScanToken:
    project_id: str
    session_id: str
    revision: int
    semantic_hash: str

    def is_stale(self, state: ProjectState, session_id: str) -> bool:
        return (
            self.project_id != state.project_id
            or self.session_id != session_id
            or self.revision != state.revision
            or self.semantic_hash != state.semantic_hash()
        )


@dataclass(frozen=True, slots=True)
class RankedRelinkCandidate:
    asset_id: str
    path: Path
    rank: int
    fingerprint_verified: bool
    evidence: str


@dataclass(frozen=True, slots=True)
class RelinkScanSnapshot:
    job_id: str
    token: RelinkScanToken
    state: ScanState
    scanned_files: int
    candidates: tuple[RankedRelinkCandidate, ...]
    safe_message: str = ""
    applied: bool = False

    @property
    def ambiguous_assets(self) -> tuple[str, ...]:
        counts: dict[str, int] = {}
        for candidate in self.candidates:
            counts[candidate.asset_id] = counts.get(candidate.asset_id, 0) + 1
        return tuple(sorted(asset for asset, count in counts.items() if count > 1))


@dataclass(slots=True)
class _Record:
    token: RelinkScanToken
    cancellation: ScanCancel
    state: ScanState = ScanState.QUEUED
    scanned_files: int = 0
    candidates: tuple[RankedRelinkCandidate, ...] = ()
    safe_message: str = ""
    applied: bool = False
    future: Future[None] | None = None


@dataclass(slots=True)
class RelinkScanJobService:
    scanner: RelinkDirectoryPort
    probe: MediaProbePort
    _executor: ThreadPoolExecutor = field(init=False, repr=False)
    _lock: Lock = field(init=False, repr=False)
    _jobs: dict[str, _Record] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="ang-relink-scan")
        self._lock = Lock()
        self._jobs = {}

    def __enter__(self) -> RelinkScanJobService:
        return self

    def __exit__(self, _type: object, _value: object, _traceback: object) -> None:
        self.shutdown()

    def shutdown(self) -> None:
        with self._lock:
            for record in self._jobs.values():
                record.cancellation.cancel()
        self._executor.shutdown(wait=True, cancel_futures=True)

    def _record(self, job_id: str) -> _Record:
        try:
            return self._jobs[job_id]
        except KeyError as exc:
            raise RelinkScanError("unknown relink scan job") from exc

    @staticmethod
    def _snapshot(job_id: str, record: _Record, *, stale: bool = False) -> RelinkScanSnapshot:
        return RelinkScanSnapshot(
            job_id, record.token, ScanState.STALE if stale else record.state,
            record.scanned_files, record.candidates if not stale else (),
            record.safe_message, record.applied,
        )

    def submit(
        self, state: ProjectState, root: Path, *, session_id: str,
        max_files: int = 400, max_depth: int = 5,
    ) -> RelinkScanSnapshot:
        state.validate()
        if not session_id.strip():
            raise RelinkScanError("active session id is required")
        if not 1 <= max_files <= 5000 or not 0 <= max_depth <= 12:
            raise RelinkScanError("scan bounds are outside allowed limits")
        if not root.is_dir():
            raise RelinkScanError("selected scan directory is unavailable")
        missing = tuple(asset for asset in state.assets if asset.availability != "online")
        token = RelinkScanToken(state.project_id, session_id, state.revision, state.semantic_hash())
        job_id = uuid4().hex
        record = _Record(token, ScanCancel())
        with self._lock:
            self._jobs[job_id] = record
        try:
            future = self._executor.submit(
                self._run, job_id, state, root.resolve(), missing, max_files, max_depth
            )
        except RuntimeError as exc:
            with self._lock:
                del self._jobs[job_id]
            raise RelinkScanError("background scan worker is unavailable") from exc
        with self._lock:
            record.future = future
            return self._snapshot(job_id, record)

    def snapshot(
        self, job_id: str, *, state: ProjectState, session_id: str
    ) -> RelinkScanSnapshot:
        with self._lock:
            record = self._record(job_id)
            return self._snapshot(
                job_id, record, stale=record.token.is_stale(state, session_id)
            )

    def cancel(self, job_id: str) -> None:
        with self._lock:
            record = self._record(job_id)
            record.cancellation.cancel()
            if record.state in {ScanState.QUEUED, ScanState.RUNNING, ScanState.SUCCESS}:
                record.state = ScanState.CANCELLED
                record.candidates = ()
                record.safe_message = "Scan dibatalkan."
            if record.future is not None:
                record.future.cancel()

    def _run(
        self, job_id: str, state: ProjectState, root: Path,
        missing: tuple[Asset, ...], max_files: int, max_depth: int,
    ) -> None:
        with self._lock:
            record = self._record(job_id)
            if record.cancellation.cancelled:
                record.state = ScanState.CANCELLED
                return
            record.state = ScanState.RUNNING
        found: list[RankedRelinkCandidate] = []
        bound_paths = {Path(asset.path_ref).resolve() for asset in state.assets}
        try:
            for path in self.scanner.paths(
                root, cancellation=record.cancellation, max_files=max_files, max_depth=max_depth
            ):
                if record.cancellation.cancelled:
                    break
                with self._lock:
                    record.scanned_files += 1
                if path in bound_paths or not missing:
                    continue
                try:
                    probe_result = self.probe.probe(path)
                except (OSError, RuntimeError, ValueError):
                    continue  # corrupt/unsupported files are not viable candidates
                if record.cancellation.cancelled:
                    break
                for asset in missing:
                    if probe_result.media_type != asset.media_type:
                        continue
                    try:
                        replacement = build_asset_from_probe(state, probe_result, asset.asset_id)
                    except (ValueError, RuntimeError):
                        continue
                    if not _metadata_compatible(asset, replacement):
                        continue
                    name = path.name
                    exact_hash = probe_result.fingerprint_sha256 == asset.fingerprint_sha256
                    if name == Path(asset.path_ref).name:
                        rank, evidence = 1, "canonical filename + compatible metadata"
                    elif asset.source_name and name == asset.source_name:
                        rank, evidence = 2, "source filename + compatible metadata"
                    elif exact_hash:
                        rank, evidence = 3, "exact SHA-256 fingerprint"
                    else:
                        rank, evidence = 4, "compatible metadata only — manual review"
                    found.append(RankedRelinkCandidate(asset.asset_id, path, rank, exact_hash, evidence))
                # Bound memory even when a folder contains many near-identical assets.
                if len(found) >= 2000:
                    break
        except (OSError, RuntimeError, ValueError):
            with self._lock:
                record.state = ScanState.FAILED
                record.safe_message = "Scan folder gagal. Pilih folder lain."
                record.candidates = ()
            return
        with self._lock:
            if record.cancellation.cancelled:
                record.state = ScanState.CANCELLED
                record.safe_message = "Scan dibatalkan."
                record.candidates = ()
            else:
                found.sort(key=lambda item: (item.asset_id, item.rank, str(item.path).casefold()))
                record.candidates = tuple(found)
                record.state = ScanState.SUCCESS

    def apply_selected(
        self, job_id: str, session: CommandSession, *,
        session_id: str, selections: tuple[tuple[str, Path], ...],
    ) -> ProjectState:
        with self._lock:
            record = self._record(job_id)
            if record.token.is_stale(session.state, session_id):
                raise RelinkScanError("scan result is stale; run a new scan")
            if record.state is not ScanState.SUCCESS or record.applied:
                raise RelinkScanError("no active scan result can be applied")
            candidates = record.candidates
        if not selections:
            raise RelinkScanError("explicit candidate selection is required")
        asset_ids = [asset_id for asset_id, _path in selections]
        paths = [path.resolve() for _asset_id, path in selections]
        if len(set(asset_ids)) != len(asset_ids) or len(set(paths)) != len(paths):
            raise RelinkScanError("duplicate asset or candidate path selected")
        selected: list[Asset] = []
        verifier = RelinkService(self.probe)
        for (asset_id, _path), path in zip(selections, paths, strict=True):
            if not any(
                item.asset_id == asset_id and item.path == path and item.fingerprint_verified
                for item in candidates
            ):
                raise RelinkScanError("candidate requires an exact fingerprint match and manual choice")
            selected.append(verifier.verify_candidate(session.state, asset_id, path).replacement)
        with self._lock:
            if record.token.is_stale(session.state, session_id) or record.cancellation.cancelled:
                raise RelinkScanError("scan result became stale or cancelled")
        batch = CommandBatch(
            batch_id=f"W8-BATCH-RELINK-{session.state.revision + 1:06d}",
            label="Relink selected media",
            actor="manual",
            expected_revision=record.token.revision,
            commands=tuple(RelinkAssetCommand(asset) for asset in selected),
        )
        try:
            applied = session.execute(batch)
        except CommandError as exc:
            raise RelinkScanError("verified batch relink was rejected") from exc
        with self._lock:
            record.applied = True
        return applied
