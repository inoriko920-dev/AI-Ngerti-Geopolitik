# HANDOFF — AI NGERTI GEOPOLITIK

**Current phase:** SF-STEP 11  
**Current wave:** W6 — Gemini Credential + L1 AI Animation Planning  
**Last completed task:** S11-W6-009 — PASS  
**Accepted W6-009 implementation HEAD:** `7a2d79115e376205571bf529624993ed5fcc5f9f`  
**Accepted W6-009 workflow:** `37620520208` — SUCCESS  
**Next exact task:** S11-W6-010 — Live Gemini + failure + regression closure  
**Previous W5 status:** PASS_WITH_PROVISIONAL_MIC_HARDWARE

## W6-009 implementation now available

Presentation:
- old AI placeholder is removed from the live editor shell;
- real PySide6 AI Director / AI Agent / Provider & API Key surfaces are wired into the existing editor;
- UI emits semantic intents only and never mutates ProjectState/provider/CommandBus directly;
- UI states are READY / PLAN / APPROVAL / APPLYING / SUCCESS / PROVIDER_ERROR /
  LOCK_CONFLICT / STALE;
- AI claims remain limited to render-qualified W6 L1 effects;
- manual editing remains available when provider state fails.

Credential presentation:
- Gemini remains the only W6 provider;
- logical credential slots remain 1..100;
- saved credentials are displayed only as the fixed masked marker;
- raw saved key material is never projected back into UI;
- new key input is transient and crosses only the explicit credential application boundary;
- UI intent metadata contains no raw key material;
- quota/rate-limit resilience is not presented as quota evasion.

## Frozen UI reference correction

A 42/42 visual audit found that historical W6 planning aliases did not match the
physical content of the frozen PNG set. The binaries and SHA-256 identities were
not changed.

Authoritative W6 semantic-to-raster mapping:
- AI Director / AI Otomatis → `UI-020.png`
- AI Agent Ready / Chat → `UI-021.png`
- AI Agent Rencana Aksi → `UI-022.png`
- AI Agent Perubahan Diterapkan → `UI-023.png`
- AI Agent Provider Tidak Tersedia → `UI-024.png`
- Provider & API Key Manager → `UI-033.png`

Correction source:
`docs/ui_reference/W6_UI_REFERENCE_CORRECTION.md`

## Tests/evidence

Workflow `37620520208` — **SUCCESS**:
- Ruff format/check PASS;
- mypy PASS — 63 source files;
- import contracts PASS;
- architecture PASS;
- source-of-truth PASS;
- no-secret verifier PASS;
- frozen UI references 42/42 SHA-256 PASS;
- targeted W6-009 Qt tests **8/8 PASS**;
- full pytest PASS;
- actual-vs-frozen capture PASS;
- evidence verifier **15/15 PASS**;
- artifact upload PASS.

Artifact:
- `ANG-S11-W6-009-Frozen-UI`;
- ID `11481533239`;
- size 7,634,355 bytes;
- SHA-256 `874615de8ff572c3ee33df858882721f7286e8bfae9c162468fc512d7615ea5e`.

Evidence:
`docs/evidence/features/S11_W6_009_FROZEN_UI_PARITY.md`

## Regression lock on accepted W6-009 implementation HEAD

All workflows are SUCCESS on `7a2d79115e376205571bf529624993ed5fcc5f9f`:
- W6-009 `37620520208`
- W6-008 `37620520190`
- W6-007 `37620520185`
- W6-006 `37620520096`
- W6-005 `37620520081`
- W6-004 `37620520090`
- W6-003 `37620520106`
- W6-002 `37620520119`
- W6-001 `37620520141`
- W5-010 `37620520083`
- W5-009 `37620520144`
- W5-008 `37620520146`
- W5-007 `37620520077`
- W5-006 `37620520087`
- W5-005 `37620520192`
- W5-004 `37620520203`
- W4 `37620520147`
- W3 `37620520102`
- W2 `37620520073`
- W1 `37620520224`
- W0 `37620520175`
- S10 `37620520070` — SUCCESS on attempt 2
- S09 `37620520129`
- S08 `37620520042`

S10 attempt 1 failed only because the Chocolatey community feed returned HTTP 504
while installing FFmpeg. The failed packaged-smoke job was rerun without a product-code
change and passed completely.

## Critical boundaries for W6-010

- W6-010 is **not started**;
- full W6 PASS requires at least one real Gemini request through the official adapter
  using a Windows secure-store credential;
- a real returned L1 plan must be validated and applied through the existing
  W6-006/W6-008 boundaries;
- raw credential material must remain absent from logs/evidence/UI;
- provider failure/invalid/stale/lock cases must retain zero unsafe mutation;
- if no live Gemini credential is available, W6 may close only as
  **PASS_WITH_PROVISIONAL_LIVE_GEMINI**;
- do not add AI L2, non-Gemini providers, export-matrix work or SF-STEP 12.

## Next exact action

After owner says `lanjutkan`, execute **S11-W6-010 only — Live Gemini + failure + regression closure**.
