# PLAN — CURRENT IMPLEMENTATION PHASE

**SF-STEP 11 is active. W0/W1/W2/W3/W4 PASS. W5-001 PASS. W5-002 PASS.**

## Accepted W5-002

- implementation HEAD:
  `d4349c925cc0f475cfa94b0db55347320954e1cf`;
- W5-002 run: `37572463564` — SUCCESS;
- strict read-only UTF-8/BOM SRT parser implemented;
- typed parser/import errors implemented;
- canonical millisecond-to-frame mapping implemented;
- valid SRT import uses existing CommandBus path;
- source-file preservation proven;
- targeted 11/11 tests + full pytest green;
- W4/W3/W2/W1/W0/S10/S09/S08 regressions all green on the same HEAD.

Evidence:
`docs/evidence/features/S11_W5_002_SRT_IMPORT_VALIDATION.md`.

## Active next task

**S11-W5-003 — Cue editing + safe working-copy flow**

W5-003 must build on the W5-001 canonical cue model and W5-002 validated
import path.

W5-003 scope:
- selected cue text/IN/OUT edits;
- insert/delete;
- split/merge;
- explicit stable sort/index normalization;
- dirty working-copy tracking and leave/reload guard;
- save edited subtitle to a new/copy SRT by default;
- never silently overwrite original source;
- committing a new source/binding remains undoable.

W5-003 must not:
- implement subtitle style rendering;
- enable subtitle animations;
- implement narration runtime/recording;
- claim ASR/speech alignment;
- start Gemini/provider work.

Do not begin W5-003 until owner says `lanjutkan`.
