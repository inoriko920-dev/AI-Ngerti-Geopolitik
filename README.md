# AI Ngerti Geopolitik

> **STATUS: SF-STEP 11 ACTIVE — W6 CLOSED PROVISIONAL LIVE GEMINI — W7 CONTRACT_LOCKED — W7-001..004 PASS — NEXT W7-005**

Repository resmi aplikasi **AI Ngerti Geopolitik**.

Baca `AGENTS.md` lalu `docs/SOURCE_OF_TRUTH_INDEX.md`.

## W7 progress

Completed:
- W7-001 canonical L2 command contracts + capability registry = **PASS**;
- W7-002 L2 ContextBuilder + selected-scope contract = **PASS**;
- W7-003 strict AutoEditPlan v2 parser/schema = **PASS**;
- W7-004 L2 semantic verifier + sequential dry-run translator = **PASS**.

Accepted W7-004 implementation:
`05bbf416e3f4440b23b23a8912aa86e2d1a39d44`

Workflow:
`37650364257` — SUCCESS.

W7-004 now proves:
- stale/selected-scope/target/lock semantic gates;
- dynamic duration/source/canvas/transition checks;
- application-owned ripple for AI duration/speed;
- sequential translation through existing manual commands;
- candidate transition legality after pacing;
- candidate semantic-hash proof;
- zero canonical ProjectState mutation;
- zero CommandBus history mutation.

Targeted W7-004 tests: **24/24 PASS**.  
Full pytest: **PASS**.  
Evidence verifier: **23/23 PASS**.  
Regression matrix: **26/26 workflows SUCCESS**, all attempt 1.

W6 remains closed as **PASS_WITH_PROVISIONAL_LIVE_GEMINI** because no real live
Gemini credential was available during W6 closure.

## Next

**S11-W7-005 — Pacing qualification: duration + speed only.**
