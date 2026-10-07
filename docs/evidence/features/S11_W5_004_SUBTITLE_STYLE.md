# S11 W5-004 — Subtitle Style

**Status:** PASS  
**Accepted implementation HEAD:** `687d31585d476541711978d5f69e5e7eafe72245`  
**Accepted workflow:** `37574406573` — SUCCESS  
**Artifact:** `ANG-S11-W5-004-Subtitle-Style`  
**Artifact ID:** `11461154582`

## Scope

W5-004 implemented canonical subtitle-style mutation, persistence/history and
real preview/export qualification.

It did not enable subtitle animation, per-word effects, narration, microphone
capture, frozen UI parity or Gemini/provider behavior.

## Canonical style mutation

Added:
- `SetSubtitleStyleCommand`.

Behavior:
- requires a bound canonical SubtitleTrack;
- replaces only SubtitleTrack.style;
- uses CommandBus/CommandBatch;
- validates resulting ProjectState;
- Undo restores previous style;
- Redo restores styled state.

Existing SubtitleStyle remains the canonical representation.

## Frozen style surface covered

Canonical and render-qualified:
- font family;
- font size;
- fill color;
- outline color;
- outline width;
- shadow;
- background box;
- background opacity;
- alignment;
- safe vertical margin.

## Render qualification adapter

Added:
`src/ai_ngerti_geopolitik/infrastructure/ffmpeg_subtitles.py`.

The adapter compiles canonical cue/style data to FFmpeg drawtext filters.

Preview:
- identifies the cue active at the requested canonical timeline frame;
- renders only that active cue.

Export:
- applies subtitle filters after canonical video/audio timeline composition;
- uses canonical cue start/end windows;
- preserves export audio and canonical duration.

FFmpeg remains a qualification adapter and does not change the recorded
production-engine priority decision.

## Font-family boundary

Real Windows evidence qualified:
- Arial;
- Segoe UI.

The qualification adapter explicitly rejects other font-family names rather
than silently substituting another font.

This does not restrict the canonical data model from storing future font
families, but UI/runtime must not advertise an unqualified family as supported.

## Independent real preview matrix

Real preview evidence was generated for:
1. font family;
2. font size;
3. fill color;
4. outline color/width;
5. shadow;
6. background box/opacity;
7. alignment;
8. safe vertical margin.

Each variant produced a preview SHA-256 different from the baseline preview.

A final combined styled preview was also rendered.

## Working-copy compatibility

W5-004 fixes an important cross-task interaction.

Scenario:
- user has dirty local cue edits in SubtitleWorkingCopy;
- project subtitle style changes through CommandBus;
- user later Save Copies the edited SRT.

The save-copy commit now carries the latest canonical project:
- style;
- animation metadata;
- enabled state;

while retaining the locally edited cue text/timing.

This prevents Save Copy from accidentally reverting style metadata to the old
working-copy baseline.

Source SRT protection remains unchanged.

## Persistence/history proof

Evidence proves:
- semantic state changes after style command;
- Undo returns baseline semantic hash;
- Redo restores styled semantic hash;
- .angproj save/reopen preserves full style;
- reopen semantic hash matches;
- source SRT SHA-256 stays unchanged.

## Animation boundary

SubtitleAnimation remains `none` only in W5-004.

W5-004 does not claim:
- Fade;
- Pop;
- Slide Up;
- Clean Documentary;
- any per-word animation.

Those belong to W5-005.

## Tests and gates

Target:
`tests/unit/test_step11_w5_004_style.py`

Targeted result:
- **6/6 PASS**.

Workflow `37574406573`:
- Ruff format PASS;
- Ruff check PASS;
- mypy PASS;
- import contracts PASS;
- architecture PASS;
- source-of-truth 70/70 PASS;
- secret scan PASS;
- targeted W5-004 tests PASS;
- full pytest PASS;
- real W5-004 evidence PASS;
- evidence verifier **18/18 PASS**.

## Real evidence artifact

Artifact:
- name: `ANG-S11-W5-004-Subtitle-Style`;
- ID: `11461154582`;
- size: 10,534,700 bytes.

Evidence bundle contains:
- report/state/history/export JSON;
- source SRT;
- .angproj project;
- styled export MP4;
- baseline preview;
- eight independent style-property previews;
- final combined style preview.

## Regression lock

All workflows on the accepted implementation HEAD are SUCCESS:
- W5-004: `37574406573`;
- W4: `37574406598`;
- W3: `37574406680`;
- W2: `37574406711`;
- W1: `37574406582`;
- W0: `37574406562`;
- S10: `37574406568`;
- S09: `37574406585`;
- S08: `37574406553`.

This includes:
- MLT Windows playback qualification;
- W2 MLT canonical projection;
- W3/W4 real-output evidence;
- S10 real-media vertical slice;
- S10 packaged real-media smoke;
- S10 portable UI regression;
- S08/S09 portable regressions.

## Next

**S11-W5-005 — Render-backed subtitle animation + per-word boundary only.**

Do not start W5-006 narration or later tasks until W5-005 closes.
