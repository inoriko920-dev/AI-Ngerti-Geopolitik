# PLAN — CURRENT IMPLEMENTATION PHASE

**SF-STEP 11 is active. W0/W1/W2/W3/W4 PASS. W5-001..006 PASS. W5-007 PASS_WITH_PROVISIONAL_MIC_HARDWARE. W5-008 PASS.**

## Accepted W5-008

- implementation HEAD:
  `b65bf585510ee442584a7ebbe8db8c3d40ac1533`;
- workflow:
  `37579815809` — SUCCESS;
- real frozen subtitle/narration PySide6 widgets implemented;
- subtitle Teks/Gaya/Animasi surfaces emit semantic intents;
- only render-qualified fonts/presets exposed;
- per-word deterministic fallback requires explicit NOT-speech-alignment
  acknowledgement;
- narration import/control/preview/recording surfaces implemented;
- microphone recording dialog is device-gated and retains provisional hardware
  wording;
- targeted Qt tests 6/6 PASS;
- full pytest PASS;
- frozen UI references 42/42 PASS;
- actual/reference visual evidence captured;
- evidence verifier 14/14 PASS;
- W5-007/W5-006/W5-005/W5-004/W4/W3/W2/W1/W0/S10/S09/S08 all SUCCESS.

Evidence:
`docs/evidence/features/S11_W5_008_FROZEN_UI_PARITY.md`.

## Active next task

**S11-W5-009 — Real subtitle/narration preview/export qualification**

W5-009 scope:
- deterministic owned video/audio/SRT fixture;
- imported subtitle at correct canonical frame;
- edited cue text/timing survives save/reopen;
- style visible in real output;
- enabled subtitle animation present in real output;
- narration audible and frame-offset;
- subtitle + narration coexist in one real export;
- output valid, has audio and duration stays within tolerance;
- source SRT remains byte-identical.

W5-009 must not:
- add new UI;
- enable unsupported animation names;
- add ASR/transcription/alignment;
- remove provisional microphone hardware qualifier;
- start W5-010 closure;
- start Gemini/provider work or SF-STEP 12.

Do not begin W5-009 until owner says `lanjutkan`.
