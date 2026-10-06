# SF-STEP 11 WAVE 0 — BASELINE & ENGINE QUALIFICATION

Status: **PASS**

Entry HEAD:
`3cab97fa8ec05f0f50d35c1c72badb489fb20aa2`.

Accepted implementation/evidence HEAD:
`f54993851f85aa5672f0d86dcb7e5ea3a49c7ae6`.

Accepted workflow:
- name: `S11 Wave0 Engine Qualification`;
- run ID: `37533447729`;
- conclusion: **SUCCESS**.

## W0 task results

| Task | Result | Evidence |
| --- | --- | --- |
| S11-W0-001 baseline identity | VERIFIED | STEP 10 accepted SHA/runs recorded |
| S11-W0-002 clean regression | VERIFIED | W0 regression job SUCCESS |
| S11-W0-003 canonical E2E | VERIFIED | STEP 10 evidence 22/22 reproduced |
| S11-W0-004 UI/schema/flags | VERIFIED | UI 42/42, schema v1 fixture, registry tests |
| S11-W0-005 engine qualification | VERIFIED | MLT Windows runtime job SUCCESS |
| S11-W0-006 playback/seek/edit coherence | VERIFIED at qualification level | SDL2 continuous/seek/edited-playlist smoke + Python seek probe + avformat render |
| S11-W0-007 engine/package/license decision | VERIFIED | D-024 records MLT direction and remaining release gate |

## Regression lock

W0 regression job proved:
- Import Linter: 4 contracts kept, 0 broken;
- architecture verifier PASS;
- source-of-truth 70/70;
- frozen UI references 42/42 SHA-256;
- no obvious committed secrets;
- pytest: **31 tests PASS**;
- canonical STEP 10 E2E rerun PASS;
- STEP 10 evidence verifier: 22/22.

Reproduced semantic backbone at W0:
- project revision: 8;
- semantic hash:
  `b83df289291e592406575347c779edd307a810faefb223cb6dd349ff39289f07`;
- asset: A001;
- clips: C001, C002;
- preview boundary frames: 149, 151;
- export SHA-256:
  `2157671678c630b3fcebd5268a011ac454a14a83cf8d8a08d83746c8fa34634e`.

Regression artifact:
- ID: `11444509597`;
- wrapper SHA-256:
  `da93d82448dcc24e7afb1b8231d708603d1ddb9c8b443830fd9c058a63ae4a3f`.

## MLT Windows qualification

Artifact ID:
`11444689616`.

Artifact wrapper SHA-256:
`1d6aea12d42b94d2f1569f54e22f73d633689b90de0b60dcbebf949eae1a6b97`.

Actual package/runtime tested:
- `mingw-w64-x86_64-mlt 7.40.0-2`;
- `melt.exe 7.40.0`;
- Python binding `mlt7` imported successfully;
- core consumers found: `sdl2`, `sdl2_audio`, `avformat`, `null`.

Python binding seek probe:
- producer valid: true;
- length: 100 frames;
- requested/observed seek pairs:
  - 0 -> 0;
  - 10 -> 10;
  - 50 -> 50;
  - 98 -> 98.

The MLT avformat edited-playlist render produced:
- H.264 video;
- AAC audio;
- 640×360;
- 30 fps;
- audio 48 kHz;
- duration about 2.517333 s.

The SDL2 CI smoke advanced frames for:
- continuous playback;
- seeked playback;
- edited-playlist playback.

The headless `SDL_VIDEODRIVER=dummy` environment also logged
`Couldn't find matching render driver`. This does **not** prove GUI display
rendering. It proves the MLT transport/consumer path can run in the CI
qualification environment. Real Qt playback presentation still belongs to W2.

Optional package plugins (for example glaxnimate/plus/qt6/resample/rnnoise/
rtaudio/rubberband/sox) emitted load warnings in the minimal CI environment.
Those warnings are recorded and must be revisited only when a corresponding
feature is promoted into scope.

## Engine decision

Fresh W0 evidence supersedes the old ordering from D-020 for implementation
priority:

- **MLT becomes the primary production-engine implementation candidate for
  STEP 11 W1/W2 feature work**.
- libopenshot remains a component/reference candidate but direct production
  binding is BLOCKED until its Windows build/package/license chain is stronger.
- the STEP 10 FFmpeg adapter remains qualification/reference infrastructure,
  not the final editor engine.
- ProjectState, CommandBus, MediaEnginePort and the AAVC UI freeze remain
  unchanged.

This is an evidence-based engine-direction change, not an architecture rewrite.

## Remaining release gate

W0 does **not** claim the final portable MLT bundle is solved. Before release:
- exact native DLL closure must be produced;
- only required plugins should be bundled;
- LGPL/GPL/codec obligations must be enumerated for the actual binary set;
- THIRD_PARTY_NOTICES/source-offer or equivalent obligations must be satisfied;
- clean-machine package smoke must pass.

Those are release/package gates and do not block W1 domain/application
hardening.

## Gate

**W0 = PASS.**

Next exact wave:
**W1 — Project, Media & Persistence Foundation.**

Do not begin W2 until W1 evidence is green.
