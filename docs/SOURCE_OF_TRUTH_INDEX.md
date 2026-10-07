# SOURCE OF TRUTH INDEX

## Mandatory read order

1. `/AGENTS.md`
2. Software Factory master + guide
3. all `/docs/planning/` numeric order
4. `/docs/project/PRODUCT.md`
5. `/docs/project/UI_SPEC.md`
6. `/docs/project/ARCHITECTURE.md`
7. `/docs/project/CODE_CONSTITUTION.md`
8. `/docs/project/PLAN.md`
9. `/docs/project/TASKS.md`
10. UI manifest + `raw/UI-001..042`
11. implementation evidence:
    - `docs/evidence/ui/S08_T01_UI_REFERENCE_GATE.md`
    - `docs/evidence/tests/S08_T02_FOUNDATION.md`
    - `docs/evidence/packaging/S08_T03_WINDOWS_CI.md`
    - `docs/evidence/ui/S09_APP_SHELL_UI_IMPLEMENTATION.md`
    - `docs/evidence/e2e/S10_MINIMUM_E2E_VERTICAL_SLICE.md`
    - `docs/evidence/features/S11_W0_BASELINE_AND_ENGINE_QUALIFICATION.md`
    - `docs/evidence/features/S11_W1_PROJECT_MEDIA_PERSISTENCE.md`
    - `docs/evidence/features/S11_W2_TIMELINE_PLAYBACK_CORE.md`
    - `docs/evidence/features/S11_W3_PROPERTIES_VIDEO_AUDIO_COLOR_SPEED.md`
    - `docs/evidence/features/S11_W4_TITLES_TRANSITIONS_EFFECTS.md`
    - `docs/evidence/features/S11_W5_001_CANONICAL_SUBTITLE_NARRATION.md`
    - `docs/evidence/features/S11_W5_002_SRT_IMPORT_VALIDATION.md`
    - `docs/evidence/features/S11_W5_003_SUBTITLE_WORKING_COPY.md`
12. current wave contract:
    - `docs/project/W5_SUBTITLE_NARRATION_CONTRACT.md`
13. HANDOFF / PROJECT_STATUS / DECISIONS / REPOSITORY_RULES
14. actual source/tests/config/workflows/evidence.

DOCX planning/reference remains in repo; TXT is machine-readable fallback.

## Current state

- SF-STEP 00–07 planning: present.
- SF-STEP 08: PASS.
- SF-STEP 09: PASS.
- SF-STEP 10: PASS_WITH_PROVISIONAL.
- SF-STEP 11 W0: PASS.
- SF-STEP 11 W1: PASS.
- SF-STEP 11 W2: PASS.
- SF-STEP 11 W3: PASS.
- SF-STEP 11 W4: **PASS**.
- W4 title/transition/render-backed effect evidence: VERIFIED.
- Reverse: explicitly disabled pending later backend qualification.
- W4 regression lock S08/S09/S10/W0/W1/W2/W3: VERIFIED.
- SF-STEP 11 W5 scope: **Subtitle + Narration — CONTRACT LOCKED**.
- SF-STEP 11 W5-001 canonical subtitle/narration model: **PASS**.
- SF-STEP 11 W5-002 SRT import + validation: **PASS**.
- SF-STEP 11 W5-003 cue editing + safe working-copy flow: **PASS**.
- exact next task: **S11-W5-004 subtitle style**.
- 42-prompt UI regeneration: VOID / DO NOT USE.
- AAVC repo: read-only.
