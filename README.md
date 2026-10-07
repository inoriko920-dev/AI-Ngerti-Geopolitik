# AI Ngerti Geopolitik

> **STATUS: SF-STEP 11 ACTIVE — W6 CLOSED PROVISIONAL LIVE GEMINI — W7 CONTRACT_LOCKED — W7-001..008 PASS — NEXT W7-009**

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
- W7-008 Gemini L2 request profile + lifecycle reuse = **PASS**.

Accepted W7-008 implementation:
`fa142e4d7eee21f79f79837339e76dfb974b8ba8`

Workflow:
`37671042698` — SUCCESS.

W7-008 proves:
- one shared Gemini provider supports frozen W6 L1 and W7 L2 profiles;
- W6 AIProviderRequest field contract remains unchanged;
- canonical AutoEditPlan schema v2 is used for L2 structured output;
- same credential pool + background job lifecycle are reused;
- L1/L2 verified results have separate safe accessors;
- invalid-auth failover, cancellation and stale-session behavior are reused;
- canonical ProjectState remains unchanged;
- no approval/apply/UI integration is introduced.

Targeted W7-008 tests: **9/9 PASS**.  
Full pytest: **370/370 PASS**.  
Evidence verifier: **1/1 PASS**.  
Regression matrix: **26/26 SUCCESS, all attempt 1**.

Artifact:
`ANG-S11-W7-008-Gemini-L2-Lifecycle` / ID `11505072385`.

W6 remains closed as **PASS_WITH_PROVISIONAL_LIVE_GEMINI** because no real live
Gemini credential was available for a network success claim.

## Next

**S11-W7-009 — Approval/apply/UI diff integration only.**
