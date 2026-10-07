# S11-W8-001 — CANONICAL VALIDATION CONTRACTS + BASELINE RULES

**Status:** PASS  
**Accepted implementation HEAD:** `fd319947ea8ce2579de4918b5c4b49c046851609`  
**Accepted workflow:** `37681708473` — SUCCESS  
**Artifact:** `ANG-S11-W8-001-Validation-Contracts`  
**Artifact ID:** `11509960710`  
**Artifact size:** 556 bytes  
**Artifact SHA-256:** `0f6e60a2bc4ee43477b5026f6a7ba1ae222cf25c9d63d0368de6c82198ec67b0`

## Scope

W8-001 establishes the canonical application-layer validation model and baseline
non-mutating rules only.

It intentionally does **not** implement:
- real filesystem/media probing;
- relink command or directory scan;
- recovery catalog/crash marker;
- diagnostic bundle;
- runtime Validation Center UI projection.

Those remain W8-002 and later serial tasks.

## Canonical contracts

Added:
`src/ai_ngerti_geopolitik/application/validation.py`.

Typed severity:
- BLOCKER;
- ERROR;
- WARNING;
- INFO.

Typed scope:
- PROJECT;
- MEDIA;
- TIMELINE_SCENE;
- SUBTITLE;
- NARRATION;
- AI;
- RENDER;
- RUNTIME.

Typed remediation actions:
- REVALIDATE;
- RELINK_MEDIA;
- OPEN_SUBTITLE;
- OPEN_NARRATION;
- NONE.

Baseline issue codes:
- PROJECT_INVALID;
- MEDIA_MISSING_REFERENCED;
- MEDIA_MISSING_UNREFERENCED;
- MEDIA_OFFLINE_REFERENCED;
- MEDIA_OFFLINE_UNREFERENCED.

`ValidationIssue` is frozen, safe-message bounded, revision-bound and carries exact
target IDs. It is not stored in `ProjectState`.

`ValidationResult` is frozen and bound to:
- project_id;
- project_revision;
- project semantic SHA-256;
- deterministic issue tuple.

## Stale safety

`ValidationResult.is_stale()` rejects:
- a different project;
- a changed revision;
- a same-revision semantic replacement.

This extends the existing stale-safety principle without creating a second project
or session owner.

## Baseline rules

`CanonicalStateRule` reuses `ProjectState.validate()`.

Therefore existing canonical structural rules remain the authority for:
- schema/project validity;
- timeline/asset references;
- subtitle cue/timing/animation validity;
- narration asset/timing/fade validity.

A canonical structural failure produces one PROJECT/BLOCKER issue and short-circuits
derived rules so an invalid state does not generate misleading follow-on issues.

`MediaAvailabilityRule` reads existing canonical `Asset.availability` only:
- referenced missing media => BLOCKER;
- referenced offline media => ERROR;
- unreferenced missing media => WARNING;
- unreferenced offline media => INFO.

Referenced target IDs include the stable Asset ID plus exact Clip/Narration IDs.

W8-001 does not add CORRUPT/DUPLICATE to canonical availability. Those remain
derived media-health projections for W8-002.

## Determinism / non-mutation

Validation:
- reads canonical ProjectState only;
- performs no CommandBus/CommandBatch mutation;
- performs no filesystem/network/provider/engine work;
- compares canonical semantic JSON before/after rule execution;
- raises if a rule mutates the canonical state;
- sorts issues deterministically by severity, scope, code and target IDs.

Deterministic evidence proves the same input returns the exact same result.

## Targeted tests

`tests/unit/test_step11_w8_001_validation.py`

Result: **9/9 PASS**.

Coverage:
- frozen typed issue contract and safe text guards;
- deterministic non-mutating projection;
- referenced missing blocker;
- referenced offline narration error;
- unreferenced missing warning;
- unreferenced offline info;
- invalid canonical project short-circuit blocker;
- revision/project/same-revision semantic stale detection;
- result/issue revision consistency.

## Full quality gates

Workflow `37681708473`:
- uv lock/frozen sync PASS;
- Ruff format PASS;
- Ruff check PASS;
- mypy **69 source files / 0 issues**;
- import contracts **4 kept / 0 broken**;
- architecture PASS;
- source-of-truth **70/70 PASS**;
- no-secret PASS;
- frozen UI references **42/42 PASS**;
- targeted tests **9/9 PASS**;
- full pytest **395/395 PASS**;
- deterministic evidence PASS;
- evidence verifier **22/22 PASS**;
- artifact upload PASS.

## Regression lock

On accepted implementation HEAD
`fd319947ea8ce2579de4918b5c4b49c046851609`:

- **27/27 triggered workflow families SUCCESS**;
- all 27 succeeded on attempt 1;
- S08 Windows portable foundation PASS;
- S09 Windows UI shell PASS;
- S10 Windows E2E + packaged real-media smoke PASS;
- W0 engine qualification PASS;
- W1–W7 regression families PASS;
- W8-001 PASS.

No prior-wave regression remains on the accepted W8-001 HEAD.

## Safety boundary

- no project mutation;
- no filesystem scan/probe added by validation service;
- no relink implementation;
- no recovery implementation;
- no diagnostics implementation;
- no runtime UI change;
- no STEP 12 export work.

## Next

**S11-W8-002 — Real Media Integrity + Validation Center Projection — READY.**

Do not start W8-003 in the same turn as W8-002.
