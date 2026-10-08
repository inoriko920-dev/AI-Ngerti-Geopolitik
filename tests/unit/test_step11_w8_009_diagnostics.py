"""W8-009 structured diagnostics and redacted asynchronous ZIP regression gates."""

from __future__ import annotations

import hashlib
import json
import time
import zipfile
from pathlib import Path
from threading import Event

import pytest

from ai_ngerti_geopolitik.application.diagnostic_bundle import (
    DiagnosticBundleJobService,
    DiagnosticJobState,
    safe_bundle_payload,
)
from ai_ngerti_geopolitik.application.diagnostics import (
    DiagnosticCode,
    DiagnosticError,
    DiagnosticErrorCode,
    DiagnosticLedger,
    DiagnosticStatus,
)
from ai_ngerti_geopolitik.application.persistence_failure import (
    PersistenceError,
    PersistenceStage,
)
from ai_ngerti_geopolitik.application.validation import (
    ValidationAction,
    ValidationIssue,
    ValidationIssueCode,
    ValidationResult,
    ValidationScope,
    ValidationSeverity,
)
from ai_ngerti_geopolitik.infrastructure.diagnostic_bundle import LocalDiagnosticZipWriter


def await_job(service: DiagnosticBundleJobService, job_id: str):
    end = time.monotonic() + 10
    while time.monotonic() < end:
        outcome = service.snapshot(job_id)
        if outcome.state not in {DiagnosticJobState.QUEUED, DiagnosticJobState.RUNNING}:
            return outcome
        time.sleep(0.01)
    raise AssertionError("diagnostic worker timeout")


def private_issue(secret: str) -> ValidationResult:
    issue = ValidationIssue(
        ValidationIssueCode.MEDIA_FILE_MISSING,
        ValidationSeverity.BLOCKER,
        ValidationScope.MEDIA,
        "Sensitive token: " + secret,
        "Raw path C:\\Users\\Private\\story.txt and API credential " + secret,
        ("A001", "id-" + secret),
        ValidationAction.RELINK_MEDIA,
        3,
    )
    return ValidationResult("private-project-" + secret, 3, "f" * 64, (issue,))


def ledger_with_private_source(secret: str) -> DiagnosticLedger:
    log = DiagnosticLedger()
    log.record(DiagnosticCode.PROJECT_OPEN, DiagnosticStatus.SUCCESS)
    log.record_validation(private_issue(secret))
    try:
        raise OSError(f"private token {secret}; C:\\Users\\Private\\story.txt")
    except OSError as failure:
        error = PersistenceError(PersistenceStage.TEMP_WRITE)
        error.__cause__ = failure
        log.record_save_failure(error)
    return log


def test_deterministic_manifest_two_archives_and_no_private_bytes(tmp_path: Path) -> None:
    secret = "super-private-test-token"
    log = ledger_with_private_source(secret)
    manifest, events = safe_bundle_payload(log.snapshot())
    assert manifest == safe_bundle_payload(log.snapshot())[0]
    with zipfile.ZipFile(tmp_path / "one.zip", "w") as _unused:
        pass
    writer = LocalDiagnosticZipWriter()
    writer.write_bundle(tmp_path / "a.zip", manifest=manifest, events=events, cancel=Event())
    writer.write_bundle(tmp_path / "b.zip", manifest=manifest, events=events, cancel=Event())
    first = (tmp_path / "a.zip").read_bytes()
    assert first == (tmp_path / "b.zip").read_bytes()
    assert secret.encode() not in first
    assert b"Private" not in first and b"story.txt" not in first
    assert b"private-project" not in first and b"A001" not in first
    with zipfile.ZipFile(tmp_path / "a.zip") as archive:
        assert archive.namelist() == ["manifest.json", "events.json"]
        meta = json.loads(archive.read("manifest.json"))
        event_items = json.loads(archive.read("events.json"))
    assert meta["redaction"] == "STRICT_ALLOWLIST"
    assert meta["event_count"] == 3
    assert meta["files"][0]["sha256"] == hashlib.sha256(events).hexdigest()
    assert event_items["events"][1]["count"] == 1
    assert event_items["events"][2]["persistence_stage"] == "temp_write"


def test_invalid_input_does_not_capture_string_payload() -> None:
    log = DiagnosticLedger()
    with pytest.raises(DiagnosticError) as caught:
        log.record(DiagnosticCode.PROJECT_OPEN, "secret-string")  # type: ignore[arg-type]
    assert caught.value.code is DiagnosticErrorCode.INVALID_INPUT
    with pytest.raises(DiagnosticError):
        log.record(DiagnosticCode.PROJECT_SAVE, DiagnosticStatus.INFO, count=100000)
    with pytest.raises(DiagnosticError):
        log.record("C:\\Users\\Private\\secret", DiagnosticStatus.INFO)  # type: ignore[arg-type]
    with pytest.raises(DiagnosticError):
        DiagnosticLedger(limit=257)
    assert log.snapshot().events == ()


def test_bounded_ledger_drops_old_records_and_snapshot_is_immutable() -> None:
    log = DiagnosticLedger(limit=2)
    for _ in range(5):
        log.record(DiagnosticCode.RELINK_SCAN, DiagnosticStatus.SUCCESS)
    snapshot = log.snapshot()
    assert [item.sequence for item in snapshot.events] == [4, 5]
    assert snapshot.dropped_count == 3
    log.record(DiagnosticCode.EXPORT_JOB, DiagnosticStatus.CANCELLED)
    assert snapshot.events[0].sequence == 4
    assert log.snapshot().dropped_count == 4


def test_worker_result_and_snapshot_isolation(tmp_path: Path) -> None:
    log = DiagnosticLedger()
    log.record(DiagnosticCode.PROJECT_OPEN, DiagnosticStatus.INFO)
    writer = LocalDiagnosticZipWriter()
    with DiagnosticBundleJobService(writer) as service:
        target = tmp_path / "support.zip"
        job = service.submit(target, log)
        # Mutating the ledger later must not leak into already-captured payload.
        log.record(DiagnosticCode.EXPORT_JOB, DiagnosticStatus.FAILED)
        state = await_job(service, job.job_id)
        assert state.state is DiagnosticJobState.SUCCESS
        assert state.event_count == 1
        assert target.is_file()
        with zipfile.ZipFile(target) as archive:
            items = json.loads(archive.read("events.json"))["events"]
        assert len(items) == 1


class PausedWriter:
    def __init__(self) -> None:
        self.started = Event()
        self.release = Event()

    def write_bundle(self, target: Path, *, manifest: bytes, events: bytes, cancel: Event) -> None:
        self.started.set()
        self.release.wait(timeout=5)
        LocalDiagnosticZipWriter().write_bundle(
            target, manifest=manifest, events=events, cancel=cancel
        )


def test_cancelled_job_never_publishes_archive(tmp_path: Path) -> None:
    writer = PausedWriter()
    log = DiagnosticLedger()
    log.record(DiagnosticCode.PROJECT_SAVE, DiagnosticStatus.INFO)
    target = tmp_path / "cancel.zip"
    with DiagnosticBundleJobService(writer) as service:
        job = service.submit(target, log)
        assert writer.started.wait(timeout=5)
        service.cancel(job.job_id)
        writer.release.set()
        status = await_job(service, job.job_id)
        assert status.state is DiagnosticJobState.CANCELLED
        assert not target.exists()


def test_existing_output_is_not_overwritten(tmp_path: Path) -> None:
    log = DiagnosticLedger()
    log.record(DiagnosticCode.PROJECT_OPEN, DiagnosticStatus.INFO)
    target = tmp_path / "existing.zip"
    target.write_bytes(b"existing-user-output")
    with DiagnosticBundleJobService(LocalDiagnosticZipWriter()) as service:
        job = service.submit(target, log)
        status = await_job(service, job.job_id)
        assert status.state is DiagnosticJobState.FAILED
        assert status.error_code is DiagnosticErrorCode.OUTPUT_EXISTS
        assert target.read_bytes() == b"existing-user-output"


def test_bad_extension_and_symlink_fail_closed(tmp_path: Path) -> None:
    log = DiagnosticLedger()
    with DiagnosticBundleJobService(LocalDiagnosticZipWriter()) as service:
        with pytest.raises(DiagnosticError):
            service.submit(tmp_path / "project.angproj", log)
        job = service.submit(tmp_path / "missing.zip", log)
        assert await_job(service, job.job_id).state is DiagnosticJobState.SUCCESS
        target = tmp_path / "linked.zip"
        try:
            target.symlink_to(tmp_path / "missing.zip")
        except (OSError, NotImplementedError):
            return
        another = service.submit(target, log)
        assert await_job(service, another.job_id).error_code is DiagnosticErrorCode.INVALID_INPUT


def test_output_write_failure_leaves_no_archive_or_owned_temp(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    original = LocalDiagnosticZipWriter.write_bundle

    def broken(
        self: LocalDiagnosticZipWriter,
        target: Path,
        *,
        manifest: bytes,
        events: bytes,
        cancel: Event,
    ) -> None:
        raise OSError("private C:\\Users\\owner\\api-key.txt")

    monkeypatch.setattr(LocalDiagnosticZipWriter, "write_bundle", broken)
    with DiagnosticBundleJobService(LocalDiagnosticZipWriter()) as service:
        job = service.submit(tmp_path / "fail.zip", DiagnosticLedger())
        status = await_job(service, job.job_id)
        assert status.error_code is DiagnosticErrorCode.OUTPUT_UNAVAILABLE
        assert not (tmp_path / "fail.zip").exists()
        assert not list(tmp_path.glob(".ang-diagnostics-*.tmp"))
    monkeypatch.setattr(LocalDiagnosticZipWriter, "write_bundle", original)


def test_archive_is_small_with_maximum_256_events() -> None:
    log = DiagnosticLedger(limit=256)
    for i in range(10000):
        log.record(DiagnosticCode.VALIDATION_RUN, DiagnosticStatus.INFO, count=i % 3)
    manifest, events = safe_bundle_payload(log.snapshot())
    assert len(manifest) + len(events) < 128 * 1024
    assert b"9744" in manifest  # dropped_count


def test_unknown_job_is_typed(tmp_path: Path) -> None:
    with DiagnosticBundleJobService(LocalDiagnosticZipWriter()) as service:
        with pytest.raises(DiagnosticError) as exc:
            service.snapshot("nonexistent")
        assert exc.value.code is DiagnosticErrorCode.UNKNOWN_JOB
        with pytest.raises(DiagnosticError):
            service.cancel("nonexistent")


def test_bad_snapshot_schema_rejected() -> None:
    log = DiagnosticLedger()
    bad = log.record(DiagnosticCode.PROJECT_OPEN, DiagnosticStatus.INFO)
    from dataclasses import replace

    from ai_ngerti_geopolitik.application.diagnostics import (
        DiagnosticSnapshot,
    )

    with pytest.raises(DiagnosticError):
        safe_bundle_payload(DiagnosticSnapshot((replace(bad, sequence=-1),), 0))
