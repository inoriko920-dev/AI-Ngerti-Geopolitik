# PLAN — CURRENT IMPLEMENTATION PHASE

**SF-STEP 11 is active. W0/W1/W2/W3/W4 PASS. W5-001..006 PASS. W5-007 PASS_WITH_PROVISIONAL_MIC_HARDWARE. W5-008 PASS. W5-009 PASS.**

## Accepted W5-009

- implementation HEAD:
  `afcdd20c74f3870aee589ad83bf20cdae3861fea`;
- workflow:
  `37581393310` — SUCCESS;
- targeted combined tests 3/3 PASS;
- full pytest PASS;
- source SRT byte-identical;
- edited subtitle text/timing survives Save Copy + project reopen;
- style visible in real preview;
- Fade/Pop/Slide Up/Clean Documentary all have preview + export evidence;
- 440 Hz narration preview audible;
- frame-60 narration offset measurable;
- subtitle + narration coexist in the same exported MP4;
- final output 1920×1080 / 30 fps with audio;
- duration within ±3 frames;
- evidence verifier 26/26 PASS.

Evidence:
`docs/evidence/features/S11_W5_009_COMBINED_PREVIEW_EXPORT.md`.

## Active next task

**S11-W5-010 — Failure paths + evidence + regression lock**

W5-010 scope:
- subtitle/narration Undo/Redo closure;
- old W4 project -> safe W5 defaults;
- malformed SRT;
- dirty working-copy leave/reload guard;
- missing/corrupt narration;
- failed/cancelled recording preserving old narration;
- deterministic W5 closure report/verifier;
- Ruff/mypy/import-contract/architecture/source-of-truth/UI/security/full pytest;
- full W4/W3/W2/W1/W0/S10/S09/S08 regression lock;
- final W5 status carrying the provisional physical-microphone qualifier if
  hardware remains unavailable.

W5-010 must not:
- add new product features;
- enable unsupported subtitle animations;
- add ASR/transcription/alignment;
- add Gemini/provider work;
- start SF-STEP 12;
- begin final release work.

Do not begin W5-010 until owner says `lanjutkan`.
