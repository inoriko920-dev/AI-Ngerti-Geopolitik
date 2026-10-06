# SF-STEP 11 W2 — TIMELINE, PLAYBACK & CORE EDITING

**Gate:** PASS  
**Accepted implementation HEAD:** `4486da29883bc42e9cd12d5d13a7784f347dc2d3`  
**Accepted W2 workflow:** `37542485728` — SUCCESS  
**Date:** 07 October 2026

## 1. Scope

W2 completes the canonical timeline/playback/core-editing foundation without
creating a second project or timeline source of truth.

Canonical ownership remains:
- `ProjectState` = semantic project truth;
- `CommandBus/CommandBatch` = canonical mutation + Undo/Redo;
- `TimelineController` = timeline interaction owner;
- `MediaEnginePort` / engine adapters = runtime projection only;
- presentation emits semantic intents and does not mutate project state directly.

## 2. Verified W2 task coverage

### S11-W2-001 — Multi-track basics
VERIFIED:
- create track;
- delete empty track;
- rename track;
- reorder track;
- lock state;
- mute state;
- visibility state;
- deterministic unique track IDs/order;
- backward-compatible persistence for new track fields.

Current W2 canonical track kind remains **video**. Audio/property track work is
not falsely claimed here and belongs to later waves.

### S11-W2-002 — Clip edit semantics
VERIFIED:
- stable clip IDs;
- clip selection;
- reorder;
- move within/across video tracks;
- duplicate;
- delete;
- invalid overlap rejection;
- no silent replacement of canonical IDs.

### S11-W2-003 — Ripple / collision policy
VERIFIED:
- duration ripple;
- delete/gap close;
- overlap validation rejects invalid canonical state;
- edit does not commit a partial invalid project.

### S11-W2-004 — Split / trim
VERIFIED:
- split at playhead;
- left-edge trim;
- right-edge trim;
- optional right-edge ripple policy;
- frame-based timing remains canonical.

### S11-W2-005 — Undo / Redo
VERIFIED:
- semantic-hash restoration for W2 mutations;
- track and clip mutations exercised through CommandBus;
- save/reopen after W2 state matches semantic hash.

### S11-W2-006 — Preview transport
VERIFIED:
- play;
- pause;
- seek;
- scrub;
- edit while playing auto-pauses;
- playhead frame;
- zoom;
- follow modes and manual-scroll follow suspension;
- preview frame evidence before/after an edit boundary.

### S11-W2-007 — Keyboard / context actions
VERIFIED:
- QAction shortcuts are real Qt actions;
- Split = `S`;
- Duplicate = `Ctrl+D`;
- Delete = `Delete`;
- Marker = `M`;
- IN = `I`;
- OUT = `O`;
- routed through semantic UI intents into the canonical controller/CommandBus.

### S11-W2-008 — Stress fixture
VERIFIED on Windows CI:
- tracks: 4;
- clips per track: 250;
- total clips: **1000**;
- reorder/Undo/Redo cycles: 40;
- measured elapsed: **63.04 ms**;
- budget: **8000 ms**;
- result: PASS.

This number is CI-runner evidence for this deterministic semantic stress fixture,
not a claim about full-GUI 1000-clip interactive FPS.

## 3. Windows quality gate

Job: **W2 timeline playback core** — SUCCESS.

PASS:
- `uv lock --check`;
- frozen dependency sync;
- Ruff format;
- Ruff lint;
- mypy;
- Import Linter;
- architecture verifier;
- source-of-truth verifier;
- frozen UI reference integrity 42/42;
- no-secrets verifier;
- pytest: **55 tests PASS**;
- owned media fixture generation;
- canonical W2 evidence;
- complete multitrack semantics;
- 1000-clip stress budget;
- final W2 evidence verifier: **9 required files + previews PASS**.

## 4. Canonical semantic evidence

The accepted run proves:
- original timeline scenario status = PASS;
- selection valid = true;
- magnetic snap = true;
- edit-during-playback auto pause = true;
- save/reopen hash match = true;
- preview evidence valid = true;
- export evidence valid = true.

Extended multitrack semantics:
- status = PASS;
- track order = `V2, V1`;
- V2 renamed to `B-roll`;
- V2 muted = true;
- V2 visible = false;
- C003 preserved as stable ID after duplicate/move to V2;
- C003 timeline start = 90;
- C002 start after left trim = 70;
- C001 duration after right trim = 50;
- all tested W2 mutations Undo/Redo checked = true;
- save/reopen semantic hash match = true.

## 5. Real MLT Windows runtime proof

Job: **W2 MLT canonical playback projection** — SUCCESS.

The accepted Windows/MSYS2 MLT test proves:
- ProjectState-derived canonical plan reaches MLT;
- clip IDs `C001, C002`;
- real SDL2 transport process starts and returns code 0;
- seek/source arguments are produced from canonical clip timing;
- MLT renders `w2-mlt-edited.mp4`;
- ffprobe confirms video and audio streams;
- canonical MLT playback/render projection = PASS.

Important scope:
- current MLT qualification projects the canonical contiguous V1 video timeline;
- W2 does not claim final arbitrary multitrack compositing/audio-property support;
- those richer engine/property semantics remain later-wave work.

## 6. Artifacts

### Core W2 evidence
- artifact: `ANG-S11-W2-Timeline-Playback-Core`;
- ID: `11449376822`;
- size: 10,138,067 bytes;
- digest:
  `sha256:1c7a5812b7d249caf51af294f14ce734cc3e58bc314cdf76b5a45ab543641e83`.

### MLT canonical projection
- artifact: `ANG-S11-W2-MLT-Canonical-Projection`;
- ID: `11448897281`;
- size: 272,204 bytes;
- digest:
  `sha256:c27584b57760121eff068040345aedf95ebd6bfe36a49af691030cfe9b8a3846`.

## 7. Regression lock on accepted implementation HEAD

All mandatory earlier workflows are SUCCESS on
`4486da29883bc42e9cd12d5d13a7784f347dc2d3`:

- S08 Windows Foundation — run `37542485951`;
- S09 Windows UI Shell — run `37542485810`;
- S10 Windows E2E Vertical Slice — run `37542485819`;
- S11 W0 Engine Qualification — run `37542485906`;
- S11 W1 Project Media Persistence — run `37542485911`;
- S11 W2 Timeline Playback Core — run `37542485728`.

## 8. Gate decision

**S11 W2 = PASS.**

W2 is closed. The next serial wave is:

**S11 W3 — Properties: Video, Audio, Color & Speed.**

W3 must not be treated as already implemented merely because the inspector UI
exists. It requires canonical property state, commands, persistence, preview and
render/output evidence according to the supported engine capability.
