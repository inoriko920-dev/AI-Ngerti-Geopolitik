# S11-W6-009 — FROZEN AI / CREDENTIAL UI PARITY

Status: **PASS**

Accepted implementation HEAD:
`7a2d79115e376205571bf529624993ed5fcc5f9f`

Accepted workflow:
`37620520208` — SUCCESS

## Scope proven

W6-009 implements real PySide6 presentation for:
- AI Director / AI Otomatis;
- AI Agent Ready / Chat;
- Plan / approval;
- applying / success;
- provider unavailable;
- lock conflict / stale;
- Provider & API Key Manager.

Presentation emits semantic UI intents only. It does not directly mutate
ProjectState, invoke Gemini, write secure storage, or create CommandBus history.

## Capability and credential boundary

- Gemini is the only V1 provider shown.
- AI capability claims are limited to W6 L1 render-qualified W4 effects.
- Saved credential values are displayed only as the fixed masked marker.
- Raw saved credentials are never projected into UI.
- New credential input is transient and crosses only the explicit application
  boundary.
- UI intent metadata contains no raw credential value.
- Manual editor fallback remains visible when provider operations fail.

## Frozen raster correction

A 42/42 visual contact-sheet audit found that historical planning aliases were
misaligned with the actual frozen PNG contents.

Authoritative physical mapping:
- AI Director → `UI-020.png`
- Ready / Chat → `UI-021.png`
- Rencana Aksi → `UI-022.png`
- Perubahan Diterapkan → `UI-023.png`
- Provider Tidak Tersedia → `UI-024.png`
- Provider & API Key Manager → `UI-033.png`

The 42 frozen files were not renamed, regenerated, rewritten or re-hashed.
See `docs/ui_reference/W6_UI_REFERENCE_CORRECTION.md`.

## CI / evidence

Workflow `37620520208`:
- Ruff format/check PASS;
- mypy PASS — 63 source files;
- import contracts PASS;
- architecture PASS;
- source-of-truth PASS;
- no-secret PASS;
- frozen UI references 42/42 SHA-256 PASS;
- targeted Qt tests 8/8 PASS;
- full pytest PASS;
- actual-vs-frozen capture PASS;
- evidence verifier 15/15 PASS;
- artifact upload PASS.

Artifact:
- name `ANG-S11-W6-009-Frozen-UI`
- ID `11481533239`
- size 7,634,355 bytes
- SHA-256 `874615de8ff572c3ee33df858882721f7286e8bfae9c162468fc512d7615ea5e`

The artifact contains:
- six real runtime captures;
- six corrected reference-vs-actual comparison images;
- the 42-image frozen-reference contact sheet;
- UI and security reports.

## Regression lock

All workflow families on the accepted implementation HEAD are SUCCESS:
W6-009..001, W5-010..004, W4, W3, W2, W1, W0, S10, S09 and S08.

S10 run `37620520070` completed SUCCESS on attempt 2. Attempt 1 failed only
because the Chocolatey community feed returned HTTP 504 while installing FFmpeg;
the failed packaged-smoke job was rerun without any product-code change.

S08 `37620520042` completed SUCCESS including security/dependency audit,
Qt tests, full tests, UI reference integrity and portable foundation smoke.

## Non-claims

W6-009 does not claim live Gemini network qualification. That remains W6-010.
AI L2, non-Gemini providers, validation/recovery hardening, export-matrix work and
SF-STEP 12 remain outside this task.
