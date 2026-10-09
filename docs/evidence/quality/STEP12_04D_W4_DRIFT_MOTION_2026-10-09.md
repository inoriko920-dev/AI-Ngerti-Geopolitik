# STEP 12-04D — W4 Drift diagonal image animation in native H264

Date: 2026-10-09 WIB. PR #20 development only. No main merge, no portable.

## Changes
- Added bounded frame-exact `qualified_still_drift` supporting canonical W4
  effect `Drift` on enter and/or exit, default 100% intensity.
- W4 0.25s enter/exit windows (at most half the clip duration); diagonal
  12% overscan crop moves simultaneously horizontally and vertically.
- Real `render_still_frame` applies crop offsets to X and Y, and the
  existing PNG -> RGB24 -> FFmpeg H264 pipeline encodes that motion.
- Only one active visible V1 HOLD image clip may animate; no V2 overlap,
  fade_black transition, Fade/Drift or Pan/Drift mixing, title, speed or
  other modified clip-property combinations. Reject unsupported inputs.
- Strict Export UI validation shares the exact same qualification;
  frozen visual UI and 42 reference screenshots remain unchanged.

## Acceptance
- Qt tests compare varied 2D source pixels at opening, entry, center,
  exit and final frames; reject unsupported mixed effects and V2.
- Actual Windows native FFmpeg test decodes an H264 MP4 from a 2D color
  pattern and requires frame-to-frame sampled pixel changes, exact
  60-frame output, source checksum, and intact following green scene.
- All existing Pan, Fade, fade_black, 1080p/120 images, audio/SRT,
  cancellation and storage-pressure tests must remain PASS.
- Full Windows regression and owner-approved native FFmpeg job must both
  be SUCCESS on the identical development HEAD before marking PASS.

## Limitations
Drift here is a narrow finite-window diagonal crop, not W4 arbitrary
motion/keyframes, Canva parity, zoom, cross dissolve, multiple lanes,
Pop/Breathe or native process-tree isolation. Owner must separately
approve merge; portable only after full product QA passes.
