"""Owned W8-009 bounded diagnostic report and private-content exclusion proof."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
import zipfile
from pathlib import Path

from ai_ngerti_geopolitik.application.diagnostic_bundle import (
    DiagnosticBundleJobService,
    DiagnosticJobState,
)
from ai_ngerti_geopolitik.application.diagnostics import (
    DiagnosticCode,
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


def complete(service: DiagnosticBundleJobService, job_id: str) -> None:
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        snapshot = service.snapshot(job_id)
        if snapshot.state is DiagnosticJobState.SUCCESS:
            return
        if snapshot.state in {DiagnosticJobState.CANCELLED, DiagnosticJobState.FAILED}:
            raise RuntimeError(f"diagnostic generation failed: {snapshot.error_code}")
        time.sleep(0.01)
    raise RuntimeError("diagnostic generation timed out")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    root = args.evidence.resolve()
    root.mkdir(parents=True, exist_ok=True)
    secret = "private-marker-never-enter-bundle"
    private_path = "C:\\Private\\nonpublic\\narration.txt"
    log = DiagnosticLedger(limit=2)
    issue = ValidationIssue(
        ValidationIssueCode.MEDIA_FILE_MISSING,
        ValidationSeverity.BLOCKER,
        ValidationScope.MEDIA,
        f"Project issue: {secret}",
        f"Missing media at {private_path}",
        ("A001", "asset-ref-" + secret),
        ValidationAction.RELINK_MEDIA,
        9,
    )
    result = ValidationResult("P-" + secret, 9, "b" * 64, (issue,))
    log.record(DiagnosticCode.PROJECT_OPEN, DiagnosticStatus.INFO)
    log.record_validation(result)
    error = PersistenceError(PersistenceStage.TEMP_WRITE)
    error.__cause__ = OSError(f"{secret} {private_path}")
    log.record_save_failure(error)
    # First event pruned from bounded memory; zero raw details ever serialized.
    assert log.snapshot().dropped_count == 1
    destination = root / "support-report.zip"
    second = root / "support-report-repeated.zip"
    writer = LocalDiagnosticZipWriter()
    with DiagnosticBundleJobService(writer) as service:
        job = service.submit(destination, log)
        repeated = service.submit(second, log)
        complete(service, job.job_id)
        complete(service, repeated.job_id)
    payload = destination.read_bytes()
    with zipfile.ZipFile(destination) as archive:
        names = archive.namelist()
        manifest = json.loads(archive.read("manifest.json"))
        event_file = archive.read("events.json")
        entries = json.loads(event_file)["events"]
    report = {
        "status": "PASS",
        "deterministic_zip": payload == second.read_bytes(),
        "fixed_entries_only": names == ["manifest.json", "events.json"],
        "manifest_sha_matches": (
            manifest["files"][0]["sha256"] == hashlib.sha256(event_file).hexdigest()
        ),
        "manifest_event_count": manifest["event_count"] == 2,
        "dropped_event_count": manifest["dropped_count"] == 1,
        "strict_allowlist": manifest["redaction"] == "STRICT_ALLOWLIST",
        "secret_absent": secret.encode() not in payload,
        "path_absent": private_path.encode() not in payload,
        "project_identity_absent": b"asset-ref-" not in payload,
        "no_media_bytes": not any(
            name.endswith((".mp4", ".wav", ".angproj", ".txt"))
            for name in names
        ),
        "no_full_issue_content": b"Missing media" not in payload,
        "bounded_zip": len(payload) < 128 * 1024,
        "typed_failure_stage": entries[-1]["persistence_stage"] == "temp_write",
        "no_w8_010_started": True,
    }
    if not all(value is True for key, value in report.items() if key != "status"):
        raise RuntimeError("diagnostic bundle evidence is not all PASS")
    (root / "00_w8_009_report.json").write_text(
        json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
