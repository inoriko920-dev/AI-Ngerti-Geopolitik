# SF12-T10 — Packaged Windows UI / Media E2E and release boundary

**Date:** 2026-10-08 WIB  
**T10 technical subgate:** **PASS_PACKAGED_UI_AND_9_EXPORTED_MEDIA_CELLS**  
**Combined-product / distribution / release gate:** **BLOCKED — NOT A FINAL PORTABLE EDITOR**  
**Accepted code SHA:** `c945d9a4d0079c4b6c1ba40cd19a2326c03fa268`  
**Windows 3-job CI:** [37746307421](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37746307421) = **SUCCESS**, same implementation HEAD.
**Draft stacked PR:** [#11](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/pull/11), base T09 branch/PR #10; all earlier PRs #1–#10 still unmerged. `main` baseline `c9154eef85f8b475630816a7c63f5e2b52bf1523` unchanged.

## What T10 actually built — two pre-existing packaging models, NOT one combined editor

1. `scripts/package/build_step09_ui.ps1` → **PyInstaller --onedir --windowed** UI shell ZIP `AI-Ngerti-Geopolitik-UI-Shell-Windows-x64.zip`. The packaged executable launched successfully in QT_QPA_PLATFORM=offscreen mode and produced the exact marker `ANG_S09_UI_SMOKE_OK`. Existing frozen UI dialog tests, W8-010 Qt controller tests and the **42/42 reference SHA-256** manifest remained PASS. It does **not** expose enabled production rendering.
2. `scripts/package/build_step10_media_smoke.ps1` → pre-existing **PyInstaller --onedir --console** packaged CLI ZIP `AI-Ngerti-Geopolitik-S10-Media-Smoke-Windows-x64.zip`; original STEP10 real import/edit/save/preview/export smoke PASSED unchanged.
3. Extended the existing *qualification-only* CLI `step10_media_smoke_entry.py` with the opt-in `--sf12-t10` flag. The executable itself, **not the source Python interpreter**, generated nine MP4 outputs using the already implemented T02 typed requests/T03 preflight/T04–T07 qualified adapters/T08 off-thread job/T09 independent FFprobe + full decode/owner acceptance, from a deterministic source-owned Windows test fixture.
4. `scripts/package/smoke_sf12_t10_packaged.ps1` verifies the success token, 9 actual output files, typed JSON evidence, **no production Qt UI binding**, original package ZIP/exe checksum manifest, third-party notices presence and **NO ffmpeg.exe/ffprobe.exe/ffplay.exe/libx264/libx265 DLL bundled** in the packaged media folder. Actual encoders are installed via Chocolatey in the runner and stay outside the ZIP.
5. The media smoke packaging script now copies `THIRD_PARTY_NOTICES.md` and labels the extension as a nonproduction test; these notices are still a foundation scaffold and **NOT complete release compliance documentation**.

### Nine real packaged verified cells

| Real packaged CLI profile | Source → output | Scope |
|---|---|---|
| h264_1080p30 | H.264 / AAC 1920×1080 at 30fps | FULL |
| h264_selection | H.264 / AAC 1920×1080 at 30fps | selection frames [5,10) |
| h264_1440p30 | H.264 / AAC 2560×1440 at 30fps | FULL, 1080p upscale |
| h264_4k30 | H.264 / AAC 3840×2160 at 30fps | FULL, 1080p upscale |
| h264_1080p60 | H.264 / AAC 1920×1080 at 60fps | FULL, 30fps conversion |
| h265_1080p30 | H.265/HEVC / AAC 1920×1080 at 30fps | FULL |
| subtitle_off | H.264 / AAC 1920×1080 at 30fps | FULL, T07 typed subtitle OFF |
| quality_crisp | H.264 / AAC 1920×1080 at 30fps | FULL, Documentary Crisp quality |
| sharpen_light | H.264 / AAC 1920×1080 at 30fps | FULL, typed light unsharp |

Each requested cell was rendered to unique private staging, independently probed, decoded, verified, then explicitly committed; no output was published merely on task READY. Evidence includes per-cell SHA256, codec, resolution, rational FPS, decoded exact frame count, audio AAC and per-request owner acceptance. Original source and canonical project were not mutated. **Small 0.5s synthetic fixtures do not prove long-project performance, perceptual improvement, or all combinatorial presets.** The subtitle-off output has no active subtitle cues in T10 fixture, so T07's separate golden on/off visual tests remain the proof of subtitle appearance.

## CI evidence at accepted code commit

- GitHub Actions [37746307421](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37746307421), SHA `c945d9a4d0079c4b6c1ba40cd19a2326c03fa268`: **all three jobs SUCCESS**: source-gates, packaged-export, packaged-ui.
- Source-gates: `uv lock --check`, Ruff format/lint, mypy **98 source files** and lint-imports, architecture, no-secrets, source-of-truth **70/70**, frozen UI **42/42**, complete repository pytest + targeted export dialog, render worker Qt heartbeat and W8 UI runtime wiring tests all PASS.
- Packaged media job: Chocolatey external FFmpeg/FFprobe, `ffmpeg -version`, `-buildconf`, libx264/libx265/AAC availability recorded. Legacy STEP10 packaged smoke **PASS**, nine real T10 packaged exports **PASS**, no native executable packaging **PASS**, independent HEVC probe and zip SHA probe **PASS**.
- Packaged UI job: pre-existing UI shell `--onedir --windowed` created, launched successfully headlessly, marker **PASS**, SHA 42 reference files and export dialog/W8 Qt smoke PASS.
- Media artifact: **`ANG-SF12-T10-Packaged-Media-Qualification`** (ID `11535444050`, artifact size **23,898,019 bytes**), containing runnable *qualification CLI ZIP*, JSON proof + 9 verified MP4 outputs and external ffmpeg build flags; GitHub artifact ZIP hash `c8339aa6c4bcc41bbb141c9ba3e6c0b5ba3f087f92ae0ebaa73aa038948dc8cd`.
- UI artifact: **`ANG-SF12-T10-Frozen-UI-Shell-Qualification`** (ID `11535718409`, artifact size **51,924,491 bytes**), containing runnable *UI-only ZIP*, smoke marker and scope; artifact ZIP hash `fde2545a0e77350aaf2f1e509a86dce326d5b6bcaed078a7a8aeaac68bc70650`. Both retention **14 days**, GitHub artifacts are not user-facing final application releases.

## Unresolved mandatory release blockers — must NOT be silently waived

**P0 — No combined portable editor with functional export UI.** The product renders only via separately packaged qualification CLI requiring an installed FFmpeg; the separately packaged UI shell displays controls but **render remains disabled and not wired to T08/T09**. A user downloading just the UI ZIP cannot render. Binding the UI and merging distinct packages requires prior ASTRA planning/ADR, correct UI capability registry, native toolchain availability behavior, thread-affine Qt close semantics and a new real Windows smoke.

**P0 — Native licensing / redistribution / dependency plan not approved.** External FFmpeg on the CI runner had `libx264` and `libx265` active. FFmpeg's official legal documentation says using those GPL components changes the FFmpeg binary's applicable obligations: https://www.ffmpeg.org/legal.html and https://ffmpeg.org/doxygen/trunk/md_LICENSE.html. libopenshot primary engine candidate is LGPL-3.0 or separately commercially licensed: https://www.openshot.org/libopenshot/; its dependencies have separate terms. This step **bundles no external FFmpeg/ffprobe executable**, chooses no new production engine, and does not assert that using an external executable automatically settles every compliance/redistribution issue. `THIRD_PARTY_NOTICES.md` is explicitly an incomplete foundation notice; repository contains no top-level LICENSE, so project distribution licensing must be formally decided. Native dependency/LICENSE, notices, possible GPL obligations, codec patents and PySide6/CPython/PyInstaller packaging notices need formal ASTRA + owner review before end-user release.

**P1 — No all-workflow same-HEAD 27/27 closure.** T10 executes the explicit three-job workflow and full Python suite, not a complete redispatch of the historical 27 workflow families on this exact feature HEAD. Claiming 27/27 same-HEAD would be false. A final integration/release gate should cover them, and test on actual Windows 11 machines outside the GitHub VM.

**P1 — Additional product qualification incomplete.** W5 physical microphone and W6/W7 live Gemini still provisional; full native libopenshot engine binding not adopted; resource/disk/cancel stress for long 4K/HEVC projects, FFmpeg process crash, AV playback and user-installed external toolchain failure recovery not proven in the packaged UI.

**P1 — Residual file identity race.** T09 owner-thread pre-commit uses fast stat identity after worker SHA256+full decode, not a second full SHA256. Target is same-volume no-clobber hardlink, yet malicious same-stat mutations are not cryptographically excluded.

## Next action and exact status

- **Technical SF12-T10 subsystem packaged Windows tests: PASS**.
- **SF12 STEP12 product-integration/release gate: BLOCKED**. Draft PR #11 remains unmerged, and no downloadable *finished* editor is declared.
- **Next task after owner continuation:** **ASTRA ADR / integration-readiness review for final product UI binding, native FFmpeg/libopenshot license/redistribution, notices and packaging strategy**; then SOL implements only the expressly approved plan, followed by true unified onedir Windows 11 E2E and 27 workflow gates. No UI redesign or breaking `MediaEnginePort` signature without the required approval.
