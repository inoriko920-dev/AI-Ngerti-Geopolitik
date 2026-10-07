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
    - `docs/evidence/features/S11_W5_004_SUBTITLE_STYLE.md`
    - `docs/evidence/features/S11_W5_005_SUBTITLE_ANIMATION_WORD_TIMING.md`
    - `docs/evidence/features/S11_W5_006_NARRATION_IMPORT_BINDING.md`
    - `docs/evidence/features/S11_W5_007_MICROPHONE_RECORDING.md`
    - `docs/evidence/features/S11_W5_008_FROZEN_UI_PARITY.md`
    - `docs/evidence/features/S11_W5_009_COMBINED_PREVIEW_EXPORT.md`
    - `docs/evidence/features/S11_W5_010_CLOSURE_REGRESSION.md`
    - `docs/evidence/features/S11_W6_001_AI_CREDENTIAL_CONTRACTS.md`
    - `docs/evidence/features/S11_W6_002_CREDENTIAL_SLOTS.md`
    - `docs/evidence/features/S11_W6_003_WINDOWS_SECURE_STORE.md`
    - `docs/evidence/features/S11_W6_004_CREDENTIAL_HEALTH_SAFE_FAILOVER.md`
    - `docs/evidence/features/S11_W6_005_L1_CONTEXT_BUILDER.md`
    - `docs/evidence/features/S11_W6_006_EDITPLAN_PLAN_VERIFIER.md`
    - `docs/evidence/features/S11_W6_007_GEMINI_ASYNC_LIFECYCLE.md`
    - `docs/evidence/features/S11_W6_008_APPROVAL_COMMANDBATCH_UNDO_REDO.md`
    - `docs/evidence/features/S11_W6_009_FROZEN_UI_PARITY.md`
    - `docs/evidence/features/S11_W6_010_LIVE_FAILURE_REGRESSION_CLOSURE.md`
12. current wave contract:
    - `docs/project/W7_AI_AUTO_EDIT_L2_CONTRACT.md`
    - historical closed W6 contract: `docs/project/W6_GEMINI_CREDENTIAL_L1_AI_CONTRACT.md`
    - historical closed W5 contract: `docs/project/W5_SUBTITLE_NARRATION_CONTRACT.md`
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
- SF-STEP 11 W5-004 subtitle style: **PASS**.
- SF-STEP 11 W5-005 render-backed subtitle animation + per-word boundary: **PASS**.
- SF-STEP 11 W5-006 narration import + binding: **PASS**.
- SF-STEP 11 W5-007 microphone recording software path:
  **PASS_WITH_PROVISIONAL_MIC_HARDWARE**.
- physical hardware evidence remains pending because CI exposed 0 DirectShow
  audio input devices.
- SF-STEP 11 W5-008 frozen UI parity: **PASS**.
- SF-STEP 11 W5-009 combined real subtitle/narration preview/export:
  **PASS**.
- SF-STEP 11 W5-010 history/failure/regression closure: **PASS**.
- SF-STEP 11 W5 final status: **PASS_WITH_PROVISIONAL_MIC_HARDWARE**.
- final W5 regression lock W4/W3/W2/W1/W0/S10/S09/S08: **VERIFIED**.
- SF-STEP 11 W6 scope: **Gemini Credential + L1 AI Animation Planning — CONTRACT LOCKED**.
- W6 is derived from Master Blueprint TECH-WAVE STEP 09.
- W6 planning TXT/DOCX and contract MD are source-of-truth.
- S11-W6-001 canonical AI + credential contracts: **PASS**.
- S11-W6-002 secure credential slots 1–100: **PASS**.
- S11-W6-003 Windows secure-store qualification: **PASS**.
- S11-W6-004 credential health + safe failover: **PASS**.
- S11-W6-005 L1 ContextBuilder + allowlist: **PASS**.
- S11-W6-006 EditPlan schema + PlanVerifier: **PASS**.
- S11-W6-007 Gemini adapter + async lifecycle: **PASS**.
- S11-W6-008 Approval → CommandBatch → Undo/Redo: **PASS**.
- S11-W6-009 Frozen UI parity: **PASS**.
- S11-W6-010 Live Gemini + failure + regression closure: **PASS_WITH_PROVISIONAL_LIVE_GEMINI**.
- production Windows Credential Manager secure-store path is qualified;
- credential health/failover/bulk TXT boundary is qualified;
- bounded secret-free L1 provider context is qualified;
- strict non-mutating L1 PlanVerifier is qualified;
- official google-genai adapter + background lifecycle is qualified;
- approval → atomic CommandBatch → exact Undo/Redo is qualified;
- W6 frozen AI/credential presentation parity is qualified with masked credentials and corrected physical raster mapping.
- W6 final status: **CLOSED / PASS_WITH_PROVISIONAL_LIVE_GEMINI**.
- real Gemini network smoke remains provisional because no live CI credential was available.
- final W6 regression lock: **25/25 workflow families SUCCESS, all attempt 1**.
- W7 planning TXT/DOCX and contract MD: **SOURCE OF TRUTH / CONTRACT LOCKED**.
- W7 implementation: **NOT STARTED**.
- S11-W7-001 Canonical L2 command contracts + capability registry: **READY**.
- S11-W7-002..010: **BLOCKED_BY_PREVIOUS_TASKS**.
- exact next action: **SOL S11-W7-001 only**.
- 42-prompt UI regeneration: VOID / DO NOT USE.
- AAVC repo: read-only.
