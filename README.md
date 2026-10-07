# AI Ngerti Geopolitik

> **STATUS: SF-STEP 11 ACTIVE — W5 CLOSED — W6 CONTRACT_LOCKED — W6-001..007 PASS — NEXT W6-008**

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
- W6-007 official Gemini adapter + async lifecycle = PASS

W6-007 accepted implementation:
`70fa8cd6f800166176889068202ab53d03044b24`

Workflow:
`37609729091` — SUCCESS.

Now available:
- official `google-genai==2.28.0` runtime locked by uv;
- Gemini adapter behind `AIProviderPort`;
- async SDK request with structured EditPlan JSON schema;
- background provider lifecycle off the caller/Qt GUI thread;
- cancellation, timeout and typed provider-error mapping;
- W6-004 credential-pool retry/failover/cooldown integration;
- project/session/revision stale-result guard;
- one-time verified-result consumption;
- zero CommandBus/canonical mutation in W6-007.

Targeted W6-007 tests: **17/17 PASS**.  
Full pytest: **PASS**.  
Evidence verifier: **11/11 PASS**.  
Official SDK runtime smoke: **PASS**.

All W6-006 through S08 regression workflows are green on the same implementation HEAD.

Real Gemini network qualification is intentionally deferred to W6-010. W6-007 does
not claim live-provider PASS.

## Next

**S11-W6-008 — Approval → CommandBatch → Undo/Redo only.**
