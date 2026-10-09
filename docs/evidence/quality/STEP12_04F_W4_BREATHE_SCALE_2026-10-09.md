# STEP 12-04F — W4 Breathe on real native H.264

Date: 2026-10-09 WIB. Owner-authorized Pilot A, PR #20 Draft.

## Limited implementation
- Single V1 image HOLD clip, W4 Breathe enter/exit, intensity 100%.
- W4 creative mapping: 0.98→1.00 center scale on IN and reverse on OUT, each in
  up to 0.25-second windows (short clips: no longer than half-duration).
- Image scaler uses a verified source with +5% overscan, proportional center
  crop of destination dimensions / qualified scale. No exposed borders, no
  external processes in still preview. Identical Qt preview and PNG→FFmpeg MP4 pixels.
- Unsupported Breathe mixed with Rise/Pan/Drift/Fade, V2 simultaneous,
  fade_black, and modified property combinations fail closed.
- Existing 42 frozen UI references unchanged. Existing Export UI options
  already flow to the strict single-V1 validation gate.

## Proof gates
- Qt image pixel tests for entering/mid/leaving/end motion and opaque corners.
- Native Windows actual H264 60-frame MP4 and decoded pixel comparisons
  of Breathe IN/OUT plus intact following scene.
- All existing native tests (including W4 Fade, Pan, Drift, Rise, FullHD,
  120 distinct images, audio/SRT, cancellation, native RSS) retain PASS.
- Exact-head Windows full regression + native FFmpeg workflow must PASS
  before closure.

Not claimed: Pop/Stomp/Tumble/Tectonic, arbitrary scale keyframes,
combined effects, true cross-dissolves/overlaps, animation parity in
general, production release readiness or portable output.
