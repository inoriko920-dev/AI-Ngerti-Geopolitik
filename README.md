# AI Ngerti Geopolitik

> **STATUS: SF-STEP 11 ACTIVE — W5 CLOSED — W6 CONTRACT_LOCKED — W6-001..009 PASS — NEXT W6-010**

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
- W6-008 approval → atomic CommandBatch → Undo/Redo = PASS
- W6-009 frozen AI / credential UI parity = PASS

W6-009 accepted implementation:
`7a2d79115e376205571bf529624993ed5fcc5f9f`

Workflow:
`37620520208` — SUCCESS.

W6-009 provides:
- real PySide6 AI Director / AI Agent / Provider & API Key surfaces;
- READY / PLAN / APPROVAL / APPLYING / SUCCESS / PROVIDER_ERROR / LOCK_CONFLICT / STALE;
- semantic-intent-only presentation boundary;
- masked credential slots 1..100;
- Gemini-only V1 provider surface;
- L1-only capability claims;
- actual-vs-frozen evidence against audited physical refs
  UI-020/021/022/023/024/033.

Targeted W6-009 tests: **8/8 PASS**.  
Full pytest: **PASS**.  
Evidence verifier: **15/15 PASS**.

All 24 regression workflows through S08 are green on the same accepted implementation
HEAD. S10 packaged smoke required a retry only because Chocolatey returned HTTP 504
while fetching FFmpeg; no product-code change was needed.

Real Gemini network qualification remains **W6-010**.

## Next

**S11-W6-010 — Live Gemini + failure + regression closure only.**
