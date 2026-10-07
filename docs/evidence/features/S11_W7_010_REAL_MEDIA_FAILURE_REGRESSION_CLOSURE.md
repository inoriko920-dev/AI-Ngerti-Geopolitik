# S11-W7-010 — REAL-MEDIA FAILURE / REGRESSION CLOSURE

**Status:** PASS_WITH_PROVISIONAL_LIVE_GEMINI  
**Accepted implementation HEAD:** `ca6dd582a4916caa4b0ac4affe4c3119e9ad2049`  
**Accepted workflow:** `37675538957` — SUCCESS  
**Artifact:** `ANG-S11-W7-010-Closure`  
**Artifact ID:** `11507307240`  
**Artifact size:** 5,864,179 bytes  
**Artifact SHA-256:** `6d9d2a6507f269f4ed8747f1448f885f88637016d868e36b95441f59ae9079af`

## Closure objective

W7-010 closes the bounded Auto Edit L2 wave without adding a new feature owner.

The final integrated path proves:

`L2ContextBuilder -> AIPlanJobService -> AutoEditPlanVerifier ->
AIPlanApprovalService -> CommandBatch(actor="ai") -> render/export -> save/reopen
-> Undo/Redo`.

No direct provider-to-ProjectState mutation exists.

## Integrated real-media proof

The owned Windows/FFmpeg fixture uses two real video clips with audio.

A deterministic L2 provider result contains six commands across the already
qualified W7 capability families:

1. L1 carry-forward effect change;
2. duration change;
3. transform change;
4. fade_black transition;
5. speed change;
6. fade_black transition on the second clip.

The result is verified, staged for review, explicitly approved and applied through
one canonical `CommandBatch(actor="ai")`.

Proof:
- review diff count = 6;
- all review lines are bounded before → after text;
- canonical state is unchanged before approval;
- apply increments project revision exactly once;
- final mixed timeline = 210 frames;
- real preview differs from baseline;
- real export = 210 frames within probe tolerance;
- real export retains audio;
- Rise effect reaches canonical state;
- position/scale/rotation/opacity transform reaches canonical state;
- fade_black transitions reach canonical state;
- source media SHA-256 remains unchanged.

## Persistence proof

After the approved AI transaction:
- project is saved as a real `.angproj`;
- a fresh `ProjectSession` reopens the saved project;
- reopened semantic hash exactly matches the applied semantic hash;
- reopened real preview SHA-256 exactly matches the applied preview SHA-256.

This closes the W7 persistence/save-reopen requirement.

## Atomic history proof

One approved mixed L2 plan is one history transaction:
- one apply = one revision increment;
- one Undo restores the exact pre-AI semantic hash;
- one Redo restores the exact applied semantic hash.

Reject/cancel and invalid plans do not create AI history entries.

## Failure taxonomy

Targeted closure tests prove zero unsafe canonical mutation for:
- invalid schema;
- out-of-range transform;
- target outside selected application scope;
- locked target;
- stale plan after concurrent manual edit;
- provider rate-limit/quota failure;
- invalid-auth exhaustion.

The valid control case also proves explicit approval + one atomic L2 transaction.

Targeted W7-010 tests: **8/8 PASS**.

## Quality gates

Workflow `37675538957` on final regression HEAD:
- FFmpeg toolchain PASS;
- uv lock/frozen sync PASS;
- Ruff format/check PASS;
- mypy PASS — 68 source files;
- import contracts PASS — 4 kept / 0 broken;
- architecture PASS;
- source-of-truth PASS — 70/70;
- no-secret PASS;
- frozen UI references 42/42 PASS;
- targeted W7-010 tests **8/8 PASS**;
- full pytest **386/386 PASS**;
- owned real-media fixture generation PASS;
- integrated real-media closure PASS;
- evidence verifier **9/9 files PASS**;
- artifact upload PASS.

## Final regression lock

On accepted final W7 HEAD
`ca6dd582a4916caa4b0ac4affe4c3119e9ad2049`:

- **27/27 workflow families SUCCESS**;
- all 27 succeeded on attempt 1;
- S08 Windows portable foundation PASS;
- S09 Windows UI shell PASS;
- S10 Windows E2E + packaged real-media smoke PASS;
- W0 engine qualification PASS;
- W1–W6 regression families PASS;
- W7-009 regression PASS;
- W7-010 closure PASS.

No product regression remains on the accepted W7 final HEAD.

## Live Gemini qualification

W7-010 deterministic closure did **not** use a real Gemini credential and makes
no live-network-success claim.

The W6 provider path remains
**PASS_WITH_PROVISIONAL_LIVE_GEMINI** until a real credential is supplied and the
existing secure-store live qualification succeeds.

Therefore final W7 status is:

**CLOSED / PASS_WITH_PROVISIONAL_LIVE_GEMINI**.

## Next boundary

W7 is finished.

Per Master Blueprint, the next product wave maps to:

**TECH-WAVE STEP 11 — Validation / recovery / diagnostics hardening**
(failure paths, relink batch, stale result, crash recovery).

That next wave has **not started**. The next owner instruction should start
**ASTRA planning only**, including a detailed planning DOCX before any SOL
implementation.
