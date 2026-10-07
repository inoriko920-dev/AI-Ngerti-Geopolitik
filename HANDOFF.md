# HANDOFF — AI NGERTI GEOPOLITIK

**Current phase:** SF-STEP 11  
**Current wave:** W5 — Subtitle + Narration  
**Last completed task:** S11-W5-007 — PASS_WITH_PROVISIONAL_MIC_HARDWARE  
**Accepted W5-007 HEAD:** `be4daa667bf5030ba3810460cc6841a2e8be4fee`  
**Accepted W5-007 run:** `37578572691` — SUCCESS  
**Next exact task:** S11-W5-008 — Frozen UI parity

## Read first

Follow `AGENTS.md` and `docs/SOURCE_OF_TRUTH_INDEX.md`.

Read:
- W0–W4 evidence;
- W5 contract;
- W5-001 through W5-007 evidence;
- current PLAN/TASKS/PROJECT_STATUS;
- frozen AAVC UI manifest and raw UI-001..UI-042 references.

## W5-007 implementation now available

Application:
- `RecorderPort`;
- `RecordingDevice`;
- `RecordingResult`;
- `MicrophoneRecordingService`.

Safety flow:
1. require active project timeline;
2. verify real selected input device exists;
3. record only to unique staging WAV;
4. validate staging existence, size, media type, duration and sample rate;
5. choose a collision-safe new final recording path;
6. reserve final destination without overwriting existing files;
7. atomically move validated staging to final;
8. use W5-006 NarrationImportService for canonical import/bind;
9. remove new final file if canonical bind fails.

Failure/cancel behavior:
- existing narration remains unchanged;
- no partial canonical asset/binding is created;
- staging is cleaned;
- existing destination files are never overwritten.

Windows adapter:
- `WindowsFfmpegRecorder`;
- DirectShow audio device enumeration;
- PCM s16le / mono / 48 kHz capture;
- CancellationToken termination support.

## Hardware status

GitHub Windows runner exposed:
- DirectShow audio devices: **0**.

Therefore:
**PASS_WITH_PROVISIONAL_MIC_HARDWARE**.

No real microphone recording was attempted because there was no physical/input
device to select. This is not a failure of the deterministic recording path,
and hardware support is not falsely claimed.

A later real-Windows hardware smoke can remove the provisional qualifier if it
enumerates a device, captures valid WAV audio and binds it canonically.

## Evidence

Workflow:
`37578572691` — SUCCESS

Artifact:
`ANG-S11-W5-007-Microphone`
ID: `11463438121`

Targeted deterministic tests:
**6/6 PASS**.

Full pytest:
PASS.

## Regression lock

All SUCCESS:
- W5-007 `37578572691`
- W5-006 `37578572686`
- W5-005 `37578572661`
- W5-004 `37578572726`
- W4 `37578572750`
- W3 `37578572725`
- W2 `37578572751`
- W1 `37578572684`
- W0 `37578572742`
- S10 `37578572702`
- S09 `37578572748`
- S08 `37578572764`

## Critical boundaries for W5-008

- Do not redesign the frozen AAVC UI.
- UI may expose only proven W5 capabilities.
- Unsupported subtitle animation labels remain hidden/disabled.
- Per-word fallback must still say **NOT speech alignment**.
- Microphone controls must surface device-unavailable/capture errors.
- UI must not claim microphone hardware qualification when hardware evidence is
  still provisional.
- Presentation emits semantic intents only; no direct ProjectState/engine JSON
  mutation.
- Do not start W5-009 or later work.

## Next exact action

After owner says `lanjutkan`, execute **S11-W5-008 only**:
wire the real subtitle + narration + microphone workflows into the frozen
SCR-008/SCR-009/UI-017/UI-018/UI-033/UI-034/UI-035/UI-036/WIN-001/WIN-003
surfaces, with disabled/hidden state for unqualified capabilities.
