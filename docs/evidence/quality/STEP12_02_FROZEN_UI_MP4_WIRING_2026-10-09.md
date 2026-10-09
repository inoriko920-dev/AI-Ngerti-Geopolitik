# STEP 12-02 — Native H264 into the approved frozen UI-042 Export dialog

Date: 2026-10-09 WIB
PR #20 Draft. Owner-approved FFmpeg Pilot A only. No main merge or portable.

## Delivered
- Frozen export dialog sends all actual user-selected fields. Initial visual
  structure, order, styles, object names and defaults are unchanged.
- Strict application-level gate rejects any non-H264 format, non-default
  quality/preset/sharpen, subtitle burn-in, project narration/SRT, media
  other than image HOLD, output resolutions other than canonical geometry,
  mismatched frame rate, invalid names, missing directories, linked
  directories and existing output filenames.
- Production controller queues a read-only snapshot in a dedicated worker.
  FFmpeg/FFprobe must exist, be canonical absolute executables and match
  SHA-256 fingerprints; native execution stays scoped to explicit
  ANG_PILOT_A_FFMPEG=1 development builds.
- Worker creates all PNG batches from canonical project, streams RGB24,
  verifies the staged H264 MP4, publishes an exclusive output filename,
  deletes temporary frames, and reports only verified completion.
- Cancellation is consulted at every frame and every batch as well as
  before encoder launch and before native MP4 publication. Shutdown and
  project switch invalidate the worker token and signal cancellation.
- Rejections are reported on the existing dialog's window title/status
  without adding or moving any UI elements.
- The source project is not mutated.

## Gates
- Pure settings validator; Qt click-to-intent and worker routing regressions.
- Windows Ruff/mypy, Qt, full pytest, 42 frozen UI SHA checks.
- A separate Windows FFmpeg job must actually create and verify native MP4.
- No silent claim of H265, narration, subtitle burn-in, effects, rendering
  arbitrary video clips, long-project proof, codec redistribution, or
  portable build.
