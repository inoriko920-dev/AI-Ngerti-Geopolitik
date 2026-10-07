# SF-STEP 11 W4 — Titles / Transitions / Effects

**Status:** PASS  
**Accepted implementation HEAD:** `3e3cd376189e9f183e70ca537ad25f037e25bcd7`  
**Accepted workflow:** `37570612799` — SUCCESS  
**Artifact:** `ANG-S11-W4-Creative` — ID `11460641864`

## Scope proven

W4 introduced canonical, persisted creative state without moving ownership into
Qt or FFmpeg:
- TitleProperties: enabled, text, font size, position, color and background
  opacity.
- TransitionProperties: `none` and `fade_black`, duration in frames.
- EffectProperties: enter effect, exit effect, bounded intensity and lock.
- ClipProperties carries W4 state.
- CreativeController mutates through CommandBus/CommandBatch.
- CreativeIntentRouter receives semantic PySide6 intents.
- JsonProjectRepository round-trips W4 state and supplies safe defaults for
  older schema-v1 project data.

## Render-backed effects

Qualified AAVC legacy subset:
1. Fade
2. Pop
3. Breathe
4. Stomp
5. Tumble
6. Tectonic
7. Rise
8. Pan
9. Drift

The following legacy names remain intentionally unavailable:
- Wipe
- Blur
- Succession
- Baseline
- Neon
- Scrapbook
- Brush
- Ink
- Digital
- Spray Paint
- Sketch
- Gradient

This follows the no-fake-capability rule: a legacy label is not exposed merely
because it existed in AAVC.

## Transition boundary

W4 qualifies `fade_black` as fade-through-black.

W4 does **not** claim dissolve/crossfade. The canonical timeline still forbids
overlapping clips; therefore a true overlap transition requires a later,
explicitly qualified timeline/engine model.

## Real evidence result

The W4 evidence runner reported:
- `status: PASS`
- `title_overlay: true`
- `transition_fade_black: true`
- `render_backed_effects: true`
- `unsupported_legacy_hidden: true`
- `crossfade_claimed: false`
- `undo_redo: true`
- `save_reopen: true`
- `preview_changed: true`
- `export_valid: true`
- `export_has_audio: true`

Verifier result:
`PASS W4 evidence files: 8/8`.

Evidence bundle:
- `00_w4_report.json`
- `01_creative_state.json`
- `02_undo_persistence.json`
- `03_preview_export.json`
- `preview_baseline.png`
- `preview_creative.png`
- `w4_creative.angproj`
- `w4_creative_export.mp4`

Artifact metadata:
- size: `9,549,652` bytes;
- digest:
  `sha256:06e87e681e0407b6e576b0ab8247eee3c900c50af7bfe2f38f81015bea64630e`;
- created from accepted HEAD
  `3e3cd376189e9f183e70ca537ad25f037e25bcd7`.

## Quality gates

On the W4 accepted run:
- uv lock/sync PASS;
- Ruff format PASS;
- Ruff check PASS;
- mypy PASS;
- import contracts PASS;
- architecture verifier PASS;
- source-of-truth verifier PASS;
- UI reference manifest PASS;
- secret verifier PASS;
- full pytest PASS;
- owned real-media fixture generation PASS;
- W4 real evidence generation PASS;
- W4 evidence verifier PASS;
- artifact upload PASS.

## Regression lock

All workflows on the same implementation HEAD are SUCCESS:
- W4: `37570612799`
- W3: `37570612705`
- W2: `37570612673`
- W1: `37570612719`
- W0: `37570612737`
- S10: `37570612830`
- S09: `37570612683`
- S08: `37570612789`

S10 additionally passed the real-media vertical slice, portable UI regression
and packaged real-media smoke. S08/S09 portable regression remained green.

## Boundaries carried forward

- ProjectState remains canonical truth.
- CommandBus/CommandBatch remains the mutation path.
- MediaEnginePort remains the engine boundary.
- MLT remains the primary production-engine implementation candidate.
- FFmpeg remains qualification evidence, not a production-engine switch.
- AAVC UI-001..UI-042 remains frozen 1:1.
- Reverse remains disabled.
- Unsupported legacy W4 effects remain unavailable.
- W5, Gemini/AI work, SF-STEP 12 and release work must follow their own gates.
