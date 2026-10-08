# INT-01K — Approved Pilot A external FFmpeg / FFprobe

Date: 2026-10-09 WIB

## User authorization
Owner explicitly approved executing external FFmpeg, generating real H.264
MP4, and testing on development branch AI-Ngerti-Geopolitik. Merging into main
requires separate explicit permission. Windows portable is last, after PASS.

## Scope
- One 2-second **synthetic** image-only scene, 60 frames at 30 FPS, 128x72.
- Exact DOCX + PNG asset canonical timeline -> real bounded PNG sequence ->
  RGB24 stream -> external FFmpeg libx264 -> staged MP4 -> FFprobe and
  full decoded-frame verification -> atomic exclusive publication.
- FFmpeg/FFprobe executables are absolute, SHA-256 pinned at invocation.
- A dedicated RGB24 writer thread is supervised for timeouts, cancellation
  and encoder termination; stdout/stderr go to DEVNULL to prevent pipe
  deadlock and private source output logging.
- FFprobe metadata capture uses temporary file rather than pipe, bounded
  to 128 KiB; codec h264, yuv420p, frame count, FPS, geometry, duration and
  successful decoding are all validated before any publication.
- Publish is exclusive new-file-only via same-volume hardlink. Existing MP4
  must never be overwritten. Temporary output is removed on failed gate.
- Negative tests check wrong binary SHA, prestart cancel, destination collision.
- Dedicated Windows CI produces an actual MP4 artifact and matching SHA256.txt.

## Boundaries
The external process is not yet integrated with GUI Export. Full process-tree
containment, codec bundling and distribution licensing, audio, subtitles,
effects, transitions, generic media export and Windows portable/release are
not covered. The pilot uses a worker thread and cooperative cancellation;
OS termination is expected to unblock writes, but this is not a general
Windows job-object solution. Keep PR #20 Draft and main unchanged.

## Qualification
PASS only when exact-head dedicated Windows FFmpeg job creates and probes a
real MP4 and the main Windows QA workflow passes. A plan/DRY RUN is not PASS.
