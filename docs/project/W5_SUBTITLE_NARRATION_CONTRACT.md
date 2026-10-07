# SF-STEP 11 W5 CONTRACT — Subtitle + Narration

**Status:** CONTRACT_LOCKED / W5-001 PASS / W5-002 PASS / W5-003 PASS / W5-004 READY  
**Derived from:** frozen Product, UI, Architecture and Master Blueprint  
**Previous accepted implementation:** W4 HEAD `3e3cd376189e9f183e70ca537ad25f037e25bcd7`

## 1. Why W5 is Subtitle + Narration

The frozen product roadmap places Subtitle + Narration immediately after the
motion/animation capability. Product requirements F-010/F-011/F-012 and
FR-011/FR-012 mark them MUST parity features. The frozen UI already reserves:
- SCR-008 Subtitle Workspace;
- SCR-009 Audio / Narration Workspace;
- UI-017 Subtitle Editor — Cue & Teks;
- UI-018 Audio / Narasi Workspace;
- UI-033 Subtitle Style;
- UI-034 Subtitle Animation;
- UI-035/UI-036 per-word/highlight timing states;
- WIN-001 Narration Recording;
- WIN-003 Subtitle Edit/Timing Tools.

W4 title overlay remains a separate creative-title feature. W5 must not reuse
or stretch TitleProperties into a subtitle system.

## 2. Canonical ownership

W5 extends the existing canonical ProjectState. It does not create a second
project model.

Expected semantic ownership:
- SubtitleTrack / subtitle source reference;
- SubtitleCue with stable identity/index, frame-aware start/end and text;
- SubtitleStyle;
- SubtitleAnimation;
- optional WordTiming metadata when explicitly created;
- NarrationTrack / narration binding with frame-aware offset and bounded audio
  controls;
- RecorderPort or equivalent application port for microphone capture;
- engine/compiler adapters remain infrastructure.

All persisted project mutations must flow through CommandBus/CommandBatch.
Presentation emits semantic intents and may keep an unsaved local subtitle
working copy, but it cannot mutate engine objects or project JSON directly.

## 3. Serial W5 task contract

### S11-W5-001 — Canonical subtitle/narration model
- add subtitle and narration entities to ProjectState;
- use the same canonical FPS/frame-time rules already used by timeline state;
- add persistence with old-schema safe defaults/migration;
- validate invalid/empty timing ranges and missing canonical references;
- do not encode Qt, FFmpeg, ASS or microphone implementation details in domain.

### S11-W5-002 — SRT import + validation
- SRT is the primary subtitle input for V1;
- support UTF-8 / UTF-8 BOM input;
- preserve cue text and multiline meaning;
- reject malformed timestamp/range/empty-cue input with actionable errors;
- detect overlap/invalid ordering without silently truncating data;
- treat SRT as untrusted external input;
- importing/reloading an SRT must not silently rewrite the source file.

### S11-W5-003 — Cue editing + safe working-copy flow
- cue list and selected-cue edit;
- text, IN and OUT edit;
- insert/delete where valid;
- split and merge;
- stable sort/index-normalization operations only when explicit;
- reload guard when local working copy is dirty;
- save edited subtitle as a new/copy SRT by default;
- source SRT may not be overwritten silently;
- committing a new subtitle source/binding to the project is undoable.

### S11-W5-004 — Subtitle style
Canonical style must cover the frozen product surface where render-backed:
- font family and size;
- fill color;
- outline color/width;
- shadow;
- optional background box/opacity;
- alignment;
- safe vertical margin.

Style changes must persist, Undo/Redo, survive reopen and appear in
preview/export evidence.

### S11-W5-005 — Subtitle animation + per-word timing boundary
Initial animation names may be exposed only after real preview/export proof.

AAVC read-only reference proves concrete compiler behavior for:
- Fade;
- Pop;
- Slide Up;
- Clean Documentary.

The following legacy/preset names must stay hidden/disabled until equivalent
render behavior is independently proven:
- Word Reveal;
- Karaoke Highlight;
- Typewriter;
- Bounce Soft;
- Emphasis Word;
- Social Caption;
- any other name that merely falls back to a generic fade.

Per-word timing may be represented/edited. Deterministic even word
distribution is allowed only as an explicitly requested fallback and must be
labeled as **not speech alignment**. W5 must not claim ASR, transcription or
automatic phoneme/word synchronization.

### S11-W5-006 — Narration import + binding
- import supported narration audio through existing media identity/probe rules;
- bind one canonical narration source/track to the project;
- frame-aware offset/sync;
- bounded gain/mute/fade behavior only when the real runtime supports it;
- narration must be audible in preview/export evidence;
- project reopen must retain the same narration binding and timing.

Narration is not just generic clip-volume state: it is a first-class project
workflow/source relationship.

### S11-W5-007 — Microphone recording
- expose microphone recording only behind a dedicated application port/adapter;
- require an active project and an available input device;
- record to a staging WAV/media file first;
- validate the staged recording before committing it;
- finalize using safe/atomic replacement semantics;
- failed/empty/cancelled recording must not clobber an existing narration;
- device unavailable/permission/capture failures must be user-visible errors;
- a successful recording becomes a normal narration media source through the
  same canonical import/binding path.

Hardware gate:
- deterministic unit/port tests are mandatory;
- a real Windows microphone smoke is required for full W5 PASS when a capture
  device is available;
- without real-device evidence, W5 may close only as
  **PASS_WITH_PROVISIONAL_MIC_HARDWARE**, not full PASS.

### S11-W5-008 — Frozen UI parity
Implement real interactive widgets for the frozen AAVC surfaces:
- SCR-008 / UI-017 subtitle cue editor;
- UI-033 subtitle style;
- UI-034 subtitle animation;
- UI-035/UI-036 timing/highlight states only for capabilities that are real;
- SCR-009 / UI-018 narration workspace;
- WIN-001 narration recording;
- WIN-003 subtitle timing/edit tools.

No redesign, no screenshot-as-runtime UI and no fake enabled controls.
Any visible deviation requires DELTA_FROM_AAVC change control.

### S11-W5-009 — Preview/export qualification
A deterministic real-media fixture must prove:
- imported SRT cue appears at the correct timeline frame;
- edited text/timing survives save/reopen;
- style is visible in output;
- every enabled subtitle animation has real render evidence;
- narration is audible and frame-synchronized;
- subtitle + narration can coexist in the same export;
- output is valid and keeps canonical duration within tolerance;
- source SRT remains unchanged unless the user explicitly selected it as an
  overwrite destination and the product policy allows that action.

### S11-W5-010 — History, failure paths and regression lock
Before W5 can close:
- subtitle/narration project mutations pass Undo/Redo;
- old W4 projects load with safe W5 defaults;
- malformed SRT failure is tested;
- dirty working-copy leave/reload guard is tested;
- missing/corrupt narration does not produce fake success;
- failed recording does not clobber existing narration;
- Ruff format/check PASS;
- mypy PASS;
- import-contract/architecture/source-of-truth/UI/secret gates PASS;
- full pytest PASS;
- deterministic W5 evidence verifier PASS;
- W4/W3/W2/W1/W0/S10/S09/S08 regressions stay green on the accepted W5 HEAD.

## 4. Explicit non-scope for W5

W5 must not start:
- Gemini credential/provider work;
- AI subtitle rewriting or AI Auto Edit;
- speech-to-text / ASR;
- automatic speech alignment claims;
- background workspace;
- full Validation Center/relink hardening beyond errors required by W5;
- expanded export matrix / final release packaging;
- unsupported subtitle animation labels;
- W4 unsupported visual effects or crossfade work;
- Reverse enablement.

## 5. Implementation order

Implementation must remain serial:
1. W5-001 canonical model;
2. W5-002 SRT parser/import;
3. W5-003 cue working-copy/editor commands;
4. W5-004 style;
5. W5-005 supported animation/per-word boundary;
6. W5-006 narration import/binding;
7. W5-007 microphone recording;
8. W5-008 UI parity wiring;
9. W5-009 real preview/export proof;
10. W5-010 failure/regression closure.

Do not skip directly to UI or recording before canonical model and parser
semantics are accepted.

## 6. Implementation progress

- S11-W5-001 — **PASS**
  - accepted implementation HEAD:
    `b5bf8543554bcf38d22a65510fe0376195676d46`;
  - accepted run: `37571740654`;
  - evidence:
    `docs/evidence/features/S11_W5_001_CANONICAL_SUBTITLE_NARRATION.md`.
- S11-W5-002 — **PASS**
  - accepted implementation HEAD:
    `d4349c925cc0f475cfa94b0db55347320954e1cf`;
  - accepted run: `37572463564`;
  - evidence:
    `docs/evidence/features/S11_W5_002_SRT_IMPORT_VALIDATION.md`.
- S11-W5-003 — **PASS**
  - accepted implementation HEAD:
    `d8db4d18cb42b71d91a9b727868b25340961702f`;
  - accepted run: `37573388357`;
  - evidence:
    `docs/evidence/features/S11_W5_003_SUBTITLE_WORKING_COPY.md`.
- S11-W5-004 — **READY**.
- S11-W5-005..010 — **BLOCKED_BY_PREVIOUS_TASKS**.

On the next owner `lanjutkan`, execute **S11-W5-004 only**.
