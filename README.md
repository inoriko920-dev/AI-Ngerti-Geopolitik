# AI Ngerti Geopolitik

> **STATUS: SF-STEP 08 PASS — NEXT SF-STEP 09 APP SHELL / UI IMPLEMENTATION**

Repository resmi aplikasi **AI Ngerti Geopolitik**.

Baca `AGENTS.md` lalu `docs/SOURCE_OF_TRUTH_INDEX.md`.

## Foundation verified

Final Windows checkpoint run: `37500196775` — **SUCCESS**.

Verified:
- CPython 3.12.10;
- uv 0.12.21 + committed `uv.lock`;
- PySide6 6.11.1;
- Ruff/mypy/Import Linter;
- pytest + Qt smoke;
- UI references 42/42;
- secret scans + pip-audit;
- PyInstaller portable foundation build;
- Windows executable smoke.

The artifact is a **foundation proof only**, not the finished product editor.

## Frozen product decisions

- UI = AAVC 1:1, exact `UI-001..UI-042`.
- prompt regeneration set is VOID.
- ProjectState + semantic CommandBus/Undo are ANG-owned.
- media remains behind MediaEnginePort.
- Gemini later only through validated EditPlan/commands.
- final distribution target = Windows portable multi-file ZIP.

**Next: SF-STEP 09 — implement the real PySide6 app shell from frozen AAVC references, with screenshot parity evidence.**
