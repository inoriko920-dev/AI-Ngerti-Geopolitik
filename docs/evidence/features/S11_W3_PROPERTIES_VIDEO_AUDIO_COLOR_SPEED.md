# SF-STEP 11 W3 — PROPERTIES: VIDEO, AUDIO, COLOR & SPEED

**Status:** PASS  
**Accepted implementation HEAD:** `79217e687a9930087260e7dd3203b6ab8492b477`  
**Accepted W3 run:** `37545032247` — SUCCESS  
**Artifact:** `11449982099` — `ANG-S11-W3-Properties`  
**Artifact digest:** `sha256:81077bc180eb29506aca3b4a7d1720675082e09759650de829083bca3ecb8533`  
**Artifact size:** 6,370,779 bytes

## Gate result

W3 is accepted because the same canonical property state is proven through:
- immutable domain value objects;
- semantic CommandBus/CommandBatch mutation;
- Undo/Redo;
- .angproj persistence and backward-compatible load defaults;
- real PySide6 inspector controls emitting semantic intents;
- real preview impact;
- real FFmpeg qualification export impact;
- full regression lock.

No presentation component mutates ProjectState or media-engine objects directly.

## Inspector binding

Verified binding contexts:
- project;
- track;
- asset;
- clip.

Only the clip binding is editable for W3 canonical clip properties. Binding
changes context without changing project revision.

## Video / composition properties

Canonical W3 video properties:
- position X/Y;
- scale X/Y;
- rotation;
- opacity;
- crop left/top/right/bottom.

Evidence fixture applied:
- position X: 36;
- position Y: -18;
- scale: 82% × 82%;
- rotation: 5.0 degrees;
- opacity: 78%;
- crop L/T/R/B: 4/3/2/3%.

The property preview differs from the baseline preview:
- baseline SHA-256:
  `5172dbf868baeb9c96735a2050581d224ba750fb0dcd69b10aea951e93ca7681`;
- W3 property preview SHA-256:
  `03323c59974e90266691d941ae5e9215d3189e7b5b344f034235516616182ff9`.

## Audio properties

Canonical W3 audio properties:
- volume;
- pan;
- fade-in;
- fade-out.

Evidence fixture:
- volume 68%;
- pan -30%;
- fade-in 12 frames;
- fade-out 18 frames.

The final real output retains an audio stream.

## Color policy

Canonical W3 basic color controls:
- brightness;
- exposure;
- contrast;
- saturation;
- white-balance temperature;
- tint.

Evidence fixture:
- brightness +8%;
- exposure +0.3 EV semantic value;
- contrast +18%;
- saturation +25%;
- temperature +12%;
- tint -8%.

The domain stores editor-level semantic values. The current qualification
adapter maps those values deterministically to FFmpeg filters for real preview
and export evidence. This mapping is not permission for presentation code to
call FFmpeg directly and does not change the production-engine priority.

## Speed semantics

Uniform clip speed is canonical and persisted:
- supported W3 range: 25%–400%;
- duration is recomputed from source duration;
- later clips ripple when requested;
- preview source-frame mapping follows the speed-aware timeline.

Evidence:
- source duration: 120 frames;
- speed: 200%;
- effective timeline duration: 60 frames;
- following clip moved to frame 60.

Audio time-stretch uses deterministic atempo chaining in the qualification
adapter.

## Reverse policy

**Reverse is NOT supported in W3.**

The control is visibly disabled and the application rejects reverse mutation
with the explicit reason:

> Reverse belum lolos qualification backend W3 dan sengaja dinonaktifkan.

This is intentional no-fake-capability behavior. Reverse may only be enabled by
a later wave after real backend qualification and regression evidence.

## Undo / Redo / persistence

Cross-property history evidence:
- baseline semantic hash:
  `c31d84c18377e834295d284781df89b182942694e8ef25f2e284dc74c5fa11e3`;
- W3 property semantic hash:
  `6424501c33b74b2526a1cba07f7863d32abab30826c51cbd63f4015f0e0b450e`;
- Undo restored the exact baseline hash;
- Redo restored the exact W3 property hash;
- save/reopen restored the exact W3 semantic hash;
- old schema-v1 clips without W3 properties load with safe default
  `ClipProperties`.

## Real preview / export evidence

Final W3 export:
- file: `w3_properties_export.mp4`;
- SHA-256:
  `faf166bb5d78e997d264d104fcc76bb72f4f5415081511b1a4a14376afb3b48b`;
- 1920×1080;
- 30 fps;
- canonical timeline: 180 frames;
- ffprobe export: 180 frames;
- audio stream: present.

Evidence verifier: **PASS 8/8 files**.

Artifact contains:
1. `00_w3_report.json`
2. `01_properties.json`
3. `02_undo_persistence.json`
4. `03_preview_export.json`
5. `preview_baseline.png`
6. `preview_properties.png`
7. `w3_properties.angproj`
8. `w3_properties_export.mp4`

## Engine truth

W3 real preview/export qualification currently uses the STEP 10 FFmpeg adapter
behind `MediaEnginePort`. This is real evidence, not a fake renderer.

**It is not an engine switch.**
D-024 remains active:
- MLT is the primary production-engine implementation candidate;
- ProjectState + CommandBus remain source-of-truth;
- MediaEnginePort remains the boundary;
- final production MLT property mapping/native bundle still requires later
  hardening before release.

## Quality and regression lock

On accepted implementation HEAD `79217e687a9930087260e7dd3203b6ab8492b477`:

- W3: `37545032247` — SUCCESS;
- W2: `37545032183` — SUCCESS;
- W1: `37545031989` — SUCCESS;
- W0: `37545032172` — SUCCESS;
- S10: `37545032214` — SUCCESS;
- S09: `37545032107` — SUCCESS;
- S08: `37545032095` — SUCCESS.

W3 quality gate also passed:
- Ruff format;
- Ruff lint;
- mypy;
- Import Linter — 4 contracts kept, 0 broken;
- architecture verifier;
- source-of-truth 70/70;
- frozen UI references 42/42;
- secret verifier;
- full pytest suite.

## Gate

**SF-STEP 11 W3 = PASS.**

Next exact wave after owner says `lanjutkan`:
**W4 — Titles / Transitions / Effects**.

Do not begin W4 automatically.
