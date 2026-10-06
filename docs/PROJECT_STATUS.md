# PROJECT STATUS — AI NGERTI GEOPOLITIK

**Phase:** SF-STEP 08 — Repository Foundation + UI Reference + CI  
**S08-T01:** PASS  
**S08-T02:** **PASS_WITH_PROVISIONAL**  
**Next:** S08-T03 — Windows CI & Portable Packaging Scaffold  
**Product features:** NOT STARTED

## S08-T02 implemented

- real minimal src-layout/package boundaries;
- pyproject + Python/tool candidate pins;
- truthful no-feature entrypoint;
- architecture/UI-SHA/source-of-truth/secret verifiers;
- pytest foundation suites;
- concise operational docs.

No 42-screen UI, media-engine feature stack, Gemini edit behavior, or render/export feature is implemented.

## Verified locally

Available runner: Linux, Python 3.13.5, pytest 9.0.2, uv 0.10.0; target Python 3.12.10 and package-index network unavailable.

PASS:
- package entrypoint smoke;
- pytest: 6 tests;
- deliberate architecture violation detection;
- current architecture boundary;
- source-of-truth existence;
- UI 42/42 SHA-256;
- secret-pattern scan;
- compileall.

Evidence: `docs/evidence/tests/S08_T02_FOUNDATION.md`.

## Provisional

Declared target: CPython 3.12.10 x64 + PySide6 6.11.1 + uv resolver family.

NOT VERIFIED:
- real `uv.lock`;
- frozen sync on target Python;
- Ruff/mypy/Import Linter/detect-secrets/pip-audit installed-tool gates;
- pytest-qt/PySide6 Windows smoke;
- Windows CI;
- portable scaffold.

Lock was not fabricated.

## Gate

S08-T02 = **PASS_WITH_PROVISIONAL**. This does not permit STEP 09.

## Exact next action

When owner says **"lanjutkan"**, execute **S08-T03 only**. First resolve target Python + uv, generate/commit a real lock, run Windows gates, then create a truthful portable foundation scaffold. No product features.
