# SF12-T09 — Independent Output Postflight & No-Clobber Publish

**Date:** 2026-10-08 WIB  
**Gate:** **PASS_STRICT_REAL_MEDIA_POSTFLIGHT / PRODUCT_GUI_RENDER_DISABLED**  
**Accepted implementation SHA:** `270fe789834354a7e2adb38fc5859023db93f547`  
**Windows GitHub Actions:** [37744843294](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37744843294) — **SUCCESS**  
**Draft PR:** [#10](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/pull/10) stacked on T08 #9 → T07 #8 → T06 #7 → T05 #6 → T04 #5 → T03 #4 → T02 #3 → T01 #2 → planning #1; **none merged into main**.

## Production-safety change

Previously the T08 worker could set READY after a nonempty file and a cooperative export adapter result. This was **not** independent MP4 qualification. T09 closes that loophole:

1. `application/export_postflight.py`: typed `PostflightCode`, redacted `ExportPostflightError`, mandatory `ExportPostflightPort` and immutable `PostflightReceipt`. Receipt SHA-256 is computed once in the worker, with captured size/mtime/inode/device and required frames; missing/nonregular files and mutation during receipt creation fail closed.
2. `infrastructure/export_postflight.py`: independent FFprobe raw metadata checking (MP4 container, exactly one video and one AAC audio stream, H264 vs HEVC matching requested codec, exact resolution/FPS and nb_frames, requested duration tolerance, adapter ExportResult identity), followed by a complete separate **FFmpeg decoding pass of both video and audio**, requiring successful decoder completion and exact independently decoded frame counter. Codec/stream metadata alone is not accepted.
3. `application/export_jobs.py`: mandatory postflight injected into job service. Worker has `POSTFLIGHT_VERIFYING` phase. **READY requires a successful verified receipt** and no stale/cancel/timeout condition. Owner-thread `accept` must revalidate session/revision/semantic identity, receipt's cheap immutable stat identity, and atomic no-overwrite destination publication. Malformed, corrupted, wrong-codec, out-of-range or altered staging can never be deliberately promoted to READY/SUCCESS by a passing nonempty-size check.
4. `infrastructure/export_job_adapters.py`: actual CI discovered and fixed a **T08 bug**: H265 1080p30 was incorrectly treated as plain H264 baseline because `plain` did not constrain `codec`. The H264 baseline predicate now explicitly demands H264; H265 routes to the qualified HEVC matrix exporter. All other unqualified combinations remain rejected.
5. Existing W8 and T08 cancellation, timeout, stale-session, close, privacy, and atomic no-clobber invariants continue; no changes to frozen `MediaEnginePort`, ProjectState, AAVC or UI-001..042. Failures expose only stable codes, never tool stderr or private file paths.

## Actual Windows independent qualification

Native FFmpeg/FFprobe installed externally in the GitHub Windows runner (not shipped or licensed as part of a portable binary). Owned synthetic source, 1080p30, 15-frame/0.5s project; exact immutable project/source hashes checked. Five concrete output profiles independently decoded **in full** before owner approval:

| Output | FFprobe codec | Decoded/expected frames | Output SHA-256 |
|---|---|---:|---|
| H264 full, 1080p30 | h264 | 15 | `26972e24078169c3ad11b15e3ca978241ff417121427517ad1db9c531283c201` |
| H264 selection [5,10), 1080p30 | h264 | 5 | `ca917e15909d9d944c2ab5bf42bd29fb4005278e25951d96be0801c61dfdc36c` |
| H264 4K30 (upscaled 1080p source) | h264 | 15 | `3b09379103af819f866251f8a774af776a8bc7d42616605992c8c1fad6cd3ce4` |
| H264 1080p60 (FPS converted from 30) | h264 | 30 | `b3d245ef0da6723fbfd5ee8c9943c92d9acfdc1d6dcb55a4dce1ec1f909e14e5` |
| H265/HEVC 1080p30 | hevc | 15 | `3e215b51afa73def3bb4a8453e4fa49af3a5d287ff06b31c653ef261cec96b1c` |

All five contain actual AAC; after decoder and metadata verification the worker reports READY with no final file. Explicit owner-thread acceptance publishes atomically via same-volume hard link. Destination existing/output collision still fails closed. Source SHA-256 remained `a19bf794db3d8c519caffe4bf2ea29799756986dea8c9c4c4eb7dd78ee4b2ec5`.

**Real corruption proof:** a copy of the full MP4 was truncated to 50% of its bytes. A probe alone might succeed because faststart metadata remains intact; the independent whole-stream decode **rejected it** as `POSTFLIGHT_DECODE_FAILED`, and no corrupt test file was published.

## Test and artifact gate

- Windows run `37744843294` at accepted source SHA **SUCCESS**. T09 and preserved T08 targeted unit and Qt tests + complete repository pytest **PASS**.
- Ruff format/lint, mypy **98 source files**, import-lint architecture contracts, app architecture verifier, secret verifier, **70/70 source-of-truth** checks and **42/42 frozen UI manifest hashes** **PASS**.
- Negative tests: wrong MP4 container, absent/extra audio/video/subtitle streams, H264/HEVC mismatch, wrong AAC, resolution, FPS, reported frame count, duration; forged export results; missing/empty file; full decode failed or count mismatch; selection [start,end) half-open; tampered stage after valid receipt; no leak of private paths; no READY and no final output on failure.
- Actual five MP4s + `t09_postflight_evidence.json` preserved in artifact **ANG-SF12-T09-StrictPostflight-RealMedia**, GitHub artifact ID **11535670942**, size **2,832,790 bytes**, upload ZIP SHA256 `b3eb5855e55de908ed9f25cb65dae56231bb970ce46c11ee6bc0afdf23a47c48` (14-day retention).

## Boundaries and handoff

- GUI **render button still intentionally DISABLED**. Postflight is an engine/worker qualification and does not automatically wire the frozen Qt export dialog or authorize app release.
- SHA256 is calculated on the background thread; `accept` uses stat identity for fast owner-thread TOCTOU protection rather than an O(file size) rehash. It does not rule out adversarial same-size/time/inode tampering. Native-code cancellation latency, 4K long-form decoding cost, FFmpeg native redistribution/license choice, Windows portable packaging and E2E frozen UI must be evaluated in T10.
- Only the five tested cells here have combined full-decode Windows evidence; earlier T04–T07 tests separately cover additional cases, not arbitrary mixtures. Sharpen/subtitle visual quality cannot be fully inferred from MP4 metadata; T07's separate golden image/audio proof remains necessary. Native libopenshot primary candidate decision stays unchanged.
- **Exact next serial task:** **SF12-T10 — Windows packaged E2E, frozen UI regression, release/engine dependency and licensing qualification.** Do not enable render controls, claim a portable binary, or merge/release without the T10/ASTRA/ADR gates. Next task only after explicit user `lanjutkan`.
