# SF12-T04 — H.264 + AAC Baseline Export, Actual Windows Media

**Date:** 8 October 2026 (WIB)  
**Status:** **PASS_REAL_MEDIA_BASELINE_WITH_PROVISIONAL_PRODUCTION_GATE**  
**Accepted implementation SHA:** `96cf5a46ecfeea6cdb9ff767414a6dde828a2a42`  
**Windows GitHub Actions:** [37737863469](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37737863469) **SUCCESS**  
**Draft review:** [PR #5](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/pull/5), stacked on T03 #4 → T02 #3 → T01 #2 → planning #1. No merge to main.

## Implemented and bounded

- Extended existing FFmpeg qualification adapter `FfmpegSliceMediaEngine` with an **additive** `export_h264_baseline` entrypoint. The frozen `MediaEnginePort.export(state, path, cancellation)` signature, original legacy export behavior, `ProjectState`, AAVC and frozen UI 001–042 were not changed.
- Consumes T02 typed ExportRequest and T03 preflight. Only **FULL, H.264, 1920×1080, 30fps, HIGH, AAC, no sharpen** profile qualified; H.265, 1440p, 4K, 60fps and selection remain blocked.
- Invokes the established FFmpeg renderer in a unique same-volume staging directory, then uses real FFprobe to inspect an actual MP4 and reject empty or mismatched video/audio codecs, dimensions, FPS and duration. T09 still owns comprehensive full-matrix postflight and safe user-facing diagnostics.
- Rechecks preflight after render, including referenced media fingerprint and output collision. Uses **atomic hard-link create-if-absent** to publish without overwriting an existing file, including a tested last-moment competing-writer race. Workspace auto-cleans on failure, cancellation or success.
- This is a **synchronous qualification entrypoint for worker use**, not a Qt-thread dispatch path. GUI render deliberately remains disabled pending T08 worker lifecycle and T09 output verification.

## Real Windows output evidence

- **Run 37737863469 = SUCCESS**, implementation SHA `96cf5a46ecfeea6cdb9ff767414a6dde828a2a42`.
- Source-owned synthetic MP4 built with existing `scripts/generate_step10_fixture.py` on runner using **external Chocolatey FFmpeg/FFprobe**. No copyrighted external sample, paid account or secret used; no FFmpeg bundle added to repository.
- Independent FFprobe confirmed video **H.264**, audio **AAC**, **1920×1080**, **30/1 fps**, **1.000000 seconds**, **30 project frames**.
- Source input SHA-256 remained unchanged: `a19bf794db3d8c519caffe4bf2ea29799756986dea8c9c4c4eb7dd78ee4b2ec5`.
- MP4 final SHA-256: `fcd8f698188f5e92cf10b0b94d5cf4e8602fc53d1bbcd233cfa9523788bc32c0`.
- Tested negatives: existing output rejected, source output collision rejected, pre-cancelled request rejected without artifact, fake renderer failure/cancellation clean up, bad codec/audio/FPS rejected, unqualified profile rejected, and last-moment file-creation race preserves competing writer.
- All targeted SF12-T04 tests and **full Python pytest suite PASS**; Ruff format/check, mypy **90 source files**, import architecture, source-of-truth **70/70**, secrets and frozen UI image manifest **42/42** PASS.
- Artifact **ANG-SF12-T04-H264-RealMedia**, GitHub artifact ID **11531514655** (size **1,194,636 bytes**). Workflow artifact ZIP SHA-256 `695a450672aee1962a42b961d0eccfcf8dd55f017e3d20264a6657a4ee3363e3`. Artifact retention configured **14 days**.

## Safety/limitations and next gate

- No claim that the old direct `MediaEnginePort.export` path is production safe: the new qualified entrypoint is separate. No GUI render button was activated; no final portable Windows release created.
- A real single-cell H.264 1080p30 + AAC render is **not** proof of selected-range, H.265, 1440p/4K/60fps, subtitle alternatives, user-selected CRF/preset, threaded progress, or comprehensive T09 postflight. Native engine/licensing/distribution remains provisional. W5 physical mic and W6/W7 live Gemini remain provisional.
- Hard-link publication is intentionally fail-closed on unsupported filesystems; T10 packaging/Windows target validation must decide any later fallback without weakening no-clobber guarantees.
- **Exact next serial task on the owner's next `lanjutkan`: SF12-T05 — Full/Selected Timeline Range Mapping**, with narration/subtitle offsets, trim edge cases and tested frame-accurate media. Do not implement T06+ in the same turn or change frozen engine interface/native dependency without ASTRA/ADR approval.
