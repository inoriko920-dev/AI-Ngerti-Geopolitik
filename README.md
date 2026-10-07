# AI Ngerti Geopolitik

> **STATUS: SF-STEP 11 ACTIVE — W5 CLOSED — W6 CONTRACT_LOCKED — W6-001..006 PASS — NEXT W6-007**

Repository resmi aplikasi **AI Ngerti Geopolitik**.

Baca `AGENTS.md` lalu `docs/SOURCE_OF_TRUTH_INDEX.md`.

## W6 progress

Completed:
- W6-001 canonical AI + credential contracts = PASS
- W6-002 secure logical credential slots 1–100 = PASS
- W6-003 Windows secure-store qualification = PASS
- W6-004 credential health + safe failover = PASS
- W6-005 L1 ContextBuilder + allowlist = PASS
- W6-006 strict EditPlan schema + PlanVerifier = PASS

W6-006 accepted implementation:
`571cf941e64124628d1f8dadafb022eb20c0a541`

Workflow:
`37606369024` — SUCCESS.

Now available:
- strict EditPlan JSON parser with exact root/command fields;
- max 20 L1 commands and fixed `set_clip_effects` capability;
- target existence + selected-scope enforcement;
- effect/range, lock, stale revision and request-ID correlation gates;
- dry-run through the same W4 `SetClipPropertiesCommand` path used by manual editing;
- zero canonical mutation and no CommandBus history during verification.

Targeted W6-006 tests: **12/12 PASS**.  
Full pytest: **PASS**.  
Evidence verifier: **24/24 PASS**.

All W6-005 through S08 regression workflows are green on the same implementation HEAD.

No Gemini network, provider background job, approval/apply, CommandBatch integration or W6 UI is implemented by W6-006.

## Next

**S11-W6-007 — Gemini adapter + async lifecycle only.**
