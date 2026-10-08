"""W8-009 fail-closed owned ZIP evidence verifier."""

from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path


def main() -> int:
    root = Path("artifacts/step11/w8-009/evidence")
    report = json.loads((root / "00_w8_009_report.json").read_text(encoding="utf-8"))
    required = (
        "deterministic_zip",
        "fixed_entries_only",
        "manifest_sha_matches",
        "manifest_event_count",
        "dropped_event_count",
        "strict_allowlist",
        "secret_absent",
        "path_absent",
        "project_identity_absent",
        "no_media_bytes",
        "no_full_issue_content",
        "bounded_zip",
        "typed_failure_stage",
        "no_w8_010_started",
    )
    checks = [report.get("status") == "PASS"]
    checks.extend(report.get(key) is True for key in required)
    bundle = root / "support-report.zip"
    assert bundle.is_file()
    with zipfile.ZipFile(bundle) as reader:
        checks.append(reader.namelist() == ["manifest.json", "events.json"])
        manifest = json.loads(reader.read("manifest.json"))
        checks.append(
            manifest["files"][0]["sha256"] == hashlib.sha256(reader.read("events.json")).hexdigest()
        )
    checks.append(bundle.stat().st_size < 128 * 1024)
    if len(report) != len(required) + 1 or not all(checks):
        raise SystemExit("W8-009 diagnostic ZIP evidence verification FAILED")
    print(f"W8-009 evidence verification PASS: {len(checks)}/{len(checks)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
