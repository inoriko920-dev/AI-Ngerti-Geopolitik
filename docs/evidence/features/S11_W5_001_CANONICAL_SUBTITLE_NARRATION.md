# S11 W5-001 — Canonical Subtitle / Narration Model

**Status:** PASS  
**Accepted implementation HEAD:** `b5bf8543554bcf38d22a65510fe0376195676d46`  
**Accepted workflow:** `37571740654` — SUCCESS

## Scope

This task implemented only the W5 canonical data foundation.

Added canonical domain entities:
- `WordTiming`;
- `SubtitleStyle`;
- `SubtitleAnimation`;
- `SubtitleCue`;
- `SubtitleTrack`;
- `NarrationTrack`.

ProjectState now has:
- `subtitle: SubtitleTrack | None`;
- `narration: NarrationTrack | None`.

No SRT parser, subtitle UI, subtitle renderer, narration renderer, microphone
capture or Gemini/provider behavior was implemented in W5-001.

## Canonical validation

Subtitle:
- source reference required when a SubtitleTrack exists;
- at least one cue required for a bound canonical track;
- unique cue IDs and indexes;
- cue start/end share FPS;
- end must be after start;
- text cannot be empty;
- canonical cue order is monotonic;
- overlapping canonical cues are rejected;
- cue FPS must match project FPS;
- cues must remain inside the video timeline.

Optional WordTiming:
- stable ID and non-empty word;
- positive start/end range;
- FPS must match the parent cue;
- timing must remain within parent cue;
- overlapping word timings are rejected.

Narration:
- stable narration ID and asset ID;
- narration must reference an existing canonical Asset;
- referenced asset must be audio;
- timeline start must use project FPS and start inside the project;
- gain is bounded;
- fade values are non-negative and may not exceed source duration.

## No-fake animation boundary

W5-001 stores SubtitleAnimation canonically but accepts only `preset="none"`.

This is deliberate. Fade, Pop, Slide Up and Clean Documentary are not enabled
until W5-005 independently proves real preview/export behavior. W5-001
therefore adds state structure without advertising an unqualified renderer.

## Command/history path

Added:
- `SetSubtitleTrackCommand`;
- `SetNarrationTrackCommand`.

Both use the existing CommandBus/CommandBatch transaction/history path.

The W5-001 test proves:
- combined subtitle+narration mutation changes semantic state;
- Undo restores the previous semantic state;
- Redo restores the W5-001 state.

## Persistence compatibility

JsonProjectRepository now decodes W5-001 state.

Save remains based on the canonical semantic ProjectState representation.

Compatibility rule:
- schema remains version 1;
- old W4/schema-v1 files that do not contain `subtitle` or `narration`
  load them as `None`;
- no destructive migration/rewrite is required to open an old file.

## Tests and gates

W5-001 targeted test:
`tests/unit/test_step11_w5_001_canonical.py`

Targeted result:
- 7 tests PASS.

Workflow `37571740654`:
- uv lock PASS;
- dependency sync PASS;
- Ruff format PASS;
- Ruff lint PASS;
- mypy PASS;
- import contracts PASS;
- architecture verifier PASS;
- source-of-truth verifier PASS 70/70;
- secret scan PASS;
- W5-001 targeted tests PASS;
- full pytest PASS.

## Regression lock

All workflows on the same accepted implementation HEAD are SUCCESS:
- W5-001: `37571740654`;
- W4: `37571740680`;
- W3: `37571740678`;
- W2: `37571740732`;
- W1: `37571741010`;
- W0: `37571740664`;
- S10: `37571740757`;
- S09: `37571740743`;
- S08: `37571740660`.

This includes:
- MLT W0 qualification;
- MLT W2 canonical playback projection;
- W3 real property preview/export;
- W4 real creative preview/export;
- S10 real-media vertical slice;
- S10 packaged real-media smoke;
- S10 portable UI regression;
- S08/S09 portable packaging regressions.

## Next

**S11-W5-002 — SRT import + validation only.**

W5-002 must map validated SRT data into these canonical entities and must not
silently rewrite the source SRT.
