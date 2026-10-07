# AI Ngerti Geopolitik

> **STATUS: SF-STEP 11 ACTIVE — W6 CLOSED PROVISIONAL LIVE GEMINI — W7 CONTRACT_LOCKED — W7-001..009 PASS — NEXT W7-010**

Repository resmi aplikasi **AI Ngerti Geopolitik**.

Baca `AGENTS.md` lalu `docs/SOURCE_OF_TRUTH_INDEX.md`.

## W7 progress

Completed:
- W7-001 canonical L2 command contracts + capability registry = **PASS**;
- W7-002 L2 ContextBuilder + selected-scope contract = **PASS**;
- W7-003 strict AutoEditPlan v2 parser/schema = **PASS**;
- W7-004 L2 semantic verifier + sequential dry-run translator = **PASS**;
- W7-005 pacing qualification — duration + speed = **PASS**;
- W7-006 transform qualification = **PASS**;
- W7-007 transition + mixed-plan qualification = **PASS**;
- W7-008 Gemini L2 request profile + lifecycle reuse = **PASS**;
- W7-009 approval/apply/UI diff integration = **PASS**.

Accepted W7-009 implementation:
`2eef5762454f367c2fad5550f75209f8ffeb0a16`

Workflow:
`37673518251` — SUCCESS.

W7-009 proves:
- existing W6 approval service is reused for L2;
- explicit review/approval remains mandatory;
- final semantic/candidate-hash verification runs before apply;
- approved mixed L2 plan executes as one CommandBatch(actor="ai");
- revision increments once;
- one Undo / one Redo cover the whole AI transaction;
- reject/cancel create no history and duplicate apply is rejected;
- same-revision semantic replacement is stale;
- bounded before→after command differences are shown on the existing W6 plan surface;
- L2 mode is explicit while L1 remains backward-compatible;
- no new screen/layout is introduced.

Targeted W7-009 tests: **8/8 PASS**.  
Full pytest: **386/386 PASS**.  
Evidence verifier: **2/2 PASS**.  
Regression matrix: **26/26 SUCCESS, all attempt 1**.

Artifact:
`ANG-S11-W7-009-Approval-UI-Diff` / ID `11505484572`.

W6 remains closed as **PASS_WITH_PROVISIONAL_LIVE_GEMINI** because no real live
Gemini credential was available for a network success claim.

## Next

**S11-W7-010 — Real-media closure + failure/regression lock only.**
