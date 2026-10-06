# HANDOFF — AI NGERTI GEOPOLITIK

**Last completed:** SF-STEP 09 — PASS  
**Accepted implementation commit:** `61225eca38115a636e062d3e795f7884049d19d4`  
**Passing S09 Windows run:** `37520166438`  
**Passing S08 regression run:** `37520166400`  
**Next exact STEP:** SF-STEP 10 — Minimum End-to-End Vertical Slice

## What STEP 09 delivered

ANG now has a real PySide6 shell matching the AAVC runtime structure as closely as practical without redesign:
- Project Hub / Home;
- Scene DOCX wizard;
- editor shell;
- SINGLE / DOUBLE scene states;
- subtitle state;
- export settings;
- validation center;
- menus/toolbars/timeline/preview/right workspace shell;
- semantic presentation intents;
- deterministic screenshot capture;
- Windows portable onedir packaging.

Representative capture set: UI-002, UI-003, UI-010, UI-013, UI-014, UI-027, UI-035, UI-041.

## Evidence

`docs/evidence/ui/S09_APP_SHELL_UI_IMPLEMENTATION.md`

Key PASS facts:
- pytest 17 PASS;
- mypy 19 source files / 0 issues;
- Import Linter 4 kept / 0 broken;
- architecture PASS;
- source-of-truth 70/70;
- frozen UI SHA 42/42;
- 8/8 representative screenshots;
- portable UI shell smoke PASS.

Direct runtime comparison used read-only AAVC CI run `37498549910` at commit `7d77fc9f724d359c7da6c4796dffce5104740952`. This supplements, not replaces, the frozen 42-reference contract.

Portable inner ZIP SHA-256:
`47fe8296d1eaa7dbf0b859b2e65335c25b51183d19b7f4eed596a64c2ea162c0`.

## Known scope gaps by design

Not yet real:
- media-engine editing/playback integration;
- .angproj save/reopen;
- split/trim domain mutations;
- production Undo/Redo;
- real export;
- Gemini execution.

Do not label STEP 09 fixture UI as functional media behavior.

## STEP 10 exact purpose

Prove **one minimum real editing flow end-to-end**, not all features.

Read the exact STEP 10 Software Factory prompt before implementation. The slice should remain narrow and should validate the architecture through a real ProjectState/command/media path, including relevant persistence, undo/redo, negative path and output evidence.

Do not start STEP 11 feature waves before STEP 10 gate PASS.
