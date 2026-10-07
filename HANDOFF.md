# HANDOFF — AI NGERTI GEOPOLITIK

**Current phase:** SF-STEP 11  
**Current wave:** W5 — Subtitle + Narration  
**Last completed task:** S11-W5-008 — PASS  
**Accepted W5-008 HEAD:** `b65bf585510ee442584a7ebbe8db8c3d40ac1533`  
**Accepted W5-008 run:** `37579815809` — SUCCESS  
**Next exact task:** S11-W5-009 — Real subtitle/narration preview/export qualification

## Read first

Follow `AGENTS.md` and `docs/SOURCE_OF_TRUTH_INDEX.md`.

Read:
- W0–W4 evidence;
- W5 contract;
- W5-001 through W5-008 evidence;
- current PLAN/TASKS/PROJECT_STATUS;
- frozen AAVC UI manifest and references.

## W5-008 implementation now available

Presentation module:
`presentation/w5_workspace.py`.

Subtitle surface:
- real Teks/Gaya/Animasi widgets;
- semantic cue editing/import/save-copy intents;
- only qualified style fonts exposed;
- only qualified subtitle animation presets selectable;
- unsupported presets not selectable;
- manual WordTiming surface;
- explicit NOT-speech-alignment gate for deterministic even distribution;
- unqualified word-highlight/karaoke remains disabled.

Narration surface:
- import;
- offset/gain/mute/fades;
- preview;
- recording entry point;
- provisional microphone qualification label.

WIN-001 recording dialog:
- device-gated start button;
- refresh/start/cancel intents;
- real device list can be projected through `apply_microphone_devices(...)`;
- no-device state is honest and disabled.

Architecture:
- presentation emits UiIntent only;
- no direct ProjectState/engine mutation;
- no presentation import of concrete infrastructure.

## Evidence

Workflow:
`37579815809` — SUCCESS

Artifact:
`ANG-S11-W5-008-Frozen-UI`
ID: `11463699327`
Size: 4,396,724 bytes.

Qt target:
**6/6 PASS**

Full pytest:
PASS.

Frozen reference integrity:
**42/42 SHA-256 PASS**.

Evidence verifier:
**14/14 PASS**.

## Regression lock

All SUCCESS:
- W5-008 `37579815809`
- W5-007 `37579815674`
- W5-006 `37579815770`
- W5-005 `37579815678`
- W5-004 `37579815803`
- W4 `37579815689`
- W3 `37579815801`
- W2 `37579815721`
- W1 `37579815778`
- W0 `37579815762`
- S10 `37579815716`
- S09 `37579815683`
- S08 `37579815729`

## Critical boundaries for W5-009

- Do not redesign or expand UI in W5-009.
- Use canonical W5 state built in W5-001..007.
- FFmpeg remains qualification adapter only.
- Source SRT must remain unchanged.
- Enabled subtitle animations are only the four already qualified presets.
- No ASR/transcription/speech alignment claim.
- Microphone hardware remains provisional.
- W5-009 must prove subtitle + narration can coexist in one real export.
- Do not start W5-010 or later work.

## Next exact action

After owner says `lanjutkan`, execute **S11-W5-009 only**:
- deterministic owned video/audio/SRT fixture;
- import SRT;
- edit text/timing and save/reopen;
- visible style;
- real enabled animation evidence;
- real narration offset/audio evidence;
- combined subtitle + narration export;
- output validity/duration/audio checks;
- source SRT unchanged.
