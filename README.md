# AI Ngerti Geopolitik

> **STATUS: SF-STEP 11 ACTIVE — W0/W1/W2/W3 PASS — NEXT W4**

Repository resmi aplikasi **AI Ngerti Geopolitik**.

Baca `AGENTS.md` lalu `docs/SOURCE_OF_TRUTH_INDEX.md`.

## Current verified baseline

W3 accepted implementation:
- HEAD `79217e687a9930087260e7dd3203b6ab8492b477`;
- W3 workflow `37545032247` — SUCCESS;
- evidence artifact `11449982099`.

W3 now verifies:
- inspector binding for project/track/asset/clip;
- video transform/opacity/crop;
- audio volume/pan/fade;
- basic color controls;
- uniform speed 25%–400% with duration recompute/ripple;
- semantic UI intents + canonical CommandBus mutation;
- cross-property Undo/Redo;
- project save/reopen;
- old-schema safe property defaults;
- real preview property impact;
- real 1920×1080 / 30 fps / 180-frame export with audio.

Reverse remains **disabled** until real backend qualification says otherwise.

All S08/S09/S10/W0/W1/W2 regression workflows are green on the same accepted
W3 implementation HEAD.

## Engine direction

MLT remains the primary STEP 11 production-engine implementation candidate.
ProjectState + CommandBus + MediaEnginePort remain canonical boundaries.

The W3 real FFmpeg property preview/export is qualification evidence behind the
existing port. It is not a production-engine switch.

## Next

**W4 — Titles / Transitions / Effects.**

Do not jump to W5, Gemini/AI coverage, SF-STEP 12, or final release packaging.
