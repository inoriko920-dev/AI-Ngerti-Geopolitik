"""SF12-T08 nonblocking staged render lifecycle, explicitly not GUI-activated.

A worker renders to private staging. Only a current-session decision on the
owner thread may atomically publish. T09 strict postflight and T10 packaging
remain independent gates. No fabricated percentage while FFmpeg is opaque.
"""

from __future__ import annotations

import shutil
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from contextlib import suppress
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from threading import Event, Lock, get_ident
from typing import Protocol

from ai_ngerti_geopolitik.application.export_postflight import (
    ExportPostflightError,
    ExportPostflightPort,
    PostflightCode,
    PostflightReceipt,
)
from ai_ngerti_geopolitik.application.export_request import ExportContractError, ExportRequest
from ai_ngerti_geopolitik.application.ports import CancellationToken, ExportResult
from ai_ngerti_geopolitik.domain import ProjectState


class ExportJobError(RuntimeError):
    """Privacy-safe lifecycle failure (no media paths or FFmpeg stderr)."""


class ExportJobState(StrEnum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    READY = "READY"
    SUCCESS = "SUCCESS"
    CANCELLED = "CANCELLED"
    TIMED_OUT = "TIMED_OUT"
    STALE = "STALE"
    FAILED = "FAILED"


TERMINAL = frozenset(
    {
        ExportJobState.SUCCESS,
        ExportJobState.CANCELLED,
        ExportJobState.TIMED_OUT,
        ExportJobState.STALE,
        ExportJobState.FAILED,
    }
)


@dataclass(frozen=True, slots=True)
class ExportJobSnapshot:
    job_id: str
    request_id: str
    status: ExportJobState
    phase: str
    progress_percent: int | None
    error_code: str | None

    @property
    def terminal(self) -> bool:
        return self.status in TERMINAL


class StagedExportPort(Protocol):
    def render(
        self,
        state: ProjectState,
        request: ExportRequest,
        *,
        stage_path: Path,
        cancellation: CancellationToken,
    ) -> ExportResult: ...


class SafeExportPublisherPort(Protocol):
    def publish(self, stage_path: Path, request: ExportRequest, state: ProjectState) -> None: ...


class _Cancel:
    def __init__(self, timeout: float) -> None:
        self.event = Event()
        self.deadline = time.monotonic() + timeout

    @property
    def cancelled(self) -> bool:
        return self.event.is_set() or time.monotonic() >= self.deadline

    def cancel(self) -> None:
        self.event.set()


@dataclass(slots=True)
class _Job:
    request: ExportRequest
    original: ProjectState
    cancel: _Cancel
    status: ExportJobState = ExportJobState.QUEUED
    phase: str = "QUEUED"
    error: str | None = None
    workspace: Path | None = None
    staged: Path | None = None
    result: ExportResult | None = None
    receipt: PostflightReceipt | None = None


class ExportJobService:
    """Single off-UI-thread queue; only explicit accept() publishes output."""

    def __init__(
        self, worker: StagedExportPort, publisher: SafeExportPublisherPort,
        *, postflight: ExportPostflightPort
    ) -> None:
        self._worker = worker
        self._publisher = publisher
        self._postflight = postflight
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="ang-export")
        self._lock = Lock()
        self._jobs: dict[str, _Job] = {}
        self._active: str | None = None
        self._closed = False
        self._owner_thread = get_ident()

    def __enter__(self) -> ExportJobService:
        return self

    def __exit__(self, _type: object, _value: object, _traceback: object) -> None:
        self.shutdown(wait=True)

    @staticmethod
    def _view(job: _Job) -> ExportJobSnapshot:
        return ExportJobSnapshot(
            job.request.request_id,
            job.request.request_id,
            job.status,
            job.phase,
            100 if job.status is ExportJobState.SUCCESS else None,
            job.error,
        )

    def _get(self, job_id: str) -> _Job:
        try:
            return self._jobs[job_id]
        except KeyError:
            raise ExportJobError("UNKNOWN_EXPORT_JOB") from None

    def _clean_later(self, job: _Job) -> None:
        folder = job.workspace
        job.workspace = None
        job.staged = None
        if folder is not None:
            # Worker still owns cleanup if shutdown already began.
            with suppress(RuntimeError):
                self._executor.submit(shutil.rmtree, folder, True)

    def _stop(self, job: _Job, status: ExportJobState, reason: str) -> None:
        if job.status in TERMINAL:
            return
        ready = job.status is ExportJobState.READY
        job.cancel.cancel()
        job.status = status
        job.phase = status.value
        job.error = reason
        job.result = None
        job.receipt = None
        if ready:
            self._clean_later(job)
        if self._active == job.request.request_id:
            self._active = None

    def _expire(self, job: _Job) -> None:
        if time.monotonic() >= job.cancel.deadline and job.status not in TERMINAL:
            self._stop(job, ExportJobState.TIMED_OUT, "EXPORT_TIMEOUT")

    @staticmethod
    def _matches(job: _Job, state: ProjectState | None, session_id: str | None) -> bool:
        if state is None:
            return False
        try:
            job.request.assert_current(state, session_id)
        except ExportContractError:
            return False
        return True

    def submit(
        self,
        state: ProjectState,
        request: ExportRequest,
        *,
        session_id: str,
        timeout_seconds: float = 600.0,
    ) -> ExportJobSnapshot:
        if type(timeout_seconds) not in (float, int) or not (0.001 <= timeout_seconds <= 14400.0):
            raise ExportJobError("INVALID_EXPORT_TIMEOUT")
        try:
            request.assert_current(state, session_id)
        except ExportContractError:
            raise ExportJobError("STALE_EXPORT_REQUEST") from None
        with self._lock:
            if self._closed:
                raise ExportJobError("EXPORT_JOBS_CLOSED")
            if request.request_id in self._jobs:
                raise ExportJobError("DUPLICATE_EXPORT_JOB")
            if self._active is not None:
                raise ExportJobError("EXPORT_ALREADY_IN_PROGRESS")
            job = _Job(request, state, _Cancel(float(timeout_seconds)))
            self._jobs[request.request_id] = job
            self._active = request.request_id
            try:
                self._executor.submit(self._run, request.request_id)
            except RuntimeError:
                del self._jobs[request.request_id]
                self._active = None
                raise ExportJobError("EXPORT_WORKER_UNAVAILABLE") from None
            return self._view(job)

    def _run(self, job_id: str) -> None:
        with self._lock:
            job = self._get(job_id)
            self._expire(job)
            if job.status is not ExportJobState.QUEUED:
                return
            job.status = ExportJobState.RUNNING
            job.phase = "PREFLIGHT_AND_ENCODING"
        folder: Path | None = None
        retain = False
        try:
            if job.cancel.cancelled:
                return
            folder = Path(
                tempfile.mkdtemp(prefix=".ang-export-job-", dir=job.request.output_path.parent)
            )
            staged = folder / "render.mp4"
            with self._lock:
                if job.status is not ExportJobState.RUNNING:
                    return
                job.workspace = folder
            result = self._worker.render(
                job.original,
                job.request,
                stage_path=staged,
                cancellation=job.cancel,
            )
            if (
                result.output_path != staged
                or result.project_revision != job.request.project_revision
                or not staged.is_file()
                or staged.stat().st_size <= 0
            ):
                raise ExportJobError("INVALID_STAGED_EXPORT")
            with self._lock:
                self._expire(job)
                if job.status is not ExportJobState.RUNNING:
                    return
                job.phase = "POSTFLIGHT_VERIFYING"
            receipt = self._postflight.verify(
                staged, job.request, job.original, result, job.cancel
            )
            if not receipt.still_current(staged):
                raise ExportPostflightError(PostflightCode.STAGING_CHANGED)
            with self._lock:
                self._expire(job)
                if job.status is ExportJobState.RUNNING:
                    if job.cancel.cancelled:
                        self._stop(job, ExportJobState.CANCELLED, "EXPORT_CANCELLED")
                    else:
                        job.result = result
                        job.receipt = receipt
                        job.staged = staged
                        job.status = ExportJobState.READY
                        job.phase = "AWAITING_ACCEPTANCE"
                        retain = True
        except ExportPostflightError as error:
            with self._lock:
                self._expire(job)
                if job.status is ExportJobState.RUNNING:
                    self._stop(job, ExportJobState.FAILED, error.code.value)
        except Exception:  # noqa: BLE001 — never expose stderr, paths or secrets
            with self._lock:
                self._expire(job)
                if job.status is ExportJobState.RUNNING:
                    self._stop(
                        job,
                        ExportJobState.CANCELLED if job.cancel.cancelled else ExportJobState.FAILED,
                        "EXPORT_CANCELLED" if job.cancel.cancelled else "EXPORT_WORKER_FAILED",
                    )
        finally:
            if folder is not None and not retain:
                shutil.rmtree(folder, ignore_errors=True)
                with self._lock:
                    if job.workspace == folder:
                        job.workspace = None
                        job.staged = None

    def snapshot(
        self, job_id: str, *, state: ProjectState | None, session_id: str | None
    ) -> ExportJobSnapshot:
        with self._lock:
            job = self._get(job_id)
            self._expire(job)
            if job.status not in TERMINAL and (
                self._closed or not self._matches(job, state, session_id)
            ):
                self._stop(job, ExportJobState.STALE, "STALE_EXPORT_REQUEST")
            return self._view(job)

    def cancel(self, job_id: str) -> bool:
        with self._lock:
            job = self._get(job_id)
            self._expire(job)
            if job.status in TERMINAL:
                return False
            self._stop(job, ExportJobState.CANCELLED, "EXPORT_CANCELLED")
            return True

    def accept(
        self, job_id: str, *, state: ProjectState | None, session_id: str | None
    ) -> ExportResult:
        if get_ident() != self._owner_thread:
            raise ExportJobError("EXPORT_ACCEPT_OWNER_THREAD_ONLY")
        with self._lock:
            job = self._get(job_id)
            self._expire(job)
            if self._closed or not self._matches(job, state, session_id):
                if job.status is ExportJobState.READY:
                    self._stop(job, ExportJobState.STALE, "STALE_EXPORT_REQUEST")
                raise ExportJobError("STALE_EXPORT_REQUEST")
            if (
                job.status is not ExportJobState.READY
                or job.staged is None
                or job.result is None
                or job.receipt is None
            ):
                raise ExportJobError("EXPORT_NOT_READY")
            if not job.receipt.still_current(job.staged):
                self._stop(job, ExportJobState.FAILED, PostflightCode.STAGING_CHANGED.value)
                raise ExportJobError(PostflightCode.STAGING_CHANGED.value)
            assert state is not None
            try:
                self._publisher.publish(job.staged, job.request, state)
            except Exception:
                self._stop(job, ExportJobState.FAILED, "EXPORT_PUBLISH_FAILED")
                raise ExportJobError("EXPORT_PUBLISH_FAILED") from None
            result = ExportResult(
                job.result.project_revision,
                job.request.output_path,
                job.result.duration_frames,
                job.result.width,
                job.result.height,
                job.result.fps,
            )
            job.status = ExportJobState.SUCCESS
            job.phase = "PUBLISHED"
            job.result = None
            self._active = None
            self._clean_later(job)
            return result

    def shutdown(self, *, wait: bool = False) -> None:
        with self._lock:
            if self._closed:
                return
            self._closed = True
            for job in self._jobs.values():
                if job.status not in TERMINAL:
                    self._stop(job, ExportJobState.CANCELLED, "EXPORT_WINDOW_CLOSED")
            self._active = None
        self._executor.shutdown(wait=wait, cancel_futures=False)
