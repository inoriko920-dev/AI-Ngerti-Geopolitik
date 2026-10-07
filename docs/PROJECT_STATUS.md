# PROJECT STATUS — AI NGERTI GEOPOLITIK

**Current STEP:** SF-STEP 11 — Feature Implementation Waves  
**Current wave:** **W6 — Gemini Credential + L1 AI Animation Planning**  
**W6 status:** **CONTRACT_LOCKED / W6-001..009 PASS / W6-010 READY**  
**Previous wave:** W5 — CLOSED / PASS_WITH_PROVISIONAL_MIC_HARDWARE  
**Accepted W6-009 implementation HEAD:** `7a2d79115e376205571bf529624993ed5fcc5f9f`  
**Accepted W6-009 workflow:** `37620520208` — SUCCESS  
**Next exact task:** **S11-W6-010 — Live Gemini + failure + regression closure**

## W6-009 proven

Runtime UI:
- real PySide6 AI Director / AI Agent replaces the prior placeholder;
- Provider & API Key Manager is a real interactive settings surface;
- semantic UI intents are the only presentation output;
- presentation performs no direct ProjectState/provider/CommandBus mutation;
- READY / PLAN / APPROVAL / APPLYING / SUCCESS / PROVIDER_ERROR /
  LOCK_CONFLICT / STALE are represented truthfully;
- manual fallback remains visible on provider failure;
- capability claims are restricted to W6 L1.

Credential safety:
- Gemini only;
- slots 1..100;
- saved values masked only;
- raw saved credentials never reappear in presentation;
- no raw key material is placed in semantic intents;
- security scanner and project no-secret verifier both pass.

Frozen reference correction:
- historical W6 semantic numbering was found to disagree with the physical frozen PNGs;
- binaries were not changed;
- authoritative physical mapping is:
  UI-020 AI Director, UI-021 Ready, UI-022 Plan, UI-023 Applied,
  UI-024 Provider unavailable, UI-033 Provider/API Key Manager;
- correction is recorded in `docs/ui_reference/W6_UI_REFERENCE_CORRECTION.md`.

## W6-009 gates

Workflow `37620520208`:
- Ruff format/check PASS;
- mypy PASS — 63 source files;
- import contracts PASS;
- architecture PASS;
- source-of-truth PASS;
- no-secret PASS;
- frozen UI references 42/42 PASS;
- targeted Qt tests **8/8 PASS**;
- full pytest PASS;
- actual-vs-frozen evidence capture PASS;
- evidence verifier **15/15 PASS**;
- artifact upload PASS.

Artifact:
- `ANG-S11-W6-009-Frozen-UI`;
- ID `11481533239`;
- size 7,634,355 bytes;
- SHA-256 `874615de8ff572c3ee33df858882721f7286e8bfae9c162468fc512d7615ea5e`.

## Regression lock

All 24 workflow families on the accepted implementation HEAD are SUCCESS,
including W6-008..001, W5-010..004, W4/W3/W2/W1/W0, S10, S09 and S08.

S10 run `37620520070` finished SUCCESS on attempt 2 because attempt 1 hit an external
Chocolatey HTTP 504 while installing FFmpeg. The successful retry required no
product-code change.

S08 `37620520042` is SUCCESS including:
- quality / architecture;
- tests;
- Qt smoke;
- UI reference integrity;
- security / dependency audit;
- portable foundation build + smoke.

## Exact next action

After owner says **lanjutkan**, execute **S11-W6-010 only — Live Gemini + failure + regression closure**.

Do not begin AI L2, non-Gemini providers, validation/recovery hardening, export matrix,
SF-STEP 12, or any other wave.
