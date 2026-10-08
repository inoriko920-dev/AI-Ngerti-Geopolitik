"""On-demand W8-009 asynchronous diagnostic export behind an application port."""

from __future__ import annotations

import hashlib
import json
from _thread import LockType
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from threading import Event, Lock
from typing import Protocol
from uuid import uuid4

from ai_ngerti_geopolitik.application.diagnostics import (
    DiagnosticError,
    DiagnosticErrorCode,
    DiagnosticLedger,
    DiagnosticSnapshot,
)


class DiagnosticJobState(StrEnum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"


class DiagnosticBundleWriterPort(Protocol):
    def write_bundle(
        self, target: Path, *, manifest: bytes, events: bytes, cancel: Event
    ) -> None: ...


@dataclass(frozen=True, slots=True)
class DiagnosticJobSnapshot:
    job_id: str
    state: DiagnosticJobState
    event_count: int
    error_code: DiagnosticErrorCode | None = None


@dataclass(slots=True)
class _Job:
    event_count: int
    cancel: Event
    state: DiagnosticJobState = DiagnosticJobState.QUEUED
    error_code: DiagnosticErrorCode | None = None
    future: Future[None] | None = None


def _json(data: object) -> bytes:
    return (
        json.dumps(data, sort_keys=True, ensure_ascii=True, separators=(",", ":")) + "\n"
    ).encode("ascii")


def safe_bundle_payload(snapshot: DiagnosticSnapshot) -> tuple[bytes, bytes]:
    if (
        not 0 <= len(snapshot.events) <= 256
        or type(snapshot.dropped_count) is not int
        or not 0 <= snapshot.dropped_count <= 1_000_000
    ):
        raise DiagnosticError(DiagnosticErrorCode.INVALID_INPUT)
    # Reconstruct only allowlisted enum members, never serialize arbitrary objects.
    from ai_ngerti_geopolitik.application.diagnostics import (
        DiagnosticCode,
        DiagnosticStatus,
    )
    from ai_ngerti_geopolitik.application.persistence_failure import PersistenceStage

    items = []
    for event in snapshot.events:
        if (
            type(event.sequence) is not int
            or not 1 <= event.sequence <= 1_000_000
            or not isinstance(event.code, DiagnosticCode)
            or not isinstance(event.status, DiagnosticStatus)
            or type(event.count) is not int
            or not 0 <= event.count <= 10_000
            or (
                event.persistence_stage is not None
                and not isinstance(event.persistence_stage, PersistenceStage)
            )
        ):
            raise DiagnosticError(DiagnosticErrorCode.INVALID_INPUT)
        items.append(
            {
                "sequence": event.sequence,
                "code": event.code.value,
                "status": event.status.value,
                "count": event.count,
                "persistence_stage": (
                    event.persistence_stage.value if event.persistence_stage else None
                ),
            }
        )
    if any(items[i]["sequence"] >= items[i + 1]["sequence"] for i in range(len(items) - 1)):
        raise DiagnosticError(DiagnosticErrorCode.INVALID_INPUT)
    events = _json({"schema": 1, "events": items})
    manifest = _json(
        {
            "schema": 1,
            "kind": "ANG_W8_009_DIAGNOSTIC",
            "redaction": "STRICT_ALLOWLIST",
            "event_count": len(items),
            "dropped_count": snapshot.dropped_count,
            "files": [{"name": "events.json", "sha256": hashlib.sha256(events).hexdigest()}],
        }
    )
    if len(events) + len(manifest) > 128 * 1024:
        raise DiagnosticError(DiagnosticErrorCode.SIZE_LIMIT)
    return manifest, events


@dataclass(slots=True)
class DiagnosticBundleJobService:
    writer: DiagnosticBundleWriterPort
    _executor: ThreadPoolExecutor = field(init=False, repr=False)
    _lock: LockType = field(init=False, repr=False)
    _jobs: dict[str, _Job] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="ang-diagnostics")
        self._lock = Lock()
        self._jobs = {}

    def __enter__(self) -> DiagnosticBundleJobService:
        return self

    def __exit__(self, _type: object, _value: object, _tb: object) -> None:
        self.shutdown()

    def shutdown(self) -> None:
        with self._lock:
            for job in self._jobs.values():
                job.cancel.set()
        self._executor.shutdown(wait=False, cancel_futures=True)

    def submit(self, target: Path, ledger: DiagnosticLedger) -> DiagnosticJobSnapshot:
        if not isinstance(ledger, DiagnosticLedger):
            raise DiagnosticError(DiagnosticErrorCode.INVALID_INPUT)
        if target.suffix.lower() != ".zip":
            raise DiagnosticError(DiagnosticErrorCode.INVALID_INPUT)
        snapshot = ledger.snapshot()
        manifest, events = safe_bundle_payload(snapshot)
        job_id = uuid4().hex
        job = _Job(len(snapshot.events), Event())
        with self._lock:
            self._jobs[job_id] = job
        try:
            future = self._executor.submit(self._run, job_id, target, manifest, events)
        except RuntimeError as exc:
            with self._lock:
                del self._jobs[job_id]
            raise DiagnosticError(DiagnosticErrorCode.OUTPUT_UNAVAILABLE) from exc
        with self._lock:
            job.future = future
        return self.snapshot(job_id)

    def snapshot(self, job_id: str) -> DiagnosticJobSnapshot:
        with self._lock:
            if job_id not in self._jobs:
                raise DiagnosticError(DiagnosticErrorCode.UNKNOWN_JOB)
            job = self._jobs[job_id]
            return DiagnosticJobSnapshot(job_id, job.state, job.event_count, job.error_code)

    def cancel(self, job_id: str) -> None:
        with self._lock:
            if job_id not in self._jobs:
                raise DiagnosticError(DiagnosticErrorCode.UNKNOWN_JOB)
            job = self._jobs[job_id]
            job.cancel.set()
            if job.state in {DiagnosticJobState.QUEUED, DiagnosticJobState.RUNNING}:
                job.state = DiagnosticJobState.CANCELLED
                job.error_code = DiagnosticErrorCode.CANCELLED
            if job.future is not None:
                job.future.cancel()

    def _run(self, job_id: str, target: Path, manifest: bytes, events: bytes) -> None:
        with self._lock:
            job = self._jobs[job_id]
            if job.cancel.is_set():
                job.state = DiagnosticJobState.CANCELLED
                return
            job.state = DiagnosticJobState.RUNNING
        try:
            self.writer.write_bundle(target, manifest=manifest, events=events, cancel=job.cancel)
            with self._lock:
                if job.cancel.is_set():
                    job.state = DiagnosticJobState.CANCELLED
                    job.error_code = DiagnosticErrorCode.CANCELLED
                else:
                    job.state = DiagnosticJobState.SUCCESS
        except DiagnosticError as exc:
            with self._lock:
                job.error_code = exc.code
                job.state = (
                    DiagnosticJobState.CANCELLED
                    if exc.code is DiagnosticErrorCode.CANCELLED
                    else DiagnosticJobState.FAILED
                )
        except (OSError, RuntimeError, ValueError):
            with self._lock:
                job.state = DiagnosticJobState.FAILED
                job.error_code = DiagnosticErrorCode.OUTPUT_UNAVAILABLE
