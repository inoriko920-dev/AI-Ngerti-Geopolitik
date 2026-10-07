# S11 W5-005 — Subtitle Animation + Per-Word Timing Boundary

**Status:** PASS  
**Accepted implementation HEAD:** `293b369e74771d16dc90956bc6a7be4c71e01d1c`  
**Accepted workflow:** `37575611940` — SUCCESS  
**Artifact:** `ANG-S11-W5-005-Subtitle-Animation`  
**Artifact ID:** `11462966698`

## Scope

W5-005 independently qualified the initial subtitle animation set and made the
per-word timing boundary explicit.

It did not implement narration, microphone recording, frozen UI parity,
ASR/transcription or Gemini/provider behavior.

## Canonical animation contract

Supported:
- `none`;
- `Fade`;
- `Pop`;
- `Slide Up`;
- `Clean Documentary`.

Still rejected/unqualified:
- Word Reveal;
- Karaoke Highlight;
- Typewriter;
- Bounce Soft;
- Emphasis Word;
- Social Caption.

Validation:
- `none` requires zero enter/exit timing;
- non-none preset requires at least one non-zero timing side;
- timings are non-negative and bounded;
- global enter + exit timing must fit every cue to which the animation applies;
- intensity stays in the canonical 0..200 range.

## Semantic mutation

Added:
- `SetSubtitleAnimationCommand`.

Behavior:
- requires a canonical SubtitleTrack;
- replaces only animation metadata;
- uses CommandBus/CommandBatch;
- validates candidate ProjectState;
- Undo/Redo proven;
- save/reopen persistence proven.

## Render-backed behavior

FFmpeg remains a qualification adapter only.

### Fade
- canonical cue enter/exit frames compile to a real alpha envelope.

### Pop
- alpha envelope;
- font-size entrance scales from a smaller value toward canonical style size;
- intensity controls the excursion.

### Slide Up
- alpha envelope;
- vertical entrance moves upward into canonical style position;
- intensity controls travel distance.

### Clean Documentary
- alpha envelope;
- smaller/subtle vertical drift into the canonical style position;
- independently rendered rather than exposed as an unverified label.

Preview evaluation samples canonical animation progress at the requested
timeline frame.

Export evaluation uses timeline-time expressions plus each cue's canonical
enable window.

## Real preview + export evidence

Evidence uses one static baseline plus all four enabled presets.

For each of:
- Fade;
- Pop;
- Slide Up;
- Clean Documentary;

the workflow generated:
- a real preview PNG;
- a real MP4 export;
- a PNG frame extracted from that exported MP4.

Gates:
- every animation preview SHA-256 differs from static baseline preview;
- every animation exported-frame SHA-256 differs from static baseline exported
  frame;
- every export remains valid;
- every export retains audio;
- canonical duration remains within tolerance.

This proves the presets affect both preview and final exported media.

## Per-word timing boundary

Added:
- `SetSubtitleCueWordTimingsCommand`;
- application helper
  `evenly_distribute_words_not_speech_alignment`;
- boundary label:
  `NOT speech alignment`.

Manual WordTiming:
- stays frame-aware;
- is validated inside the cue;
- is semantic ProjectState;
- is Undo/Redo safe;
- persists through .angproj reopen.

Deterministic fallback:
- uses only the already-written cue text;
- splits written text by whitespace;
- distributes the cue's existing frame duration deterministically;
- requires explicit
  `acknowledge_not_speech_alignment=True`;
- refuses cues too short to give each word at least one frame.

It does **not**:
- listen to audio;
- transcribe speech;
- perform ASR;
- detect phonemes;
- infer actual spoken word boundaries;
- claim automatic speech synchronization.

## Source protection

The real evidence confirms source SRT SHA-256 is unchanged.

W5-005 does not alter the W5-003 safe-copy policy.

## Tests and gates

Target:
`tests/unit/test_step11_w5_005_animation.py`

Targeted result:
- **6/6 PASS**.

Full pytest also passes W5-001 through W5-004 regression tests.

Workflow `37575611940`:
- Ruff format PASS;
- Ruff check PASS;
- mypy PASS;
- import contracts PASS;
- architecture PASS;
- source-of-truth 70/70 PASS;
- secret scan PASS;
- targeted tests PASS;
- full pytest PASS;
- real preview/export evidence PASS;
- evidence verifier **21/21 PASS**.

## Evidence artifact

Artifact:
- name: `ANG-S11-W5-005-Subtitle-Animation`;
- ID: `11462966698`;
- size: 39,295,019 bytes.

The bundle contains:
- W5-005 report;
- animation matrix;
- per-word boundary evidence;
- history/persistence evidence;
- source SRT;
- .angproj project;
- static baseline preview/export/export-frame;
- preview/export/export-frame for each of the four qualified animations.

## Regression lock

All workflows on the accepted W5-005 HEAD are SUCCESS:
- W5-005: `37575611940`;
- W5-004: `37575611926`;
- W4: `37575611960`;
- W3: `37575611838`;
- W2: `37575611846`;
- W1: `37575611922`;
- W0: `37575611959`;
- S10: `37575611977`;
- S09: `37575611886`;
- S08: `37575611855`.

This includes:
- MLT Windows playback qualification;
- W2 MLT canonical playback projection;
- W3/W4 real-output evidence;
- W5-004 real style qualification;
- S10 real-media vertical slice;
- S10 packaged real-media smoke;
- S10 portable UI regression;
- S08/S09 portable regressions.

## Next

**S11-W5-006 — Narration import + binding only.**

Do not start microphone recording or later W5 tasks until W5-006 closes.
