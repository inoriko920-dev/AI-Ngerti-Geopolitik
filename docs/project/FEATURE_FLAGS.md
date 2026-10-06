# STEP 11 FEATURE / READINESS FLAGS

This document mirrors
`src/ai_ngerti_geopolitik/application/feature_flags.py`.

| Key | State after W0 | Meaning |
| --- | --- | --- |
| canonical_editing_backbone | VERIFIED | STEP 10 E2E remains real and green |
| mlt_windows_runtime | VERIFIED | Windows MLT runtime, Python binding, seek, continuous playback smoke and avformat render are evidence-backed |
| production_media_engine | QUALIFYING | MLT is primary implementation candidate; final bundled native package/license chain remains a release gate |
| continuous_playback | QUALIFYING | MLT transport is qualified; real Qt transport integration belongs to W2 |
| libopenshot_direct_binding | BLOCKED | Windows/package/license evidence remains insufficient |
| gemini_service | RESERVED | real Gemini/provider wiring belongs to STEP 12 |

## W0 evidence

Accepted W0 run: `37533447729` on
`f54993851f85aa5672f0d86dcb7e5ea3a49c7ae6`.

Actual Windows MLT package under test:
- package: `mingw-w64-x86_64-mlt 7.40.0-2`;
- runtime: `melt.exe 7.40.0`;
- Python binding: `mlt7`;
- consumers present: `sdl2`, `sdl2_audio`, `avformat`, `null`.

Important scope:
- this qualifies the MLT runtime direction for ANG feature waves;
- it does not yet prove the final clean-machine bundled native dependency set;
- optional MLT plugins missing in the CI package emitted load warnings but did not block the core tested playback/seek/render path;
- user-facing Qt playback remains a later W2 feature, not a W0 claim.
