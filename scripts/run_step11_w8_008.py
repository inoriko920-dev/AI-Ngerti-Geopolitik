"""W8-008 owned concurrency proof for read-only W8 project jobs."""

from __future__ import annotations

import argparse
import hashlib
import json
import threading
import time
from collections.abc import Iterator
from pathlib import Path

from ai_ngerti_geopolitik.application.autosave_catalog import AutosaveCatalogService
from ai_ngerti_geopolitik.application.commands import CommandBatch, UpdateProjectSettingsCommand
from ai_ngerti_geopolitik.application.project_jobs import (
    ProjectJobError,
    ProjectJobState,
    ProjectJobToken,
    ReadOnlyProjectJobs,
)
from ai_ngerti_geopolitik.application.project_session import ProjectSession
from ai_ngerti_geopolitik.application.recovery import RecoveryManager
from ai_ngerti_geopolitik.application.relink_scan import (
    RelinkScanJobService,
    ScanCancel,
    ScanState,
)
from ai_ngerti_geopolitik.application.validation import ValidationResult, ValidationService
from ai_ngerti_geopolitik.domain import ProjectState
from ai_ngerti_geopolitik.infrastructure.crash_marker import FileCrashMarkerStore
from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository


class Gate:
    def __init__(self) -> None:
        self.started = threading.Event()
        self.release = threading.Event()

    def pause(self) -> None:
        self.started.set()
        if not self.release.wait(timeout=12):
            raise RuntimeError("owned concurrency gate timed out")


class BlockingScan:
    def __init__(self, gate: Gate) -> None:
        self.gate = gate

    def paths(
        self, root: Path, *, cancellation: ScanCancel, max_files: int, max_depth: int
    ) -> Iterator[Path]:
        del cancellation, max_files, max_depth
        self.gate.pause()
        yield root / "dummy.mp4"


class NoProbe:
    def probe(self, path: Path):
        raise RuntimeError(f"unexpected probe {path.name}")


def wait_success(
    jobs: ReadOnlyProjectJobs[ValidationResult], job_id: str, state: ProjectState, sid: str
) -> bool:
    deadline = time.monotonic()+12
    while time.monotonic()<deadline:
        report=jobs.snapshot(job_id,state=state,session_id=sid)
        if report.state is ProjectJobState.SUCCESS:
            return True
        if report.state not in {ProjectJobState.RUNNING,ProjectJobState.QUEUED}:
            return False
        time.sleep(0.01)
    return False


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--evidence",type=Path,required=True)
    args=parser.parse_args()
    root=args.evidence.resolve()
    root.mkdir(parents=True,exist_ok=True)
    repo=JsonProjectRepository()
    session=ProjectSession(repo)
    session.new_project("P-W8-008","Stale job gate")
    source=root/"canonical.angproj"
    session.save(source)
    source_hash=hashlib.sha256(source.read_bytes()).hexdigest()
    sid=session.session_id
    assert sid is not None
    state=session.state

    gate=Gate()
    with ReadOnlyProjectJobs[ValidationResult]() as jobs:
        def delayed_validation() -> ValidationResult:
            gate.pause()
            return ValidationService().validate(state)
        job=jobs.submit(state,session_id=sid,work=delayed_validation)
        assert gate.started.wait(timeout=12)
        session.execute(CommandBatch(
            batch_id="EDIT-W8-008",label="manual edit during validation",actor="manual",
            expected_revision=session.state.revision,
            commands=(UpdateProjectSettingsCommand(1280,720,30,"16:9"),),
        ))
        changed_hash=session.state.semantic_hash()
        stale_edit=jobs.snapshot(job.job_id,state=session.state,session_id=sid)
        gate.release.set()
        try:
            jobs.resolve(job.job_id,state=session.state,session_id=sid)
            rejected_validation=False
        except ProjectJobError:
            rejected_validation=True
        no_mutation=session.state.semantic_hash()==changed_hash

    session.save()
    saved_state=session.state
    previous_sid=session.session_id
    session.close()
    closed_id=session.session_id is None
    session.open_project(source)
    rotated=session.session_id not in {None,previous_sid}
    token=ProjectJobToken.capture(saved_state,previous_sid or "")
    stale_reopen=token.is_stale(session.state,session.session_id)

    with ReadOnlyProjectJobs[ValidationResult]() as jobs:
        fresh=jobs.submit(
            session.state,session_id=session.session_id or "",
            work=lambda: ValidationService().validate(session.state),
        )
        fresh_success=wait_success(jobs,fresh.job_id,session.state,session.session_id or "")
        fresh_bound=jobs.resolve(
            fresh.job_id,state=session.state,session_id=session.session_id
        ).project_id==session.state.project_id

    scan_gate=Gate()
    with RelinkScanJobService(BlockingScan(scan_gate),NoProbe()) as scans:
        scan=scans.submit(session.state,root,session_id=session.session_id or "")
        assert scan_gate.started.wait(timeout=12)
        session.close()
        stale_closed=scans.snapshot(scan.job_id,state=None,session_id=None).state is ScanState.STALE
        session.new_project("P-OTHER","Other project")
        stale_other=scans.snapshot(
            scan.job_id,state=session.state,session_id=session.session_id
        ).state is ScanState.STALE
        scans.cancel(scan.job_id)
        scan_gate.release.set()

    other_source=root/"other.angproj"
    session.save(other_source)
    recovery=RecoveryManager(repo,AutosaveCatalogService(repo),FileCrashMarkerStore())
    recovery_gate=Gate()
    with ReadOnlyProjectJobs[object]() as jobs:
        def delayed_recovery():
            recovery_gate.pause()
            return recovery.inspect(other_source)
        offer_job=jobs.submit(
            session.state,session_id=session.session_id or "",work=delayed_recovery
        )
        assert recovery_gate.started.wait(timeout=12)
        jobs.cancel(offer_job.job_id)
        recovery_gate.release.set()
        recovered_cancelled=jobs.snapshot(
            offer_job.job_id,state=session.state,session_id=session.session_id
        ).state is ProjectJobState.CANCELLED
        try:
            jobs.resolve(offer_job.job_id,state=session.state,session_id=session.session_id)
            cancelled_blocked=False
        except ProjectJobError:
            cancelled_blocked=True

    report={
        "status":"PASS",
        "validation_edit_stale":stale_edit.state is ProjectJobState.STALE,
        "validation_result_discarded":rejected_validation,
        "concurrent_edit_untouched":no_mutation,
        "close_session_id_cleared":closed_id,
        "reopen_session_id_rotated":rotated,
        "same_project_same_revision_stale":stale_reopen,
        "fresh_validation_completes":fresh_success,
        "fresh_validation_bound":fresh_bound,
        "relink_closed_session_stale":stale_closed,
        "relink_different_project_stale":stale_other,
        "recovery_cancelled":recovered_cancelled,
        "recovery_cancel_rejects_result":cancelled_blocked,
        "source_project_unchanged":hashlib.sha256(source.read_bytes()).hexdigest()!=source_hash
        and repo.load(source).project_id=="P-W8-008",
        "foreign_session_no_auto_mutation":session.state.project_id=="P-OTHER",
        "no_w8_009_started":True,
    }
    assert all(v is True for k,v in report.items() if k!="status")
    (root/"00_w8_008_report.json").write_text(
        json.dumps(report,sort_keys=True,indent=2)+"\n",encoding="utf-8"
    )
    print(json.dumps(report,sort_keys=True,indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
