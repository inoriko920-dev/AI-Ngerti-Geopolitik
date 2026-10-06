# SF-STEP 11 WAVE 0 — BASELINE & ENGINE QUALIFICATION

Status: **ACTIVE / CI EVIDENCE PENDING**

Entry HEAD:
`3cab97fa8ec05f0f50d35c1c72badb489fb20aa2`.

## Regression baseline

STEP 10 accepted implementation is already green:
- S10 `37527851180` SUCCESS;
- S09 `37527851222` SUCCESS;
- S08 `37527851230` SUCCESS.

Wave 0 reruns regression on the new W0 code before acceptance.

## Fresh upstream qualification facts

### libopenshot v1.0.1

Pinned tag:
`1c46200eaedeebce3fbce74b5584dc0c04d70903`.

Positive:
- current release includes playback/seek/frame-handoff/reader-lifecycle race fixes;
- libopenshot itself is LGPL-3.0-or-later;
- Python bindings and Qt playback capability exist upstream.

Blocking/risk evidence for ANG Windows production adoption:
- current upstream libopenshot CI has Windows build disabled;
- v1.0.1 GitHub release publishes no prebuilt release assets;
- v1.0.1 requires libopenshot-audio v1.0.1;
- libopenshot-audio is GPLv3-or-later / commercial-license dual path.

Therefore direct libopenshot adoption stays BLOCKED for ANG production packaging until a reproducible Windows native build + distribution/license strategy is proven.

### MLT v7.42.0

Pinned tag:
`11e84ecf42e1a7bc885953afa58ba35d228a76ad`.

Positive current evidence:
- active Windows MSYS2 workflow;
- active Windows MSVC workflow;
- MSYS2 workflow explicitly builds with `SWIG_PYTHON=ON`;
- core framework/mlt++ are LGPLv2.1+;
- v7.42.0 specifically fixes SDL2 Windows playback freezing and pause/stop hangs;
- official docs expose `sdl2`, `null`, `avformat` consumers and Python bindings.

Wave 0 CI now performs a real Windows MLT runtime qualification before changing the locked production-engine direction.

## Gate

Do not mark W0 PASS until:
1. regression job is green;
2. MLT Windows runtime/playback qualification is green;
3. evidence artifacts are inspected;
4. engine decision and D-020 replacement/supplement are recorded explicitly.
