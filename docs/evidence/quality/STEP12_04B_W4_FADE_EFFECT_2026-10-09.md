# STEP 12-04B — Real W4 Fade IN/OUT effect in still-image MP4

Date: 2026-10-09 WIB. Owner-authorized Pilot A development only.
PR #20 Draft. No main merge or Windows portable.

## Added
- Qualifies canonical `ClipProperties.effects.enter_effect/exit_effect = Fade`
  on one V1 image HOLD lane, independently or in both directions.
- Effect envelope uses existing W4 FFmpeg creative plan's
  min(0.25 seconds, half clip duration) enter/exit windows; evaluated at
  exact integer timeline frames, not a placeholder/still.
- Default effects intensity 100 only; non-default video transforms,
  color, titles, audio, other W4 effects, modified intensity or
  Fade combined with fade_black transition are not silently ignored.
- Maintains all old fade-through-black support, old method-name alias,
  and legacy unmodified SINGLE/DOUBLE frame composition.
- Existing UI-042 remains structurally unchanged. Export intent preflight
  applies the single-V1-only guard to effects as well as transitions.
- Native FFmpeg Windows integration test encodes the W4 Fade enter/exit
  property from a real saved canonical project to H.264 MP4, decodes
  every frame, checks beginning black, mid-video red, exit dimming,
  and other-scene frame, and exports the MP4 plus SHA256.

## Tests and limitations
Require exact-head general Windows CI and real FFmpeg Pilot A workflow PASS.
No Pop, Breathe, Pan, Drift, Tumble, Rise or 21 Canva-style motion effects
supported by this still adapter yet, and no overlapping dissolve/crossfade.
No assumed compatibility with MLT renderer or other video-media engines.
No release, no portable, no merge.
