# PLAN — CURRENT IMPLEMENTATION PHASE

**SF-STEP 11 remains active. W5 is closed. W6 is CONTRACT_LOCKED. W6-001..009 PASS.**

## Accepted W6-009

Implementation:
`7a2d79115e376205571bf529624993ed5fcc5f9f`

Workflow:
`37620520208` — SUCCESS.

Implemented:
- real PySide6 AI Director / AI Agent / credential-manager surfaces;
- semantic-intent-only presentation boundary;
- READY / PLAN / APPROVAL / APPLYING / SUCCESS / PROVIDER_ERROR /
  LOCK_CONFLICT / STALE projections;
- masked 1..100 credential slots;
- Gemini-only V1 provider presentation;
- L1-only effect claims;
- actual-vs-frozen screenshot evidence;
- physical frozen-raster correction:
  UI-020 Director, UI-021 Ready, UI-022 Plan, UI-023 Applied,
  UI-024 Provider unavailable, UI-033 Provider/API keys.

Gates:
- targeted Qt tests 8/8 PASS;
- full pytest PASS;
- evidence verifier 15/15 PASS;
- quality/architecture/security/source-of-truth/UI-reference PASS;
- regression matrix 24/24 workflow families SUCCESS;
- S08 portable foundation PASS;
- S10 packaged real-media smoke PASS on retry after external Chocolatey 504.

Evidence:
`docs/evidence/features/S11_W6_009_FROZEN_UI_PARITY.md`

## Active next task

**S11-W6-010 — Live Gemini + failure + regression closure**

Required closure work:
- attempt a real Gemini request through the official W6-007 adapter using a
  Windows secure-store credential when available;
- prove returned valid L1 plan → W6-006 verification → W6-008 explicit approval/apply;
- prove invalid/stale/provider failure paths remain safe and non-partial;
- prove no raw credential leakage in logs/evidence/UI;
- run final full regression closure.

Final status rule:
- with real live-Gemini evidence: W6 may close PASS if every gate is green;
- without an available live credential: W6 may close only
  **PASS_WITH_PROVISIONAL_LIVE_GEMINI**.

W6-010 must not:
- add AI L2;
- add providers other than Gemini;
- implement validation/recovery hardening;
- implement the export matrix;
- begin SF-STEP 12.

Do not begin W6-010 until owner says `lanjutkan`.
