# STEP12-03F — 120 distinct media files, Windows RSS and fail-closed storage

Date: 2026-10-09 WIB. PR #20 Draft. No main merge or portable.

- Independently generate 120 PNG files at 64x48; require 120 distinct SHA-256 digests and unique canonical Asset + Clip IDs (no source alias/reuse).
- Run actual 30 FPS (3-frame holds) and 60 FPS (4-frame holds) synthetic image timelines through verified complete-frame export, RGB24 native FFmpeg, and ffprobe/decoded MP4.
- Verify 120 scene center pixels one by one against distinct source colors with <=25-channel H264 tolerance; assert exact number of frames, FPS, duration, SHA-256, size, no staging remnants.
- Sample Windows process working-set with Win32 GetProcessMemoryInfo during export, including Python UI render process plus tracked FFmpeg/FFprobe children. Enforce a generous <1 GiB sampled combined ceiling and print actual MiB. This is a sampling metric, not a hard peak guarantee or 1080p/4K capacity proof.
- Inject ENOSPC on third frame-batch manifest write (after frames already created): require no published MP4 and all intermediate files removed.
- Delete the tenth distinct input PNG during frame processing and require fail-closed export and complete cleanup.
- Repair duplicated cancellation check in batch publisher and add missing cancellation check immediately before atomic complete-project manifest publication.
- Preserve full Windows regression and 42 frozen UI hashes, current native A/V test suite, and no merge/portable rules.

This is still synthetic 128x72 with 120 genuinely distinct assets; separate future work covers full-resolution RAM/disk quotas, varied real photography and user datasets, safe Windows process-tree containment, image effects and animated subtitle/scene transitions.
