# HANDOFF — AI NGERTI GEOPOLITIK

**Phase:** SF-STEP 08  
**Completed:** S08-T01 PASS; S08-T02 PASS_WITH_PROVISIONAL  
**Next exact task:** S08-T03 — Windows CI & Portable Packaging Scaffold  
**Product features:** NOT STARTED

## Read first

AGENTS -> Software Factory -> planning -> docs/project contracts -> TASKS -> S08 evidence -> status/handoff -> current source/tests.

## S08-T02 result

Foundation exists at `src/ai_ngerti_geopolitik/` with bootstrap/domain/application/presentation/infrastructure boundaries and a truthful no-feature bootstrap.

Verifiers:
- `verify_architecture.py`
- `verify_source_of_truth.py`
- `verify_ui_reference_manifest.py`
- `verify_no_secrets.py`
- `run_foundation_checks.py`

Local PASS:
- entrypoint;
- 6 pytest tests;
- architecture + deliberate-violation rejection;
- UI 42/42 SHA;
- source-of-truth;
- secret scan;
- compileall.

Evidence: `docs/evidence/tests/S08_T02_FOUNDATION.md`.

## Target toolchain

- CPython 3.12.10 x64
- PySide6 6.11.1
- uv resolver/lock family
- candidate direct quality/test pins in pyproject

## Provisional

Current runner has Python 3.13.5 and no dependency network. Therefore no truthful uv.lock or target-Windows third-party-tool evidence exists. Never fabricate the lock.

## Next exact action

On **"lanjutkan"**, run S08-T03 only:
1. Windows CI foundation on Python 3.12.10;
2. install/pin uv and resolve dependencies;
3. generate/commit real `uv.lock`;
4. run quality/type/import/test/security/UI gates;
5. add minimal portable multi-file foundation scaffold;
6. record real workflow/artifact evidence;
7. stop before STEP 09.

Do not implement product UI, media-engine features, Gemini editing or real render/export.
