# W8 — VALIDATION / RECOVERY / DIAGNOSTICS HARDENING CONTRACT

**Status:** CONTRACT_LOCKED / W8-001..003 PASS / W8-004 READY / W8-005..010 SERIAL_BLOCKED  
**Runtime:** ACTIVE  
**Master Blueprint mapping:** TECH-WAVE STEP 11  
**Planning date:** 2026-10-08  
**Planning baseline:** `a39c6c6d5941f69a2b5b662f26df94d82b7f94ac`  
**Accepted W7 implementation/regression HEAD:** `ca6dd582a4916caa4b0ac4affe4c3119e9ad2049`

Planning sources:
- `docs/planning/11_S11_W8_VALIDATION_RECOVERY_DIAGNOSTICS_HARDENING_CONTRACT_PLAN_2026-10-08.docx`
- `docs/planning/11_S11_W8_VALIDATION_RECOVERY_DIAGNOSTICS_HARDENING_CONTRACT_PLAN_2026-10-08.txt`

## Purpose

W8 hardens the existing product against missing/relocated/corrupt media, stale
background results, persistence failures, crash recovery and support diagnostics.
It adds no new editing family and does not enter Master Blueprint STEP 12 export work.

## Canonical owners

- `ProjectState`: canonical project truth.
- `CommandBus / CommandBatch`: only committed mutation/history owner.
- `ProjectSession`: lifecycle/dirty/open/save/autosave owner.
- `JsonProjectRepository`: atomic project persistence owner.
- `ValidationService`: non-mutating typed issue aggregation — **qualified W8-001**.
- `RelinkAssetCommand`: qualified canonical relink mutation preserving asset_id (W8-003).
- `RelinkService`: qualified verified candidate + canonical command construction (W8-003).
- planned `RelinkScanJobService`: background scan/hash/probe with stale token.
- planned `RecoveryCatalogService / RecoveryManager`: snapshot discovery/validation/retention/decision.
- planned `DiagnosticBundleService`: redacted diagnostics orchestration.
- presentation: projection/intent only; no direct infrastructure/project mutation.

No parallel project store, history owner, serializer, media identity or AI stale owner is allowed.

## Validation contract — W8-001 qualified

`ValidationIssue` and `ValidationResult` are transient frozen application DTOs,
never new ProjectState fields.

Severity:
- BLOCKER
- ERROR
- WARNING
- INFO

Scopes:
PROJECT, MEDIA, TIMELINE_SCENE, SUBTITLE, NARRATION, AI, RENDER, RUNTIME.

Result is bound to project ID + revision + semantic SHA-256.
Different project, changed revision or same-revision semantic replacement is STALE.

Canonical `Asset.availability` remains `online/offline/missing`.
CORRUPT/DUPLICATE remain derived validation/media-health projections; W8-002 real-media integrity is qualified.

Baseline:
- ProjectState.validate() remains structural authority;
- referenced missing = BLOCKER;
- referenced offline = ERROR;
- unreferenced missing = WARNING;
- unreferenced offline = INFO;
- validation is deterministic and non-mutating.

Accepted W8-001:
- HEAD `fd319947ea8ce2579de4918b5c4b49c046851609`;
- workflow `37681708473` SUCCESS;
- targeted 9/9 PASS;
- full pytest 395/395 PASS;
- evidence 22/22 PASS;
- regression 27/27 SUCCESS, all attempt 1;
- artifact `ANG-S11-W8-001-Validation-Contracts` / ID `11509960710`.

Evidence:
`docs/evidence/features/S11_W8_001_CANONICAL_VALIDATION_CONTRACTS.md`.

## Relink contract

Candidate ranking remains locked:
1. exact canonical Axxx basename + compatible probe;
2. exact source_name + compatible media/metadata;
3. exact SHA-256 fingerprint;
4. compatible metadata candidate = manual choice only.

Filename similarity alone never auto-applies. Relink preserves Asset ID and clip references.

## Recovery contract

Autosave never silently overwrites source. Default managed retention max 20 validated
snapshots/project. Source .angproj and .bak are never prune targets. Recovery remains explicit.

## Diagnostics contract

Structured diagnostics must redact credentials/private content and remain bounded.
Diagnostic bundle implementation is deferred to W8-009.

## Frozen UI reuse

No new UI image-generation gate:
- UI-039 — Pemulihan Project;
- UI-040 — Asset Scan;
- UI-041 — Validation Center.

## Serial implementation contract

- **W8-001 — Canonical Validation Contracts + Baseline Rules — PASS**
- **W8-002 — Real Media Integrity + Validation Center Projection — PASS**
- **W8-003 — Single Asset Relink Command + Exact Identity Preservation — PASS**
- W8-004 — Batch Directory Relink Scan + Candidate Ranking — READY
- W8-005 — Autosave Catalog + Retention Hardening — BLOCKED_BY_W8_004
- W8-006 — Crash Marker + Startup Recovery Decision — BLOCKED_BY_W8_005
- W8-007 — Atomic Persistence Failure Injection + Remediation — BLOCKED_BY_W8_006
- W8-008 — Stale Result Hardening for Validation/Relink/Recovery Jobs — BLOCKED_BY_W8_007
- W8-009 — Structured Diagnostics + Redacted Diagnostic Bundle — BLOCKED_BY_W8_008
- W8-010 — Frozen UI Wiring + GOLDEN-03 Recovery/Relink Closure + Regression Lock — BLOCKED_BY_W8_009

## Exact next action

Accepted W8-002:
- HEAD `c73a38d8fd6d3796f988769ca43354185eb66a6d`;
- workflow `37684517658` SUCCESS;
- targeted 7/7 PASS;
- full pytest 402/402 PASS;
- real ffprobe missing/zero/probe-failure/duplicate evidence PASS;
- frozen UI-041 projection + stale gating PASS;
- evidence 18/18 PASS;
- regression 27/27 SUCCESS, all attempt 1;
- artifact `ANG-S11-W8-002-Real-Media-Validation` / ID `11510448492`.

Evidence:
`docs/evidence/features/S11_W8_002_REAL_MEDIA_VALIDATION_CENTER.md`.

Accepted W8-003:
- HEAD `25e5f6cefbbef5f554bd17e64d50a61db948bf13`;
- workflow `37689420848` SUCCESS;
- targeted 9/9 PASS; full pytest 411/411 PASS;
- real relocated-media/Undo-Redo/save-reopen proof PASS; evidence 23/23 PASS;
- regression 27/27 SUCCESS, all attempt 1;
- artifact `ANG-S11-W8-003-Single-Asset-Relink` / ID `11513225118`.

Evidence:
`docs/evidence/features/S11_W8_003_SINGLE_ASSET_RELINK.md`.

After owner says `lanjutkan`, execute **SOL S11-W8-004 only — Batch Directory Relink Scan + Candidate Ranking**.

Do not start W8-005 in the same turn.
