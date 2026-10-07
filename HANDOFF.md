# HANDOFF — AI NGERTI GEOPOLITIK

**Current phase:** SF-STEP 11  
**Current wave:** W5 — Subtitle + Narration  
**Last completed task:** S11-W5-002 — PASS  
**Accepted W5-002 HEAD:** `d4349c925cc0f475cfa94b0db55347320954e1cf`  
**Accepted W5-002 run:** `37572463564` — SUCCESS  
**Next exact task:** S11-W5-003 — Cue editing + safe working-copy flow

## Read first

Follow `AGENTS.md` and `docs/SOURCE_OF_TRUTH_INDEX.md`.

Read:
- W0–W4 evidence in order;
- `docs/project/W5_SUBTITLE_NARRATION_CONTRACT.md`;
- `docs/evidence/features/S11_W5_001_CANONICAL_SUBTITLE_NARRATION.md`;
- `docs/evidence/features/S11_W5_002_SRT_IMPORT_VALIDATION.md`;
- current PLAN/TASKS/PROJECT_STATUS.

## W5-001 foundation

Canonical ProjectState owns:
- SubtitleTrack / SubtitleCue / SubtitleStyle / SubtitleAnimation / WordTiming;
- NarrationTrack.

## W5-002 import path

Application:
- `SubtitleParserPort`;
- `ParsedSubtitleCue`;
- `SubtitleImportService`;
- `SubtitleImportError`.

Infrastructure:
- `Utf8SrtParser`;
- typed `SubtitleParseError`.

Behavior proven:
- UTF-8 / UTF-8 BOM SRT;
- multiline preservation;
- strict timestamp/range/text validation;
- duplicate/order/overlap rejection;
- deterministic project-FPS conversion;
- sub-frame/frame-overlap/timeline-overflow rejection;
- import through CommandBus;
- Undo;
- source SRT SHA-256 unchanged.

## Critical boundary carried forward

W5-003 may edit a **working copy** of canonical cues, but:
- source SRT may not be silently overwritten;
- dirty working-copy leave/reload must be guarded;
- save defaults to a new/copy SRT;
- commit of the new source/binding remains semantic and undoable;
- no style/animation/narration/recorder work yet.

SubtitleAnimation still accepts only `none`; do not enable any visual
animation until W5-005.

## Regression lock on W5-002 accepted HEAD

All SUCCESS:
- W5-002 `37572463564`
- W4 `37572463547`
- W3 `37572463561`
- W2 `37572463569`
- W1 `37572463539`
- W0 `37572463562`
- S10 `37572463627`
- S09 `37572463558`
- S08 `37572463571`

## Next exact action

After owner says `lanjutkan`, execute **S11-W5-003 only**:
cue text/IN/OUT edit, insert/delete, split/merge, explicit sort/index
normalization, safe dirty working copy, reload guard and save-copy semantics.

Do not start W5-004 or later tasks.
