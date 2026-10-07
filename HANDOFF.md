# HANDOFF — AI NGERTI GEOPOLITIK

**Current phase:** SF-STEP 11  
**Current wave:** W6 — Gemini Credential + L1 AI Animation Planning  
**Last completed task:** S11-W6-008 — PASS  
**Accepted W6-008 implementation HEAD:** `544bbde03a55c673e26b5e933b04c23b5336ba42`  
**Accepted W6-008 workflow:** `37613133911` — SUCCESS  
**Next exact task:** S11-W6-009 — Frozen UI parity  
**Previous W5 status:** PASS_WITH_PROVISIONAL_MIC_HARDWARE

## W6-008 implementation now available

Application:
- `application/ai_approval.py` is the single approval/apply owner;
- only a successful W6-007 job result already verified by W6-006 may be staged;
- staging consumes the verified job result once and creates a non-mutating approval record;
- states: PENDING / APPROVED / REJECTED / CANCELLED / APPLIED.

Approval boundary:
- staging = zero canonical mutation;
- approve = zero canonical mutation;
- reject = terminal zero mutation;
- cancel before apply = terminal zero mutation;
- apply is impossible until explicit APPROVED state;
- duplicate staging and duplicate apply fail safely.

Pre-apply safety:
- current project ID must still match;
- base revision must still match;
- base semantic hash must still match;
- PlanVerifier runs again immediately before apply;
- verified candidate semantic hash must still match;
- commands are translated sequentially through the existing manual
  `SetClipPropertiesCommand` path.

Atomic history:
- one approved EditPlan becomes exactly one `CommandBatch`;
- batch actor is `ai`;
- CommandBus increments revision once for the whole plan;
- a two-command AI plan is reverted by one Undo;
- Redo restores the exact applied semantic state;
- failed/stale/rejected/cancelled plans add no AI history transaction.

Still not implemented:
- W6 frozen UI widgets;
- live Gemini qualification/closure;
- AI L2.

## Tests/evidence

Targeted W6-008 tests: **9/9 PASS**.  
Full pytest: **PASS**.  
Evidence verifier: **15/15 PASS**.  
Workflow: `37613133911` — **SUCCESS**.

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

S08 portable build/smoke and S10 packaged real-media smoke both PASS.

## Critical boundaries for W6-009

- use frozen AAVC UI references UI-010/011/012/013/014/023;
- AAVC remains read-only;
- existing 42-prompt UI regeneration is VOID / DO NOT USE;
- semantic UI intents only; no direct ProjectState/provider mutation from presentation;
- expose READY / PLAN / APPROVAL / APPLYING / SUCCESS / PROVIDER_ERROR /
  LOCK_CONFLICT / STALE states truthfully;
- only W6 L1 capabilities may be claimed;
- credential display remains masked; never reveal raw keys;
- no live Gemini closure yet.

## Next exact action

After owner says `lanjutkan`, execute **S11-W6-009 only — Frozen UI parity**.
