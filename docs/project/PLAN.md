# PLAN — CURRENT IMPLEMENTATION PHASE

**SF-STEP 11 is active. W0 = PASS. W1 = PASS. W2 = PASS.**

W2 accepted:
- implementation HEAD `4486da29883bc42e9cd12d5d13a7784f347dc2d3`;
- W2 run `37542485728`;
- full timeline/playback/core-editing gate green;
- MLT canonical Windows playback/render proof green;
- S08/S09/S10/W0/W1 regressions green on the same implementation HEAD.

## Active next wave

**W3 — Properties: Video, Audio, Color & Speed**

W3 must reuse:
- canonical ProjectState;
- CommandBus/CommandBatch;
- W1 media identity/persistence;
- W2 timeline/selection/history;
- MediaEnginePort;
- MLT as primary production-engine implementation candidate;
- frozen AAVC UI references for inspector surfaces.

W3 must not create:
- a second property/project state owner;
- presentation-to-engine direct mutation;
- unsupported controls that look functional;
- AI/provider coupling.

Required proof includes persistence, Undo/Redo, preview/output impact for
supported properties, and explicit disabled/blocker status for unsupported
engine capabilities.

Do not begin W4 or STEP 12 until W3 evidence is green.
