# PROJECT STATUS — AI NGERTI GEOPOLITIK

**Current STEP:** SF-STEP 11 — Feature Implementation Waves  
**Current wave:** **W6 — Gemini Credential + L1 AI Animation Planning**  
**W6 status:** **CONTRACT_LOCKED / W6-001..008 PASS / W6-009 READY**  
**Previous wave:** W5 — CLOSED / PASS_WITH_PROVISIONAL_MIC_HARDWARE  
**Accepted W6-008 implementation HEAD:** `544bbde03a55c673e26b5e933b04c23b5336ba42`  
**Accepted W6-008 workflow:** `37613133911` — SUCCESS  
**Next exact task:** **S11-W6-009 — Frozen UI parity**

## W6-008 proven

Approval lifecycle:
- only W6-007 successful verified results can be staged;
- verified result is consumed once;
- states PENDING / APPROVED / REJECTED / CANCELLED / APPLIED;
- staging/approval/reject/cancel do not mutate ProjectState;
- apply requires explicit APPROVED state;
- duplicate stage/apply is rejected.

Stale/revalidation gate:
- project ID, base revision and semantic hash are checked before apply;
- W6-006 PlanVerifier is executed again immediately before canonical mutation;
- translated candidate must match the previously verified candidate semantic hash.

Canonical apply:
- AI proposals become existing W4 `SetClipPropertiesCommand` commands;
- partial proposals preserve unspecified effect values;
- one EditPlan creates one `CommandBatch`;
- one batch causes one revision increment;
- CommandBus remains the only canonical mutation/history owner;
- one Undo restores before semantics for the entire AI plan;
- one Redo restores applied semantics.

## W6-008 gates

Workflow `37613133911`:
- uv lock PASS;
- Ruff format/check PASS;
- mypy PASS — 62 source files;
- import contracts PASS;
- architecture PASS;
- source-of-truth 70/70 PASS;
- no-secret scan PASS;
- frozen UI references 42/42 PASS;
- targeted W6-008 tests **9/9 PASS**;
- full pytest PASS;
- deterministic evidence PASS;
- evidence verifier **15/15 PASS**;
- artifact upload PASS.

Artifact:
- `ANG-S11-W6-008-Approval-CommandBatch`;
- ID `11479655608`;
- size 412 bytes;
- SHA-256 `34d85ae83a39b97d94bee06d758643f51e5793ec4ddca68f001299d05f9668ea`.

## Regression lock on accepted W6-008 implementation HEAD

All SUCCESS, attempt 1:
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

S08 portable build/smoke PASS. S10 packaged real-media smoke PASS.

## Exact next action

After owner says **lanjutkan**, execute **S11-W6-009 only — Frozen UI parity**.

Use the existing frozen AAVC UI references. Do not regenerate the void 42-prompt UI set,
and do not perform live Gemini closure in W6-009.
