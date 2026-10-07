# S11 W5-003 — Subtitle Working Copy + Safe Save-Copy

**Status:** PASS  
**Accepted implementation HEAD:** `d8db4d18cb42b71d91a9b727868b25340961702f`  
**Accepted workflow:** `37573388357` — SUCCESS

## Scope

W5-003 implements cue editing as an application-level working copy and a safe
save-copy/commit path.

It does not implement subtitle style rendering, subtitle animation, narration,
microphone capture, UI parity or Gemini.

## Working-copy ownership

`SubtitleWorkingCopy` is mutable local editor state.

Important invariant:
- edits do not mutate ProjectState while the user is typing;
- the canonical subtitle binding changes only after explicit save-copy + commit;
- the W5-001 `SubtitleTrack` remains the project source of truth.

The working copy tracks:
- source reference;
- cue list;
- selected cue;
- baseline cue state;
- dirty state.

## Cue editing

Implemented:
- cue selection by stable ID;
- text edit;
- IN frame edit;
- OUT frame edit;
- insert after selected cue;
- delete selected cue where valid;
- split selected cue;
- merge selected cue with next cue.

Safety:
- invalid ranges are rejected;
- overlaps are rejected;
- final cue cannot be deleted;
- split requires explicit left and right text;
- merge requires explicit merged text;
- split/merge therefore do not guess or silently rewrite wording.

WordTiming is cleared on explicit split/merge because inherited per-word timing
would no longer be semantically valid. No new automatic alignment is claimed.

## Explicit ordering and indexes

Insert preserves existing indexes and assigns a new unique index. It does not
silently renumber existing cues.

Working-copy list ordering is allowed to differ from chronological ordering.

User/application must explicitly invoke:
- `sort_by_time()`;
- `normalize_indexes()`.

Building a canonical track for save fails until ordering is canonical.

This enforces the W5 contract that sort/index normalization are explicit
operations, not hidden side effects.

## Dirty/reload guard

`dirty` compares current cues with the baseline.

A dirty working copy cannot be reloaded/discarded implicitly.
`DirtySubtitleWorkingCopyError` is raised until the caller explicitly chooses
`discard_dirty=True`.

## Safe SRT save-copy

Application port:
- `SubtitleWriterPort`;
- `SubtitleWriteError`.

Infrastructure:
- `Utf8SrtWriter`.

Default naming:
- `source.edited.srt`;
- if occupied, `source.edited-2.srt`, then the next free number.

Protection:
- source path is rejected;
- existing destination is rejected;
- writer uses exclusive-create mode;
- failed partial writes are cleaned when possible;
- multiline text is preserved;
- no existing SRT is silently overwritten.

W5-003 intentionally exposes save-copy only. Original-source overwrite remains
disabled.

## Commit/history behavior

After successful file creation:
- edited cues become a new canonical `SubtitleTrack`;
- new `source_ref` points to the saved copy;
- style/animation/enabled state are carried forward unchanged;
- commit uses `SetSubtitleTrackCommand` through CommandBus/CommandBatch;
- working copy becomes clean only after successful project commit.

Undo restores the prior canonical subtitle track.

If the writer fails:
- ProjectState remains unchanged;
- working copy stays dirty;
- no fake success is reported.

## Tests

Target:
`tests/unit/test_step11_w5_003_working_copy.py`

Targeted coverage:
- local text/timing edit;
- invalid edit rollback;
- insert/delete;
- last-cue delete protection;
- split/merge;
- explicit sort/index normalization;
- dirty reload guard;
- default safe save-copy;
- source SHA preservation;
- canonical commit + Undo;
- source/existing-destination protection;
- non-colliding default name;
- multiline writer round-trip;
- failed writer no-commit behavior.

Targeted result:
- **12/12 PASS**.

Workflow `37573388357`:
- uv lock/sync PASS;
- Ruff format PASS;
- Ruff check PASS;
- mypy PASS;
- import contracts PASS;
- architecture verifier PASS;
- source-of-truth verifier PASS 70/70 on implementation HEAD;
- secret scan PASS;
- targeted W5-003 tests PASS;
- full pytest PASS.

The full pytest run includes W5-001 and W5-002 tests, so the SRT parser/import
path remains regression-covered on the accepted W5-003 HEAD.

## Regression lock

All workflows on the accepted implementation HEAD are SUCCESS:
- W5-003: `37573388357`;
- W4: `37573388429`;
- W3: `37573388403`;
- W2: `37573388383`;
- W1: `37573388372`;
- W0: `37573388385`;
- S10: `37573388378`;
- S09: `37573388370`;
- S08: `37573388358`.

This includes:
- MLT Windows playback qualification;
- W2 MLT canonical playback projection;
- W3/W4 real-output evidence;
- S10 real-media vertical slice;
- S10 packaged real-media smoke;
- S10 portable UI regression;
- S08/S09 portable regressions.

## Next

**S11-W5-004 — Subtitle style only.**

Do not begin W5-005 animation/per-word behavior or later tasks until W5-004
closes.
