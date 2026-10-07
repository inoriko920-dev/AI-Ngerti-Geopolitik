# S11 W6-006 — EditPlan Schema + PlanVerifier

**Status:** PASS  
**Accepted implementation HEAD:** `571cf941e64124628d1f8dadafb022eb20c0a541`  
**Accepted workflow:** `37606369024` — SUCCESS  
**Artifact:** `ANG-S11-W6-006-EditPlan-PlanVerifier`  
**Artifact ID:** `11475207107`  
**Artifact size:** 800 bytes

## Scope

W6-006 implements strict provider EditPlan parsing and non-mutating semantic verification.

It intentionally does not implement:
- Gemini SDK/network;
- provider background jobs;
- approval/apply;
- CommandBatch/Undo/Redo integration;
- W6 UI.

## Application implementation

Added:
`src/ai_ngerti_geopolitik/application/ai_plan_verifier.py`.

Canonical owner:
`PlanVerifier`.

Proof DTO:
`VerifiedEditPlan`.

The verifier returns:
- the validated immutable EditPlan;
- dry-run candidate semantic hash;
- candidate revision;
- command count.

It does not return a mutable/applyable alternate ProjectState path.

## Strict JSON/schema parser

Root must contain exactly:
- schema_version;
- base_project_revision;
- request_id;
- summary;
- commands.

Rules:
- root must be a JSON object;
- schema version must be strict integer 1;
- base revision must be a strict integer;
- request ID and summary must be strings;
- commands must be a non-empty array;
- maximum 20 L1 commands.

Each command:
- must be a JSON object;
- required: command_type, target_clip_id;
- optional changes: enter_effect, exit_effect, intensity_percent;
- no unknown command fields;
- command type exactly `set_clip_effects`;
- at least one effect change;
- effect values must be strings;
- intensity must be a strict integer, so boolean values are rejected.

Malformed JSON, unknown root/command fields, missing fields, invalid scalar types and
unsupported command types fail as SCHEMA_INVALID.

## Semantic gates

- EditPlan base revision must equal current ProjectState revision;
- ProviderPlanResponse request ID must match inner EditPlan request ID;
- allowed selected-target scope is mandatory;
- allowed target IDs must be unique, non-empty and at most 20;
- proposed clip must be in selected scope;
- proposed clip must exist in canonical ProjectState;
- unsupported W4 effects fail as SEMANTIC_INVALID;
- intensity outside 0..200 fails as SEMANTIC_INVALID;
- track lock or effect lock fails as LOCK_CONFLICT;
- stale revision fails as STALE_PLAN.

## Manual command parity dry-run

For every validated proposal:
1. current target is resolved from the local candidate ProjectState;
2. current effect values are read;
3. unspecified effect fields remain unchanged;
4. lock state remains unchanged;
5. canonical `EffectProperties` is constructed;
6. the exact manual W4 `SetClipPropertiesCommand` is applied to the local candidate.

The live ProjectState is never replaced and CommandBus is never executed.

Ordered proposals are dry-run in order against the previous candidate result.

## Zero-mutation proof

Tests and deterministic evidence compare the live semantic project JSON before/after
verification and prove it is unchanged.

Candidate revision remains equal to the base revision because no canonical history
transaction occurs.

## Deterministic tests

Target:
`tests/unit/test_step11_w6_006_plan_verifier.py`.

Coverage:
1. valid plan + manual-command dry-run + zero mutation;
2. malformed/root/unknown/missing/type schema rejection;
3. unknown command type/field rejection;
4. unknown and out-of-scope target rejection;
5. unsupported effect/range/type rejection;
6. effect-lock conflict;
7. track-lock conflict;
8. stale revision;
9. partial proposal preserves unspecified fields;
10. empty/over-bound commands rejection;
11. outer/inner request-ID mismatch;
12. ordered multi-command dry-run with no CommandBus history.

Result:
**12/12 PASS**.

## Quality gates

Workflow `37606369024`:
- Ruff format PASS;
- Ruff check PASS;
- mypy PASS — 59 source files;
- import contracts PASS;
- architecture PASS;
- source-of-truth 70/70 PASS;
- no-secret scan PASS;
- frozen UI references 42/42 PASS;
- targeted W6-006 tests 12/12 PASS;
- full pytest PASS;
- deterministic evidence PASS;
- evidence verifier 24/24 PASS;
- artifact upload PASS.

## Regression lock

All SUCCESS on accepted W6-006 implementation HEAD, all attempt 1:
- W6-005 `37606368964`;
- W6-004 `37606368943`;
- W6-003 `37606369038`;
- W6-002 `37606368839`;
- W6-001 `37606369003`;
- W5-010 `37606368937`;
- W5-009 `37606369064`;
- W5-008 `37606368830`;
- W5-007 `37606368954`;
- W5-006 `37606369030`;
- W5-005 `37606369016`;
- W5-004 `37606368963`;
- W4 `37606368993`;
- W3 `37606368996`;
- W2 `37606368898`;
- W1 `37606369019`;
- W0 `37606369029`;
- S10 `37606369131`;
- S09 `37606369020`;
- S08 `37606368969`.

## Next

**S11-W6-007 — Gemini adapter + async lifecycle only.**
