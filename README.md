# AI Ngerti Geopolitik

> **STATUS: SF-STEP 11 ACTIVE — W6 CLOSED PROVISIONAL LIVE GEMINI — W7 CONTRACT_LOCKED — W7-001..002 PASS — NEXT W7-003**

Repository resmi aplikasi **AI Ngerti Geopolitik**.

Baca `AGENTS.md` lalu `docs/SOURCE_OF_TRUTH_INDEX.md`.

## W7 progress

W7 maps to Master Blueprint TECH-WAVE STEP 10: bounded AI Auto Edit L2.

Completed:
- W7-001 canonical L2 command contracts + capability registry = **PASS**;
- W7-002 L2 ContextBuilder + selected-scope contract = **PASS**.

Accepted W7-002 implementation:
`23aad912cb789f98dd3ec61d11e799390d602381`

Workflow:
`37644007477` — SUCCESS.

W7-002 now provides:
- selected scope 1..20 stable unique clips;
- deterministic schema-v2 L2 context;
- source-duration availability for pacing validation;
- bounded speed/transform/transition/effect state;
- lock/editability state;
- one previous + one next neighbor;
- exact W7 policy bounds and capability allowlist;
- exclusion of credentials, paths, media bytes, logs and unrelated content;
- zero ProjectState mutation.

Targeted W7-002 tests: **18/18 PASS**.  
Full pytest: **PASS**.  
Evidence verifier: **24/24 PASS**.  
Regression matrix: **26/26 triggered workflows SUCCESS**, all attempt 1.

W6 remains closed as **PASS_WITH_PROVISIONAL_LIVE_GEMINI** because no real live
Gemini credential was available during W6 closure.

## Next

**S11-W7-003 — strict AutoEditPlan v2 parser/schema only.**

Semantic verification and sequential dry-run remain W7-004.
