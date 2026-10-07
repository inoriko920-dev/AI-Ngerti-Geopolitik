# HANDOFF — AI NGERTI GEOPOLITIK

**Current phase:** SF-STEP 11  
**Current wave:** W5 — Subtitle + Narration  
**Last completed task:** S11-W5-005 — PASS  
**Accepted W5-005 HEAD:** `293b369e74771d16dc90956bc6a7be4c71e01d1c`  
**Accepted W5-005 run:** `37575611940` — SUCCESS  
**Next exact task:** S11-W5-006 — Narration import + binding

## Read first

Follow `AGENTS.md` and `docs/SOURCE_OF_TRUTH_INDEX.md`.

Read:
- W0–W4 evidence;
- W5 contract;
- W5-001 through W5-005 evidence;
- current PLAN/TASKS/PROJECT_STATUS.

## W5-005 implementation now available

Canonical animation:
- `SUPPORTED_SUBTITLE_ANIMATIONS`:
  none, Fade, Pop, Slide Up, Clean Documentary;
- `UNSUPPORTED_SUBTITLE_ANIMATIONS`:
  Word Reveal, Karaoke Highlight, Typewriter, Bounce Soft, Emphasis Word,
  Social Caption;
- `SetSubtitleAnimationCommand`;
- cue-length validation for global enter/exit timing;
- persistence/Undo/Redo.

Qualification rendering:
- Fade = alpha envelope;
- Pop = alpha + font-size entrance;
- Slide Up = alpha + vertical rise;
- Clean Documentary = alpha + subtle vertical drift;
- real preview and exported-frame evidence exists for all four enabled presets.

Per-word boundary:
- `SetSubtitleCueWordTimingsCommand` for explicit/manual semantic timing;
- `evenly_distribute_words_not_speech_alignment` is an explicit deterministic
  fallback only;
- fallback requires `acknowledge_not_speech_alignment=True`;
- boundary label is `NOT speech alignment`;
- no ASR/transcription/audio analysis exists.

## Evidence

Workflow:
`37575611940` — SUCCESS

Verifier:
**21/21 PASS**

Artifact:
`ANG-S11-W5-005-Subtitle-Animation`
ID: `11462966698`
Size: 39,295,019 bytes.

## Critical boundaries carried forward

- ProjectState + CommandBus remain canonical.
- FFmpeg remains qualification, not production-engine switch.
- Only four non-none subtitle animation presets are render-qualified.
- Unsupported animation labels remain hidden/disabled.
- WordTiming metadata is not evidence of speech alignment.
- No ASR/transcription claim may be introduced.
- Source SRT remains protected.
- W5-006 is narration import/binding only.
- Do not start microphone capture in W5-006.
- Do not start Gemini/provider work.

## Regression lock on accepted W5-005 HEAD

All SUCCESS:
- W5-005 `37575611940`
- W5-004 `37575611926`
- W4 `37575611960`
- W3 `37575611838`
- W2 `37575611846`
- W1 `37575611922`
- W0 `37575611959`
- S10 `37575611977`
- S09 `37575611886`
- S08 `37575611855`

## Next exact action

After owner says `lanjutkan`, execute **S11-W5-006 only**:
- import a supported narration audio file through canonical media probe/identity;
- bind one canonical NarrationTrack;
- frame-aware timeline offset;
- bounded gain/mute/fade only if real runtime proves them;
- narration audible in preview/export evidence;
- save/reopen and Undo/Redo.

Do not start W5-007 microphone recording or later tasks.
