# AI Ngerti Geopolitik

> **STATUS: SF-STEP 10 PASS_WITH_PROVISIONAL — NEXT SF-STEP 11 FEATURE IMPLEMENTATION WAVES**

Repository resmi aplikasi **AI Ngerti Geopolitik**.

Baca `AGENTS.md` lalu `docs/SOURCE_OF_TRUTH_INDEX.md`.

## Real vertical slice verified

STEP 10 final Windows run `37527851180` passed on commit `852610f55a6e99dc98234114c3cf099ed85dfd42`.

Verified:
- real Qt Import Media action -> semantic application path;
- real media probe;
- ProjectState + CommandBus;
- split/trim + exact Undo/Redo;
- current state projected into the real Qt timeline;
- real backend preview projected into the real Qt preview;
- atomic `.angproj` save/load;
- real H.264/AAC 1920×1080 30 fps export;
- cancellation/error cleanup;
- 26 tests;
- packaged Windows real-media qualification smoke;
- S08/S09 regressions remain green.

Detailed evidence:
`docs/evidence/e2e/S10_MINIMUM_E2E_VERTICAL_SLICE.md`.

Canonical export SHA-256:
`2157671678c630b3fcebd5268a011ac454a14a83cf8d8a08d83746c8fa34634e`.

## Scope truth

STEP 10 proves the backbone, not the whole editor. Continuous production playback and the final libopenshot-vs-MLT engine qualification remain provisional. The FFmpeg adapter used by STEP 10 is real qualification infrastructure, not a silent replacement for the production media-engine decision.

## Frozen decisions remain

- UI = AAVC 1:1 as close as practical; no creative redesign.
- `UI-001..UI-042` remain frozen design authority.
- ProjectState + semantic CommandBus/Undo are ANG-owned.
- media stays behind MediaEnginePort.
- Gemini later executes only through validated EditPlan/commands.
- Windows target remains portable multi-file ZIP.

**Next: SF-STEP 11 — Feature Implementation Waves, starting with production media-engine + continuous-playback qualification.**
