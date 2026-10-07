# S11 W5-008 — Frozen UI Parity

**Status:** PASS  
**Accepted implementation HEAD:** `b65bf585510ee442584a7ebbe8db8c3d40ac1533`  
**Accepted workflow:** `37579815809` — SUCCESS  
**Artifact:** `ANG-S11-W5-008-Frozen-UI`  
**Artifact ID:** `11463699327`

## Scope

W5-008 replaced the previous subtitle placeholder surface with real interactive
PySide6 controls for the frozen Subtitle + Narration workflow.

It did not start W5-009 combined media qualification, W5-010 closure,
Gemini/provider work or release work.

## Subtitle cue/text surface

The Subtitle workspace retains the frozen three-tab structure:
- Teks;
- Gaya;
- Animasi.

Teks includes:
- SRT import;
- cue list/select;
- text edit;
- IN/OUT edit;
- add/delete;
- split/merge;
- reload SRT;
- Save Copy;
- timing-lock presentation state.

The source-safety rule is visible:
the source SRT is not silently overwritten.

All actions emit semantic UiIntent values only.

## Subtitle style surface

Enabled controls map to the W5-004 qualified canonical style:
- font family;
- font size;
- fill;
- outline;
- outline width;
- shadow;
- background;
- background opacity;
- alignment;
- vertical margin.

The UI exposes only render-qualified fonts:
- Arial;
- Segoe UI.

## Subtitle animation surface

Selectable canonical values:
- none;
- Fade;
- Pop;
- Slide Up;
- Clean Documentary.

Unqualified legacy names remain non-selectable and are presented only as an
informational unavailable list.

No unsupported preset is fake-enabled.

## Per-word boundary

W5-008 exposes:
- editable manual WordTiming rows;
- manual semantic timing intent;
- deterministic even-distribution action only after explicit acknowledgement.

The visible acknowledgement is:
**NOT speech alignment**.

The UI also explicitly states that no ASR/transcription is used.

Karaoke/highlight controls remain unavailable because that behavior is not
render-qualified.

## Narration workspace

The Narasi tab provides:
- audio import;
- timeline start frame;
- gain;
- mute;
- fade in;
- fade out;
- apply controls;
- real narration preview intent;
- recording entry point.

The physical-microphone qualifier from W5-007 remains visible as provisional.

## WIN-001 narration recording dialog

The recording dialog provides:
- device selector;
- refresh devices;
- max duration;
- timeline start;
- start;
- cancel/stop.

Start is disabled until a real device projection is supplied.

`MainWindow.apply_microphone_devices(...)` can project device identity into
the open dialog.

The dialog emits semantic intents and does not import concrete DirectShow or
FFmpeg infrastructure.

## Qt tests

Target:
`tests/qt/test_step11_w5_008_ui.py`

Proven:
1. subtitle cue/text actions emit semantic intents;
2. style UI exposes only Arial + Segoe UI;
3. animation UI exposes only qualified presets;
4. even WordTiming requires explicit NOT-speech-alignment acknowledgement;
5. narration controls emit semantic intents;
6. recording dialog is device-gated and emits start/cancel intents.

Result:
**6/6 PASS**.

## Frozen visual evidence

Reference integrity:
**42/42 SHA-256 PASS**.

Actual 1920×1080 captures:
- UI-017 subtitle text;
- UI-018 narration;
- UI-033 subtitle style;
- UI-034 subtitle animation;
- UI-035 word-timing boundary;
- UI-036 word-timing acknowledged state;
- WIN-001 recording dialog.

For UI-017/018/033/034/035/036, the evidence artifact includes
REFERENCE_VS_ACTUAL images built from the frozen raw references and the real
PySide6 runtime.

Evidence verifier:
**14/14 PASS**.

## Quality gates

Workflow `37579815809`:
- Ruff format PASS;
- Ruff check PASS;
- mypy PASS — 52 source files;
- import contracts PASS;
- architecture PASS;
- source-of-truth 70/70 PASS;
- secret scan PASS;
- UI reference manifest 42/42 PASS;
- targeted Qt tests 6/6 PASS;
- full pytest PASS;
- W5 UI capture PASS;
- evidence verifier 14/14 PASS.

## Artifact

- name: `ANG-S11-W5-008-Frozen-UI`;
- ID: `11463699327`;
- size: 4,396,724 bytes.

## Regression lock

All workflows on the accepted W5-008 implementation HEAD are SUCCESS:
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

## Hardware qualifier

W5-007 remains **PASS_WITH_PROVISIONAL_MIC_HARDWARE**.

W5-008 presents that state honestly and does not upgrade the hardware
qualification.

## Next

**S11-W5-009 — Real subtitle/narration preview/export qualification only.**
