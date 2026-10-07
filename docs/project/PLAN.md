# PLAN — CURRENT IMPLEMENTATION PHASE

**SF-STEP 11 is active. W0/W1/W2/W3/W4 PASS. W5-001/W5-002/W5-003/W5-004 PASS.**

## Accepted W5-004

- implementation HEAD:
  `687d31585d476541711978d5f69e5e7eafe72245`;
- workflow:
  `37574406573` — SUCCESS;
- canonical subtitle-style command/history implemented;
- persistence/reopen proven;
- dirty cue working-copy compatibility fixed and tested;
- real preview qualification for every enabled style dimension;
- real styled export with audio;
- source SRT unchanged;
- render-qualified font-family boundary locked to Arial + Segoe UI;
- targeted 6/6 tests + full pytest green;
- evidence verifier 18/18 PASS;
- W4/W3/W2/W1/W0/S10/S09/S08 regressions all green on the same HEAD.

Evidence:
`docs/evidence/features/S11_W5_004_SUBTITLE_STYLE.md`.

## Active next task

**S11-W5-005 — Render-backed subtitle animation + per-word boundary**

Candidate animation names may be enabled only after independent real render
proof.

Legacy AAVC code gives concrete behavior candidates:
- Fade;
- Pop;
- Slide Up;
- Clean Documentary.

Keep hidden/disabled unless independently proven:
- Word Reveal;
- Karaoke Highlight;
- Typewriter;
- Bounce Soft;
- Emphasis Word;
- Social Caption;
- any label that merely falls back to a generic effect.

Per-word timing:
- canonical WordTiming already exists;
- explicit edit/representation is allowed;
- deterministic even word distribution is allowed only as an explicit
  fallback and must be labeled **not speech alignment**;
- no ASR, transcription or phoneme/word auto-alignment claim.

W5-005 must not start narration, microphone, full frozen UI parity, Gemini or
later tasks.

Do not begin W5-005 until owner says `lanjutkan`.
