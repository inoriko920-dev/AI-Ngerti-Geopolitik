# PLAN — CURRENT IMPLEMENTATION PHASE

**SF-STEP 11 remains active. W6 is closed. W7 is CONTRACT_LOCKED and W7-001..008 are PASS.**

## Accepted W7-008

Implementation:
`fa142e4d7eee21f79f79837339e76dfb974b8ba8`

Workflow:
`37671042698` — SUCCESS.

Qualified:
- one existing GeminiAIProvider now supports bounded L1 and L2 request profiles;
- L1 remains schema v1 / effect-only and backward-compatible;
- L2 uses canonical AutoEditPlan schema v2;
- W6 AIProviderRequest stays frozen at exactly four dataclass fields;
- L2AIProviderRequest selects L2 without adding provider-request fields;
- same AIPlanJobService background worker is reused;
- same CredentialPoolService and provider error mapping are reused;
- L2 dispatches to AutoEditPlanVerifier + W7SelectedScope;
- take_verified() remains L1-only and take_verified_l2() is L2-only;
- cancellation, stale-session/revision and invalid-auth failover are shared;
- canonical ProjectState remains unchanged;
- no W7-009 approval/apply/UI integration started.

Evidence:
- targeted W7-008 tests 9/9 PASS;
- full pytest 370/370 PASS;
- official google-genai 2.28.0 runtime PASS;
- evidence verifier 1/1 PASS;
- 26/26 triggered workflow families SUCCESS, all attempt 1;
- S08 portable foundation PASS;
- S09 UI shell PASS;
- S10 Windows E2E PASS;
- all prior W0..W7 regression families green.

Artifact:
- `ANG-S11-W7-008-Gemini-L2-Lifecycle`;
- ID `11505072385`;
- SHA-256 `75207c3be32f8b967848719e48c3677de34e6608d063fe38121a6deb03f3be39`.

## Serial W7 plan

1. W7-001 canonical L2 command contracts + capability registry — **PASS**
2. W7-002 L2 ContextBuilder + selected-scope contract — **PASS**
3. W7-003 strict AutoEditPlan v2 parser/schema — **PASS**
4. W7-004 L2 semantic verifier + sequential dry-run translator — **PASS**
5. W7-005 pacing qualification — duration + speed — **PASS**
6. W7-006 transform qualification — **PASS**
7. W7-007 transition + mixed-plan qualification — **PASS**
8. W7-008 Gemini L2 request profile + lifecycle reuse — **PASS**
9. W7-009 approval/apply/UI diff integration — **READY**
10. W7-010 real-media closure + failure/regression lock — BLOCKED_BY_W7_009

## W7-009 boundary

W7-009 owns only:
- consume a successful verified L2 job result through explicit review/approval;
- final stale/hash/lock revalidation before apply;
- one atomic `CommandBatch(actor="ai")` for the approved mixed plan;
- one Undo / one Redo transaction;
- bounded before→after command differences on the existing frozen W6 AI surfaces;
- no new screen/layout unless the Software Factory UI gate is explicitly triggered.

It must not start:
- W7-010 final real-media/failure/regression closure.

Do not begin W7-009 until owner says `lanjutkan`.
