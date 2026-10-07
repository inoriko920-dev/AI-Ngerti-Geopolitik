# PROJECT STATUS — AI NGERTI GEOPOLITIK

**Current STEP:** SF-STEP 11 — Feature Implementation Waves  
**Current wave:** **W5 — Subtitle + Narration**  
**W5 progress:** **S11-W5-001 PASS / S11-W5-002 PASS / S11-W5-003 PASS**  
**Accepted W5-003 implementation HEAD:** `d8db4d18cb42b71d91a9b727868b25340961702f`  
**Accepted W5-003 workflow:** `37573388357` — SUCCESS  
**Next exact task:** **S11-W5-004 — Subtitle style**

## W5-003 proven

Working-copy ownership:
- cue edits live in application-level `SubtitleWorkingCopy`;
- typing/edit operations do not mutate ProjectState directly;
- ProjectState changes only at explicit save-copy + commit;
- canonical `SubtitleTrack` remains the project truth.

Cue editing:
- select cue by stable cue ID;
- edit text, IN frame and OUT frame;
- invalid/overlapping edits are rejected before mutation;
- insert/delete supported where valid;
- deleting the final cue is rejected;
- split requires an explicit split frame and explicit left/right text;
- merge requires explicit merged text;
- split/merge do not invent or silently rewrite wording.

Explicit ordering/index behavior:
- insert does not silently renumber existing cue indexes;
- working-copy list may remain intentionally unsorted;
- stable chronological sort occurs only via explicit `sort_by_time()`;
- index normalization occurs only via explicit `normalize_indexes()`;
- save/commit refuses a non-canonical unsorted result.

Dirty/reload safety:
- working copy tracks dirty state against its baseline;
- reload/leave guard raises when unsaved changes would be discarded;
- discard requires an explicit `discard_dirty=True` decision.

Safe save-copy:
- default destination is `<source>.edited.srt`;
- collisions advance to `edited-2`, etc.;
- source path is rejected as a save-copy destination;
- existing destinations are never silently clobbered;
- concrete UTF-8 writer uses exclusive create;
- multiline subtitle text survives write + parse round-trip;
- writer failure leaves canonical project binding unchanged.

Commit/history:
- successful copy becomes the new canonical subtitle source binding;
- commit flows through `SetSubtitleTrackCommand` + CommandBus/CommandBatch;
- working copy becomes clean only after successful commit;
- Undo restores the previously bound subtitle track;
- original source SRT remains unchanged.

W5-003 intentionally supports **save-copy only**. Explicit overwrite of the
original source is not enabled here; that is stricter than the minimum safety
requirement and may only be revisited by a later explicit product policy.

Evidence:
`docs/evidence/features/S11_W5_003_SUBTITLE_WORKING_COPY.md`.

## W5-003 quality gate

Workflow `37573388357`:
- uv lock/sync PASS;
- Ruff format PASS;
- Ruff check PASS;
- mypy PASS;
- import contracts PASS;
- architecture PASS;
- source-of-truth 70/70 PASS on implementation HEAD;
- secret scan PASS;
- W5-003 targeted tests: **12/12 PASS**;
- full pytest PASS, including W5-002 parser/import regressions.

## Regression lock on accepted W5-003 HEAD

All SUCCESS:
- W5-003: `37573388357`;
- W4: `37573388429`;
- W3: `37573388403`;
- W2: `37573388383`;
- W1: `37573388372`;
- W0: `37573388385`;
- S10: `37573388378`;
- S09: `37573388370`;
- S08: `37573388358`.

S10 real-media vertical slice, packaged real-media smoke and portable UI
regression remain green. MLT W0/W2 qualification remains green.

## Exact next action

On owner **"lanjutkan"**, execute **S11-W5-004 — Subtitle style only**.

Do not start W5-005 animation/per-word behavior, narration, microphone, UI
parity, Gemini or later tasks in the same turn.
