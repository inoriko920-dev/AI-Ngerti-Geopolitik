# S11 W5-002 — SRT Import + Validation

**Status:** PASS  
**Accepted implementation HEAD:** `d4349c925cc0f475cfa94b0db55347320954e1cf`  
**Accepted workflow:** `37572463564` — SUCCESS

## Scope

W5-002 implements validated, read-only SRT import into the W5-001 canonical
subtitle model.

It does not implement cue editing UI, subtitle styling, subtitle animation,
narration, recording or Gemini.

## Architecture

Application owns:
- `ParsedSubtitleCue` DTO;
- `SubtitleParserPort`;
- `SubtitleParseError` contract;
- `SubtitleImportService`;
- `SubtitleImportError`;
- millisecond-to-project-frame mapping.

Infrastructure owns:
- concrete `Utf8SrtParser`.

The concrete parser depends inward on application port/DTO contracts. The
application layer does not import concrete infrastructure.

## SRT parsing

Accepted input:
- `.srt` files;
- UTF-8;
- UTF-8 with BOM;
- LF, CRLF and CR line endings.

Behavior:
- line endings normalize only in memory;
- cue multiline text is retained with newline separators;
- a terminal file newline is not treated as subtitle content;
- source file is never opened for writing.

Strict validation:
- numeric positive cue index;
- duplicate cue indexes rejected;
- timestamp format `HH:MM:SS,mmm`;
- minute/second component range 00..59;
- exactly one timing separator `-->`;
- end must be after start;
- non-empty cue text;
- chronological order;
- no source-time overlap.

Malformed, missing, wrong-extension, unreadable or non-UTF8 input produces
typed `SubtitleParseError`.

## Canonical mapping

W5-002 converts validated milliseconds to project frames deterministically.

Additional canonical checks:
- a cue may not collapse to zero frames at the project FPS;
- frame conversion may not create a new overlap;
- cue end may not exceed canonical project timeline;
- valid entries become W5-001 `SubtitleCue` values inside `SubtitleTrack`.

This preserves one project truth rather than creating a second SRT-owned
timeline model.

## Import transaction and source protection

`SubtitleImportService` commits through:
- `CommandBatch`;
- `SetSubtitleTrackCommand`;
- existing CommandBus history.

Proof:
- valid import binds canonical SubtitleTrack;
- project revision advances;
- Undo removes the binding;
- source SRT SHA-256 is identical before and after import.

W5-002 does not implement save/edit behavior, so there is no write path to the
source SRT.

## Tests

Target:
`tests/unit/test_step11_w5_002_srt.py`

Covered:
- BOM + multiline parsing;
- canonical frame mapping;
- import + Undo + source SHA preservation;
- invalid timestamp;
- backwards range;
- overlap;
- chronological-order failure;
- duplicate index;
- empty text;
- non-UTF8;
- wrong extension;
- sub-frame cue rejection;
- project overflow;
- frame-quantization overlap.

Targeted result:
- **11/11 PASS**.

Workflow `37572463564`:
- uv lock/sync PASS;
- Ruff format PASS;
- Ruff check PASS;
- mypy PASS;
- import contracts PASS;
- architecture verifier PASS;
- source-of-truth verifier PASS 70/70;
- secret scan PASS;
- targeted tests PASS;
- full pytest PASS.

## Regression lock

All workflows on the accepted W5-002 implementation HEAD are SUCCESS:
- W5-002: `37572463564`;
- W4: `37572463547`;
- W3: `37572463561`;
- W2: `37572463569`;
- W1: `37572463539`;
- W0: `37572463562`;
- S10: `37572463627`;
- S09: `37572463558`;
- S08: `37572463571`.

This includes:
- MLT Windows playback qualification;
- W2 MLT canonical projection;
- W3/W4 real-output evidence;
- S10 real-media vertical slice;
- S10 packaged real-media smoke;
- S10 portable UI regression;
- S08/S09 portable regressions.

## Next

**S11-W5-003 — Cue editing + safe working-copy flow only.**

W5-003 must protect the imported source and use save-copy semantics. It must
not begin W5-004 style or later tasks.
