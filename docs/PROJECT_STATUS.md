# PROJECT STATUS — AI NGERTI GEOPOLITIK

**Current STEP:** SF-STEP 11 — Feature Implementation Waves  
**Current wave:** **W5 — Subtitle + Narration**  
**W5 progress:** **S11-W5-001..006 PASS / W5-007 PASS_WITH_PROVISIONAL_MIC_HARDWARE**  
**Accepted W5-007 implementation HEAD:** `be4daa667bf5030ba3810460cc6841a2e8be4fee`  
**Accepted W5-007 workflow:** `37578572691` — SUCCESS  
**Next exact task:** **S11-W5-008 — Frozen UI parity**

## W5-007 software path proven

Application boundary:
- added dedicated `RecorderPort`;
- added `RecordingDevice` and `RecordingResult`;
- presentation/domain do not depend on DirectShow or FFmpeg details.

Recording orchestration:
- active canonical project timeline is required;
- requested microphone must exist in the recorder device list;
- recording duration must be positive and is bounded to 3600 seconds;
- pre-cancel is rejected without starting capture;
- capture writes only to a unique staging WAV under `.staging`;
- recorder-returned path must exactly match the expected staging path;
- staging file must be non-empty;
- staging is probed and must be real audio;
- duration must exceed the empty/near-empty threshold;
- sample rate must be valid.

Safe finalization:
- final output name is collision-safe:
  `narration-recording.wav`, then `-2`, `-3`, etc.;
- existing files are never silently overwritten;
- target is reserved exclusively before atomic replacement;
- only after staging validation/finalization does the app call the accepted
  W5-006 `NarrationImportService`;
- failed canonical binding removes the newly finalized file;
- current narration is not mutated before successful canonical import/bind.

Failure safety proven:
- no device preserves existing narration;
- unknown device preserves existing narration;
- cancelled capture preserves existing narration;
- recorder exception preserves existing narration;
- empty capture preserves existing narration;
- invalid staged media preserves existing narration;
- pre-cancel preserves existing narration;
- staging cleanup is guaranteed.

Successful path:
- successful recording becomes a normal canonical audio Asset + NarrationTrack
  through W5-006;
- import/bind remains one semantic CommandBatch;
- Undo removes the new recorded asset/binding;
- Redo restores it.

Windows adapter:
- added FFmpeg DirectShow recorder adapter;
- enumerates only actual DirectShow audio input devices;
- real capture target is mono PCM WAV at 48 kHz;
- CancellationToken can terminate a running FFmpeg capture;
- partial cancelled capture is removed.

## Physical hardware gate

Workflow runner enumeration result:
- DirectShow audio input device count: **0**;
- real physical capture attempted: **NO**;
- fake hardware claim: **NO**.

Therefore W5-007 status is:
**PASS_WITH_PROVISIONAL_MIC_HARDWARE**.

This is intentional. The software path is qualified, but physical microphone
evidence cannot be claimed from a runner that exposes no input hardware.

Full W5 closure must retain the provisional microphone qualification until a
real Windows machine with an available microphone passes the same hardware
smoke.

Evidence:
`docs/evidence/features/S11_W5_007_MICROPHONE_RECORDING.md`.

Artifact:
- `ANG-S11-W5-007-Microphone`;
- ID `11463438121`;
- size 541 bytes;
- contains the hardware report and DirectShow device enumeration report.

## W5-007 gates

Workflow `37578572691`:
- Ruff format PASS;
- Ruff check PASS;
- mypy PASS — 51 source files;
- import contracts PASS;
- architecture PASS;
- source-of-truth PASS;
- secret scan PASS;
- targeted W5-007 tests: **6/6 PASS**;
- full pytest PASS;
- Windows DirectShow hardware gate:
  **PASS_WITH_PROVISIONAL_MIC_HARDWARE**;
- evidence verifier PASS.

## Regression lock on accepted W5-007 HEAD

All SUCCESS:
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

This retains MLT qualification, real-media output, packaged smoke, portable UI
and Windows foundation regressions.

## Exact next action

On owner **"lanjutkan"**, execute **S11-W5-008 — Frozen UI parity only**.

W5-008 must wire only capabilities already proven by W5-001..007 into the
frozen AAVC UI surfaces. Do not start W5-009 combined qualification, W5-010
closure, Gemini/provider work, or final release work in the same turn.
