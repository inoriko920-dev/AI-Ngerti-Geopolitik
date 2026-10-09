# STEP 12-04A — First real transition in image MP4

Status: implementation submitted to development PR #20; verify exact-head
Windows general CI plus authorized external FFmpeg CI before marking PASS.

## Exact scope
- Implement canonical ClipProperties.transition "fade_black" on single
  active V1 image HOLD lane only. Every affected frame is still generated
  from the saved project's verified image bytes; no timeline overlaps or
  crossfade. UI references remain frozen (42 checks).
- Match W4 duration rule: transition window = minimum of configured frames
  and max(1 frame, one-half the clip duration). Visibility linearly fades
  from black at frame zero, stays full in the middle, then fades toward
  black at the clip end. No unqualified effects are ignored.
- Two-image (V1+V2) scenes with any transition, as well as any additional
  creative effect, transform, title, motion or mixed media fail closed.
- Application-side validation rejects unsupported media/effects/lanes
  before invoking native FFmpeg. This is a restricted non-overlap transition.
- Unit/Qt output tests verify exact pixel intensity at clip boundaries.
  A native FFmpeg Windows test encodes an actual 60-frame/30 FPS H264 MP4,
  decodes every frame, samples black/middle/fade-end/next-scene colors,
  checks checksum, and uploads a playable sample with SHA256.

## Not qualified
No Canva-style 21 animation presets, zoom/pan keyframes, dissolves,
animated subtitle, two-lane effects, audio transitions, or long production
motion parity. MLT remains a separate engine; this is only a Pilot A
still-image transition slice. No merge to main, no portable build.
