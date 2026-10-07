# W8 — VALIDATION / RECOVERY / DIAGNOSTICS HARDENING CONTRACT

**Status:** CONTRACT_LOCKED / IMPLEMENTATION_NOT_STARTED / W8-001 READY / W8-002..010 SERIAL_BLOCKED  
**Role:** ASTRA planning  
**Master Blueprint mapping:** TECH-WAVE STEP 11  
**Planning date:** 2026-10-08  
**Planning baseline:** `a39c6c6d5941f69a2b5b662f26df94d82b7f94ac`  
**Accepted W7 implementation/regression HEAD:** `ca6dd582a4916caa4b0ac4affe4c3119e9ad2049`

Planning sources:
- `docs/planning/11_S11_W8_VALIDATION_RECOVERY_DIAGNOSTICS_HARDENING_CONTRACT_PLAN_2026-10-08.docx`
- `docs/planning/11_S11_W8_VALIDATION_RECOVERY_DIAGNOSTICS_HARDENING_CONTRACT_PLAN_2026-10-08.txt`

## Purpose

W8 hardens the existing product against missing/relocated/corrupt media, stale background
results, persistence failures, crash recovery and support diagnostics. It adds no new editing
family and does not enter Master Blueprint STEP 12 export work.

## Canonical owners

- `ProjectState`: canonical project truth.
- `CommandBus / CommandBatch`: only committed mutation/history owner.
- `ProjectSession`: lifecycle/dirty/open/save/autosave owner.
- `JsonProjectRepository`: atomic project persistence owner.
- planned `ValidationService`: non-mutating typed issue aggregation.
- planned `RelinkAssetCommand`: canonical relink mutation preserving `asset_id`.
- planned `RelinkService`: candidate verification + command construction.
- planned `RelinkScanJobService`: background scan/hash/probe with stale token.
- planned `RecoveryCatalogService / RecoveryManager`: snapshot discovery/validation/retention/decision.
- planned `DiagnosticBundleService`: redacted diagnostics orchestration.
- presentation: projection/intent only; no direct infrastructure/project mutation.

No parallel project store, history owner, serializer, media identity or AI stale owner is allowed.

## Validation contract

`ValidationIssue` is transient application state, never a new ProjectState field.

Severity:
- BLOCKER
- ERROR
- WARNING
- INFO

Result is immutable and bound to `project_revision`. Revision change makes prior result STALE.

Canonical `Asset.availability` remains `online/offline/missing`.
CORRUPT/DUPLICATE are derived validation/media-health projections for W8.

## Relink contract

Candidate ranking:
1. exact canonical Axxx basename + compatible probe;
2. exact source_name + compatible media/metadata;
3. exact SHA-256 fingerprint;
4. compatible metadata candidate = manual choice only.

Filename similarity alone never auto-applies. Explicit confirmation is required before commit.
Relink preserves Asset ID and clip references. One confirmed multi-relink operation is one
intentional `CommandBatch`.

## Recovery contract

- autosave never silently overwrites source;
- snapshot identity supports project_id + revision + timestamp;
- old revision/hash snapshots remain discoverable;
- default retention max 20 validated managed snapshots/project;
- source `.angproj` and `.bak` are never prune targets;
- unclean session + valid newer snapshot produces explicit recovery decision;
- recovered snapshot opens as working state and source remains untouched until Save;
- corrupt snapshot is isolated/reported, not destructive.

## Diagnostics contract

Structured safe fields include timestamp/severity/subsystem/action/job/project/revision/error code.
Never include raw credentials, full prompt/subtitle/narration/media by default. Paths are redacted
where practical. Diagnostic bundle manifest must be deterministic and secret-scannable.

## Frozen UI reuse

No new UI image-generation gate is required:
- UI-039 — Pemulihan Project — Final Parity Variant;
- UI-040 — Asset Scan — Final Parity Variant;
- UI-041 — Validation Center — Final Parity Variant.

Existing geometry/hierarchy remains frozen. Any structural delta requires DELTA_FROM_AAVC.

## Serial implementation contract

- **W8-001 — Canonical Validation Contracts + Baseline Rules — READY**
- W8-002 — Real Media Integrity + Validation Center Projection — BLOCKED_BY_W8_001
- W8-003 — Single Asset Relink Command + Exact Identity Preservation — BLOCKED_BY_W8_002
- W8-004 — Batch Directory Relink Scan + Candidate Ranking — BLOCKED_BY_W8_003
- W8-005 — Autosave Catalog + Retention Hardening — BLOCKED_BY_W8_004
- W8-006 — Crash Marker + Startup Recovery Decision — BLOCKED_BY_W8_005
- W8-007 — Atomic Persistence Failure Injection + Remediation — BLOCKED_BY_W8_006
- W8-008 — Stale Result Hardening for Validation/Relink/Recovery Jobs — BLOCKED_BY_W8_007
- W8-009 — Structured Diagnostics + Redacted Diagnostic Bundle — BLOCKED_BY_W8_008
- W8-010 — Frozen UI Wiring + GOLDEN-03 Recovery/Relink Closure + Regression Lock — BLOCKED_BY_W8_009

Every task must pass Ruff, mypy, import contracts, architecture, source-of-truth, no-secret,
frozen UI manifest, targeted tests, full pytest and task-specific deterministic/real evidence.
Media/filesystem tasks require real-file evidence. Final W8 regression must include all prior
implementation families plus every W8 family on the same accepted HEAD.

## Non-goals

- no STEP 12 export matrix;
- no legacy AAVC importer;
- no 100–300 scene stress wave;
- no UI redesign/regeneration;
- no new AI editing capability;
- no auto-relink by filename similarity;
- no source overwrite during recovery without explicit Save.

## Exact next action

After owner says `lanjutkan`, execute **SOL S11-W8-001 only — Canonical Validation Contracts + Baseline Rules**.

Do not start W8-002 in the same turn. Report W8-001 gate PASS/FAIL and stop.
