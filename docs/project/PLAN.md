# PLAN — CURRENT IMPLEMENTATION PHASE

**SF-STEP 11 is active. W0/W1/W2/W3/W4 PASS. W5-001/W5-002/W5-003 PASS.**

## Accepted W5-003

- implementation HEAD:
  `d8db4d18cb42b71d91a9b727868b25340961702f`;
- W5-003 run: `37573388357` — SUCCESS;
- application-level subtitle working copy implemented;
- text/IN/OUT edit, insert/delete, split/merge implemented;
- explicit sort/index normalization implemented;
- dirty reload/discard guard implemented;
- no-clobber UTF-8 save-copy writer implemented;
- default non-colliding copy naming implemented;
- source SRT overwrite remains disabled;
- successful copy commit uses CommandBus and is undoable;
- failed writer does not alter project binding;
- targeted 12/12 tests + full pytest green;
- W4/W3/W2/W1/W0/S10/S09/S08 regressions all green on the same HEAD.

Evidence:
`docs/evidence/features/S11_W5_003_SUBTITLE_WORKING_COPY.md`.

## Active next task

**S11-W5-004 — Subtitle style**

W5-004 must build on the existing canonical `SubtitleStyle` and preserve the
safe W5-003 working-copy/source behavior.

W5-004 scope:
- font family and size;
- fill color;
- outline color/width;
- shadow;
- optional background box/opacity;
- alignment;
- safe vertical margin;
- semantic mutation through CommandBus;
- Undo/Redo;
- persistence/reopen;
- real preview/export proof for each enabled style property.

W5-004 must not:
- enable subtitle animation presets;
- add per-word animation/alignment behavior;
- implement narration/recording;
- start UI parity beyond what is minimally required for qualification;
- start Gemini/provider work.

Do not begin W5-004 until owner says `lanjutkan`.
