# TASKS

## S08-T01 — DONE / PASS
Exact planning/reference pack and 42/42 raw frozen UI references are in GitHub and verified.

## S08-T02 — DONE / PASS_WITH_PROVISIONAL
Foundation source/package boundaries, test harness, architecture verifier, UI SHA verifier, source-of-truth verifier, secret verifier, and concise operational docs are committed.

Verified locally:
- package entrypoint smoke;
- 6 pytest tests;
- architecture boundary + deliberate violation detection;
- UI reference SHA 42/42;
- source-of-truth existence;
- secret-pattern scan;
- Python compileall.

Provisional:
- target CPython 3.12.10 environment was unavailable locally;
- `uv.lock` was not fabricated;
- Ruff/mypy/Import Linter/detect-secrets/pip-audit installed-tool runs remain for Windows CI/toolchain resolution.

## S08-T03 — READY
Windows CI & Portable Packaging Scaffold. Start by resolving Python 3.12.10 with uv, generate/commit a real `uv.lock`, run mandatory quality/test/import/security/UI gates on Windows, then build a truthful portable foundation scaffold. No final-release claim.
