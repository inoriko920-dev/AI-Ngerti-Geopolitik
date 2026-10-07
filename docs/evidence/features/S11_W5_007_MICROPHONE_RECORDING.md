# S11 W5-007 — Microphone Recording

**Status:** PASS_WITH_PROVISIONAL_MIC_HARDWARE  
**Accepted implementation HEAD:** `be4daa667bf5030ba3810460cc6841a2e8be4fee`  
**Accepted workflow:** `37578572691` — SUCCESS  
**Artifact:** `ANG-S11-W5-007-Microphone`  
**Artifact ID:** `11463438121`

## Scope

W5-007 implemented the microphone recording application boundary, deterministic
recording safety path and a real Windows DirectShow hardware gate.

It did not start frozen UI parity, W5 combined qualification, W5 closure,
Gemini/provider work or release work.

## RecorderPort boundary

Application ports now include:
- `RecordingDevice`;
- `RecordingResult`;
- `RecorderPort`.

The application layer knows only the abstract device/capture contract.
DirectShow/FFmpeg details remain infrastructure.

The capture operation accepts a CancellationToken so W5-008 can later connect
Stop/Cancel behavior without moving capture control into presentation code.

## MicrophoneRecordingService

Added:
`src/ai_ngerti_geopolitik/application/microphone.py`.

Preconditions:
- canonical project must have an active/non-empty timeline;
- recording duration must be > 0 and <= 3600 seconds;
- pre-cancel is rejected;
- at least one input device must exist;
- selected device ID must be present in the enumerated list.

Recording flow:
1. create recordings destination if needed;
2. create a dedicated `.staging` directory;
3. allocate a unique staging WAV path;
4. call RecorderPort only with that staging path;
5. reject cancelled capture;
6. reject a backend that returns a different path;
7. reject missing/empty recording;
8. probe staging media;
9. require media_type=audio and has_audio=true;
10. require meaningful duration;
11. require valid sample rate;
12. choose a collision-safe final name;
13. reserve the destination exclusively;
14. atomically replace the reserved destination with validated staging;
15. call accepted W5-006 NarrationImportService for canonical import/bind.

## No-overwrite finalization

The default recording name is:
`narration-recording.wav`.

If it exists:
- `narration-recording-2.wav`;
- then `-3`, etc.

Existing recording files are never silently overwritten.

Finalization reserves the destination using exclusive creation before
`os.replace`, preventing a normal existing path from being clobbered.

If canonical NarrationImportService binding later fails, the newly finalized
file is removed.

## Failure/cancel safety

Deterministic tests prove the current canonical narration is preserved when:
- no device is available;
- selected device does not exist;
- capture raises;
- capture is cancelled;
- capture is empty;
- staging probe says non-audio;
- recording is pre-cancelled.

Staging cleanup is guaranteed.

No canonical project mutation happens until after capture validation and safe
finalization.

## Successful canonical path

On success:
- recorded WAV becomes a normal canonical audio Asset;
- one NarrationTrack binds to it using W5-006;
- import+bind is one CommandBatch;
- Undo removes the new recorded asset/binding;
- Redo restores it.

This deliberately reuses the accepted narration path instead of creating a
second microphone-only project model.

## Windows FFmpeg DirectShow adapter

Added:
`src/ai_ngerti_geopolitik/infrastructure/ffmpeg_recorder.py`.

Behavior:
- Windows-only DirectShow capture;
- enumerates actual entries marked `(audio)`;
- input identity is the reported device name;
- capture is mono PCM s16le;
- sample rate: 48 kHz;
- max-duration stop supported;
- CancellationToken terminates FFmpeg;
- cancelled/failed partial output is removed;
- empty output is rejected.

## Physical hardware gate result

The accepted GitHub Windows runner reported:
- DirectShow audio input device count: **0**;
- real device available: **false**;
- hardware recording attempted: **false**;
- hardware recording bound: **false**;
- fake hardware claimed: **false**.

Hardware report status:
**PASS_WITH_PROVISIONAL_MIC_HARDWARE**.

This is the correct contract result. The workflow must not invent a microphone
or synthesize fake capture and call it physical-device evidence.

A real Windows machine with a microphone must later:
1. enumerate at least one DirectShow audio input device;
2. perform real capture;
3. probe valid audio;
4. bind the captured WAV through MicrophoneRecordingService;
5. save the resulting project.

Only then can the physical microphone qualifier be removed.

## Tests and gates

Target:
`tests/unit/test_step11_w5_007_microphone.py`

Targeted deterministic result:
- **6/6 PASS**.

Workflow `37578572691`:
- Ruff format PASS;
- Ruff check PASS;
- mypy PASS — 51 source files;
- import contracts PASS;
- architecture PASS;
- source-of-truth PASS;
- secret scan PASS;
- targeted W5-007 tests PASS;
- full pytest PASS;
- real Windows device enumeration PASS;
- hardware verifier PASS with provisional hardware status.

## Artifact

- name: `ANG-S11-W5-007-Microphone`;
- ID: `11463438121`;
- size: 541 bytes.

Because no microphone device existed, the artifact intentionally contains only:
- hardware status JSON;
- device enumeration JSON.

There is no fake WAV artifact.

## Regression lock

All workflows on accepted W5-007 HEAD are SUCCESS:
- W5-007: `37578572691`;
- W5-006: `37578572686`;
- W5-005: `37578572661`;
- W5-004: `37578572726`;
- W4: `37578572750`;
- W3: `37578572725`;
- W2: `37578572751`;
- W1: `37578572684`;
- W0: `37578572742`;
- S10: `37578572702`;
- S09: `37578572748`;
- S08: `37578572764`.

## Next

**S11-W5-008 — Frozen UI parity only.**

The UI must expose the provisional hardware state honestly and must not show a
successful microphone hardware qualification that does not exist.
