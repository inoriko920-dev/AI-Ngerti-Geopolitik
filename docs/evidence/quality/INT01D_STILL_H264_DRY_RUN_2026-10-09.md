# INT-01D — Offline H.264 encode plan for existing still-image frames

Date: 2026-10-09 WIB
Scope: Draft PR #20, strictly NO native process, NO MP4 output, NO UI change.

## Motivation
INT-01C verifies full PNG batches and their SHA-256 chain against one canonical
image-only ProjectState. The project has distinct SF12 native-video export
workstreams and INT-01B process safety qualifications; neither is an approved
still-image FFmpeg encoder for this scene workflow.

## Implemented offline handoff
- An immutable SilentH264Plan comes only from verified, ordered PNG frames and
  a checked absolute, previously unoccupied .mp4 destination OUTSIDE the
  source frame directory.
- Existing output files, symlinked/junction parents, relative paths, unsafe
  Windows names and path extensions other than .mp4 are rejected without writes.
- 30 or 60 FPS and even 2+ pixel width/height (YUV420p) are required;
  no silent crop, resample or padding of odd-size images.
- Future rawvideo pipe contract is packed RGB24, exact WxH and frame rate,
  one exact input image per source timeline frame, H.264/libx264 yuv420p,
  preset medium, CRF 18, no audio/subtitles/data, -n never overwrite and
  explicit -frames:v frame limit.
- No executable is chosen; no subprocess is started; no output path is
  written or touched. FFmpeg availability, codec support and license are
  UNVERIFIED. The argv suffix is not a production-ready command.
- CLI: \`uv run python scripts/verify_still_frames.py --project film.angproj --frames frames --plan-mp4 C:\video\final.mp4\`.
  This emits an offline summary only; it never creates video.

## Tests
\`tests/unit/test_still_h264_plan.py\`: exact frame order, rational duration,
raw byte count and argv shape; repeated caller CLI non-execution;
existing output protection; nested/relative path refusal;
odd-width YUV420p rejection; source mutation and missing frame fail closed.

Same-HEAD Windows gate: full pytest, targeted new tests, Ruff, mypy,
lint-imports, architecture/security, 42 frozen UI references.

## Known NOT implemented
- Actual per-frame PNG->RGB24 conversion and bounded streaming
- External FFmpeg executable selection / identity / Pilot A D1 authorization
- Native capability/codec probing, ffmpeg process lifecycle, cancellation
- Media output postflight (H.264 codec, frame count, duration, playback)
- Soundtrack/mixed audio, subtitle render, effects/transitions, integrated Export
- File staging and atomic publication of real MP4
- Final portable Windows build

The next milestone should start only after owner authorization of Pilot A,
then reverify sources at execution time, stream bounded frames and stage output
to a new temporary target before postflight and final publication.
Do not merge Draft PR #20 without owner's explicit approval.
