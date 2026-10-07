# S11-W6-010 — LIVE GEMINI + FAILURE + REGRESSION CLOSURE

**Status:** PASS_WITH_PROVISIONAL_LIVE_GEMINI  
**Accepted implementation HEAD:** `0915a7045014e5ea1209f933dd703d6601ff26e9`  
**Accepted workflow:** `37628909459` — SUCCESS  
**Artifact:** `ANG-S11-W6-010-Closure`  
**Artifact ID:** `11485567340`  
**Artifact size:** 572,559 bytes  
**Artifact SHA-256:** `7ee54212f333b685ffa986f81a6b58810fb07a4969ebe61bf767888a00f113ba`

## Closure objective

W6-010 closes the W6 software path without faking live-provider evidence.

It proves:
- valid L1 provider plan → PlanVerifier → explicit approval → one CommandBatch;
- deterministic provider/plan failure safety;
- stale and lock safety;
- render-backed effect visibility;
- exact Undo/Redo;
- secret-safe evidence;
- final regression lock.

It also attempts live Gemini qualification only when a real credential is available.

## Deterministic targeted tests

Target:
`tests/unit/test_step11_w6_010_closure.py`

Result:
**6/6 PASS**.

Covered:
1. valid chain: one provider call, atomic apply, exact Undo/Redo;
2. invalid-auth exhaustion: disabled affected credential, zero mutation;
3. rate-limit/quota: one request only, no credential rotation, zero mutation;
4. malformed provider payload: schema failure, zero mutation;
5. lock conflict: hard reject, zero mutation;
6. stale project after provider success: AI plan is not staged/applied.

## AI → render proof

Runner:
`scripts/run_step11_w6_010.py`

The deterministic closure:
- generated owned real media;
- built canonical project state;
- generated bounded L1 context;
- provider proposed `Rise` with intensity `120`;
- W6-006 verified it;
- W6-008 explicitly staged, approved and applied it;
- W4 FFmpeg qualification engine rendered baseline and AI-applied previews.

Evidence:
- selected effect = `Rise`;
- selected intensity = `120`;
- `render_effect_visible = true`;
- baseline and AI-applied SHA-256 differ;
- one revision apply = true;
- exact Undo = true;
- exact Redo = true.

This proves the AI selection reaches a render-backed W4 effect rather than only
changing a DTO or UI label.

## Live Gemini qualification

Runner:
`scripts/run_step11_w6_010_live.py`

Designed live path:
1. receive transient CI credential only if supplied;
2. place it into Windows Credential Manager;
3. remove it from process environment;
4. load it through `WindowsCredentialStore`;
5. call official `GeminiAIProvider`;
6. verify returned L1 plan;
7. explicit approval/apply;
8. exact Undo/Redo;
9. remove secure-store credential;
10. scan evidence for raw credential leakage.

Actual accepted run:
- live credential available = **false**;
- request attempted = **false**;
- official live adapter request = **not executed**;
- live report = `PROVISIONAL_NO_CREDENTIAL`.

Therefore W6 is **not** full live-provider PASS.

Final accepted status:
**PASS_WITH_PROVISIONAL_LIVE_GEMINI**.

## CI gates

Workflow `37628909459`:
- FFmpeg toolchain PASS;
- uv lock/sync PASS;
- Ruff format/check PASS;
- mypy PASS — 63 source files;
- import contracts PASS;
- architecture PASS;
- source-of-truth 70/70 PASS;
- no-secret verifier PASS;
- UI-reference integrity 42/42 PASS;
- targeted W6-010 tests 6/6 PASS;
- full pytest PASS;
- owned fixture generation PASS;
- deterministic AI → render closure PASS;
- optional live step completed with provisional no-credential report;
- evidence verifier PASS;
- artifact upload PASS.

## Final regression lock

All **25/25** workflow families are SUCCESS on `0915a7045014e5ea1209f933dd703d6601ff26e9`, all attempt 1:

- S08 `37628909435` — SUCCESS, attempt 1
- S09 `37628909324` — SUCCESS, attempt 1
- S10 `37628909385` — SUCCESS, attempt 1
- W0 `37628909327` — SUCCESS, attempt 1
- W1 `37628909561` — SUCCESS, attempt 1
- W2 `37628909475` — SUCCESS, attempt 1
- W3 `37628909545` — SUCCESS, attempt 1
- W4 `37628909381` — SUCCESS, attempt 1
- W5-004 `37628909273` — SUCCESS, attempt 1
- W5-005 `37628909461` — SUCCESS, attempt 1
- W5-006 `37628909408` — SUCCESS, attempt 1
- W5-007 `37628909315` — SUCCESS, attempt 1
- W5-008 `37628909292` — SUCCESS, attempt 1
- W5-009 `37628909521` — SUCCESS, attempt 1
- W5-010 `37628909748` — SUCCESS, attempt 1
- W6-001 `37628909300` — SUCCESS, attempt 1
- W6-002 `37628909577` — SUCCESS, attempt 1
- W6-003 `37628909598` — SUCCESS, attempt 1
- W6-004 `37628909335` — SUCCESS, attempt 1
- W6-005 `37628909445` — SUCCESS, attempt 1
- W6-006 `37628909506` — SUCCESS, attempt 1
- W6-007 `37628909456` — SUCCESS, attempt 1
- W6-008 `37628909610` — SUCCESS, attempt 1
- W6-009 `37628909407` — SUCCESS, attempt 1
- W6-010 `37628909459` — SUCCESS, attempt 1

No product regression remains on the accepted W6-010 implementation HEAD.

## Promotion rule

W6 may be promoted from `PASS_WITH_PROVISIONAL_LIVE_GEMINI` only after a real
Gemini credential is supplied and the live secure-store qualification path executes
successfully. A fake provider, deterministic provider or an absent credential cannot
satisfy that gate.

## Next

W7 — AI Auto Edit L2 — is not started.

The next owner instruction should begin ASTRA planning/contract work only, with the
required detailed planning DOCX before SOL implementation.
