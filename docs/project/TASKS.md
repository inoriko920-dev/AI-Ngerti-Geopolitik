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

### W5 — ACTIVE / CONTRACT LOCKED

**Subtitle + Narration**

Contract:
`docs/project/W5_SUBTITLE_NARRATION_CONTRACT.md`

Implementation status:
**W5-001 PASS / W5-002 PASS / W5-003 PASS / W5-004 PASS / W5-005 PASS / W5-006 PASS / W5-007 READY**

W5-006 accepted implementation HEAD:
`77770cd98210dbed18cbe1715111a935f2135b77`

W5-006 workflow:
`37577639655` — SUCCESS

W5-006 evidence:
`docs/evidence/features/S11_W5_006_NARRATION_IMPORT_BINDING.md`

W5-006 artifact:
`ANG-S11-W5-006-Narration` / ID `11462194359`

W5-005 accepted implementation HEAD:
`293b369e74771d16dc90956bc6a7be4c71e01d1c`

W5-005 workflow:
`37575611940` — SUCCESS

W5-005 evidence:
`docs/evidence/features/S11_W5_005_SUBTITLE_ANIMATION_WORD_TIMING.md`

W5-005 artifact:
`ANG-S11-W5-005-Subtitle-Animation` / ID `11462966698`

W5-004 accepted implementation HEAD:
`687d31585d476541711978d5f69e5e7eafe72245`

W5-004 workflow:
`37574406573` — SUCCESS

W5-004 evidence:
`docs/evidence/features/S11_W5_004_SUBTITLE_STYLE.md`

W5-004 artifact:
`ANG-S11-W5-004-Subtitle-Style` / ID `11461154582`

W5-003 accepted implementation HEAD:
`d8db4d18cb42b71d91a9b727868b25340961702f`

W5-003 workflow:
`37573388357` — SUCCESS

W5-003 evidence:
`docs/evidence/features/S11_W5_003_SUBTITLE_WORKING_COPY.md`

W5-002 accepted implementation HEAD:
`d4349c925cc0f475cfa94b0db55347320954e1cf`

W5-002 workflow:
`37572463564` — SUCCESS

W5-002 evidence:
`docs/evidence/features/S11_W5_002_SRT_IMPORT_VALIDATION.md`

W5-001 accepted implementation HEAD:
`b5bf8543554bcf38d22a65510fe0376195676d46`

W5-001 workflow:
`37571740654` — SUCCESS

W5-001 evidence:
`docs/evidence/features/S11_W5_001_CANONICAL_SUBTITLE_NARRATION.md`

Serial contract:
- [x] **S11-W5-001 — Canonical subtitle/narration model — PASS**
- [x] **S11-W5-002 — SRT import + validation — PASS**
- [x] **S11-W5-003 — Cue editing + safe working-copy flow — PASS**
- [x] **S11-W5-004 — Subtitle style — PASS**
- [x] **S11-W5-005 — Render-backed subtitle animation + per-word boundary — PASS**
- [x] **S11-W5-006 — Narration import + binding — PASS**
- [ ] **S11-W5-007 — Microphone recording**
- [ ] **S11-W5-008 — Frozen UI parity**
- [ ] **S11-W5-009 — Real subtitle/narration preview/export qualification**
- [ ] **S11-W5-010 — Failure paths + evidence + regression lock**

Hard boundaries:
- W4 title overlay is not the subtitle model;
- source SRT is never silently overwritten;
- no ASR/speech-alignment claim;
- only render-proven subtitle animations may be enabled;
- failed recording cannot clobber existing narration;
- no Gemini/provider/AI Auto Edit work;
- no SF-STEP 12 or final release work.

**Exact next task:** S11-W5-007 — Microphone recording only.
