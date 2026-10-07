# PLAN — CURRENT IMPLEMENTATION PHASE

**SF-STEP 11 is active. W0 = PASS. W1 = PASS. W2 = PASS. W3 = PASS. W4 = PASS.**

W4 accepted:
- implementation HEAD `3e3cd376189e9f183e70ca537ad25f037e25bcd7`;
- W4 run `37570612799`;
- title/transition/render-backed effect state/history/persistence gate green;
- real W4 preview/export evidence 8/8 green;
- S08/S09/S10/W0/W1/W2/W3 regressions green on the same implementation HEAD.

## Active wave

**W5 — Subtitle + Narration**

W5 contract is locked in:
`docs/project/W5_SUBTITLE_NARRATION_CONTRACT.md`.

W5 must continue to reuse:
- canonical ProjectState;
- CommandBus/CommandBatch;
- W1 media identity/persistence;
- W2 timeline/history/playback;
- W3 audio property foundations;
- W4 no-fake-capability rule;
- MediaEnginePort;
- MLT as primary production-engine implementation candidate;
- frozen AAVC visual/interaction contract.

W5 must not:
- convert W4 title overlay into the subtitle system;
- let presentation or subtitle working-copy code mutate project JSON/engine
  directly;
- silently overwrite source SRT;
- claim speech alignment/ASR;
- expose subtitle animation names without real render proof;
- clobber existing narration after failed recording;
- start Gemini/provider/AI Auto Edit work.

## Exact next task

**S11-W5-001 — Canonical subtitle/narration model.**

Do not start W5-002 or later tasks until W5-001 is completed and gated.
