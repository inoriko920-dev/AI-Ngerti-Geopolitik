# HANDOFF — AI NGERTI GEOPOLITIK

**Fase:** SF-STEP 08 / S08-T01 BLOCKED  
**Active task:** S08-T01 — Source-of-Truth & Exact UI Reference Gate  
**Task status:** BLOCKED ON REMOTE BINARY UPLOAD  
**Application source:** NONE  
**Production coding:** FORBIDDEN

## Read first

1. `AGENTS.md`
2. Software Factory master + guide
3. `docs/planning/00..08` in order
4. `docs/ui_reference/UI_REFERENCE_MANIFEST.md`
5. `docs/evidence/ui/S08_T01_UI_REFERENCE_GATE.md`
6. `docs/DECISIONS_LOCKED.md`
7. `docs/PROJECT_STATUS.md`
8. `docs/REPOSITORY_RULES.md`
9. this `HANDOFF.md`

## S08-T01 work completed

Verified repo baseline:
- repo: `inoriko920-dev/AI-Ngerti-Geopolitik`
- branch: `main`
- starting HEAD: `47942565c6b34f5d5d70dc4eed8f732f6f5c5643`

Source-of-truth verification:
- Master Blueprint DOCX+TXT present.
- STEP 00–07 DOCX+TXT present.
- STEP 04/05 UI manifest/index present.
- no product source code exists.

Exact visual verification:
- recovered exact original `UI-001.png..UI-042.png`;
- local SHA-256/size verification against authoritative manifest: **42/42 PASS**;
- local exact pack: `ANG_UI_REFERENCE_RAW_42_EXACT.zip`;
- pack SHA-256: `2fc3e43b5625b0ec709095b53549c6c098f0dbd9c32a0789eb6e2683e59feef2`;
- pack size: `65,497,507 bytes`.

## Blocker

The available GitHub connector cannot ingest the exact local binary files/pack from the model working container. It can write UTF-8 files and Git blobs from supplied text/base64, but there is no connector file-reference/binary upload bridge exposed for these 65 MB of already-verified PNG bytes.

This is a **tooling transport blocker**, not a missing-design blocker.

Do not weaken the gate by treating the existing hash manifest, compressed preview JPGs, reconstructed DOCX, or VOID prompt batch as the raw UI pack.

## Exact next action

Continue **S08-T01 only** when an exact binary upload path is available.

Required completion:
1. commit exact raw UI reference payload to GitHub;
2. verify remote-extracted `UI-001..UI-042` SHA-256 = existing manifest, 42/42;
3. update status/handoff to S08-T01 PASS;
4. only then activate S08-T02.

## Still forbidden

- no product source code;
- no UI implementation;
- no libopenshot/MLT feature implementation;
- no Gemini implementation;
- no render feature;
- no STEP 09;
- no UI regeneration;
- no use of the VOID 42-prompt ZIP.
