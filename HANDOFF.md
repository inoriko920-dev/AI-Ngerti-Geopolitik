# HANDOFF — AI NGERTI GEOPOLITIK

**Current phase:** SF-STEP 11  
**Current wave:** W5 — Subtitle + Narration  
**Last completed task:** S11-W5-006 — PASS  
**Accepted W5-006 HEAD:** `77770cd98210dbed18cbe1715111a935f2135b77`  
**Accepted W5-006 run:** `37577639655` — SUCCESS  
**Next exact task:** S11-W5-007 — Microphone recording

## Read first

Follow `AGENTS.md` and `docs/SOURCE_OF_TRUTH_INDEX.md`.

Read:
- W0–W4 evidence;
- W5 contract;
- W5-001 through W5-006 evidence;
- current PLAN/TASKS/PROJECT_STATUS.

## W5-006 implementation now available

Application:
- `application/narration.py`;
- `NarrationImportService.import_and_bind(...)`;
- atomic ImportAssetCommand + SetNarrationTrackCommand;
- `bind_existing(...)` for an existing canonical audio asset;
- stable narration IDs;
- non-audio sources rejected before project mutation.

Domain:
- NarrationTrack remains canonical;
- frame-aware offset;
- gain/mute/fade;
- fade bounds now use the audible segment remaining inside the project timeline.

Qualification runtime:
- `infrastructure/ffmpeg_narration.py`;
- source trim;
- gain;
- mute;
- fade in/out;
- timeline delay;
- mix with existing project audio;
- narration preview WAV excerpt;
- narration mixed into real exported MP4.

## Real audio evidence

Fixture:
- base video audio: 880 Hz;
- narration: 440 Hz.

Evidence proves:
- 440 Hz is audible in preview WAV;
- 440 Hz is low before narration offset and strong after offset;
- gain boost increases narration band level;
- mute removes narration band energy;
- fade-in changes narration level near start;
- narrated export keeps audio;
- source narration WAV is unchanged;
- project save/reopen retains binding/timing/controls.

Workflow:
`37577639655` — SUCCESS

Verifier:
**11/11 PASS**

Artifact:
`ANG-S11-W5-006-Narration`
ID: `11462194359`
Size: 28,535,901 bytes.

## Critical boundaries carried forward

- ProjectState + CommandBus remain canonical.
- FFmpeg remains qualification, not a production-engine switch.
- Narration is a first-class source/binding, not generic clip-volume state.
- Only one canonical NarrationTrack is bound at a time.
- W5-006 does not implement microphone capture.
- W5-007 must use a dedicated recording application port/adapter.
- Recording must stage first and validate before binding.
- Failed/cancelled/empty recording must not clobber existing narration.
- No Gemini/provider work.

## Regression lock on accepted W5-006 HEAD

All SUCCESS:
- W5-006 `37577639655`
- W5-005 `37577639727`
- W5-004 `37577639737`
- W4 `37577639656`
- W3 `37577639667`
- W2 `37577639693`
- W1 `37577639687`
- W0 `37577639704`
- S10 `37577639665`
- S09 `37577639668`
- S08 `37577639634`

## Next exact action

After owner says `lanjutkan`, execute **S11-W5-007 only**:
- define/use a dedicated microphone RecorderPort;
- require active project and available device;
- record first to a staging WAV;
- validate staged recording before canonical import/bind;
- use safe finalization semantics;
- failed/empty/cancelled capture must preserve current narration;
- deterministic tests mandatory;
- real Windows microphone evidence if a capture device exists;
- if no physical capture device exists in CI/evidence environment, document
  the hardware gate precisely instead of faking a PASS.

Do not start W5-008 or later tasks.
