# PROJECT STATUS — AI NGERTI GEOPOLITIK

**Last known phase:** PRE-IMPLEMENTATION / ARCHITECTURE BASELINE DEFINED  
**Formal Software Factory completed:** SF-STEP 06 — Architecture & Technology Decision  
**Gate:** PASS_WITH_PROVISIONAL  
**FREEZE-A/B:** ACTIVE / AAVC UI-001..UI-042 42/42  
**Primary UI stack:** Python 3.12 x64 family + PySide6 / Qt 6 Widgets  
**Architecture:** modular monolith, presentation -> application -> domain  
**Project source-of-truth:** ANG ProjectState / versioned JSON .angproj  
**Media boundary:** MediaEnginePort  
**Primary engine qualification candidate:** libopenshot v1.0.1  
**Engine fallback:** MLT 7.42  
**Formal next STEP:** SF-STEP 07 — Code Constitution & Repository Architecture  
**Code status:** NONE / FORBIDDEN  
**Build:** NONE  
**Release:** NONE

## STEP 06 evidence

Canonical architecture decision:
- `docs/planning/07_STEP_06_ARCHITECTURE_TECHNOLOGY_DECISION_AI_NGERTI_GEOPOLITIK.docx`
- machine-readable mirror: `docs/planning/07_STEP_06_ARCHITECTURE_TECHNOLOGY_DECISION_AI_NGERTI_GEOPOLITIK.txt`

## Frozen architecture decisions

- PySide6/Qt Widgets keeps the frozen AAVC UI without web/QML redesign.
- ANG owns ProjectState, semantic CommandBus/CommandBatch, grouped Undo/Redo and .angproj persistence.
- Engine graph is derived and rebuildable from ProjectState.
- Preview must be engine-derived; no second hand-written preview compositor.
- Render uses immutable project revision snapshot in an isolated child worker.
- Gemini uses AIProviderPort + structured plan/tool calls and cannot mutate state directly.
- 1–100 API-key slots use OS credential storage; raw keys are never project/settings/log data.
- Portable release is a standalone multi-file folder packaged as ZIP.
- UI-001..UI-042 remain frozen direct AAVC references; the void 42-prompt batch remains DO NOT USE.

## Mandatory qualification before engine-dependent claims

The primary libopenshot candidate must pass:
- clean Windows binding/DLL import;
- 300-scene seek/play stress;
- SINGLE/DOUBLE composition golden cases;
- 21-effect compatibility mapping;
- narration/audio sync;
- repeated preview lifecycle stress;
- reference render verification;
- safe cancel;
- clean-machine portable package;
- exact dependency/license manifest.

## Material license gate

libopenshot is LGPL-3.0-or-later, but libopenshot-audio is GPLv3 upstream. Because ANG needs audio/narration, final project/source license and bundled dependency strategy must be resolved before distributable engine build. MLT remains the defined fallback behind the same MediaEnginePort.

## Pre-coding blockers

Production coding remains forbidden until:
1. SF-STEP 07 is completed;
2. exact full-resolution UI reference pack is in repo and verified;
3. repository/source-of-truth pre-coding checks pass.

The engine qualification spike is mandatory before making engine-dependent stability/distribution claims.

## Exact next action

After owner says **"lanjutkan"**, execute **SF-STEP 07 — Code Constitution & Repository Architecture only**.

Do not:
- code production app;
- run SF-STEP 08;
- copy openshot-qt source;
- redesign frozen UI.
