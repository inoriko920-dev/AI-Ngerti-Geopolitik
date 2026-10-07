# PROJECT STATUS — AI NGERTI GEOPOLITIK

**Current STEP:** SF-STEP 11 — Feature Implementation Waves  
**Current wave:** **W5 — Subtitle + Narration**  
**W5 progress:** **S11-W5-001/002/003/004/005 PASS**  
**Accepted W5-005 implementation HEAD:** `293b369e74771d16dc90956bc6a7be4c71e01d1c`  
**Accepted W5-005 workflow:** `37575611940` — SUCCESS  
**Next exact task:** **S11-W5-006 — Narration import + binding**

## W5-005 proven

Canonical animation boundary:
- supported canonical presets are exactly:
  - `none`;
  - `Fade`;
  - `Pop`;
  - `Slide Up`;
  - `Clean Documentary`;
- unsupported/unqualified legacy names remain rejected:
  - Word Reveal;
  - Karaoke Highlight;
  - Typewriter;
  - Bounce Soft;
  - Emphasis Word;
  - Social Caption;
- animation enter/exit timing is frame-based;
- non-none animation requires at least one non-zero timing side;
- enter/exit timing is bounded and must fit every cue;
- intensity remains bounded 0..200.

Semantic mutation/history:
- `SetSubtitleAnimationCommand` requires a bound SubtitleTrack;
- mutation flows through CommandBus/CommandBatch;
- Undo/Redo proven;
- .angproj save/reopen preserves animation.

Real render semantics:
- **Fade:** real alpha envelope;
- **Pop:** alpha envelope + real animated font-size entrance;
- **Slide Up:** alpha envelope + real vertical rise;
- **Clean Documentary:** alpha envelope + smaller/subtle vertical drift;
- preview uses canonical cue/frame progress;
- export uses canonical cue timing windows on the composed timeline;
- every enabled preset changed a real preview relative to static subtitle;
- every enabled preset changed a frame extracted from its real exported MP4;
- every animated export remained valid and retained audio.

Per-word boundary:
- added semantic `SetSubtitleCueWordTimingsCommand`;
- manual WordTiming remains canonical, frame-aware and undoable;
- WordTiming persists through .angproj reopen;
- deterministic even distribution exists only behind the explicit API
  `evenly_distribute_words_not_speech_alignment(...)`;
- caller must explicitly acknowledge `NOT speech alignment`;
- fallback uses only existing written cue text + cue duration;
- **no audio analysis, ASR, transcription, phoneme recognition or speech
  alignment is performed or claimed**.

Source protection:
- W5-005 does not rewrite source SRT;
- source SHA-256 remained unchanged in real evidence.

Evidence:
`docs/evidence/features/S11_W5_005_SUBTITLE_ANIMATION_WORD_TIMING.md`.

Artifact:
- `ANG-S11-W5-005-Subtitle-Animation`;
- ID `11462966698`;
- size 39,295,019 bytes.

## W5-005 quality/evidence gate

Workflow `37575611940`:
- Ruff format PASS;
- Ruff check PASS;
- mypy PASS;
- import contracts PASS;
- architecture PASS;
- source-of-truth 70/70 PASS;
- secret scan PASS;
- targeted W5-005 tests: **6/6 PASS**;
- full pytest PASS;
- real W5-005 animation/export evidence PASS;
- evidence verifier: **21/21 PASS**.

## Regression lock on accepted W5-005 HEAD

All SUCCESS:
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

This includes MLT W0/W2 qualification, W3/W4 real output, W5-004 style real
output, S10 real-media vertical slice, packaged real-media smoke, portable UI
regression and S08/S09 portable regressions.

## Exact next action

On owner **"lanjutkan"**, execute **S11-W5-006 — Narration import + binding
only**.

Do not start microphone recording, frozen UI parity, final W5 qualification,
Gemini/provider work or later tasks in the same turn.
