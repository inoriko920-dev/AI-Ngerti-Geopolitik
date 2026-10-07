# PLAN — CURRENT IMPLEMENTATION PHASE

**SF-STEP 11 is active. W0/W1/W2/W3/W4 PASS. W5-001 through W5-006 PASS.**

## Accepted W5-006

- implementation HEAD:
  `77770cd98210dbed18cbe1715111a935f2135b77`;
- workflow:
  `37577639655` — SUCCESS;
- narration import uses canonical media probe/identity;
- import + bind is atomic in one CommandBatch;
- non-audio failure leaves project unchanged;
- existing audio assets can be bound;
- offset/gain/mute/fade are canonical and persistent;
- fades are bounded to the actual audible project segment;
- FFmpeg qualification mixes narration into existing timeline audio;
- real narration preview WAV supported;
- real MP4 export contains narration;
- 440 Hz spectral evidence proves offset/gain/mute/fade behavior;
- narration source SHA-256 unchanged;
- targeted 5/5 tests + full pytest green;
- evidence verifier 11/11 PASS;
- W5-005/W5-004/W4/W3/W2/W1/W0/S10/S09/S08 regressions all green on the
  same implementation HEAD.

Evidence:
`docs/evidence/features/S11_W5_006_NARRATION_IMPORT_BINDING.md`.

## Active next task

**S11-W5-007 — Microphone recording**

W5-007 scope:
- dedicated RecorderPort/application boundary;
- active project requirement;
- input-device availability handling;
- staging WAV recording;
- validate staging before finalization;
- successful recording enters the same canonical narration import/binding path;
- cancel/failure/empty output must not replace current narration;
- deterministic fake-adapter tests;
- real Windows microphone smoke if hardware exists.

Hardware gate:
- do not fake a microphone;
- if CI has no physical capture device, record the missing hardware evidence and
  preserve the contract's PASS_WITH_PROVISIONAL_MIC_HARDWARE rule for final W5
  closure.

W5-007 must not start:
- W5 frozen UI parity;
- final combined W5 preview/export qualification;
- W5 failure/regression closure;
- Gemini/provider work.

Do not begin W5-007 until owner says `lanjutkan`.
