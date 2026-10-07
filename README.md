# AI Ngerti Geopolitik

> **STATUS: SF-STEP 11 ACTIVE — W5 CLOSED — W6 CONTRACT_LOCKED — W6-001/002/003/004/005 PASS — NEXT W6-006**

Repository resmi aplikasi **AI Ngerti Geopolitik**.

Baca `AGENTS.md` lalu `docs/SOURCE_OF_TRUTH_INDEX.md`.

## W6 progress

Completed:
- W6-001 canonical AI + credential contracts = PASS
- W6-002 secure logical credential slots 1–100 = PASS
- W6-003 Windows secure-store qualification = PASS
- W6-004 credential health + safe failover = PASS
- W6-005 L1 ContextBuilder + allowlist = PASS

W6-005 accepted implementation:
`043f8f250b7d61356bdf71757e8c6a7904615a06`

Workflow:
`37604630826` — SUCCESS.

Now available:
- bounded deterministic L1 provider context;
- stable target IDs + lock representation;
- media aspect/type metadata without filesystem paths;
- exact render-qualified W4 effect allowlist + intensity range;
- bounded one-before/one-after neighbor summary;
- untrusted project text isolation;
- no credential/API-key or private media metadata in context.

Targeted W6-005 tests: **10/10 PASS**.  
Full pytest: **PASS**.  
Evidence verifier: **23/23 PASS**.

All W6-004/W6-003/W6-002/W6-001/W5/W4/W3/W2/W1/W0/S10/S09/S08
regressions are green on the same implementation HEAD.

No Gemini network call, PlanVerifier, W6 UI or AI-plan apply is implemented by W6-005.

## Next

**S11-W6-006 — EditPlan schema + PlanVerifier only.**
