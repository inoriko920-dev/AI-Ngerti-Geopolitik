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

Accepted implementation HEAD:
`4486da29883bc42e9cd12d5d13a7784f347dc2d3`

Accepted workflow:
`37542485728` — SUCCESS

- [x] S11-W2-001 multi-track video create/delete/rename/order/lock/mute/visibility;
- [x] S11-W2-002 clip move/duplicate/delete/selection with stable IDs;
- [x] S11-W2-003 ripple/gap-close policy + collision validation;
- [x] S11-W2-004 split + left/right trim multi-track-safe semantics;
- [x] S11-W2-005 Undo/Redo coverage for core W2 mutations;
- [x] S11-W2-006 play/pause/scrub/seek/timecode/zoom/follow;
- [x] S11-W2-007 Qt keyboard/context actions through semantic intent/CommandBus;
- [x] S11-W2-008 stress fixture: 1000 clips, 40 reorder/Undo/Redo cycles,
  63.04 ms measured vs 8000 ms budget.

Additional runtime proof:
- [x] real MLT Windows canonical playback/render projection;
- [x] ffprobe video + audio;
- [x] W2 save/reopen semantic hash;
- [x] 55-test W2 quality suite;
- [x] earlier S08/S09/S10/W0/W1 regressions all green on accepted HEAD.

Evidence:
`docs/evidence/features/S11_W2_TIMELINE_PLAYBACK_CORE.md`.

### W3 — READY

**Properties: Video, Audio, Color & Speed**

Planned serial tasks:
- [ ] S11-W3-001 inspector context binding by selected object type;
- [ ] S11-W3-002 video position/scale/rotation/opacity;
- [ ] S11-W3-003 crop/basic composition;
- [ ] S11-W3-004 audio volume/pan/fade in/out;
- [ ] S11-W3-005 color basics;
- [ ] S11-W3-006 uniform speed + duration recompute;
- [ ] S11-W3-007 reverse only if engine qualification proves safe; otherwise
  explicitly disabled;
- [ ] S11-W3-008 cross-property Undo/Redo + project reload/evidence.

W4 remains BLOCKED_BY_W3.
