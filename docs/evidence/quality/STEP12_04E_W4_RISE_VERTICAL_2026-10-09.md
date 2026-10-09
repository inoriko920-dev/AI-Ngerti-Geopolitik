# STEP 12-04E — W4 Rise native Pilot A implementation

Date: 2026-10-09 WIB | Repo: inoriko920-dev/AI-Ngerti-Geopolitik
PR #20 development branch only; no merge to main and no portable.

## Accepted scope
- Canonical still image HOLD W4 Rise IN and/or OUT at intensity 100%.
- W4 creative mapping reference: vertical Y displacement +8% at beginning/end,
  easing to zero in min(0.25 seconds, half-clip) windows.
- Limited single V1 image with no overlapping V2, no fade_black transition,
  and no additional effect/transform/color/title changes.
- Qualified Rise is rendered into Qt still preview, frame sequence PNG, and
  genuine externally encoded H.264 MP4 via the existing verified pipeline.
- 16% bounded overscan and pixel-shift crop maintain full-canvas coverage.
- V1 export qualification shares the same checks and fails closed on
  Rise+Pan/Drift/Fade, V2 parallel layout and transitions.
- Native Windows acceptance test validates actual decoded frame movement
  for IN/OUT and following scene unaffected; unit tests check effect
  monotonic motion, geometry, overlap and invalid combinations.

## Non-goals
This does not implement Breathe, Pop, Stomp, Tectonic or Tumble, mixed
motion presets, arbitrary keyframe animation, crossfade or general
production release parity. Frozen 42 UI references remain unchanged.
Both Windows full QA and native FFmpeg CI on exact branch HEAD must PASS
before marking STEP 12-04E complete.
