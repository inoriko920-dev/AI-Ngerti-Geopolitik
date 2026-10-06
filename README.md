# AI Ngerti Geopolitik

> **STATUS: SF-STEP 11 ACTIVE — W0 PASS — NEXT W1 PROJECT/MEDIA/PERSISTENCE**

Repository resmi aplikasi **AI Ngerti Geopolitik**.

Baca `AGENTS.md` lalu `docs/SOURCE_OF_TRUTH_INDEX.md`.

## Current verified baseline

W0 run `37533447729` passed on
`f54993851f85aa5672f0d86dcb7e5ea3a49c7ae6`.

Verified:
- regression baseline + STEP 10 E2E;
- 31 tests;
- UI references 42/42;
- MLT Windows runtime;
- Python `mlt7` binding and exact seek;
- continuous/edited-playlist transport smoke;
- H.264/AAC MLT render.

Actual CI MLT package:
`mingw-w64-x86_64-mlt 7.40.0-2`.

MLT is now the primary STEP 11 production-engine implementation candidate.
Final portable native dependency/license closure remains a later release gate.

## Next

**W1 — Project, Media & Persistence Foundation.**

Do not jump to W2, Gemini/STEP12, or final release packaging.
