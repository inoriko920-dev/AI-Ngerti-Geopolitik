# SF-STEP 10 — MINIMUM END-TO-END VERTICAL SLICE

**Project:** AI Ngerti Geopolitik  
**Gate:** **PASS_WITH_PROVISIONAL**  
**Accepted implementation commit:** `852610f55a6e99dc98234114c3cf099ed85dfd42`  
**Final S10 Windows run:** `37527851180` — **SUCCESS**  
**S09 regression run:** `37527851222` — **SUCCESS**  
**S08 regression run:** `37527851230` — **SUCCESS**

## 1. What the vertical slice proves

The canonical STEP 10 path is real, not a mock-only green path:

`real Qt QAction -> semantic UiIntent -> application use-case -> CommandBus -> ProjectState -> real media adapter -> persistence / preview / export -> verified artifacts`.

Verified flow:
1. real toolbar Import Media QAction emits a semantic `IMPORT_MEDIA` intent;
2. ffprobe probes a generated/owned H.264 + AAC fixture;
3. ProjectState receives canonical asset `A001`;
4. clip `C001` is added to V1 through CommandBus;
5. clip is split at frame 150 into stable `C001` + `C002`;
6. `C002` is trimmed by 30 frames;
7. invalid split is atomic and leaves semantic state unchanged;
8. Undo/Redo restores exact semantic hashes;
9. current ProjectState is projected into real Qt timeline widgets;
10. engine-derived preview frames are produced at frames 149 and 151 and the frame-151 result is projected into the real Qt preview canvas;
11. `.angproj` save/load preserves the semantic hash;
12. corrupted project load is rejected;
13. real export produces H.264 video + AAC audio;
14. cancellation terminates the media process and leaves no false final/partial output;
15. packaged PyInstaller onedir qualification executable repeats import/edit/save/preview/export against real FFmpeg/ffprobe.

## 2. Exact state proof

Final semantic facts:
- project revision: **8**;
- semantic hash: `59f2d632f402b3dd1b08e66cb1f5c3e7cf8146d46c4efdd86372a13bccb30457`;
- asset: `A001`;
- clips: `C001`, `C002`;
- timeline block 1: `C001  0-150f`;
- timeline block 2: `C002  150-210f`;
- real preview boundary frames: **149** and **151**;
- live Qt preview frame: **151**.

The live projection evidence is captured in:
- `07_live_ui_projection.txt`;
- `screenshots/live_ui_projectstate_preview_151.png`.

The CI/headless screenshot is state-binding evidence, not a replacement for STEP 09 typography/visual acceptance. Frozen AAVC UI references remain the design authority.

## 3. Persistence / Undo / negative-path proof

Verified:
- atomic `.angproj` JSON save;
- schema version = 1;
- semantic hash identical after save/load;
- Undo/Redo exact semantic restoration;
- missing media rejected;
- invalid split rejected atomically;
- corrupt project rejected;
- wrong project extension rejected;
- cancelled export leaves no final or partial artifact.

Negative paths recorded: **5**.

## 4. Real output proof

Independent ffprobe result:
- video codec: **H.264**;
- audio codec: **AAC**;
- resolution: **1920×1080**;
- frame rate: **30 fps**;
- duration: **7.000000 s / 210 frames**.

Export SHA-256:
`2157671678c630b3fcebd5268a011ac454a14a83cf8d8a08d83746c8fa34634e`.

Measured final-run timings on the GitHub Windows runner:
- media import/probe: ~0.058 s;
- save: ~0.002 s;
- load: ~0.0002 s;
- export: ~0.796 s.

These timings apply only to the tiny deterministic STEP 10 fixture and are not production performance targets.

## 5. Quality / regression proof

Final STEP 10 run:
- Ruff format: PASS;
- Ruff lint: PASS;
- mypy: **25 source files / 0 issues**;
- Import Linter: **4 kept / 0 broken**;
- architecture verifier: PASS;
- source-of-truth verifier: **70/70**;
- frozen UI verifier: **42/42 SHA-256**;
- secret verifier: PASS;
- pytest: **26 PASS**;
- STEP 10 evidence verifier: **22/22 required files**.

Prior milestones also remain green on the same accepted commit:
- S09 UI workflow `37527851222`: SUCCESS;
- S08 foundation workflow `37527851230`: SUCCESS.

## 6. Artifacts

### Canonical E2E evidence

Artifact:
- name: `ANG-S10-E2E-Evidence`;
- ID: `11442927357`;
- size: 9,477,562 bytes;
- wrapper digest: `sha256:f0840c34805a7500bdb1231415cb692356d5c649de4352c0f095de04552f9cb1`.

### Packaged real-media qualification smoke

Artifact:
- name: `ANG-S10-Packaged-Media-Smoke-Windows-x64`;
- ID: `11443860096`;
- size: 17,804,939 bytes;
- wrapper digest: `sha256:4caa469422d9c57ee87eff82a8bde7ae621821dde11e97ecbf65caeac840b4db`.

Inner packaged qualification ZIP SHA-256:
`a5e10ca7bef929a19c6f0f6cac20bd7b3198e517b4e06f49a600f823fe070301`.

The packaged qualification executable passed import -> edit -> save/load -> preview -> export. It uses **external system FFmpeg/ffprobe** and is not the final user-facing product package.

## 7. Provisional items

STEP 10 is deliberately **PASS_WITH_PROVISIONAL**, not full production-engine PASS.

Non-blocking provisional items:
1. continuous interactive timeline playback/transport against the final production engine is not yet proven;
2. D-020 final production media-engine qualification remains open: libopenshot is still the primary candidate and MLT the fallback pending evidence;
3. the STEP 10 FFmpeg adapter is a real qualification backend, but it is not a silent replacement for the D-020 engine decision;
4. native dependency/license/package strategy for the final production media engine remains a later gate.

These items do not invalidate the canonical vertical slice. They become priority work in STEP 11 before broad media feature expansion.

## 8. Gate decision

**SF-STEP 10 = PASS_WITH_PROVISIONAL.**

Reason: the architecture is no longer theoretical. A real UI entry, deterministic domain editing, Undo/Redo, real Qt state projection, persistence, real media preview/export, cancellation, negative paths, Windows CI, and packaged real-media smoke are all proven on one exact repository baseline.

## 9. Handoff

Next exact step after owner says `lanjutkan`:

**SF-STEP 11 — FEATURE IMPLEMENTATION WAVES**

First wave must preserve this E2E regression baseline and prioritize production MediaEnginePort qualification + continuous playback before broad feature growth. Do not start STEP 12 integrations and do not claim Gemini/service wiring complete in STEP 11.
