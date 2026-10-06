# AI Ngerti Geopolitik

> **STATUS: SF-STEP 11 ACTIVE — W0 PASS — W1 PASS — NEXT W2**

Repository resmi aplikasi **AI Ngerti Geopolitik**.

Baca `AGENTS.md` lalu `docs/SOURCE_OF_TRUTH_INDEX.md`.

## Current verified baseline

W1 run `37536861625` passed on
`1f354cddc68eb9f129ba22d0410480964c6b1b85`.

W1 now verifies:
- safe project new/open/close + dirty state;
- atomic Save and Save As;
- previous successful Save backup;
- real video/audio/image import;
- stable media IDs and metadata;
- media-bin query/selection;
- persisted resolution/FPS/aspect;
- separate autosave snapshots;
- online/offline/missing media states;
- no silent clip deletion when media disappears.

All earlier W0/S10/S09/S08 regression workflows are also green on the same
accepted code HEAD.

MLT remains the primary STEP 11 production-engine implementation candidate.
Final portable native dependency/license closure remains a later release gate.

## Next

**W2 — Timeline, Playback & Core Editing.**

Do not jump to W3, Gemini/STEP12, or final release packaging.
