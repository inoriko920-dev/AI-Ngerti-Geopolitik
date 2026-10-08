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
    - `docs/evidence/features/S11_W7_001_L2_CONTRACTS.md`
    - `docs/evidence/features/S11_W7_002_L2_CONTEXT.md`
    - `docs/evidence/features/S11_W7_003_L2_PARSER.md`
    - `docs/evidence/features/S11_W7_004_L2_SEMANTIC_VERIFIER.md`
    - `docs/evidence/features/S11_W7_005_PACING_QUALIFICATION.md`
    - `docs/evidence/features/S11_W7_006_TRANSFORM_QUALIFICATION.md`
    - `docs/evidence/features/S11_W7_007_TRANSITION_MIXED_QUALIFICATION.md`
    - `docs/evidence/features/S11_W7_008_GEMINI_L2_LIFECYCLE.md`
    - `docs/evidence/features/S11_W7_009_APPROVAL_APPLY_UI_DIFF.md`
    - `docs/evidence/features/S11_W7_010_REAL_MEDIA_FAILURE_REGRESSION_CLOSURE.md`
    - `docs/evidence/features/S11_W8_001_CANONICAL_VALIDATION_CONTRACTS.md`
    - `docs/evidence/features/S11_W8_002_REAL_MEDIA_VALIDATION_CENTER.md`
    - `docs/evidence/features/S11_W8_003_SINGLE_ASSET_RELINK.md`
    - `docs/evidence/features/S11_W8_004_BATCH_RELINK_SCAN.md`
    - `docs/evidence/features/S11_W8_005_AUTOSAVE_CATALOG.md`
    - `docs/evidence/features/S11_W8_006_CRASH_RECOVERY.md`
    - `docs/evidence/features/S11_W8_007_ATOMIC_PERSISTENCE.md`
    - `docs/evidence/features/S11_W8_008_STALE_JOBS.md`
    - `docs/evidence/features/S11_W8_009_DIAGNOSTIC_BUNDLE.md`
12. current wave contract:
    - `docs/project/W8_VALIDATION_RECOVERY_DIAGNOSTICS_CONTRACT.md`
    - historical closed W7 contract: `docs/project/W7_AI_AUTO_EDIT_L2_CONTRACT.md`
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
- W7 implementation: **CLOSED / PASS_WITH_PROVISIONAL_LIVE_GEMINI**.
- S11-W7-001 Canonical L2 command contracts + capability registry: **PASS**.
- S11-W7-002 L2 ContextBuilder + selected-scope contract: **PASS**.
- S11-W7-003 strict AutoEditPlan v2 parser/schema: **PASS**.
- S11-W7-004 L2 semantic verifier + sequential dry-run translator: **PASS**.
- S11-W7-005 pacing qualification — duration + speed: **PASS**.
- S11-W7-006 transform qualification: **PASS**.
- S11-W7-007 transition + mixed-plan qualification: **PASS**.
- S11-W7-008 Gemini L2 request profile + lifecycle reuse: **PASS**.
- S11-W7-009 approval/apply/UI diff integration: **PASS**.
- S11-W7-010 real-media closure + failure/regression lock: **PASS**.
- W7-001 exact capability registry/policy bounds and W6 backward compatibility are qualified.
- W7-002 selected-scope + bounded deterministic L2 context are qualified.
- W7-003 strict closed AutoEditPlan v2 parser/schema is qualified.
- W7-004 semantic verifier + sequential manual-command dry-run translator is qualified.
- W7-005 real duration/speed pacing and ripple are render-qualified with unchanged canonical state/history.
- W7-006 real position/scale/rotation/opacity transform preview/export is qualified through the canonical manual command path with unchanged canonical state/history.
- W7-007 real fade_black transition + six-command mixed L1/L2 plan are qualified through existing canonical manual/render owners with unchanged canonical state/history.
- W7-007 regression lock is 26/26 triggered workflow families SUCCESS; 23 attempt 1 and 3 attempt 2 after transient Chocolatey FFmpeg HTTP 504 only.
- W7-008 shared Gemini L1/L2 profile + async lifecycle reuse is qualified with frozen W6 request fields, canonical schema-v2 L2 verification, unchanged canonical state and no second provider/credential owner.
- W7-009 explicit L2 review/approval, bounded before→after UI diff, one atomic AI CommandBatch and exact one Undo/Redo transaction are qualified through existing W6 owners.
- W7-009 regression lock is 26/26 triggered workflow families SUCCESS, all attempt 1.
- W7-010 final integrated real-media/persistence/Undo-Redo/failure closure is qualified.
- final W7 regression lock is **27/27 workflow families SUCCESS, all attempt 1**.
- W7 final status: **CLOSED / PASS_WITH_PROVISIONAL_LIVE_GEMINI**.
- W8 planning TXT/DOCX + contract: **SOURCE OF TRUTH / CONTRACT_LOCKED**.
- W8 runtime implementation: **ACTIVE**.
- W8-001 Canonical Validation Contracts + Baseline Rules: **PASS**.
- W8-002 Real Media Integrity + Validation Center Projection: **PASS**.
- W8-003 Single Asset Relink Command + Exact Identity Preservation: **PASS**.
- W8-004 Batch Directory Relink Scan + Candidate Ranking: **PASS**.
- W8-005 Autosave Catalog + Retention Hardening: **PASS**.
- W8-006 Crash Marker + Startup Recovery Decision: **PASS**.
- W8-007 Atomic Persistence Failure Injection + Remediation: **PASS**.
- W8-008 Stale Result Hardening for W8 Background Jobs: **PASS**.
- W8-009 Structured Diagnostics + Redacted Diagnostic Bundle: **PASS**.
- W8-010: **READY**.
- W8 reuses frozen UI-039 Recovery, UI-040 Asset Scan and UI-041 Validation Center; no new UI generation is required.
- W8 preserves ProjectState/CommandBus/ProjectSession/JsonProjectRepository ownership and extends stale safety to W8 jobs.
- W8-001 evidence: `docs/evidence/features/S11_W8_001_CANONICAL_VALIDATION_CONTRACTS.md`.
- W8-001 regression lock: **27/27 workflow families SUCCESS, all attempt 1**.
- W8-002 real ffprobe media integrity + frozen UI-041 projection: **PASS**.
- W8-002 evidence: `docs/evidence/features/S11_W8_002_REAL_MEDIA_VALIDATION_CENTER.md`.
- W8-002 regression lock: **27/27 workflow families SUCCESS, all attempt 1**.
- W8-003 real relink, exact identity, undo/redo/save-reopen: **PASS**;
- W8-003 targeted tests 9/9, full pytest 411/411, evidence 23/23: **PASS**;
- W8-003 accepted HEAD `25e5f6cefbbef5f554bd17e64d50a61db948bf13`; workflow `37689420848`; regression 27/27 SUCCESS;
- W8-003 evidence: `docs/evidence/features/S11_W8_003_SINGLE_ASSET_RELINK.md`;
- W8-004 accepted HEAD `4988e84ca6bca1e64fc5a755ff0d3287802e70f8`; Windows workflow `37721840504` SUCCESS;
- W8-004 targeted 9/9, full pytest 420/420, real-media evidence 14/14 PASS;
- W8-004 full same-HEAD regression 27/27 SUCCESS, all attempt 1;
- W8-004 evidence: `docs/evidence/features/S11_W8_004_BATCH_RELINK_SCAN.md`;
- W8-005 accepted HEAD `43cb1d04b5d519c26f843714c4b7cd9793054fe9`; workflow `37724812333` SUCCESS, artifact `11526779061`;
- W8-005 targeted 9/9, full pytest 429/429, evidence 12/12, regression 27/27 PASS;
- W8-005 evidence `docs/evidence/features/S11_W8_005_AUTOSAVE_CATALOG.md`;
- W8-006 accepted HEAD `5a975bb312714f84315b9b752deac75a33021fab`; Windows workflow `37726261665` SUCCESS;
- W8-006 targeted 15/15, full pytest 444/444, crash evidence 12/12 and regression 27/27 PASS;
- W8-006 evidence `docs/evidence/features/S11_W8_006_CRASH_RECOVERY.md`;
- W8-007 accepted HEAD `130407dc728b6417c30dbbc935ecd9b04d37ba43`, workflow `37727525574` SUCCESS;
- W8-007 targeted 15/15, full pytest 459/459, evidence 19/19, regression 28/28 PASS;
- W8-007 artifact `ANG-S11-W8-007-Atomic-Persistence`, ID `11528930146`;
- W8-008 accepted code HEAD `6c35b70bd9122664473a69eff6635ed9b71da5cb`, Windows `37728798520` SUCCESS;
- W8-008 targeted 12/12, full pytest 471/471, evidence 18/18, regression 27/27 PASS;
- W8-008 evidence `docs/evidence/features/S11_W8_008_STALE_JOBS.md`;
- W8-009 accepted code HEAD `6a4ec93d445e71dc037bcc4dc6edff2008894268` and Windows workflow `37730435314` SUCCESS;
- W8-009 targeted 11/11, full pytest 482/482, redaction evidence 18/18, same-HEAD regression 27/27 SUCCESS;
- W8-009 evidence `docs/evidence/features/S11_W8_009_DIAGNOSTIC_BUNDLE.md`;
- exact next action: **SOL S11-W8-010 Frozen UI Wiring + GOLDEN-03 Closure ONLY**.
- 42-prompt UI regeneration: VOID / DO NOT USE.
- AAVC repo: read-only.

W8-006 accepted PASS: 12 unit + 3 Qt tests, strict crash-marker
and source-byte integrity evidence, 27/27 same-HEAD workflow lock.
W8-007 READY; W8-008 BLOCKED.

W8-007 accepted PASS: full same-HEAD 28/28 regression, real
fault-injection evidence and typed safe error projection. W8-008 READY;
W8-009 BLOCKED.

W8-008 accepted PASS at `6c35b70bd9122664473a69eff6635ed9b71da5cb` with source-safe stale/cancel evidence,
27/27 same-HEAD regression and no W8-009 implementation.
W8-009 READY; W8-010 BLOCKED.

W8-009 accepted PASS at `6a4ec93d445e71dc037bcc4dc6edff2008894268`:
11/11 targeted, 482/482 full pytest, 18/18 redacted ZIP proof, 27/27
same-HEAD workflow regression. W8-010 READY; STEP 12 not started.
