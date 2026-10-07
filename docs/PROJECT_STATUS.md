# PROJECT STATUS — AI NGERTI GEOPOLITIK

**Current STEP:** SF-STEP 11 — Feature Implementation Waves  
**Current wave:** **W5 — Subtitle + Narration**  
**W5 progress:** **S11-W5-001..006 PASS / W5-007 PASS_WITH_PROVISIONAL_MIC_HARDWARE / W5-008 PASS**  
**Accepted W5-008 implementation HEAD:** `b65bf585510ee442584a7ebbe8db8c3d40ac1533`  
**Accepted W5-008 workflow:** `37579815809` — SUCCESS  
**Next exact task:** **S11-W5-009 — Real subtitle/narration preview/export qualification**

## W5-008 proven

Frozen W5 surfaces are now real PySide6 widgets, not screenshot-as-runtime UI.

Subtitle workspace:
- Teks / Gaya / Animasi tabs retained;
- cue list, cue edit text, IN/OUT, split, merge, delete, reload and save-copy controls;
- semantic subtitle intents only; no direct project/engine mutation;
- source SRT no-overwrite policy is visible in the UI.

Style:
- visible controls match the already-qualified canonical style surface;
- font UI exposes only render-qualified Arial and Segoe UI;
- size/fill/outline/shadow/background/alignment/margin controls emit one semantic
  style intent.

Animation:
- UI exposes only:
  none, Fade, Pop, Slide Up, Clean Documentary;
- unqualified legacy labels remain visible only as unavailable information, not
  selectable controls;
- animation timing/intensity emits semantic intent.

Per-word boundary:
- manual timing table is interactive;
- deterministic even distribution is gated behind an explicit
  **NOT speech alignment** acknowledgement;
- the UI explicitly states no ASR/transcription;
- karaoke/highlight remains unavailable because it is not render-qualified.

Narration workspace:
- real narration import control;
- timeline offset, gain, mute, fade-in and fade-out controls;
- real narration preview intent;
- real recording entry point;
- provisional physical-microphone qualification is stated honestly.

Recording dialog:
- device list is empty/disabled until actual devices are supplied;
- refresh, duration, timeline start, start and cancel controls are real widgets;
- Start remains disabled with no device;
- semantic microphone intents are emitted;
- the dialog does not fake a hardware-qualified microphone.

## Frozen-reference evidence

UI reference integrity:
- **42/42 SHA-256 PASS**.

Captured W5 actual surfaces at 1920×1080:
- UI-017 — Subtitle cue/text;
- UI-018 — Narration;
- UI-033 — Subtitle style;
- UI-034 — Subtitle animation;
- UI-035 — word-timing boundary;
- UI-036 — explicit NOT-speech-alignment acknowledgement;
- WIN-001 — narration recording dialog.

For UI-017/018/033/034/035/036 the artifact also contains
REFERENCE_VS_ACTUAL comparison images against the frozen repository references.

Evidence verifier:
- **14/14 files PASS**.

Artifact:
- `ANG-S11-W5-008-Frozen-UI`;
- ID `11463699327`;
- size 4,396,724 bytes.

## W5-008 gates

Workflow `37579815809`:
- Ruff format PASS;
- Ruff check PASS;
- mypy PASS — 52 source files;
- import contracts PASS;
- architecture PASS;
- source-of-truth 70/70 PASS;
- secret scan PASS;
- frozen UI references 42/42 SHA-256 PASS;
- targeted W5-008 Qt tests: **6/6 PASS**;
- full pytest PASS;
- UI evidence capture PASS;
- evidence verifier 14/14 PASS.

## Regression lock on accepted W5-008 HEAD

All SUCCESS:
- W5-008: `37579815809`;
- W5-007: `37579815674`;
- W5-006: `37579815770`;
- W5-005: `37579815678`;
- W5-004: `37579815803`;
- W4: `37579815689`;
- W3: `37579815801`;
- W2: `37579815721`;
- W1: `37579815778`;
- W0: `37579815762`;
- S10: `37579815716`;
- S09: `37579815683`;
- S08: `37579815729`.

This includes MLT qualification, real-media output, packaged real-media smoke,
portable UI regression and Windows foundation regression.

## Hardware qualifier carried forward

W5-007 remains **PASS_WITH_PROVISIONAL_MIC_HARDWARE** because the accepted
GitHub Windows runner exposed 0 DirectShow audio-input devices.

W5-008 does not weaken or hide that qualifier.

## Exact next action

On owner **"lanjutkan"**, execute **S11-W5-009 only**.

W5-009 must combine real subtitle + narration behavior in deterministic
preview/export evidence. Do not start W5-010 closure, Gemini/provider work,
SF-STEP 12, or final release work in the same turn.
