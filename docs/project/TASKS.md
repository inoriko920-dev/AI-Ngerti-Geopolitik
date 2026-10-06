# TASKS

## SF-STEP 08 — DONE / PASS
Repository foundation, exact UI references, Windows CI and portable foundation verified.

## SF-STEP 09 — DONE / PASS
Real AAVC-derived PySide6 app shell, screenshot evidence and portable UI shell verified.

## SF-STEP 10 — DONE / PASS_WITH_PROVISIONAL

Accepted commit: `852610f55a6e99dc98234114c3cf099ed85dfd42`  
Windows run: `37527851180` — SUCCESS

Completed:
- [x] real UI import action -> semantic UiIntent;
- [x] real ffprobe import/probe;
- [x] ProjectState + CommandBus canonical edit path;
- [x] add/split/trim with stable IDs;
- [x] invalid edit atomicity;
- [x] exact Undo/Redo semantic hashes;
- [x] real ProjectState -> Qt timeline projection;
- [x] engine preview frames 149/151 -> Qt preview canvas;
- [x] atomic `.angproj` save/load roundtrip;
- [x] corrupt/wrong-extension negative paths;
- [x] H.264/AAC 1920×1080 30 fps export;
- [x] cancellation + no false/partial output;
- [x] generated/owned fixture provenance;
- [x] evidence verifier 22/22;
- [x] pytest 26 PASS;
- [x] packaged onedir real-media qualification smoke;
- [x] S08 + S09 regressions green.

Evidence:
`docs/evidence/e2e/S10_MINIMUM_E2E_VERTICAL_SLICE.md`.

Provisional:
- [ ] continuous interactive production playback;
- [ ] final libopenshot-vs-MLT qualification;
- [ ] final native media-engine package/license chain.

## NEXT — SF-STEP 11

**Feature Implementation Waves**

First wave:
- freeze current green regression baseline;
- production MediaEnginePort qualification;
- continuous playback/seek/edit coherence;
- evidence-based libopenshot primary vs MLT fallback decision.

Only after that expand media/editor features in small regression-safe waves. External-service/Gemini production wiring belongs to STEP 12 unless the authoritative STEP 11 prompt says otherwise.
