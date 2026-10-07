# PLAN — CURRENT IMPLEMENTATION PHASE

**SF-STEP 11 is active. W0/W1/W2/W3/W4 PASS. W5-001 through W5-005 PASS.**

## Accepted W5-005

- implementation HEAD:
  `293b369e74771d16dc90956bc6a7be4c71e01d1c`;
- workflow:
  `37575611940` — SUCCESS;
- four render-qualified animation presets implemented:
  Fade, Pop, Slide Up, Clean Documentary;
- unsupported legacy animation labels remain rejected;
- animation timing is canonical/frame-bounded and cue-safe;
- animation CommandBus mutation + Undo/Redo + persistence proven;
- real preview evidence for all four presets;
- real export + extracted-frame evidence for all four presets;
- manual per-word WordTiming command implemented;
- explicit deterministic even-distribution fallback implemented only behind
  `NOT speech alignment` acknowledgement;
- no ASR/transcription/audio alignment;
- targeted 6/6 tests + full pytest green;
- evidence verifier 21/21 PASS;
- W5-004/W4/W3/W2/W1/W0/S10/S09/S08 regressions all green on the same HEAD.

Evidence:
`docs/evidence/features/S11_W5_005_SUBTITLE_ANIMATION_WORD_TIMING.md`.

## Active next task

**S11-W5-006 — Narration import + binding**

W5-006 scope:
- import supported narration audio through existing MediaImport/probe identity;
- create/bind one canonical NarrationTrack;
- frame-aware narration offset;
- prove bounded gain/mute/fade only if qualification runtime supports them;
- narration must be audible in real preview/export evidence;
- project save/reopen must retain narration binding/timing;
- narration mutation must be Undo/Redo safe.

W5-006 must not:
- implement microphone recording;
- start W5 frozen UI parity;
- start W5 final combined qualification/closure;
- change subtitle animation boundaries;
- start Gemini/provider work.

Do not begin W5-006 until owner says `lanjutkan`.
