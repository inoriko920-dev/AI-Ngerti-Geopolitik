# INT-01J — Pilot A production-MP4 readiness decision

Date: 2026-10-09 WIB
Repository: inoriko920-dev/AI-Ngerti-Geopolitik
PR: #20 (Draft, base main), reviewed HEAD: `c8f9e736e7930bd406569d5f4eec050641c791d9`
Gate outcome: **NO-GO for production native execution until owner's explicit Pilot A D1 permission**

## Confirmed working image-only path

- Scene import: DOCX + Axxx scene PNGs + timeline duration TXT.
- Canonical .angproj save, static SINGLE/DOUBLE preview, and complete PNG
  timeline export in bounded batches.
- INT-01C: manifest, SHA-256, continuous numbering and original image integrity.
- INT-01D and INT-01I: strict H.264 target preflight and verified silent
  rawvideo RGB24 FFmpeg argument suffix, 30/60 FPS, even dimensions,
  <=8192 pixels per axis, <=16 million pixels, <=128 MiB encoded PNG/frame.
- INT-01E: real CPU Qt PNG-to-tightly-packed RGB24 scanline generator.
- INT-01F/G/H: short-write aware bounded synthetic sink, checksum/progress
  receipt, cooperative cancellation/deadline, staged publish/discard and
  immediate pre-publication gate, with Windows regression.
- None of these creates a playable MP4 or authorizes real native subprocess
  execution.

## Reuse rather than rebuild

### Existing legacy media engine is NOT the scene-image MP4 solution

`src/ai_ngerti_geopolitik/infrastructure/ffmpeg_slice.py` contains an older
real FFmpeg video/audio adapter for contiguous video clips with audio.
Its `_video_clips()` expects source video clips with audio, not the
canonical still image HOLD timeline in PR #20. Direct substitution would
reject the image-only project.

Existing safety gaps in that legacy path (inspection only, not executed):
1. `FfmpegProcessRunner.run()` creates stdout and stderr pipes but polls
   for process exit before draining either. If an external child fills a pipe,
   it can block while the parent continues polling indefinitely.
   There is no general deadline for an uncancelled process.
2. `FfprobeMediaProbe.raw_probe()` calls `subprocess.run(capture_output=True)`
   without `timeout` or output-size cap. It can wait without a bound
   or retain excessive untrusted output.
3. Therefore, DO NOT connect the old runner directly to this new image
   export pipeline and do not treat its presence as an approved Pilot A.

### Reusable process-safety preparation exists elsewhere

PR #19, currently Draft and unmerged, contains fixed-Python-fixture-only
subprocess tests for bounded stdout/stderr, timeout, cancellation,
command-shape validation, redaction and child-lifecycle handling. This is
useful implementation evidence, but does **not** authorize arbitrary
executables, FFmpeg, FFprobe, Windows process-tree enforcement, or licensing.
Its branch is stacked on earlier Draft work; integration must respect
branch dependencies and must not blindly merge the PR stack.

## Pilot A D1 entry gate (requires owner's explicit grant)

Owner must explicitly authorize a constrained external FFmpeg/FFprobe Pilot A.
Generic `lanjutkan` is not such authorization under current project policy.
Scope of later first pilot should be one short, synthetic image-only scene
project (no private footage and no user credentials). Execution must be on
a dedicated branch, never `main`.

Pilot A should only be considered PASS with all of:
- Immutable, approved FFmpeg/FFprobe executable identities and absolute
  trusted paths; version/codec availability probes with bounded output.
- A single owner-controlled native process runner with `shell=False`,
  bounded stderr/stdout, monotonic deadlines, cancellation, process-tree
  cleanup, no private-path leakage and no unbounded blocking pipe.
- Verified INT-01I image frames, RGB24 frame order and exact fps/geometry.
- New-file-only staged destination, secure cleanup, no overwrite of an
  existing MP4 on failure and no premature publish.
- Real postflight on the newly generated MP4: H.264 video, yuv420p,
  exact width/height, frame count, rational duration, decoded playback.
- A negative matrix: invalid input, stale PNG, missing FFmpeg, codec
  missing, child stall, stderr flood, forced cancel, disk full, corrupt
  output, destination collision and Windows Suspend/Resume as applicable.
- Same-HEAD Windows CI PASS, manual playback evidence and review before
  considering any later merge.

## Strictly not yet delivered

Production H.264 MP4 export, audio synchronization, subtitles, effects,
transitions, general-purpose GUI Export parity, Windows portable package,
distribution/license decision for native codecs, and release validation.

## Handoff

**Do not add more mock/native-pretend PRs.** Once permission is granted,
use the already-reviewed RGB24 stream and process-qualification work as
inputs to a narrowly scoped real encoder Pilot A. Preserve frozen 42 UI
references; seek explicit approval for UI changes and for merging to main.
Windows portable distribution remains the final project milestone.
