# HANDOFF — AI NGERTI GEOPOLITIK

**Fase:** PRE-IMPLEMENTATION / UI FROZEN  
**SF-STEP terakhir:** 05 — UI Freeze & Product Blueprint  
**Gate:** PASS_WITH_PROVISIONAL  
**FREEZE-A:** SPEC_FROZEN  
**FREEZE-B:** RASTER_FROZEN 42/42  
**Coding:** FORBIDDEN

## Read first

1. AGENTS.md
2. Software Factory master + guide
3. docs/planning/00..06 in order
4. docs/ui_reference/UI_REFERENCE_MANIFEST.md
5. DECISIONS_LOCKED.md
6. PROJECT_STATUS.md
7. this HANDOFF.md

## Frozen UI rule

AI Ngerti Geopolitik must implement the AAVC UI **1:1 as closely as practical**:
- AAVC UIF-AAVC-v1.0
- UI-001..UI-042
- 1920x1080 canonical reference
- Indonesian
- white/light + restrained blue
- real widgets, not screenshot UI
- branding may become AI Ngerti Geopolitik

## Owner correction — mandatory

The 42 ANG prompts/ZIP created after STEP 04 are **VOID / NON-AUTHORITATIVE**.

Do not:
- regenerate UI-001..UI-042;
- use those prompts as source-of-truth;
- commit them as canonical planning;
- redesign baseline UI.

For the baseline, use the already existing 42 AAVC canonical references directly.

Only a true new ANG-visible surface without AAVC coverage may receive `UI-ANG-Dxx` + prompt + image + review + change record.

## Freeze model

**FREEZE-A / SPEC_FROZEN**
- screen/state registry
- design tokens/shell hierarchy
- components/control semantics
- timeline interactions
- AI command/approval/undo/fallback
- subtitle/audio/background
- validation/recovery
- render/export
- copy/state/accessibility
- change governance

**FREEZE-B / RASTER_FROZEN**
- UI-001..UI-042 = 42/42
- hashes in UI_REFERENCE_MANIFEST
- later parity references UI-038..042 remain frozen evidence

**FREEZE-C / IMPLEMENTATION_CONFORMED**
- future STEP 09/13 after actual runtime screenshots and interaction QA.

## Pre-coding gate

Exact full-resolution visual/raw reference pack still must be present in repo and verified before production coding. Current repo has connector-safe index + hashes. This does not block STEP 06–07 planning.

## Exact next action

If owner says **"lanjutkan"**, execute **SF-STEP 06 — Architecture & Technology Decision** only.

STEP 06 must decide:
- primary framework/UI stack;
- libopenshot vs fallback decision/integration boundary;
- domain/project state ownership;
- command/history/Undo-Redo architecture;
- preview/playback/render bridge;
- persistence/project schema strategy;
- validation/relink/recovery boundaries;
- worker/background job model;
- Gemini provider/credential security boundary;
- Windows portable packaging and native DLL strategy;
- dependency/license compliance strategy;
- test architecture and performance/stability evidence plan.

Preserve FREEZE-A/B. No production coding and no STEP 07 in the same turn.
