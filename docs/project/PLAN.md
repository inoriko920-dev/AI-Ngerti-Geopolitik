# PLAN — CURRENT IMPLEMENTATION PHASE

**SF-STEP 11 is active. W0 = PASS. W1 = PASS. W2 = PASS. W3 = PASS.**

W3 accepted:
- implementation HEAD `79217e687a9930087260e7dd3203b6ab8492b477`;
- W3 run `37545032247`;
- property/state/history/persistence gate green;
- real preview and export evidence green;
- S08/S09/S10/W0/W1/W2 regressions green on the same implementation HEAD.

## Active next wave

**W4 — Titles / Transitions / Effects**

W4 must continue to reuse:
- canonical ProjectState;
- CommandBus/CommandBatch;
- W1 media identity/persistence;
- W2 timeline/history/playback;
- W3 property model;
- MediaEnginePort;
- MLT as primary production-engine implementation candidate;
- frozen AAVC visual/interaction contract.

W4 must not:
- create a second project/effect state owner;
- let presentation mutate concrete engine objects;
- silently enable unsupported engine capabilities;
- reinterpret W3 FFmpeg qualification evidence as a production-engine switch;
- start Gemini/provider work.

Do not begin W4 until owner says `lanjutkan`.
