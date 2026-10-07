# HANDOFF — AI NGERTI GEOPOLITIK

**Current phase:** SF-STEP 11  
**Current wave:** W5 — Subtitle + Narration  
**Last completed task:** S11-W5-003 — PASS  
**Accepted W5-003 HEAD:** `d8db4d18cb42b71d91a9b727868b25340961702f`  
**Accepted W5-003 run:** `37573388357` — SUCCESS  
**Next exact task:** S11-W5-004 — Subtitle style

## Read first

Follow `AGENTS.md` and `docs/SOURCE_OF_TRUTH_INDEX.md`.

Read:
- W0–W4 evidence in order;
- `docs/project/W5_SUBTITLE_NARRATION_CONTRACT.md`;
- W5-001 / W5-002 / W5-003 evidence;
- current PLAN/TASKS/PROJECT_STATUS.

## W5-003 working-copy path

Application:
- `SubtitleWorkingCopy`;
- `SubtitleWorkingCopyService`;
- `SubtitleWorkingCopyError`;
- `DirtySubtitleWorkingCopyError`;
- `SubtitleWriterPort` / `SubtitleWriteError`.

Infrastructure:
- `Utf8SrtWriter` no-clobber save-copy writer;
- existing `Utf8SrtParser` remains the read path.

Behavior proven:
- local text/IN/OUT edit;
- insert/delete;
- split/merge with explicit text;
- explicit sort and index normalization;
- dirty discard/reload guard;
- default non-colliding save-copy name;
- no source overwrite;
- no existing destination clobber;
- multiline round-trip;
- failed writer cannot commit project state;
- save-copy commit is undoable.

## Critical boundaries carried forward

- ProjectState is not mutated while typing in the subtitle working copy.
- Original source SRT cannot be overwritten by W5-003.
- SubtitleAnimation still accepts only `none`.
- W5-004 may change only canonical subtitle style.
- Do not enable visual subtitle animation until W5-005.
- Do not start narration/recording/Gemini work.

## Regression lock on W5-003 accepted HEAD

All SUCCESS:
- W5-003 `37573388357`
- W4 `37573388429`
- W3 `37573388403`
- W2 `37573388383`
- W1 `37573388372`
- W0 `37573388385`
- S10 `37573388378`
- S09 `37573388370`
- S08 `37573388358`

Full pytest in W5-003 also includes W5-002 parser/import tests.

## Next exact action

After owner says `lanjutkan`, execute **S11-W5-004 only**:
canonical subtitle style mutation/persistence/history and render qualification
for the frozen style properties.

Do not start W5-005 or later tasks.
