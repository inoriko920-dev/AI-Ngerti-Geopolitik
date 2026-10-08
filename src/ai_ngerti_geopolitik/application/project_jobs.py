"""W8-008 read-only background results tied to the active project lifecycle."""

from __future__ import annotations

from _thread import LockType
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from enum import StrEnum
from threading import Event, Lock
from typing import Generic, TypeVar
from uuid import uuid4

from ai_ngerti_geopolitik.domain import ProjectState

T = TypeVar("T")


class ProjectJobError(RuntimeError):
    """Safe failure without private project contents or filesystem paths."""


@dataclass(frozen=True, slots=True)
class ProjectJobToken:
    project_id: str
    session_id: str
    revision: int
    semantic_hash: str

    @classmethod
    def capture(cls, state: ProjectState, session_id: str) -> ProjectJobToken:
        if not session_id.strip():
            raise ProjectJobError("active project session is required")
        return cls(state.project_id, session_id, state.revision, state.semantic_hash())

    def is_stale(self, state: ProjectState | None, session_id: str | None) -> bool:
        return (
            state is None
            or session_id is None
            or self.project_id != state.project_id
            or self.session_id != session_id
            or self.revision != state.revision
            or self.semantic_hash != state.semantic_hash()
        )


class ProjectJobState(StrEnum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"
    STALE = "STALE"


@dataclass(frozen=True, slots=True)
class ProjectJobSnapshot(Generic[T]):
    job_id: str
    token: ProjectJobToken
    state: ProjectJobState
    result: T | None


@dataclass(slots=True)
class _Record(Generic[T]):
    token: ProjectJobToken
    cancel: Event
    state: ProjectJobState = ProjectJobState.QUEUED
    result: T | None = None


class ReadOnlyProjectJobs(Generic[T]):
    """Background validation and recovery inspection with no second state owner."""

    def __init__(self) -> None:
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="ang-w8-reader")
        self._lock: LockType = Lock()
        self._records: dict[str, _Record[T]] = {}
        self._closed = False

    def __enter__(self) -> ReadOnlyProjectJobs[T]:
        return self

    def __exit__(self, _type: object, _value: object, _traceback: object) -> None:
        self.shutdown()

    def shutdown(self) -> None:
        with self._lock:
            self._closed = True
            for record in self._records.values():
                record.cancel.set()
                record.result = None
                if record.state in {ProjectJobState.QUEUED, ProjectJobState.RUNNING}:
                    record.state = ProjectJobState.CANCELLED
        self._executor.shutdown(wait=False, cancel_futures=True)

    def submit(
        self, state: ProjectState, *, session_id: str, work: Callable[[], T]
    ) -> ProjectJobSnapshot[T]:
        token = ProjectJobToken.capture(state, session_id)
        job_id = uuid4().hex
        record: _Record[T] = _Record(token, Event())
        with self._lock:
            if self._closed:
                raise ProjectJobError("background runner is closed")
            self._records[job_id] = record
            try:
                self._executor.submit(self._run, record, work)
            except RuntimeError as exc:
                del self._records[job_id]
                raise ProjectJobError("background runner is unavailable") from exc
        return self.snapshot(job_id, state=state, session_id=session_id)

    def _run(self, record: _Record[T], work: Callable[[], T]) -> None:
        with self._lock:
            if record.cancel.is_set():
                return
            record.state = ProjectJobState.RUNNING
        try:
            result = work()
        except Exception:  # noqa: BLE001 — never leak private worker exceptions
            with self._lock:
                if not record.cancel.is_set():
                    record.state = ProjectJobState.FAILED
            return
        with self._lock:
            if record.cancel.is_set():
                record.state = ProjectJobState.CANCELLED
                record.result = None
            else:
                record.state = ProjectJobState.SUCCESS
                record.result = result

    def snapshot(
        self, job_id: str, *, state: ProjectState | None, session_id: str | None
    ) -> ProjectJobSnapshot[T]:
        with self._lock:
            if job_id not in self._records:
                raise ProjectJobError("unknown background job")
            record = self._records[job_id]
            if record.token.is_stale(state, session_id):
                return ProjectJobSnapshot(job_id, record.token, ProjectJobState.STALE, None)
            return ProjectJobSnapshot(job_id, record.token, record.state, record.result)

    def cancel(self, job_id: str) -> None:
        with self._lock:
            if job_id not in self._records:
                raise ProjectJobError("unknown background job")
            record = self._records[job_id]
            record.cancel.set()
            record.result = None
            record.state = ProjectJobState.CANCELLED

    def resolve(
        self, job_id: str, *, state: ProjectState | None, session_id: str | None
    ) -> T:
        item = self.snapshot(job_id, state=state, session_id=session_id)
        if item.state is ProjectJobState.STALE:
            raise ProjectJobError("result is stale; run a new job")
        if item.state is not ProjectJobState.SUCCESS or item.result is None:
            raise ProjectJobError("no eligible background result")
        return item.result
