# AI Ngerti Geopolitik

> **STATUS: SF-STEP 08 — S08-T03 FINAL CHECKPOINT — PRODUCT UI BELUM DIMULAI**

Repository resmi aplikasi **AI Ngerti Geopolitik**.

Baca `AGENTS.md` lalu `docs/SOURCE_OF_TRUTH_INDEX.md`.

## Foundation evidence

Windows workflow run `37499102659` succeeded end-to-end on CPython 3.12.10.

Verified:
- real `uv.lock`;
- Ruff format/lint;
- mypy;
- Import Linter;
- pytest 7 tests;
- PySide6 Qt smoke;
- UI references 42/42 SHA-256;
- secret scans;
- pip-audit with no known vulnerabilities;
- PyInstaller onedir foundation build;
- Windows executable smoke;
- portable foundation artifact.

The portable foundation is deliberately **not the product editor**. It proves build/package infrastructure only.

## Frozen product decisions

- UI = AAVC 1:1, `UI-001..UI-042`.
- prompt regeneration set is VOID.
- ProjectState + semantic CommandBus/Undo are ANG-owned.
- media remains behind MediaEnginePort.
- Gemini later only through validated EditPlan/commands.
- final distribution target = Windows portable multi-file ZIP.

After the final checkpoint CI is green, SF-STEP 08 closes and the next step is **SF-STEP 09 — App Shell / UI Implementation**.
