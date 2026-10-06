# HANDOFF — AI NGERTI GEOPOLITIK

**Fase:** PRE-IMPLEMENTATION / STEP 07 COMPLETE  
**SF-STEP terakhir:** 07 — Code Constitution & Repository Architecture  
**Gate:** PASS_WITH_PROVISIONAL  
**Code Constitution:** CC-ANG-v1.0  
**Repository Map:** REPO-ANG-v1.0  
**Application source:** NONE  
**Next role:** SOL  
**Next STEP:** SF-STEP 08  
**First task:** S08-T01

## Read first

1. AGENTS.md
2. Software Factory master + guide
3. docs/planning/00..08 in order
4. docs/ui_reference/UI_REFERENCE_MANIFEST.md
5. docs/DECISIONS_LOCKED.md
6. docs/PROJECT_STATUS.md
7. docs/REPOSITORY_RULES.md
8. this HANDOFF.md

## Core constitution

Canonical package: `src/ai_ngerti_geopolitik/`.

Dependency:
- presentation -> application -> domain
- infrastructure -> application ports + domain contract types
- bootstrap -> all for construction only

Rules:
- ProjectState is truth.
- All manual/AI mutations through semantic CommandBus.
- No generic god service/manager.
- Presentation cannot directly call engine/provider/persistence/credential adapters.
- Domain cannot import Qt/libopenshot/MLT/FFmpeg/Gemini/keyring/subprocess/filesystem I/O.
- Long work stays off UI thread.
- Worker results are revision/task validated.
- Secrets never enter project/settings/log/repo.
- UI remains AAVC 1:1 and real widgets.
- Search -> Understand -> Modify before create.

## STEP 08 exact order

### S08-T01 — FIRST / P0
Source-of-Truth & Exact UI Reference Gate.

Goal:
- ensure STEP00–07 planning DOCX+TXT are in repo;
- commit exact full-resolution UI-001..UI-042 raw/reference files;
- verify 42/42 SHA-256 against manifest;
- update source-of-truth index/status/handoff;
- **do not create product source code yet**.

PASS evidence:
- 42/42 hash verification;
- planning 00–07 present/readable;
- commit SHA;
- pre-coding docs/UI gate explicitly PASS.

### S08-T02
After T01 PASS only: minimal src-layout + Python/toolchain + architecture fitness checks.

### S08-T03
After T02 PASS only: Windows CI + portable packaging scaffold.

## Important architecture

- UI: PySide6/Qt Widgets.
- Project: versioned .angproj JSON.
- Media: MediaEnginePort; libopenshot v1.0.1 qualification candidate; MLT fallback.
- AI: AIProviderPort + Gemini structured plans -> PlanVerifier -> CommandBatch.
- Credentials: Windows credential adapter, 1–100 logical slots.
- Render: snapshot -> isolated child worker.
- Portable: standalone multi-file folder -> ZIP.

## Do not do in first STEP 08 task

- no UI coding;
- no engine feature;
- no Gemini feature;
- no rendering feature;
- no upstream source copy;
- no new design;
- no use of the VOID 42 ANG prompt ZIP.

## Astra review triggers

Stop/review on: new top-level layer/service, dependency exception, breaking schema/port, engine switch, new native dependency, frozen UI structural delta, new AI destructive permission family, secret backend change, packaging-model change.

## Next exact action

On owner **"lanjutkan"**, execute **S08-T01 only** and report its PASS/FAIL evidence before proceeding to T02.
