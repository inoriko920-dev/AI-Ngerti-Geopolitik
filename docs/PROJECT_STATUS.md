# PROJECT STATUS — AI NGERTI GEOPOLITIK

**Current STEP:** SF-STEP 11 — Feature Implementation Waves  
**Current wave:** **W5 — Subtitle + Narration**  
**W5 progress:** **S11-W5-001 PASS / S11-W5-002 PASS**  
**Accepted W5-002 implementation HEAD:** `d4349c925cc0f475cfa94b0db55347320954e1cf`  
**Accepted W5-002 workflow:** `37572463564` — SUCCESS  
**Next exact task:** **S11-W5-003 — Cue editing + safe working-copy flow**

## W5-002 proven

Architecture:
- application owns `SubtitleParserPort`, `ParsedSubtitleCue` and import use-case;
- concrete `Utf8SrtParser` lives in infrastructure;
- parser output is mapped into the W5-001 canonical `SubtitleCue` /
  `SubtitleTrack` model;
- no parallel subtitle project-state owner was created.

SRT input:
- `.srt` extension required;
- UTF-8 and UTF-8 BOM accepted;
- CRLF/CR/LF normalized in memory only;
- multiline cue meaning is preserved;
- terminal file newline is not treated as subtitle text;
- source file is opened read-only and is never rewritten during import.

Validation:
- strict `HH:MM:SS,mmm` timestamps;
- minute/second components must be within 00..59;
- positive numeric cue index;
- duplicate cue index rejected;
- end must be after start;
- empty cue text rejected;
- out-of-order cues rejected;
- overlapping SRT cues rejected;
- malformed/unreadable/non-UTF8 sources produce typed actionable failures.

Canonical frame mapping:
- milliseconds are deterministically mapped to project FPS;
- cue timing that collapses below one representable frame is rejected;
- overlap introduced by frame conversion is rejected;
- cues outside the canonical project timeline are rejected.

Import transaction:
- valid SRT is committed through `SetSubtitleTrackCommand` and the existing
  CommandBus/CommandBatch path;
- import increments project revision;
- Undo removes the imported subtitle binding;
- source-file SHA-256 remains unchanged before/after import.

Evidence:
`docs/evidence/features/S11_W5_002_SRT_IMPORT_VALIDATION.md`.

## Explicit non-claims

W5-002 does **not** implement:
- cue editor/working-copy save flow;
- source overwrite/save-copy behavior;
- subtitle style rendering;
- subtitle animation rendering;
- narration runtime/recording;
- ASR/speech alignment;
- Gemini/provider/AI Auto Edit.

Those remain gated to later W5 tasks.

## W5-002 quality gate

Workflow `37572463564`:
- uv lock/sync PASS;
- Ruff format PASS;
- Ruff check PASS;
- mypy PASS;
- import contracts PASS;
- architecture PASS;
- source-of-truth 70/70 PASS;
- secret scan PASS;
- W5-002 targeted tests: **11/11 PASS**;
- full pytest PASS.

## Regression lock on accepted W5-002 HEAD

All SUCCESS:
- W5-002: `37572463564`;
- W4: `37572463547`;
- W3: `37572463561`;
- W2: `37572463569`;
- W1: `37572463539`;
- W0: `37572463562`;
- S10: `37572463627`;
- S09: `37572463558`;
- S08: `37572463571`.

S10 real-media vertical slice, packaged real-media smoke and portable UI
regression all remain green. MLT W0/W2 qualification remains green.

## Exact next action

On owner **"lanjutkan"**, execute **S11-W5-003 — Cue editing + safe
working-copy flow only**.

Do not start W5-004 style, W5-005 animation, narration, microphone, Gemini or
later tasks in the same turn.
