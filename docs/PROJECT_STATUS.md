# PROJECT STATUS — AI NGERTI GEOPOLITIK

**Last known phase:** PRE-IMPLEMENTATION / CODE CONSTITUTION DEFINED  
**Formal Software Factory completed:** SF-STEP 07 — Code Constitution & Repository Architecture  
**Gate:** PASS_WITH_PROVISIONAL  
**Code Constitution:** CC-ANG-v1.0  
**Repository Map:** REPO-ANG-v1.0  
**Architecture:** ANG-SF-STEP06-ARCH-TECH-v1.0  
**UI:** FREEZE-A/B ACTIVE — AAVC UI-001..UI-042 42/42  
**Application source:** NONE  
**Build/CI product:** NONE  
**Formal next STEP:** SF-STEP 08 — Repository Foundation & UI Reference Gate  
**First STEP 08 task:** S08-T01  
**Production coding:** BLOCKED until S08-T01 passes

## STEP 07 evidence

Canonical planning:
- `docs/planning/08_STEP_07_CODE_CONSTITUTION_REPOSITORY_ARCHITECTURE_AI_NGERTI_GEOPOLITIK.docx`
- mirror: `docs/planning/08_STEP_07_CODE_CONSTITUTION_REPOSITORY_ARCHITECTURE_AI_NGERTI_GEOPOLITIK.txt`

## Frozen repository constitution

- package: `src/ai_ngerti_geopolitik/`
- boundaries: domain / application / presentation / infrastructure / bootstrap
- dependency direction: presentation -> application -> domain
- infrastructure implements application ports
- bootstrap wires concrete adapters only
- one concern = one canonical owner
- all project mutation = semantic CommandBus / CommandBatch
- ProjectState = source-of-truth
- no Qt/provider/engine/filesystem implementation in domain
- no concrete infrastructure access from presentation
- no hidden mutable global project state
- no long job on Qt UI thread
- no plaintext secrets
- no silent UI redesign
- no fake green/capability

## STEP 08 READY tasks

**S08-T01 — Source-of-Truth & Exact UI Reference Gate**  
Commit/verify STEP00–07 planning DOCX+TXT and exact full-resolution UI-001..UI-042 raw references. 42/42 hashes must match manifest. **No product source code in this task.**

**S08-T02 — Repository Skeleton, Toolchain & Architecture Fitness**  
Only after T01 PASS. Materialize minimal src-layout, Python/tooling, tests and import/secret/source-truth checks. No feature UI/engine/Gemini implementation.

**S08-T03 — Windows CI & Portable Packaging Scaffold**  
Only after T02 PASS. Windows CI + minimal portable scaffold/evidence; no final release claim.

## Pre-coding blocker

Exact full-resolution UI visual/raw pack is still not fully committed/verified in repo. This is now the explicit first task of STEP 08 and blocks production source coding.

## Exact next action

After owner says **"lanjutkan"**, SOL executes **SF-STEP 08 beginning S08-T01 only**.

Do not jump to UI implementation, media-engine feature implementation, Gemini features, or STEP 09 before the STEP 08 foundation gate is completed.
