# TASKS

## SF-STEP 08 — DONE / PASS
Repository foundation, exact UI references, Windows CI and portable foundation.

## SF-STEP 09 — DONE / PASS
Real AAVC-derived PySide6 shell and visual evidence.

## SF-STEP 10 — DONE / PASS_WITH_PROVISIONAL
Minimum real E2E backbone.

## SF-STEP 11

### W0 — DONE / PASS
Engine qualification and regression lock.

### W1 — DONE / PASS
Project, Media & Persistence Foundation.

### W2 — DONE / PASS
Timeline, playback and core editing.

### W3 — DONE / PASS

Accepted implementation HEAD:
`79217e687a9930087260e7dd3203b6ab8492b477`

Accepted workflow:
`37545032247` — SUCCESS

- [x] S11-W3-001 inspector context binding by project/track/asset/clip;
- [x] S11-W3-002 video position/scale/rotation/opacity;
- [x] S11-W3-003 crop/basic composition;
- [x] S11-W3-004 audio volume/pan/fade in/out;
- [x] S11-W3-005 brightness/exposure/contrast/saturation/WB/tint;
- [x] S11-W3-006 uniform speed 25%–400% + duration recompute/ripple;
- [x] S11-W3-007 Reverse explicitly disabled because backend qualification is
  not yet safe;
- [x] S11-W3-008 cross-property Undo/Redo + project reload + real preview/output
  evidence.

Additional proof:
- [x] real PySide6 property controls emit semantic intents;
- [x] old schema-v1 clip properties load with safe defaults;
- [x] real W3 preview differs from baseline;
- [x] real 1920×1080 / 30 fps / 180-frame export with audio;
- [x] W3 evidence verifier PASS 8/8;
- [x] S08/S09/S10/W0/W1/W2 regressions all green on accepted HEAD.

Evidence:
`docs/evidence/features/S11_W3_PROPERTIES_VIDEO_AUDIO_COLOR_SPEED.md`.

### W4 — DONE / PASS

**Titles / Transitions / Effects**

Accepted implementation HEAD:
`3e3cd376189e9f183e70ca537ad25f037e25bcd7`

Accepted workflow:
`37570612799` — SUCCESS

- [x] **S11-W4-001 — Canonical title overlay**
  - per-clip enabled/text/font size/position/color/background;
  - title remains distinct from the later full subtitle workspace;
  - state belongs to ProjectState through ClipProperties.
- [x] **S11-W4-002 — Transition semantics**
  - qualified presets: `none` and `fade_black`;
  - duration is frame-based and bounded to the clip;
  - dissolve/crossfade is intentionally not claimed while the canonical
    timeline forbids overlapping clips.
- [x] **S11-W4-003 — Render-backed AAVC effect subset**
  - qualified legacy effects: Fade, Pop, Breathe, Stomp, Tumble, Tectonic,
    Rise, Pan and Drift;
  - unsupported legacy effects remain unavailable rather than fake:
    Wipe, Blur, Succession, Baseline, Neon, Scrapbook, Brush, Ink, Digital,
    Spray Paint, Sketch and Gradient;
  - effect state includes enter/exit, bounded intensity and lock.
- [x] **S11-W4-004 — Semantic UI controls**
  - AAVC-compatible Animation inspector surface;
  - PySide6 emits semantic intents only;
  - no presentation-to-engine/project direct mutation.
- [x] **S11-W4-005 — History and persistence**
  - title/transition/effect mutation through CommandBus/CommandBatch;
  - Undo/Redo across W4 mutations;
  - .angproj save/reopen round-trip;
  - schema-v1 projects without W4 fields load with safe defaults.
- [x] **S11-W4-006 — Real media qualification**
  - preview visibly reflects W4 creative state;
  - export reflects title/transition/effect state;
  - output remains valid and retains audio.
- [x] **S11-W4-007 — Evidence + regression lock**
  - deterministic W4 evidence bundle and verifier PASS 8/8;
  - Ruff format/check, mypy, import contracts, architecture, source-of-truth,
    UI-reference and secret gates PASS;
  - full pytest PASS;
  - W3/W2/W1/W0/S10/S09/S08 all SUCCESS on the same implementation HEAD.

Evidence:
`docs/evidence/features/S11_W4_TITLES_TRANSITIONS_EFFECTS.md`.

Locked boundaries carried forward:
- ProjectState + CommandBus + MediaEnginePort remain canonical;
- MLT remains the primary production-engine implementation candidate;
- FFmpeg remains a real qualification adapter, not a production-engine switch;
- AAVC UI-001..UI-042 remains frozen 1:1;
- Reverse remains disabled;
- dissolve/crossfade remains unsupported until overlap semantics are qualified;
- unsupported legacy W4 effect names must stay unavailable;
- Gemini/AI implementation, SF-STEP 12 and release packaging remain blocked
  until their proper wave/STEP.

### W5 — READY

W5 may start only after its exact task contract is derived from the frozen
Product/UI/Architecture source-of-truth. Do not guess its scope from legacy
code and do not jump directly to Gemini/AI or release work.
