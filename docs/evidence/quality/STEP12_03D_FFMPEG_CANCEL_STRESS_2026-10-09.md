# STEP 12-03D — Native A/V cancellation and many-scene stress proof

Date: 2026-10-09 WIB
PR #20 development branch only. No main merge, no Windows portable.

## Code
- Explicit native postcompose subprocess ownership using subprocess.Popen
  with shell=False, DEVNULL stdout/stderr and deadline-driven polling.
- Cooperative cancellation checked during the actual native FFmpeg execution,
  not only before/after; on cancel, timeout or nonzero exit the process is
  killed and reaped before temporary files are removed.
- Prepublication WAV/MP3 fingerprint and size are rechecked after FFmpeg
  finishes, protecting against changes during encoding.
- Final H264 postflight additionally checks exact canonical FPS.

## Native Windows acceptance
- Existing project regression suite, FFmpeg 17 tests and frozen UI 42 hashes.
- New 24-second 30fps image-HOLD project spanning 12 independently named
  scenes (720 video frames, batch size 75), one narration at 3 seconds,
  and three correctly timed Unicode subtitle cues; verify decoded PCM,
  FFprobe frame/duration/codec, decoded image-pixel cue windows and distinct
  scene boundaries.
- Real FFmpeg realtime input is explicitly interrupted by cancellation and
  timeout to verify child cleanup on Windows, without publishing output.
- No unsupported claims: no 100-300-scene production stress, concurrent
  real world source-edit races, Windows Job Objects/process-tree containment,
  complex typesetting, general codec distribution, release or portable.
