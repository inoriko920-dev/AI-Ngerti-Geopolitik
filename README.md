# AI Ngerti Geopolitik

> **STATUS: SF-STEP 11 ACTIVE — W6 CLOSED PROVISIONAL LIVE GEMINI — W7 CONTRACT_LOCKED — W7-001..003 PASS — NEXT W7-004**

Repository resmi aplikasi **AI Ngerti Geopolitik**.

Baca `AGENTS.md` lalu `docs/SOURCE_OF_TRUTH_INDEX.md`.

## W7 progress

W7 maps to Master Blueprint TECH-WAVE STEP 10: bounded AI Auto Edit L2.

Completed:
- W7-001 canonical L2 command contracts + capability registry = **PASS**;
- W7-002 L2 ContextBuilder + selected-scope contract = **PASS**;
- W7-003 strict AutoEditPlan v2 parser/schema = **PASS**.

Accepted W7-003 implementation:
`a57c8acd96cdcff8b20f659171229ad0bff913d0`

Workflow:
`37647150710` — SUCCESS.

W7-003 now provides:
- closed canonical JSON Schema v2;
- exact root fields;
- five exact command shapes;
- strict integer typing with booleans rejected;
- unknown root/command/field hard rejection;
- no provider-selected ripple;
- no crop/crossfade/unlock fields;
- conversion into W7-001 typed DTOs;
- 1..40 command bound;
- zero ProjectState/CommandBus/provider/UI/apply work.

Targeted W7-003 tests: **41/41 PASS**.  
Full pytest: **PASS**.  
Evidence verifier: **24/24 PASS**.  
Regression matrix: **26/26 workflows SUCCESS**, all attempt 1.

W6 remains closed as **PASS_WITH_PROVISIONAL_LIVE_GEMINI** because no real live
Gemini credential was available during W6 closure.

## Next

**S11-W7-004 — L2 semantic verifier + sequential dry-run translator only.**
