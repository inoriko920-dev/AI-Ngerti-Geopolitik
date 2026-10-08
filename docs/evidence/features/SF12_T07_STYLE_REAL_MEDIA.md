# SF12-T07 — Subtitle, Narration, Sharpen and Quality Binding

**Date:** 8 October 2026 WIB  
**Result:** **PASS_REAL_MEDIA_STYLES / PRODUCT_RENDER_DISABLED**  
**Accepted CODE SHA:** `79b24e93d4574cff0fc8a1650a6bd569e7640965`  
**Windows Actions:** [37741355411](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37741355411) **SUCCESS**  
**Draft:** [PR #8](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/pull/8), stacked on T06 #7 and earlier T05–T01/planning PRs. Not merged into `main`.

## Evidence table — six exact real-media cells

Source-owned synthetic 1080p30 project, two seconds / **60 frames**, one subtitle cue **[15,55)**, generated 440 Hz WAV narration starting at **frame 15**. External Chocolatey FFmpeg/FFprobe on Windows runner; each published file has exactly one **H.264 1920×1080/30** video stream, exactly one **AAC** audio stream, 60 frames and ~2.00-second MP4 container. W5 canonical subtitle/narration plans are reused, not reimplemented.

| Style index | Subtitle policy | Quality name | Video preset | CRF | Sharpen filter | Output SHA-256 |
|---|---|---|---|---:|---|---|
| 0 | burn_in | high | ultrafast | 28 | null | `253ef5252b622d87339df0b696e21cd8c51a1863264d789babe53b7056151008` |
| 1 | off | high | ultrafast | 28 | null | `83b5c33adfe820d0fc129fe9342844486da551b62783adb37069f2092394cccd` |
| 2 | burn_in | youtube_clean | medium | 21 | null | `c86a8debb7ffb098ad86e32decbe6c45f19ea38c936f58564408f618aa4ddb91` |
| 3 | burn_in | documentary_crisp | slow | 18 | null | `45036c9e492e0acdc0f659eb1ea0d58439bc2d536f37ab442251d24ae29994b6` |
| 4 | burn_in | high | ultrafast | 28 | unsharp=5:5:0.6:3:3:0.0 | `c9035f1edd75a56166cb903943e4742aacb8576712762a32aa9731c176c5e84e` |
| 5 | burn_in | high | ultrafast | 28 | unsharp=5:5:1.2:3:3:0.0 | `3636e8d49a42dddf2713fb1be8015bc9c5faa28ee66de68fb0b121db637af4d2` |

Visual and audio proofs from `t07_style_evidence.json`:

- **Subtitle burn-in/on vs OFF:** mean absolute gray pixel difference of **1.1399** at the active subtitle frame. Turning subtitles off makes a read-only derived state with `enabled=False`; the original project and subtitle data remain unchanged.
- **Sharpen LIGHT vs original:** mean absolute gray pixel difference **0.6486**. **Sharpen CRISP vs original:** **1.0716**. Each is a measured pixel alteration, **not** proof that perceived image quality improves.
- **Narration AAC mix:** reference with no narration was rendered independently from a derived `narration=None` state. The mean sample difference relative to that control was **4.2776** in the period before frame 15, versus **2399.3156** while narration is active; this supports proper late-start mixing. These are integer PCM amplitude differences, not dB or a formal listening test.
- Quality preset / CRF choices are exact FFmpeg `-preset`/`-crf` arguments verified by unit tests. Each output has a different SHA; size differences or labels are **not** a perceptual ranking guarantee.
- Video source digest **`a19bf794db3d8c519caffe4bf2ea29799756986dea8c9c4c4eb7dd78ee4b2ec5`**, synthetic narration digest **`ecf689d9e9d63b52cb09312be8bf67637c49edd6da256b65aee4b14cc8c46a8b`**. Both unchanged after all renders.

## Architecture / regression acceptance

- `application/export_style_policy.py`: six strict style candidate tuples. No free-form sharpen or quality matrix and no implicit permission for other combinations.
- `application/export_preflight.py`: explicit `style_candidate` only for the separate T07 adapter; default paths still fail closed for unsupported options. `can_start_render=False` is preserved.
- `infrastructure/ffmpeg_export_style.py`: additive synchronous style qualification, W5 narration/subtitle reuse, secure source copy-on-write for subtitle-OFF; post-encode FFprobe, re-preflight, same-volume unique staging, atomic no-clobber output. No `MediaEnginePort` signature change or UI wiring. User project state/assets never modified.
- Negative unit tests include six mapped variants, missing/unsupported combos, default preflight deny, wrong audio codec, wrong frame count, both-stage failures, pre-cancel, existing output protection, repeat invocation and no temp leaks.
- All targeted T07 and **full repository pytest PASS**; Ruff formatting/lint, mypy **94 source files** PASS, lint-imports, architecture, no secrets, **70/70 source-of-truth** and **42/42 frozen UI reference SHA-256** PASS.

## Reproducibility and limitations

- Run **37741355411** same CODE SHA SUCCESS. Artifact **ANG-SF12-T07-Style-RealMedia**, GitHub artifact ID **11533749234**, size **15,296,055 bytes**; ZIP SHA256 `894f7381105616d68ba27d64748713fd876127bf806ba1f4727824ff96d3c6ec` (14-day retention).
- This is a synchronous external FFmpeg *qualification* path, not the frozen production engine, a packaged Windows build, or a wired Qt render operation. **Product GUI render remains DISABLED** until T08/T09/T10. Six variants qualify individually, **not their arbitrary permutations**.
- Audio OFF, separate SRT/sidecar, arbitrary slider percentages, 4K style combinations, H.265 style combinations and non-allowlisted permutations are still blocked. Long-duration resource usage, physical microphone W5 and Gemini W6/W7 live network proof remain provisional.
- **Exact next serial task upon user's next `lanjutkan`: SF12-T08 Nonblocking Render Job Lifecycle.** Use worker-bound immutable request/session/revision, cancellation/timeout/progress and Qt close-lifecycle guard. Do not enable UI render or claim shipped capability without T09/T10 verification; preserve frozen UI-001..042 and avoid breaking MediaEnginePort/ASTRA ADR dependencies.
