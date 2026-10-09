# STEP 12-04C — W4 Pan motion, read-only image editor and real FFmpeg H264

Date: 2026-10-09 WIB. PR #20 Draft, unmerged. Portable prohibited.

## Narrowly scoped real effect
- Canonical W4 ClipProperties.effects enter_effect and/or exit_effect "Pan" with
  intensity_percent=100 only, no other modified clip properties and no fade
  transition/effect in combination.
- Frame-exact 0.25 second enter or exit window (or half clip duration).
- Overscan source decode by 12% and crop horizontally from left to center
  to right. The canonical source image and project are not modified.
- Only one active V1 HOLD image may animate; multiple parallel image lanes,
  other W4 effects and contradictory transitions fail closed.
- Existing W4 Fade and fade_black behavior is preserved.
- Preview, PNG frame sequence, and FFmpeg H264 share the same pixel renderer.
- Qt unit tests compare pan frame pixels and deny unsupported combinations.
- Real Windows FFmpeg native test verifies genuine decoded MP4 frame-to-frame
  differences from a source gradient and requires real SHA256 artifact output.
- Approved frozen UI remains structurally unchanged (42 image hashes).

## Limits and next
This proves a deliberately narrow W4 Pan effect, NOT all Pan/Drift presets,
full freehand keyframes, zoom, crossfade/overlap, arbitrary per-image
transformations, or large photo corpora. No merge and no portable without
separate explicit user authorization and all subsequent PASS gates.
