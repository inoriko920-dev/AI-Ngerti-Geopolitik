# SF12-T06 — Codec, Resolution & FPS Matrix: Real Windows Output

**Date:** 8 October 2026 WIB  
**Acceptance:** **PASS_FOUR_REAL_MEDIA_CELLS / PRODUCTION_UI_NOT_QUALIFIED**  
**Accepted CODE SHA:** `00761740666c66c8787aec4865d3e2184a13fe7d`  
**Windows CI:** [37740103975](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37740103975) — **SUCCESS**  
**Review:** [Draft PR #7](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/pull/7), stacked T06 → T05 #6 → T04 #5 → T03 #4 → T02 #3 → T01 #2 → planning #1. **Unmerged to main**.

## Proven four-cell matrix (0.5-second synthetic 1080p30 source; actual FFmpeg native encoders on Windows)

| Explicit profile | FFprobe codec | Dimensions | FPS | Video frames | Container duration | Output SHA-256 |
|---|---|---|---|---:|---:|---|
| H264 1440p30 | h264 / libx264 | 2560×1440 | 30/1 | 15 | 0.500000 s | `e392e37e2e37e68babf33b3b2312e5bde5c93d92c0965ed5770a6488dfad8c2b` |
| H264 4K30 | h264 / libx264 | 3840×2160 | 30/1 | 15 | 0.500000 s | `3b09379103af819f866251f8a774af776a8bc7d42616605992c8c1fad6cd3ce4` |
| H264 1080p60 | h264 / libx264 | 1920×1080 | 60/1 | 30 | 0.500000 s | `b3d245ef0da6723fbfd5ee8c9943c92d9acfdc1d6dcb55a4dce1ec1f909e14e5` |
| H265 1080p30 | hevc / libx265 | 1920×1080 | 30/1 | 15 | 0.500000 s | `3e215b51afa73def3bb4a8453e4fa49af3a5d287ff06b31c653ef261cec96b1c` |

Every cell has exactly one verified video stream and **one AAC audio stream**, MP4 container, correct rational FPS, expected frame count and duration. Independently inspected FFprobe logs are in workflow; per-cell `matrix_qualification.json` and actual MP4 files are preserved as GitHub artifact. Source-owned fixture SHA-256 **`a19bf794db3d8c519caffe4bf2ea29799756986dea8c9c4c4eb7dd78ee4b2ec5`**, unchanged after all conversions.

**Important interpretation:** 1440p and 4K output pixels are *upscaled from a 1080p intermediate*, not native UHD detail. 60fps output duplicates/interpolates cadence using FFmpeg `fps=60` on original 30fps; it is not extra captured temporal detail. These samples do not prove long-video performance, sync beyond stream structure, chroma/chapter metadata or compatibility on users' computers without external FFmpeg.

## Implementation and safety boundaries

- `application/export_profiles.py` defines only four explicit typed `MatrixProfile` *qualification candidates* keyed by codec/width/height/FPS; there is **no generic all-options wildcard**.
- `application/export_preflight.py` remains fail-closed. Unqualified codec/profile request is rejected unless a strictly matching explicit matrix candidate is passed from the T06 adapter. Real detected H265 encoder is mandatory for HEVC; existing base H264/1080p30 and T05 selection behavior are unchanged.
- `infrastructure/ffmpeg_export_profiles.py` adds a separate **synchronous qualification exporter**. It composes 1080p30 canonical timeline with existing FFmpeg qualification engine (W3/W4/W5), then transcodes to the requested matrix candidate in a temporary same-volume directory. Uses real FFprobe verification **before** atomic hardlink/no-clobber publish, and repeats media/output preflight after encoding. Cancellation/error removes temporary outputs. Source `ProjectState` never mutates.
- Native codec binaries used for this run were **Chocolatey-provided external FFmpeg/FFprobe** on GitHub Windows. No FFmpeg binary bundled or new MediaEnginePort signature. AAVC and frozen UI 001..042 unchanged. UI render button remains deliberately **DISABLED**; T08 worker and T09 full postflight and T10 packaged Windows qualification still required.
- H265 4K60, H265 1440p30, H264 4K60, other combinations, quality preset variants, sharpen or alternate subtitle/audio options remain **NOT QUALIFIED** and **not selectable via this adapter**. HEVC presence or a real HEVC 1080p30 file does not imply all HEVC permutations.
- Disk reserve and temporary full intermediate can be substantial for longer projects, including upscaled UHD. T10 must validate resource limits; T06 does not promise full-product performance or packaging/licensing readiness.

## Exact Windows CI evidence

- Same-code-HEAD run `37740103975` **SUCCESS**, SHA `00761740666c66c8787aec4865d3e2184a13fe7d`.
- **Ruff format/check PASS**, **mypy 92 source files PASS**, lint-imports, architecture boundaries, source-of-truth **70/70**, no secrets, frozen UI SHA manifest **42/42** PASS.
- Targeted T06 unit/negative tests and complete repository pytest PASS. Tests cover four exact allowlisted profiles, absence of H265 encoder, original T03 default rejection, unsupported H265 4K60, mismatched codec/frame count, FFmpeg failure on either pass, pre-cancellation and existing-output no overwrite. Prior T04 last-moment competing-writer regression is part of full suite.
- Windows source-owned generator, observed libx264/libx265/AAC encoders, four actual MP4 produces and independent FFprobe stream verification **PASS**.
- Artifact **`ANG-SF12-T06-CodecMatrix-RealMedia`**, GitHub artifact ID **11533866135**, size **2,739,991 bytes**. Wrapper ZIP SHA-256 `04fea1ca343b133cedb838fe3a4924d50763cc01a63c67e0292080155468d1fd`, retention 14 days.

## Next stage after explicit owner instruction

**SF12-T07 — Subtitle, Narration, Sharpen & Quality Binding ONLY.** Test actual on/off subtitle policies, narration AAC, sharpen before/after golden-pixel difference and quality CRF/preset behavior with honest fail-closed capability flags. No UI render activation, no STEP13/release, and no AAVC mutation. ASTRA/ADR needed for breaking port signature, native packaging/licensing decisions or frozen UI redesign.
