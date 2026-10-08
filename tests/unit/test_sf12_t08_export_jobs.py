"""T08 parallel lifecycle proofs: queued/run, stale, cancel, deadline and safe commit."""

from __future__ import annotations

import threading
import time
from dataclasses import replace
from pathlib import Path

import pytest

from ai_ngerti_geopolitik.application.export_jobs import (
    ExportJobError,
    ExportJobService,
    ExportJobState,
)
from ai_ngerti_geopolitik.application.export_request import ExportRequest
from ai_ngerti_geopolitik.application.ports import ExportResult
from ai_ngerti_geopolitik.domain import Asset, Clip, FrameTime, ProjectState, Track
from ai_ngerti_geopolitik.infrastructure.export_job_adapters import AtomicExportPublisher


class FakeRender:
    def __init__(self, *, paused: bool = False, fail: bool = False, cooperative: bool = True) -> None:
        self.entered = threading.Event()
        self.release = threading.Event()
        if not paused:
            self.release.set()
        self.fail = fail
        self.cooperative = cooperative
        self.calls = 0
        self.thread_ids: list[int] = []

    def render(self, state, request, *, stage_path, cancellation):
        self.calls += 1
        self.thread_ids.append(threading.get_ident())
        self.entered.set()
        while not self.release.wait(0.01):
            if self.cooperative and cancellation.cancelled:
                raise RuntimeError("private C:\\Users\\Someone\\secret.mp4")
        stage_path.write_bytes(b"qualified fixture only")
        if self.fail:
            raise RuntimeError("private C:\\Users\\Someone\\secret.mp4")
        return ExportResult(state.revision, stage_path, 30, 1920, 1080, 30)


def _case(tmp_path: Path) -> tuple[ProjectState, ExportRequest]:
    source = tmp_path / "source.mp4"
    source.write_bytes(b"untouched source")
    asset = Asset(
        "A001", str(source), "video", FrameTime(30, 30),
        1920, 1080, True, "a" * 64
    )
    clip = Clip("C001", "A001", FrameTime(0, 30), FrameTime(0, 30), FrameTime(30, 30))
    state = replace(
        ProjectState.create("P001", "T08"),
        assets=(asset,), tracks=(Track("V1", "video", 0, (clip,)),),
    )
    request = ExportRequest.for_project(
        state,
        session_id="T08-session",
        request_id="T08-request",
        output_path=tmp_path / "final.mp4",
    )
    return state, request


def _wait(
    jobs: ExportJobService,
    request: ExportRequest,
    state: ProjectState,
    wanted: ExportJobState,
) -> None:
    end = time.monotonic() + 8
    while time.monotonic() < end:
        snap = jobs.snapshot(
            request.request_id, state=state, session_id="T08-session"
        )
        if snap.status is wanted:
            return
        if snap.terminal and snap.status is not wanted:
            raise AssertionError(f"unexpected worker state: {snap.status}")
        time.sleep(0.01)
    raise AssertionError(f"worker did not reach {wanted}")


def _no_workspaces(tmp_path: Path) -> None:
    end = time.monotonic() + 8
    while time.monotonic() < end:
        if not list(tmp_path.glob(".ang-export-job-*")):
            return
        time.sleep(0.01)
    raise AssertionError("temporary render files remained")


def test_accept_is_owner_thread_only_and_does_not_publish_before_accept(
    tmp_path: Path,
) -> None:
    state, request = _case(tmp_path)
    fake = FakeRender()
    before = state.semantic_json(include_revision=True)
    with ExportJobService(fake, AtomicExportPublisher()) as jobs:
        queued = jobs.submit(state, request, session_id="T08-session")
        assert queued.status in {ExportJobState.QUEUED, ExportJobState.RUNNING}
        _wait(jobs, request, state, ExportJobState.READY)
        ready = jobs.snapshot(request.request_id, state=state, session_id="T08-session")
        assert ready.progress_percent is None
        assert ready.phase == "AWAITING_ACCEPTANCE"
        assert not request.output_path.exists()
        assert fake.thread_ids[0] != threading.get_ident()
        errors: list[str] = []

        def non_owner_attempt() -> None:
            try:
                jobs.accept(request.request_id, state=state, session_id="T08-session")
            except ExportJobError as exc:
                errors.append(str(exc))

        thread = threading.Thread(target=non_owner_attempt)
        thread.start()
        thread.join(timeout=4)
        assert errors == ["EXPORT_ACCEPT_OWNER_THREAD_ONLY"]
        assert not request.output_path.exists()
        result = jobs.accept(request.request_id, state=state, session_id="T08-session")
        assert result.output_path.read_bytes() == b"qualified fixture only"
        done = jobs.snapshot(request.request_id, state=state, session_id="T08-session")
        assert done.status is ExportJobState.SUCCESS
        assert done.progress_percent == 100
        assert not jobs.cancel(request.request_id)
        assert state.semantic_json(include_revision=True) == before
    _no_workspaces(tmp_path)


def test_double_click_and_duplicate_id_are_rejected(tmp_path: Path) -> None:
    state, request = _case(tmp_path)
    fake = FakeRender(paused=True)
    with ExportJobService(fake, AtomicExportPublisher()) as jobs:
        jobs.submit(state, request, session_id="T08-session")
        assert fake.entered.wait(4)
        with pytest.raises(ExportJobError, match="DUPLICATE_EXPORT_JOB"):
            jobs.submit(state, request, session_id="T08-session")
        other = replace(request, request_id="another-request")
        with pytest.raises(ExportJobError, match="EXPORT_ALREADY_IN_PROGRESS"):
            jobs.submit(state, other, session_id="T08-session")
        assert jobs.cancel(request.request_id)
        fake.release.set()
        assert not request.output_path.exists()
    _no_workspaces(tmp_path)


def test_revision_and_session_close_reject_ready_result(tmp_path: Path) -> None:
    state, request = _case(tmp_path)
    with ExportJobService(FakeRender(), AtomicExportPublisher()) as jobs:
        jobs.submit(state, request, session_id="T08-session")
        _wait(jobs, request, state, ExportJobState.READY)
        edited = replace(state, name="same revision different semantics")
        assert jobs.snapshot(
            request.request_id, state=edited, session_id="T08-session"
        ).status is ExportJobState.STALE
        with pytest.raises(ExportJobError):
            jobs.accept(request.request_id, state=edited, session_id="T08-session")
        assert not request.output_path.exists()
    _no_workspaces(tmp_path)

    state2, req2 = _case(tmp_path)
    with ExportJobService(FakeRender(), AtomicExportPublisher()) as jobs:
        jobs.submit(state2, req2, session_id="T08-session")
        _wait(jobs, req2, state2, ExportJobState.READY)
        snap = jobs.snapshot(req2.request_id, state=None, session_id=None)
        assert snap.status is ExportJobState.STALE
        assert not req2.output_path.exists()
    _no_workspaces(tmp_path)


def test_timeout_aborts_paused_worker_without_publishing(tmp_path: Path) -> None:
    state, request = _case(tmp_path)
    fake = FakeRender(paused=True)
    with ExportJobService(fake, AtomicExportPublisher()) as jobs:
        jobs.submit(state, request, session_id="T08-session", timeout_seconds=0.08)
        assert fake.entered.wait(4)
        _wait(jobs, request, state, ExportJobState.TIMED_OUT)
        fake.release.set()
        with pytest.raises(ExportJobError, match="EXPORT_NOT_READY"):
            jobs.accept(request.request_id, state=state, session_id="T08-session")
        assert not request.output_path.exists()
    _no_workspaces(tmp_path)


def test_cancel_while_worker_ignores_cancellation_never_publishes(tmp_path: Path) -> None:
    state, request = _case(tmp_path)
    fake = FakeRender(paused=True, cooperative=False)
    jobs = ExportJobService(fake, AtomicExportPublisher())
    jobs.submit(state, request, session_id="T08-session")
    assert fake.entered.wait(4)
    started = time.monotonic()
    jobs.shutdown(wait=False)
    assert time.monotonic() - started < 0.5
    assert jobs.snapshot(request.request_id, state=state, session_id="T08-session").status is (
        ExportJobState.CANCELLED
    )
    fake.release.set()
    jobs.shutdown(wait=True)
    _no_workspaces(tmp_path)
    assert not request.output_path.exists()


def test_cancel_ready_cleans_staging_and_retains_source(tmp_path: Path) -> None:
    state, request = _case(tmp_path)
    with ExportJobService(FakeRender(), AtomicExportPublisher()) as jobs:
        jobs.submit(state, request, session_id="T08-session")
        _wait(jobs, request, state, ExportJobState.READY)
        assert jobs.cancel(request.request_id)
        assert not jobs.cancel(request.request_id)
        assert not request.output_path.exists()
        with pytest.raises(ExportJobError, match="EXPORT_NOT_READY"):
            jobs.accept(request.request_id, state=state, session_id="T08-session")
    _no_workspaces(tmp_path)
    assert (tmp_path / "source.mp4").read_bytes() == b"untouched source"


def test_worker_failure_leaks_no_private_path(tmp_path: Path) -> None:
    state, request = _case(tmp_path)
    with ExportJobService(FakeRender(fail=True), AtomicExportPublisher()) as jobs:
        jobs.submit(state, request, session_id="T08-session")
        _wait(jobs, request, state, ExportJobState.FAILED)
        snap = jobs.snapshot(request.request_id, state=state, session_id="T08-session")
        assert snap.error_code == "EXPORT_WORKER_FAILED"
        assert "Users" not in repr(snap) and "secret" not in repr(snap)
    _no_workspaces(tmp_path)
    assert not request.output_path.exists()


def test_output_race_and_protected_source_are_never_overwritten(tmp_path: Path) -> None:
    state, request = _case(tmp_path)
    with ExportJobService(FakeRender(), AtomicExportPublisher()) as jobs:
        jobs.submit(state, request, session_id="T08-session")
        _wait(jobs, request, state, ExportJobState.READY)
        request.output_path.write_bytes(b"other writer")
        with pytest.raises(ExportJobError, match="EXPORT_PUBLISH_FAILED"):
            jobs.accept(request.request_id, state=state, session_id="T08-session")
        assert request.output_path.read_bytes() == b"other writer"
    _no_workspaces(tmp_path)

    source = tmp_path / "source.mp4"
    colliding = replace(request, output_path=source)
    with ExportJobService(FakeRender(), AtomicExportPublisher()) as jobs:
        jobs.submit(state, colliding, session_id="T08-session")
        _wait(jobs, colliding, state, ExportJobState.READY)
        with pytest.raises(ExportJobError, match="EXPORT_PUBLISH_FAILED"):
            jobs.accept(colliding.request_id, state=state, session_id="T08-session")
        assert source.read_bytes() == b"untouched source"
    _no_workspaces(tmp_path)


def test_invalid_timeout_and_closed_service_rejected(tmp_path: Path) -> None:
    state, request = _case(tmp_path)
    jobs = ExportJobService(FakeRender(), AtomicExportPublisher())
    with pytest.raises(ExportJobError, match="INVALID_EXPORT_TIMEOUT"):
        jobs.submit(state, request, session_id="T08-session", timeout_seconds=-1)
    jobs.shutdown()
    with pytest.raises(ExportJobError, match="EXPORT_JOBS_CLOSED"):
        jobs.submit(state, request, session_id="T08-session")
