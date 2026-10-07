# PROJECT STATUS — AI NGERTI GEOPOLITIK

**Current STEP:** SF-STEP 11 — Feature Implementation Waves  
**Last completed wave:** **W4 — PASS**  
**Accepted W4 implementation HEAD:** `3e3cd376189e9f183e70ca537ad25f037e25bcd7`  
**Accepted W4 run:** `37570612799` — SUCCESS  
**Next exact wave:** **W5 — derive its exact contract from source-of-truth before coding**

## W4 proven

Canonical creative state:
- per-clip title overlay: enabled, text, font size, position, color and
  background opacity;
- transition presets `none` and real `fade_black`;
- frame-bounded transition duration;
- render-backed legacy AAVC effects: Fade, Pop, Breathe, Stomp, Tumble,
  Tectonic, Rise, Pan and Drift;
- effect enter/exit, bounded intensity and lock;
- all W4 mutations through CommandBus/CommandBatch;
- Undo/Redo;
- .angproj save/reopen;
- safe defaults when opening schema-v1 projects without W4 fields.

Runtime/UI:
- real PySide6 Animation inspector emits semantic intents;
- unsupported effects are not selectable/faked;
- dissolve/crossfade is not advertised because canonical W4 timeline semantics
  still forbid clip overlap.

Real media evidence:
- baseline and W4 creative preview differ;
- title/transition/effect state reaches the qualification render path;
- export file is valid;
- export retains audio;
- evidence verifier PASS 8/8.

Evidence:
`docs/evidence/features/S11_W4_TITLES_TRANSITIONS_EFFECTS.md`.

Artifact:
- name `ANG-S11-W4-Creative`;
- ID `11460641864`;
- size `9,549,652` bytes;
- digest
  `sha256:06e87e681e0407b6e576b0ab8247eee3c900c50af7bfe2f38f81015bea64630e`.

## Explicit W4 non-claims

The following legacy AAVC effects remain unsupported in W4 and must stay
unavailable until a real engine mapping and evidence exist:
- Wipe;
- Blur;
- Succession;
- Baseline;
- Neon;
- Scrapbook;
- Brush;
- Ink;
- Digital;
- Spray Paint;
- Sketch;
- Gradient.

Dissolve/crossfade is also not claimed. `fade_black` is fade-through-black,
not overlapping two clips.

## Regression lock

On accepted W4 implementation HEAD:
- W4: `37570612799` — SUCCESS;
- W3: `37570612705` — SUCCESS;
- W2: `37570612673` — SUCCESS;
- W1: `37570612719` — SUCCESS;
- W0: `37570612737` — SUCCESS;
- S10: `37570612830` — SUCCESS;
- S09: `37570612683` — SUCCESS;
- S08: `37570612789` — SUCCESS.

S10 includes successful real-media vertical slice, portable UI regression and
packaged real-media smoke. S08/S09 portable regressions are also green.

## Engine direction

Unchanged:
- MLT = primary production-engine implementation candidate;
- ProjectState + CommandBus + MediaEnginePort remain canonical;
- FFmpeg W4 is a real qualification adapter, not an engine switch;
- final production MLT mapping/native DLL closure remains a later hardening or
  release gate.

## Reverse

Reverse remains intentionally **disabled** because it has not passed safe
backend qualification. Do not expose it as functional until real evidence
exists.

## Exact next action

On owner **"lanjutkan"**, start **W5 only** by deriving its exact serial task
contract from the frozen Product/UI/Architecture source-of-truth before any
implementation.

Do not jump to Gemini/AI coverage, SF-STEP 12, or final release packaging
unless that work is explicitly the correct gated wave/STEP.
