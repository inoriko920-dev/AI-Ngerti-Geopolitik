# HANDOFF — AI NGERTI GEOPOLITIK

**Current phase:** SF-STEP 11  
**Last completed wave:** W5 — Subtitle + Narration  
**W5 status:** PASS_WITH_PROVISIONAL_MIC_HARDWARE  
**Accepted implementation HEAD:** `cb54b544dd8c6977d117bb71e137117830feb061`  
**W5-010 run:** `37583174352` — SUCCESS

## Read first

Follow `AGENTS.md` and `docs/SOURCE_OF_TRUTH_INDEX.md`.

Read:
- frozen Product / Master Blueprint;
- W0–W4 evidence;
- W5 contract;
- W5-001 through W5-010 evidence;
- current PLAN/TASKS/PROJECT_STATUS.

## W5 is closed

Implemented and qualified:
- canonical SRT subtitle model/import/edit/save-copy;
- subtitle style;
- Fade, Pop, Slide Up, Clean Documentary;
- explicit NOT-speech-alignment per-word boundary;
- narration import/binding/offset/gain/mute/fades;
- microphone software/staging path;
- frozen subtitle/narration UI;
- combined subtitle+narration real preview/export;
- history, compatibility and failure safety.

W5-010 additionally proves:
- malformed SRT cannot mutate project state;
- dirty working copy cannot be silently discarded;
- missing/corrupt narration cannot fake success;
- missing bound narration source cannot create fake preview output;
- failed recording cannot clobber existing narration;
- pre-W5 W4 project loads with safe W5 defaults.

## Final regression lock

Same accepted HEAD all SUCCESS:
- W5-010 `37583174352`
- W5-009 `37583174359`
- W5-008 `37583174310`
- W5-007 `37583174255` attempt 2
- W5-006 `37583174384` attempt 2
- W5-005 `37583174296`
- W5-004 `37583174275`
- W4 `37583174301`
- W3 `37583174280`
- W2 `37583174363` attempt 2
- W1 `37583174318`
- W0 `37583174261`
- S10 `37583174258` attempt 2
- S09 `37583174265`
- S08 `37583174297`

Attempt 2 was used only after external Chocolatey 504 failures.

## Hardware qualifier

The software microphone path is PASS.

Physical microphone capture remains **PROVISIONAL** because GitHub hosted
Windows runners exposed zero DirectShow audio input devices.

Never upgrade that claim without real-device evidence.

## Boundaries carried forward

- ProjectState / CommandBus remain canonical.
- MLT remains primary production-engine candidate.
- FFmpeg remains qualification adapter.
- no ASR/transcription/speech alignment.
- unsupported subtitle animations remain disabled.
- unsupported W4 effects/crossfade remain disabled.
- Reverse remains disabled.
- no Gemini/provider work unless the next frozen wave explicitly requires it.
- SF-STEP 12 remains blocked.

## Next exact action

There is currently **no W6 contract in repository source-of-truth**.

After owner says `lanjutkan`:
1. read frozen Product/Master Blueprint;
2. identify the actual next SF-STEP 11 feature wave;
3. lock its contract/planning first;
4. do not implement until that next wave is explicitly defined.
