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
12. HANDOFF / PROJECT_STATUS / DECISIONS / REPOSITORY_RULES
13. actual source/tests/config/workflows/evidence.

DOCX planning/reference remains in repo; TXT is machine-readable fallback.

## Current state

- SF-STEP 00–07 planning: present.
- SF-STEP 08: PASS.
- SF-STEP 09: PASS.
- SF-STEP 10: **PASS_WITH_PROVISIONAL**.
- real Qt -> application -> CommandBus -> ProjectState -> persistence/media/output vertical slice: VERIFIED.
- live ProjectState -> timeline UI + backend preview -> preview UI: VERIFIED.
- real H.264/AAC export + cancellation + packaged real-media smoke: VERIFIED.
- UI raw references: 42/42 exact + verified.
- continuous production playback: PROVISIONAL / STEP 11 priority.
- final libopenshot-vs-MLT production qualification: PROVISIONAL / STEP 11 priority.
- next exact STEP: **SF-STEP 11 — Feature Implementation Waves**.
- 42-prompt UI regeneration: VOID / DO NOT USE.
- AAVC repo: read-only.
