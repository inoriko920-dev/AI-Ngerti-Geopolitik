# S08-T02 — FOUNDATION / ARCHITECTURE FITNESS EVIDENCE

Date: 2026-10-06  
Role: SOL  
Baseline before change: `main @ f64faf36bae9c13f4472687ddb686566983b0729`  
Task: S08-T02 only

## Implemented

- minimal Python src-layout at `src/ai_ngerti_geopolitik/`;
- explicit bootstrap/domain/application/presentation/infrastructure boundaries;
- truthful no-feature entrypoint;
- pyproject/tooling configs;
- architecture/source-of-truth/UI-reference/secret verification scripts;
- pytest unit + architecture + verification harness;
- concise operational docs under `docs/project/`.

## Target toolchain declaration

- Windows target Python: CPython 3.12.10 x64.
- Python package target: `>=3.12.10,<3.13`.
- PySide6: 6.11.1.
- uv remains the selected resolver/lock family.
- quality/test candidate pins are declared in `pyproject.toml`.

Python 3.12.10 is used because it is the last full-maintenance Python 3.12 release with Windows installers; later 3.12 security releases are source-only.

## Executed evidence in available runner

Runner reality:
- Linux container;
- Python 3.13.5;
- pytest 9.0.2;
- uv 0.10.0;
- target Python 3.12.10 not installed;
- package-index network unavailable.

PASS commands:
- `PYTHONPATH=src python -m ai_ngerti_geopolitik`
- `PYTHONPATH=src python -m pytest -q` — 6 tests passed
- `python scripts/verify/run_foundation_checks.py --root .`
- `python scripts/verify/verify_architecture.py --root .`
- `python scripts/verify/verify_ui_reference_manifest.py --root .` — 42/42
- `python scripts/verify/verify_no_secrets.py --root .`
- `python -m compileall -q src`

The architecture test injects a deliberate presentation -> infrastructure violation and confirms it is rejected.

## NOT VERIFIED / provisional

- no `uv.lock` generated because target Python 3.12.10 and dependency network were unavailable;
- lock deliberately NOT fabricated;
- exact Ruff/mypy/Import Linter/detect-secrets/pip-audit executable runs NOT TESTED;
- PySide6/pytest-qt Windows runtime NOT TESTED;
- Windows CI and portable package are S08-T03;
- product UI, media engine, Gemini and render features remain NOT IMPLEMENTED.

## Gate

S08-T02 = **PASS_WITH_PROVISIONAL**.

Next exact action: **S08-T03 — Windows CI & Portable Packaging Scaffold** only.
