# STEP 12-04G — W4 Pop animated still image → real H264

Date: 2026-10-09 WIB. Approved Pilot A FFmpeg. PR #20 Draft, no merge or portable.

## Implementation
- Qualify W4 Pop IN and/or OUT at intensity 100% on one still HOLD V1 clip.
- Scale 0.85 → 1.00 over min(0.25s, half clip) and reverse on exit.
- Render a verified 120%-sized image source with center crop varying to
  ceil(canvas / scale) pixels. Canvas remains completely covered, so no
  transparent/black border appears. This is crop-based image scale, not
  arbitrary affine keyframes or a revealed canvas backdrop.
- Same frame function feeds Qt Preview, complete PNG frame sequence,
  RGB24 and real external FFmpeg H264 MP4.
- Strictly reject Pop+Fade/Pan/Rise/Drift/Breathe, fade_black+Pop, simultaneous
  second image lane or modified non-effect video/color properties.
- Frozen UI reference images and existing controls remain unchanged.

## Windows proof
- Unit/Qt: assert scale values at frame offsets, visible RGB movement,
  opaque frame corners and fail-closed combinations.
- Native: real encoded H264 with Pop IN/OUT at 256x144, decode and measure
  changing nonuniform pixels, verify following scene unmodified.
- Existing 36/36 native tests, real FullHD/120-media, WAV/MP3/SRT,
  shutdown/deadline and 42 frozen UI hashes must continue to PASS.
- Close STEP 12-04G only after both latest-head Windows CI workflows SUCCESS.

## Limits
No Stomp/Tumble/Tectonic, compound keyframes, simultaneous multiple still
Pop effects, actual alpha-composited background scale, mixed video clips,
Windows job object isolation, complete GUI manual QA or release readiness.
