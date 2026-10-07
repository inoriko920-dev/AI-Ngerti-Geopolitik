# AI Ngerti Geopolitik

> **STATUS: SF-STEP 11 ACTIVE — W0/W1/W2/W3/W4 PASS — NEXT W5**

Repository resmi aplikasi **AI Ngerti Geopolitik**.

Baca `AGENTS.md` lalu `docs/SOURCE_OF_TRUTH_INDEX.md`.

## Current verified baseline

W4 accepted implementation:
- HEAD `3e3cd376189e9f183e70ca537ad25f037e25bcd7`;
- W4 workflow `37570612799` — SUCCESS;
- evidence artifact `11460641864`.

W4 now verifies:
- canonical per-clip title overlay;
- real `fade_black` transition plus `none`;
- nine render-backed AAVC effects: Fade, Pop, Breathe, Stomp, Tumble,
  Tectonic, Rise, Pan and Drift;
- semantic UI intents + canonical CommandBus mutation;
- Undo/Redo;
- project save/reopen and old-schema safe defaults;
- real preview impact;
- real export impact with audio retained;
- evidence verifier PASS 8/8.

Unsupported legacy effects remain unavailable rather than faked. Dissolve /
crossfade is also not claimed because W4 canonical timeline semantics do not
support clip overlap.

Reverse remains **disabled** until real backend qualification says otherwise.

All S08/S09/S10/W0/W1/W2/W3 regression workflows are green on the same
accepted W4 implementation HEAD.

## Engine direction

MLT remains the primary STEP 11 production-engine implementation candidate.
ProjectState + CommandBus + MediaEnginePort remain canonical boundaries.

The W4 real FFmpeg creative preview/export is qualification evidence behind
the existing port. It is not a production-engine switch.

## Next

**W5.** Its exact task contract must be derived from the frozen
Product/UI/Architecture source-of-truth before implementation.

Do not jump directly to Gemini/AI coverage, SF-STEP 12, or final release
packaging.
