"""W8-008 real lifecycle, concurrency, cancel and stale-result fault gates."""

from __future__ import annotations

import hashlib
import threading
import time
from collections.abc import Iterator
from dataclasses import replace
from pathlib import Path

import pytest

from ai_ngerti_geopolitik.application.autosave_catalog import AutosaveCatalogService
from ai_ngerti_geopolitik.application.commands import CommandBatch, UpdateProjectSettingsCommand
from ai_ngerti_geopolitik.application.project_jobs import (
    ProjectJobError,
    ProjectJobState,
    ProjectJobToken,
    ReadOnlyProjectJobs,
)
from ai_ngerti_geopolitik.application.project_session import ProjectSession
from ai_ngerti_geopolitik.application.recovery import RecoveryChoice, RecoveryManager
from ai_ngerti_geopolitik.application.relink_scan import (
    RelinkScanError,
    RelinkScanJobService,
    ScanCancel,
    ScanState,
)
from ai_ngerti_geopolitik.application.validation import ValidationResult, ValidationService
from ai_ngerti_geopolitik.domain import ProjectState
from ai_ngerti_geopolitik.infrastructure.crash_marker import FileCrashMarkerStore
from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository


class PausedWork:
    def __init__(self) -> None:
        self.entered = threading.Event()
        self.release = threading.Event()

    def wait(self) -> None:
        self.entered.set()
        if not self.release.wait(timeout=8):
            raise AssertionError("background worker release timed out")


class PausedScanner:
    def __init__(self, gate: PausedWork) -> None:
        self.gate = gate

    def paths(
        self, root: Path, *, cancellation: ScanCancel, max_files: int, max_depth: int
    ) -> Iterator[Path]:
        del cancellation, max_files, max_depth
        self.gate.wait()
        yield root / "missing-file.mp4"


class NeverProbe:
    def probe(self, path: Path):
        raise AssertionError(f"probe must not be called: {path.name}")


def session(tmp_path: Path, project_id: str = "P-JOB") -> ProjectSession:
    result = ProjectSession(JsonProjectRepository())
    result.new_project(project_id, "Original project")
    result.save(tmp_path / (project_id + ".angproj"))
    assert result.session_id is not None
    return result


def edit(current: ProjectSession, width: int = 1440) -> None:
    current.execute(
        CommandBatch(
            batch_id=f"EDIT-{current.state.revision+1}",
            label="edit during background work",
            actor="manual",
            expected_revision=current.state.revision,
            commands=(UpdateProjectSettingsCommand(width, 1080, 30, "16:9"),),
        )
    )


def complete(
    jobs: ReadOnlyProjectJobs[ValidationResult], job_id: str, state: ProjectState,
    sid: str,
):
    until = time.monotonic() + 8
    while time.monotonic() < until:
        item = jobs.snapshot(job_id, state=state, session_id=sid)
        if item.state not in {ProjectJobState.QUEUED, ProjectJobState.RUNNING}:
            return item
        time.sleep(0.01)
    raise AssertionError("background job did not complete")


def test_session_identity_rotates_close_reopen_and_new(tmp_path: Path) -> None:
    current = session(tmp_path)
    original = current.session_id
    state = current.state
    path = current.current_path
    assert original is not None and path is not None
    current.close()
    assert current.session_id is None
    assert current.snapshot.project_id is None
    current.open_project(path)
    assert current.session_id and current.session_id != original
    assert current.state.semantic_hash() == state.semantic_hash()
    renewed = current.session_id
    current.new_project("P-OTHER", "Other project")
    assert current.session_id not in {original, renewed}
    current.close(discard_unsaved=True)
    assert current.session_id is None


def test_session_identity_rotates_on_recover_same_project(tmp_path: Path) -> None:
    current = session(tmp_path)
    old = current.session_id
    src = current.current_path
    assert src is not None
    snap = current.autosave()
    current.recover_snapshot(src, snap)
    assert current.session_id not in {old, None}
    assert current.dirty
    assert current.current_path == src


def test_token_rejects_same_revision_different_semantics_and_lifecycle(
    tmp_path: Path,
) -> None:
    current = session(tmp_path)
    sid = current.session_id
    assert sid is not None
    token = ProjectJobToken.capture(current.state, sid)
    assert not token.is_stale(current.state, sid)
    different = replace(current.state, name="same revision, different content")
    assert different.revision == current.state.revision
    assert token.is_stale(different, sid)
    assert token.is_stale(current.state.with_revision(current.state.revision+1), sid)
    assert token.is_stale(current.state, "wrong-session")
    assert token.is_stale(None, None)
    assert token.is_stale(ProjectState.create("P-OTHER", "Other", 30), sid)
    with pytest.raises(ProjectJobError, match="active"):
        ProjectJobToken.capture(current.state, " ")


def test_paused_validation_manual_edit_discards_stale_and_no_mutation(
    tmp_path: Path,
) -> None:
    current = session(tmp_path)
    sid = current.session_id
    assert sid is not None
    base = current.state
    gate = PausedWork()

    def work() -> ValidationResult:
        gate.wait()
        return ValidationService().validate(base)

    with ReadOnlyProjectJobs[ValidationResult]() as jobs:
        job = jobs.submit(base, session_id=sid, work=work)
        assert gate.entered.wait(timeout=8)
        edit(current)
        changed_hash = current.state.semantic_hash()
        assert jobs.snapshot(job.job_id, state=current.state, session_id=sid).state is ProjectJobState.STALE
        gate.release.set()
        with pytest.raises(ProjectJobError, match="stale"):
            jobs.resolve(job.job_id, state=current.state, session_id=sid)
        assert current.state.semantic_hash() == changed_hash
        assert current.dirty


def test_validation_close_reopen_identical_content_stale(tmp_path: Path) -> None:
    current = session(tmp_path)
    sid = current.session_id
    source = current.current_path
    assert sid is not None and source is not None
    old = current.state
    with ReadOnlyProjectJobs[ValidationResult]() as jobs:
        job = jobs.submit(
            old, session_id=sid, work=lambda: ValidationService().validate(old)
        )
        current.close()
        assert jobs.snapshot(job.job_id, state=None, session_id=None).state is ProjectJobState.STALE
        current.open_project(source)
        assert current.state.semantic_hash() == old.semantic_hash()
        assert jobs.snapshot(
            job.job_id, state=current.state, session_id=current.session_id
        ).state is ProjectJobState.STALE
        with pytest.raises(ProjectJobError, match="stale"):
            jobs.resolve(job.job_id, state=current.state, session_id=current.session_id)


def test_background_cancel_late_result_never_publishes(tmp_path: Path) -> None:
    current = session(tmp_path)
    sid = current.session_id
    assert sid is not None
    gate = PausedWork()
    base = current.state

    def work() -> ValidationResult:
        gate.wait()
        return ValidationService().validate(base)

    with ReadOnlyProjectJobs[ValidationResult]() as jobs:
        job = jobs.submit(base, session_id=sid, work=work)
        assert gate.entered.wait(timeout=8)
        jobs.cancel(job.job_id)
        gate.release.set()
        assert jobs.snapshot(job.job_id, state=base, session_id=sid).state is ProjectJobState.CANCELLED
        with pytest.raises(ProjectJobError, match="eligible"):
            jobs.resolve(job.job_id, state=base, session_id=sid)
        assert current.state.semantic_hash() == base.semantic_hash()


def test_completed_validation_result_bound_to_session(tmp_path: Path) -> None:
    current = session(tmp_path)
    sid = current.session_id
    assert sid is not None
    base = current.state
    with ReadOnlyProjectJobs[ValidationResult]() as jobs:
        submitted = jobs.submit(
            base, session_id=sid, work=lambda: ValidationService().validate(base)
        )
        done = complete(jobs, submitted.job_id, base, sid)
        assert done.state is ProjectJobState.SUCCESS
        accepted = jobs.resolve(submitted.job_id, state=base, session_id=sid)
        assert accepted.project_id == base.project_id
        assert accepted.project_revision == base.revision
        assert not accepted.is_stale(current.state)
        jobs.cancel(submitted.job_id)
        with pytest.raises(ProjectJobError):
            jobs.resolve(submitted.job_id, state=base, session_id=sid)


def test_failing_background_job_leaks_no_private_details(tmp_path: Path) -> None:
    current = session(tmp_path)
    sid = current.session_id
    assert sid is not None
    with ReadOnlyProjectJobs[str]() as jobs:
        def unsafe() -> str:
            raise RuntimeError("API-KEY-SECRET C:\\Users\\private\\file.mp4")
        job = jobs.submit(current.state, session_id=sid, work=unsafe)
        end = time.monotonic()+8
        while jobs.snapshot(job.job_id, state=current.state, session_id=sid).state in {
            ProjectJobState.QUEUED, ProjectJobState.RUNNING
        }:
            assert time.monotonic()<end
            time.sleep(0.01)
        status = jobs.snapshot(job.job_id, state=current.state, session_id=sid)
        assert status.state is ProjectJobState.FAILED
        assert status.result is None
        assert "SECRET" not in repr(status)


def test_relink_paused_scan_drops_result_after_revision_edit(tmp_path: Path) -> None:
    current = session(tmp_path)
    sid = current.session_id
    assert sid is not None
    gate = PausedWork()
    with RelinkScanJobService(PausedScanner(gate), NeverProbe()) as scans:
        job = scans.submit(current.state, tmp_path, session_id=sid)
        assert gate.entered.wait(timeout=8)
        edit(current)
        before = current.state.semantic_hash()
        gate.release.set()
        result = scans.snapshot(job.job_id, state=current.state, session_id=sid)
        assert result.state is ScanState.STALE
        assert result.candidates == ()
        with pytest.raises(RelinkScanError, match="stale"):
            scans.apply_selected(job.job_id, current, session_id=sid, selections=())
        assert current.state.semantic_hash() == before


def test_relink_close_reopen_other_project_no_result_leak(tmp_path: Path) -> None:
    current = session(tmp_path)
    sid = current.session_id
    assert sid is not None
    gate = PausedWork()
    with RelinkScanJobService(PausedScanner(gate), NeverProbe()) as scans:
        job = scans.submit(current.state, tmp_path, session_id=sid)
        assert gate.entered.wait(timeout=8)
        current.close()
        assert scans.snapshot(job.job_id, state=None, session_id=None).state is ScanState.STALE
        current.new_project("P-OTHER", "Other project")
        assert scans.snapshot(
            job.job_id, state=current.state, session_id=current.session_id
        ).state is ScanState.STALE
        scans.cancel(job.job_id)
        gate.release.set()
        assert current.state.project_id == "P-OTHER"


def test_recovery_inspection_result_stale_after_close_reopen_same_project(
    tmp_path: Path,
) -> None:
    current = session(tmp_path)
    source = current.current_path
    sid = current.session_id
    assert sid is not None and source is not None
    repo = current.repository
    assert isinstance(repo, JsonProjectRepository)
    recovery = RecoveryManager(
        repo, AutosaveCatalogService(repo), FileCrashMarkerStore()
    )
    begin = recovery.decide(
        recovery.inspect(source), RecoveryChoice.OPEN_SOURCE,
        ProjectSession(repo)
    )
    assert begin.active_marker is not None
    snapshot = AutosaveCatalogService(repo).create_snapshot(
        current.state.with_revision(4), source.parent / ".ang-autosave", source_path=source
    )
    gate = PausedWork()
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()

    def inspect():
        gate.wait()
        return recovery.inspect(source)

    with ReadOnlyProjectJobs[object]() as jobs:
        job = jobs.submit(current.state, session_id=sid, work=inspect)
        assert gate.entered.wait(timeout=8)
        current.close()
        current.open_project(source)
        gate.release.set()
        with pytest.raises(ProjectJobError, match="stale"):
            jobs.resolve(
                job.job_id, state=current.state, session_id=current.session_id
            )
        assert snapshot.is_file()
        assert current.state.revision == 0
        assert hashlib.sha256(source.read_bytes()).hexdigest() == source_hash
        assert not current.dirty


def test_recovery_cancellation_zero_mutation(tmp_path: Path) -> None:
    current = session(tmp_path)
    source = current.current_path
    sid = current.session_id
    assert sid is not None and source is not None
    repo = current.repository
    assert isinstance(repo, JsonProjectRepository)
    recovery = RecoveryManager(
        repo, AutosaveCatalogService(repo), FileCrashMarkerStore()
    )
    gate = PausedWork()
    before = source.read_bytes()

    def work():
        gate.wait()
        return recovery.inspect(source)

    with ReadOnlyProjectJobs[object]() as jobs:
        job = jobs.submit(current.state, session_id=sid, work=work)
        assert gate.entered.wait(timeout=8)
        jobs.cancel(job.job_id)
        gate.release.set()
        assert jobs.snapshot(
            job.job_id, state=current.state, session_id=sid
        ).state is ProjectJobState.CANCELLED
        assert source.read_bytes() == before
        with pytest.raises(ProjectJobError):
            jobs.resolve(job.job_id, state=current.state, session_id=sid)
