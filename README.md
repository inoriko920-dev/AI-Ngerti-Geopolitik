# AI Ngerti Geopolitik

> **STATUS: SF-STEP 08 — S08-T01 PASS — S08-T02 PASS_WITH_PROVISIONAL — NEXT S08-T03**

Repository resmi aplikasi **AI Ngerti Geopolitik**.

## AI / sesi baru

Baca `AGENTS.md` lalu `docs/SOURCE_OF_TRUTH_INDEX.md`.

## Foundation status

Real foundation now exists:
- `src/ai_ngerti_geopolitik/`;
- boundary packages bootstrap/domain/application/presentation/infrastructure;
- tests under `tests/`;
- verification scripts under `scripts/verify/`;
- operational contracts under `docs/project/`.

Current entrypoint is intentionally foundation smoke only, not a fake editor UI.

Verified S08-T02:
- 6 pytest tests PASS;
- architecture boundary PASS + deliberate violation rejected;
- source-of-truth PASS;
- frozen UI SHA-256 42/42 PASS;
- secret-pattern gate PASS;
- compileall PASS.

Evidence: `docs/evidence/tests/S08_T02_FOUNDATION.md`.

## Provisional toolchain

Target: CPython 3.12.10 x64 + PySide6 6.11.1.

A real `uv.lock`, Windows quality gates, Qt smoke and portable foundation artifact are not yet verified. They belong to S08-T03; no lock was fabricated in the offline non-target runner.

## Frozen decisions

- UI = AAVC visual/workflow contract 1:1.
- exact UI-001..UI-042 in `docs/ui_reference/raw/`.
- VOID 42-prompt regeneration must not be used.
- ProjectState + semantic commands/Undo are ANG-owned.
- media behind MediaEnginePort.
- Gemini only via validated EditPlan/commands.
- final target = Windows portable multi-file ZIP.

**Next exact task: S08-T03 — Windows CI & Portable Packaging Scaffold.**
