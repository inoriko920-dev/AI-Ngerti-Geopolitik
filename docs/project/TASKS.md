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

Final W1 regression reference:
- W0 run `37536861597` SUCCESS on W1 accepted HEAD.

### W1 — DONE / PASS

Accepted run: `37536861625`  
Accepted HEAD: `1f354cddc68eb9f129ba22d0410480964c6b1b85`

- [x] S11-W1-001 project new/open/close + dirty state;
- [x] S11-W1-002 atomic Save/Save As + backup/replace;
- [x] S11-W1-003 video/audio/image media import + metadata/offline states;
- [x] S11-W1-004 media-bin search/sort/filter/selection;
- [x] S11-W1-005 project settings resolution/FPS/aspect ratio;
- [x] S11-W1-006 autosave snapshot foundation;
- [x] S11-W1-007 missing/offline asset state; no silent clip deletion.

Evidence:
`docs/evidence/features/S11_W1_PROJECT_MEDIA_PERSISTENCE.md`.

### W2 — READY

Timeline, Playback & Core Editing.

W3 remains BLOCKED_BY_W2.
