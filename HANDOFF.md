# HANDOFF — AI NGERTI GEOPOLITIK

**Fase:** PRE-IMPLEMENTATION / ARCHITECTURE DEFINED  
**SF-STEP terakhir:** 06 — Architecture & Technology Decision  
**Gate:** PASS_WITH_PROVISIONAL  
**Coding:** FORBIDDEN

## Read first

1. AGENTS.md
2. Software Factory master + guide
3. docs/planning/00..07 in order
4. docs/ui_reference/UI_REFERENCE_MANIFEST.md
5. DECISIONS_LOCKED.md
6. PROJECT_STATUS.md
7. this HANDOFF.md

## Architecture baseline

- UI: Python 3.12 x64 family + PySide6 / Qt 6 Widgets.
- UI freeze: AAVC 42/42 direct reuse; no redesign; 42-prompt ANG ZIP remains VOID.
- Dependency direction: presentation -> application -> domain; adapters implement inward ports.
- Product source-of-truth: ANG-owned ProjectState.
- Project format: versioned UTF-8 JSON `.angproj`.
- Time: rational/frame-aware.
- Mutation: semantic CommandBus / CommandBatch + grouped Undo/Redo.
- Media: frozen `MediaEnginePort`; libopenshot v1.0.1 primary qualification candidate; MLT 7.42 fallback.
- Preview: engine-derived, serialized EngineSession; no second manual compositor.
- Render: committed state snapshot -> isolated child worker -> temp -> verify -> atomic final.
- AI: AIProviderPort + official google-genai family + strict structured EditPlan/tool calls.
- Credentials: CredentialPort + Windows generic credential storage/keyring; 1–100 logical slots; no plaintext fallback.
- Jobs: long work off UI thread; stale revision/results rejected.
- Packaging: standalone folder -> ZIP; pyside6-deploy/Nuitka preferred, PyInstaller onedir fallback.

## Material open item

libopenshot-audio is GPLv3 upstream while ANG needs narration/audio. Actual Windows dependency tree + source/distribution license strategy must be qualified before a distributable engine build. openshot-qt remains REFERENCE_ONLY.

## Engine qualification contract

STEP 07 repository architecture must preserve an isolated qualification path for:
ENG-Q1 clean import/native DLL,
ENG-Q2 300-scene seek/play,
ENG-Q3 composition golden cases,
ENG-Q4 21 effects mapping,
ENG-Q5 audio,
ENG-Q6 preview lifecycle,
ENG-Q7 render,
ENG-Q8 cancel,
ENG-Q9 portable clean machine,
ENG-Q10 license manifest.

Do not execute production engine work in STEP 07.

## Pre-coding gate

Before production code:
- STEP 07 must pass;
- all required planning/reference DOCX must remain in repo;
- exact full-resolution UI reference/raw pack must be committed and verified;
- status must explicitly authorize implementation.

## Exact next action

On a NEW owner **"lanjutkan"**, execute **SF-STEP 07 — Code Constitution & Repository Architecture only**.

STEP 07 should define:
- final repository tree;
- module/package ownership;
- public ports/contracts;
- dependency rules/enforcement;
- naming and file responsibility rules;
- config/path/log/error conventions;
- tests/fixtures/golden/evidence layout;
- build/package/third-party manifest layout;
- docs/ADR/task/state structure;
- explicit no-duplicate-service / no-god-file / search-before-create rules;
- AI/SOL handoff rules.

STOP before SF-STEP 08. No production code or engine spike in STEP 07.
