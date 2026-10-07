# HANDOFF — AI NGERTI GEOPOLITIK

**Current phase:** SF-STEP 11  
**Last completed wave:** W4 — PASS  
**Current wave:** W5 — Subtitle + Narration  
**W5 state:** CONTRACT_LOCKED / IMPLEMENTATION_NOT_STARTED  
**Next exact task:** S11-W5-001 — Canonical subtitle/narration model

## Read first

Follow `AGENTS.md` and `docs/SOURCE_OF_TRUTH_INDEX.md`.

Read:
- W0–W4 evidence in order;
- `docs/project/W5_SUBTITLE_NARRATION_CONTRACT.md`;
- `docs/project/PLAN.md`;
- `docs/project/TASKS.md`;
- `docs/PROJECT_STATUS.md`.

## W5 decision

W5 is not Gemini. It is the MUST-parity **Subtitle + Narration** wave.

Frozen user-facing references:
- SCR-008 Subtitle Workspace;
- SCR-009 Audio/Narration Workspace;
- UI-017 subtitle cue/text editor;
- UI-018 audio/narration workspace;
- UI-033 style;
- UI-034 animation;
- UI-035/UI-036 per-word/highlight timing states;
- WIN-001 narration recording;
- WIN-003 subtitle edit/timing tools.

## Critical W5 boundaries

- Subtitle is a new canonical project subsystem; do not reuse W4 title overlay.
- SRT text/timing must not be silently rewritten.
- Edited subtitle defaults to save-copy behavior; never silently overwrite the
  original SRT.
- Subtitle animation controls must be hidden/disabled unless render-backed.
- AAVC reference currently proves concrete compiler behavior for Fade, Pop,
  Slide Up and Clean Documentary. Do not assume the rest are equivalent.
- Even word distribution is not speech alignment.
- Narration is a first-class project binding/track, not merely generic clip
  volume.
- Microphone capture must stage and validate before commit; failed capture may
  not clobber an existing narration.
- Project mutations remain CommandBus/CommandBatch.
- Presentation cannot mutate concrete engine objects or project JSON.
- No Gemini/provider/AI Auto Edit in W5.

## Accepted previous baseline

W4 implementation HEAD:
`3e3cd376189e9f183e70ca537ad25f037e25bcd7`

Regression workflow IDs:
- W4 `37570612799`
- W3 `37570612705`
- W2 `37570612673`
- W1 `37570612719`
- W0 `37570612737`
- S10 `37570612830`
- S09 `37570612683`
- S08 `37570612789`

All are SUCCESS.

## Next exact action

After owner says `lanjutkan`, implement **S11-W5-001 only**:
canonical subtitle/narration domain state + validation + persistence migration
+ unit tests.

Do not implement SRT parsing/UI/recording yet in that turn unless required only
to compile a contract test for W5-001.
