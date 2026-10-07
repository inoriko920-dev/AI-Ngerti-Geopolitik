# S11 W6-008 — Approval → CommandBatch → Undo/Redo

**Status:** PASS  
**Accepted implementation HEAD:** `544bbde03a55c673e26b5e933b04c23b5336ba42`  
**Accepted workflow:** `37613133911` — SUCCESS  
**Artifact:** `ANG-S11-W6-008-Approval-CommandBatch`  
**Artifact ID:** `11479655608`  
**Artifact size:** 412 bytes  
**Artifact SHA-256:** `34d85ae83a39b97d94bee06d758643f51e5793ec4ddca68f001299d05f9668ea`

## Scope

W6-008 implements the explicit approval boundary and canonical atomic apply path.

It intentionally does not implement:
- W6 UI;
- live Gemini qualification;
- AI L2.

## Application implementation

Added:
`src/ai_ngerti_geopolitik/application/ai_approval.py`.

Canonical owner:
`AIPlanApprovalService`.

States:
- PENDING;
- APPROVED;
- REJECTED;
- CANCELLED;
- APPLIED.

## Verified-result admission

A plan can enter approval only through `stage_from_job()`.

That path:
1. reads the current canonical CommandBus state;
2. calls W6-007 `AIPlanJobService.take_verified()`;
3. therefore requires a successful W6-006-verified provider result;
4. rechecks base revision;
5. records project ID + base semantic hash;
6. consumes the verified job result once;
7. creates a PENDING approval record without mutation.

Duplicate staging fails safely.

## Approval/cancel/reject

- PENDING → APPROVED is non-mutating.
- PENDING → REJECTED is terminal and non-mutating.
- PENDING/APPROVED → CANCELLED is terminal and non-mutating.
- apply before approval is rejected.
- rejected/cancelled plans cannot apply.

## Pre-apply safety

Immediately before canonical mutation:
- project ID must match;
- revision must equal plan base revision;
- semantic hash must equal the staged base hash;
- W6-006 PlanVerifier runs again;
- verified candidate semantic hash must match the original verified candidate.

This blocks revision-stale and same-revision semantic replacement cases.

## Canonical command translation

Each L1 proposal is translated sequentially using current candidate state into
the existing manual W4 `SetClipPropertiesCommand`.

Unspecified enter/exit/intensity fields are preserved.

The translated candidate semantic hash must equal the reverified candidate hash.

No AI-specific ProjectState mutation path exists.

## Atomic history

One approved plan creates:
- one `CommandBatch`;
- batch actor `ai`;
- expected revision = current canonical revision;
- all translated commands ordered inside that batch.

CommandBus applies the whole working candidate before commit, so:
- one AI plan increments revision once;
- one Undo reverts the entire AI plan;
- one Redo restores the entire applied semantic state;
- stale/failure before commit causes no AI history transaction.

## Deterministic targeted tests

Target:
`tests/unit/test_step11_w6_008_ai_approval.py`.

Result:
**9/9 PASS**.

Coverage:
- verified staging is zero mutation + one-consume;
- apply-before-approval rejection;
- reject zero mutation;
- cancel-after-approval zero mutation;
- two-command plan in one atomic batch;
- exact semantic Undo/Redo;
- duplicate apply rejection;
- revision-stale rejection;
- same-revision semantic replacement rejection;
- partial effect field preservation.

## Deterministic evidence

Proof:
- staged state PENDING;
- approved state APPROVED;
- applied state APPLIED;
- staging and approval do not change semantic hash;
- apply increments revision exactly once;
- two effect commands both appear;
- one Undo restores before semantics and leaves no earlier AI undo entry;
- one Redo restores applied semantics;
- batch ID is `AI-BATCH:REQ-EVIDENCE-008`;
- no W6 UI;
- no live Gemini network.

Evidence verifier:
**15/15 PASS**.

## Quality gates

Workflow `37613133911`:
- uv lock PASS;
- frozen dependency sync PASS;
- Ruff format PASS;
- Ruff check PASS;
- mypy PASS — 62 source files;
- import contracts PASS;
- architecture PASS;
- source-of-truth 70/70 PASS;
- no-secret scan PASS;
- UI-reference integrity 42/42 PASS;
- targeted W6-008 tests 9/9 PASS;
- full pytest PASS;
- deterministic evidence PASS;
- evidence verifier 15/15 PASS;
- artifact upload PASS.

## Regression lock

All SUCCESS on accepted W6-008 implementation HEAD, all attempt 1:
- W6-008 `37613133911`
- W6-007 `37613134080`
- W6-006 `37613134062`
- W6-005 `37613133875`
- W6-004 `37613133710`
- W6-003 `37613133646`
- W6-002 `37613134017`
- W6-001 `37613133838`
- W5-010 `37613133722`
- W5-009 `37613133835`
- W5-008 `37613133712`
- W5-007 `37613133955`
- W5-006 `37613133725`
- W5-005 `37613133778`
- W5-004 `37613133817`
- W4 `37613133949`
- W3 `37613133651`
- W2 `37613133793`
- W1 `37613133971`
- W0 `37613133751`
- S10 `37613133927`
- S09 `37613134030`
- S08 `37613133893`

S08 portable foundation build/smoke PASS.
S10 packaged real-media smoke PASS.

## Next

**S11-W6-009 — Frozen UI parity only.**
