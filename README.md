# AI Ngerti Geopolitik

> **STATUS: SF-STEP 11 ACTIVE — W5 CLOSED — W6 CONTRACT_LOCKED — W6-001/002/003/004 PASS — NEXT W6-005**

Repository resmi aplikasi **AI Ngerti Geopolitik**.

Baca `AGENTS.md` lalu `docs/SOURCE_OF_TRUTH_INDEX.md`.

## W6 progress

Completed:
- W6-001 canonical AI + credential contracts = PASS
- W6-002 secure logical credential slots 1–100 = PASS
- W6-003 Windows secure-store qualification = PASS
- W6-004 credential health + safe failover = PASS

W6-004 accepted implementation:
`2ebe3fbd89e0cbbf62135a44bb2e4193c4906e32`

Workflow:
`37602706734` — SUCCESS.

Now available:
- non-secret credential health states;
- invalid-auth isolation;
- bounded network retry and failover;
- provider-wide bounded cooldown for rate/quota outcomes;
- typed all-slots-unavailable handling;
- bulk TXT trim/dedupe/max100/count-only preview with no source retention.

Targeted W6-004 tests: **10/10 PASS**.  
Full pytest: **PASS**.  
Evidence verifier: **18/18 PASS**.

All W6-003/W6-002/W6-001/W5/W4/W3/W2/W1/W0/S10/S09/S08 regressions
are green on the same implementation HEAD.

No Gemini network call, ContextBuilder, PlanVerifier, W6 UI or AI-plan apply is
implemented by W6-004.

## Next

**S11-W6-005 — L1 ContextBuilder + allowlist only.**
