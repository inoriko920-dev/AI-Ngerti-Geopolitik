# STEP 12-03E — 120-scene Windows stress and bounded resources

Scope: 9 October 2026 WIB | AI-Ngerti-Geopolitik | PR #20 Draft

## Native real-video test
- Two synthetic canonical 120-clip projects:
  - 30 FPS / 600 frames / 20 seconds; pinned WAV narration starts at second 3
  - 60 FPS / 720 frames / 12 seconds; no narration
- Use verified source image assets with 120 unique timeline clip IDs,
  repeated alternating scene appearance and exact integer frame boundaries.
- Export through **real** Pilot A FFmpeg/FFprobe, not a fake renderer.
- Assert full frame count, H264 codec, exact FPS, expected video duration,
  SHA256 checksum, AAC audio track iff narration requested, source scene
  image pixel, output under 32 MiB, and no leftover temporary directories.
- Preserve the independent 24-second/12-scene subtitles and narration test,
  12-second VBR MP3/SRT test and native FFmpeg cancellation/reaping tests.
- Python `tracemalloc` peak <256 MiB is only a Python heap ceiling; it
  does NOT measure native Qt, FFmpeg subprocess working set, or global RSS.
  No claim of production RAM limit follows from this test.
- A cancellation callback that turns true well after frame staging begins
  must leave no final output, PNG batches or partial encoder artifacts.

## Further gates not covered
- 100-300 real unique media files or thousands of assets from users;
  sustained 1080p 60 FPS memory/RSS with desktop instrumentation;
  Windows Job Object process tree isolation;
  300-scene real editing UI responsiveness; portable/release.
- PR #20 stays Draft and unmerged. Do not build portable.
