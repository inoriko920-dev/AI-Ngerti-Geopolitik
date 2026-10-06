# S08-T01 — Source-of-Truth & Exact UI Reference Gate

**Project:** AI Ngerti Geopolitik  
**SF-STEP:** 08  
**Task:** S08-T01  
**Role:** SOL  
**Starting baseline:** `main @ 47942565c6b34f5d5d70dc4eed8f732f6f5c5643`  
**Result:** **BLOCKED — REMOTE BINARY UPLOAD NOT AVAILABLE**

## 1. Repository/source-of-truth verification

Verified in GitHub:
- Master Blueprint DOCX + TXT;
- STEP 00 DOCX + TXT;
- STEP 01 DOCX + TXT;
- STEP 02 DOCX + TXT;
- STEP 03 DOCX + TXT;
- STEP 04 DOCX + TXT;
- STEP 05 DOCX + TXT;
- STEP 06 DOCX + TXT;
- STEP 07 DOCX + TXT;
- UI reference index;
- UI SHA manifest;
- Software Factory guide/master;
- status, decisions, rules, handoff.

No application source tree exists yet. This is correct for S08-T01.

## 2. Exact UI raw recovery

Recovered exactly 42 original AAVC reference PNG files and normalized only their filenames to:
`UI-001.png` through `UI-042.png`.

No image pixels were regenerated, resized, recompressed, or edited.

## 3. Integrity verification

Each recovered PNG was checked against the authoritative STEP 04/05 manifest using:
- byte count;
- SHA-256.

Result: **42 / 42 PASS**.

Examples:
- UI-001: 839156 bytes — `de8ea60f323f0c7cd3a0fc0a626e431b194b6142fcc4e14236aa6e9f9c6af4af`
- UI-042: 1477719 bytes — `e0f57b1f37ed47bf1109207023e1dae1fa9f88fd5c633657b3c8060efe95b0e8`

Full per-file expected hashes remain in `docs/ui_reference/UI_REFERENCE_MANIFEST.md`.

## 4. Exact transport artifact

A deterministic archive containing the 42 exact PNG bytes + verification/source manifest was created locally:

- filename: `ANG_UI_REFERENCE_RAW_42_EXACT.zip`
- size: **65,497,507 bytes**
- SHA-256: `2fc3e43b5625b0ec709095b53549c6c098f0dbd9c32a0789eb6e2683e59feef2`

Extracted PNG bytes are the authority; archive hash identifies this exact transfer artifact.

## 5. Remote write attempt / blocker

The GitHub connector available in this session supports repository text writes / Git blobs from supplied content, but it does not expose a direct binary file-reference upload from the model working container or conversation file store.

The exact payload is ~65 MB and cannot be truthfully reconstructed in-repo through the connector-safe text path without changing/omitting the binary source.

Therefore the task is **not** marked PASS.

## 6. Gate decision

Planning/source-of-truth presence: **PASS**  
Local exact UI recovery: **PASS**  
Local SHA verification: **PASS 42/42**  
Exact UI binary committed to GitHub: **FAIL / BLOCKED**  
Remote hash verification: **NOT TESTED**  
S08-T01 final: **BLOCKED**

## 7. Required next action

When an exact binary upload path is available:
1. commit the exact UI raw pack to the repo;
2. verify the 42 extracted PNG hashes from the remote commit;
3. record the commit SHA;
4. mark S08-T01 PASS;
5. activate S08-T02.

No product source coding is authorized before that.
