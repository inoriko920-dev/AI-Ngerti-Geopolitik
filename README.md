# AI Ngerti Geopolitik

> **STATUS: SF-STEP 11 ACTIVE — W0/W1/W2 PASS — NEXT W3**

Repository resmi aplikasi **AI Ngerti Geopolitik**.

Baca `AGENTS.md` lalu `docs/SOURCE_OF_TRUTH_INDEX.md`.

## Current verified baseline

W2 accepted implementation:
- HEAD `4486da29883bc42e9cd12d5d13a7784f347dc2d3`;
- W2 workflow `37542485728` — SUCCESS.

W2 now verifies:
- canonical multi-track video state;
- track create/delete/rename/reorder/lock/mute/visibility;
- clip select/move/duplicate/delete/reorder;
- collision rejection and ripple policy;
- split + left/right trim;
- markers and IN/OUT;
- snap, zoom and follow;
- semantic Qt shortcuts/context actions;
- Undo/Redo and project round-trip;
- play/pause/scrub/seek;
- real Windows MLT canonical playback/render projection;
- ffprobe video + audio;
- 1000-clip deterministic stress fixture: 63.04 ms vs 8000 ms budget.

All S08/S09/S10/W0/W1 regression workflows are also green on the same
accepted implementation HEAD.

## Engine direction

MLT remains the primary STEP 11 production-engine implementation candidate.
ProjectState + CommandBus + MediaEnginePort remain canonical boundaries.

The W2 MLT evidence is a real contiguous V1 canonical projection. It is not a
claim that arbitrary multitrack/audio/color property behavior is already done.

## Next

**W3 — Properties: Video, Audio, Color & Speed.**

Do not jump to W4, Gemini/STEP 12, or final release packaging.
