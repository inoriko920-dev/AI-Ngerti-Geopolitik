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

### W4 — READY

**Titles / Transitions / Effects**

W4 is the next exact wave. Its detailed task decomposition must be derived from
the existing product/UI/architecture source-of-truth before implementation.

W5 remains BLOCKED_BY_W4.
