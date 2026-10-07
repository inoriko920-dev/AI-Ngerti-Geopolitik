# PROJECT STATUS — AI NGERTI GEOPOLITIK

**Current STEP:** SF-STEP 11 — Feature Implementation Waves  
**Last completed wave:** **W4 — PASS**  
**Current wave:** **W5 — Subtitle + Narration**  
**W5 progress:** **S11-W5-001 — PASS**  
**Accepted W5-001 implementation HEAD:** `b5bf8543554bcf38d22a65510fe0376195676d46`  
**Accepted W5-001 workflow:** `37571740654` — SUCCESS  
**Next exact task:** **S11-W5-002 — SRT import + validation**

## W5-001 proven

Canonical domain now owns:
- `SubtitleTrack`;
- `SubtitleCue`;
- `SubtitleStyle`;
- `SubtitleAnimation`;
- optional `WordTiming`;
- `NarrationTrack`.

ProjectState now stores subtitle/narration as first-class optional state without
reusing W4 title overlay or generic video-track state.

Validation proven:
- cue IDs/indexes are unique;
- cue timing is frame-aware and ordered;
- overlapping canonical subtitle cues are rejected;
- empty/invalid timing ranges are rejected;
- word timings must stay inside their cue and share project FPS;
- subtitle cues must stay inside the canonical video timeline;
- narration must reference a canonical audio Asset;
- narration timing/FPS/fades are bounded;
- narration may not start outside the project timeline.

Mutation/persistence:
- `SetSubtitleTrackCommand` and `SetNarrationTrackCommand` use the existing
  CommandBus/CommandBatch path;
- Undo/Redo restores semantic state;
- .angproj round-trip preserves W5-001 state;
- legacy W4/schema-v1 files without `subtitle` or `narration` load with
  safe `None` defaults;
- schema version remains 1 because the new fields are backward-compatible
  optional extensions.

No capability overclaim:
- subtitle animation remains canonical `none` only at W5-001;
- render-backed animation names remain blocked until W5-005;
- no SRT parser, subtitle UI, narration runtime, recorder or Gemini work was
  started.

Evidence:
`docs/evidence/features/S11_W5_001_CANONICAL_SUBTITLE_NARRATION.md`.

## W5-001 quality gate

Workflow `37571740654`:
- uv lock/sync PASS;
- Ruff format PASS;
- Ruff check PASS;
- mypy PASS;
- import contracts PASS;
- architecture PASS;
- source-of-truth 70/70 PASS;
- secret scan PASS;
- W5-001 targeted tests: 7/7 PASS;
- full pytest PASS.

## Regression lock on accepted W5-001 HEAD

All SUCCESS:
- W5-001: `37571740654`;
- W4: `37571740680`;
- W3: `37571740678`;
- W2: `37571740732`;
- W1: `37571741010`;
- W0: `37571740664`;
- S10: `37571740757`;
- S09: `37571740743`;
- S08: `37571740660`.

S10 real-media, packaged real-media and portable UI regression remain green.
MLT W0/W2 qualification also remains green.

## Exact next action

On owner **"lanjutkan"**, execute **S11-W5-002 — SRT import + validation only**.

Do not start cue UI/editing, style, animations, narration binding/recording,
Gemini, or later W5 tasks in the same turn.
