# AI Ngerti Geopolitik

> **STATUS: SF-STEP 09 PASS — NEXT SF-STEP 10 MINIMUM END-TO-END VERTICAL SLICE**

Repository resmi aplikasi **AI Ngerti Geopolitik**.

Baca `AGENTS.md` lalu `docs/SOURCE_OF_TRUTH_INDEX.md`.

## UI shell verified

STEP 09 Windows run `37520166438` passed on commit `61225eca38115a636e062d3e795f7884049d19d4`.

Verified:
- real PySide6 app shell;
- AAVC-derived hierarchy with no redesign;
- frozen UI references 42/42 intact;
- representative UI capture 8/8 at 1920×1080;
- 17 tests;
- Ruff/mypy/Import Linter/architecture gates;
- Windows portable UI shell build and smoke;
- S08 foundation regression remains green.

Detailed evidence:
`docs/evidence/ui/S09_APP_SHELL_UI_IMPLEMENTATION.md`.

Portable UI shell inner ZIP SHA-256:
`47fe8296d1eaa7dbf0b859b2e65335c25b51183d19b7f4eed596a64c2ea162c0`.

## Scope truth

This is not yet the finished video editor. STEP 09 does not claim real media-engine editing, .angproj persistence, production render/export, or Gemini execution.

## Frozen product decisions

- UI = AAVC 1:1 as close as practical; no creative redesign.
- `UI-001..UI-042` remain frozen design authority.
- runtime uses real interactive widgets, not PNG screens.
- ProjectState + semantic CommandBus/Undo are ANG-owned.
- media stays behind MediaEnginePort.
- Gemini later executes only through validated EditPlan/commands.
- Windows target remains portable multi-file ZIP.

**Next: SF-STEP 10 — prove one narrow real end-to-end editing workflow before feature waves.**
