# HANDOFF — AI NGERTI GEOPOLITIK

**Current phase:** SF-STEP 11 — Feature Implementation Waves  
**Current wave:** W8 — Validation / Recovery / Diagnostics Hardening  
**Last completed task:** S11-W8-010 — PASS  
**Accepted implementation/regression HEAD:** `45c3294f5a8c93cee17369fa4b95122e3fca035b`  
**Accepted W8-003 workflow:** [37689420848](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37689420848) — SUCCESS  
**Current implementation:** S11-W8-005 — PASS
**Last implementation:** S11-W8-006 — Crash Marker + Startup Recovery Decision — PASS
**Last implementation:** S11-W8-007 — Atomic Persistence Failure Injection + Remediation — PASS
**Last implementation:** S11-W8-008 — Stale Result Hardening for W8 Background Jobs — PASS
**Last implementation:** S11-W8-009 — Structured Diagnostics + Redacted Diagnostic Bundle — PASS
**W8 status:** CLOSED / PASS (W8-001..010)
**Next exact task:** SF-STEP 12 — planning/contract readiness review — READY

## Read-first constraints

Read `AGENTS.md`, the Software Factory guide, planning DOCX/TXT, frozen UI manifest,
W8 contract, current task list, evidence and source before writing. AAVC remains
read-only. UI-001..042 frozen. All canonical mutations require CommandBus; no
presentation-to-infrastructure shortcuts. One serial W8 task per continuation.

## W8 accepted progress

- W8-001 canonical deterministic validation: PASS.
- W8-002 real media integrity + frozen UI-041 validation projection: PASS.
- W8-003 verified single asset relink: PASS.
- W8-004 batch directory relink scan + candidate ranking: PASS.
- W8-005 autosave catalog + retention hardening: PASS.
- W8-006 crash marker + explicit startup recovery: PASS.
- W8-007 atomic persistence failure injection + remediation: PASS.

## W8-003 qualification

- validated manual single-asset relink through canonical CommandBatch / CommandBus;
- exact Asset ID and clip references preserved;
- wrong media type, fingerprint, duration, dimensions and audio metadata fail safely with zero mutation;
- path already owned by another asset is rejected;
- missing source -> renamed relocated media -> verified rebind -> validation clears;
- one revision on apply, exact Undo and Redo, exact .angproj save/reopen;
- no batch scan, ranking, recovery flow or frozen UI redesign in W8-003;
- targeted tests **9/9 PASS**, full pytest **411/411 PASS**;
- real-media evidence verifier **23/23 PASS**;
- Windows CI lint, mypy, architecture, source-of-truth, secret and UI 42/42 gates PASS;
- full main-HEAD regression **27/27 workflow families SUCCESS**, all attempt 1.

**Workflow:** `37689420848`  
**Artifact:** `ANG-S11-W8-003-Single-Asset-Relink` / ID `11513225118`  
**Long-lived evidence:** `docs/evidence/features/S11_W8_003_SINGLE_ASSET_RELINK.md`.

## W8-004 accepted evidence

**Accepted W8-004 implementation/regression HEAD:** `4988e84ca6bca1e64fc5a755ff0d3287802e70f8`  
**Dedicated Windows workflow:** [37721840504](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37721840504) — SUCCESS  
**Artifact:** `ANG-S11-W8-004-Batch-Directory-Relink`, ID `11525753140`  
**Artifact SHA-256:** `75f33b72c4cf147d37b151e17bb7ae6bddc84982941f9f0aa8847c97d4fe4fb4`  
**Tests:** targeted 9/9 PASS; full pytest 420/420 PASS; real-media evidence 14/14 PASS  
**Gates:** Ruff, mypy (75 modules), import contracts, architecture, no-secret, source-of-truth 70/70, UI SHA 42/42 PASS  
**Full same-HEAD regression:** 27/27 workflow families SUCCESS, all attempt 1.

Verified: bounded worker scan, cancellation, stale project/session/revision/hash safety,
rank 1–4, SHA-256 verified explicit selection only, ambiguous candidate review,
one atomic CommandBatch, stable asset/clip IDs, exact Undo/Redo, save/reopen and
real-media validation. UI-040 projects intents; controller wiring remains W8-010.

## Accepted W8-005 qualification

- Accepted W8-005 implementation/regression HEAD: `43cb1d04b5d519c26f843714c4b7cd9793054fe9`.
- Windows autosave qualification: [37724812333](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37724812333) **SUCCESS**.
- Artifact `ANG-S11-W8-005-Autosave-Catalog`, ID `11526779061`; ZIP SHA-256 `c9a305ccc6cee9744e271e7520df4722192fa27a2a44544cf8ab68c717cf556c`.
- Dedicated catalog tests **9/9 PASS**; full pytest **429/429 PASS**; owned evidence **12/12 PASS**.
- Ruff, mypy (76 files), lint-imports, architecture, no-secrets, source-of-truth **70/70**, frozen UI **42/42 SHA-256 PASS**.
- Full same-HEAD regression **27/27 workflow families SUCCESS, all attempt 1**; Windows portable foundation PASS.
- New and legacy autosave filename compatibility, deterministic timestamp ordering, validated per-project catalog, maximum **20** managed valid snapshots, corrupt/foreign isolation and write/unlink failure guards qualified.
- Source `.angproj` and `.bak` are never retention/prune targets; source bytes unchanged in evidence. UI-039 recovery is deferred to W8-006.

## W8-006 accepted evidence

- Accepted W8-006 implementation and same-HEAD regression commit: `5a975bb312714f84315b9b752deac75a33021fab`.
- [Dedicated Windows recovery workflow](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37726261665): **SUCCESS**.
- Artifact: `ANG-S11-W8-006-Crash-Recovery`, ID `11528226010`,
  ZIP SHA-256 `adc9591b108a82f2b4e09d7f7bc3714133a6dd7ec839ed2216e7568351ad1165`.
- Dedicated recovery tests **15/15 PASS** (12 unit + 3 Qt).
- Full Python suite **444/444 PASS**; owned crash evidence verifier **12/12 PASS**.
- Ruff, mypy (79 source files), import contracts, architecture, no-secrets,
  source-of-truth **70/70** and frozen UI references **42/42 SHA-256 PASS**.
- Same-HEAD regression **27/27 workflow families SUCCESS, attempt 1**,
  including Windows portable foundation, UI shell, timeline, E2E, subtitle,
  media and previous W8 qualification.
- Proven: clean/unclean marker, valid newer-only snapshots, corrupt-newest
  isolation, explicit Open Source / Recover Snapshot / Ignore choices,
  stale snapshot/source rejection, exact project source bytes unchanged
  during recovery, dirty working state until explicit Save, clean-close guard.
- UI-039 intent/projection qualification only; complete main-window wiring
  remains W8-010. W8-007 persistence-failure injection is a separate next STEP.

## W8-007 acceptance

- Accepted W8-007 implementation + same-HEAD regression: `130407dc728b6417c30dbbc935ecd9b04d37ba43`.
- [Windows atomic-persistence workflow](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37727525574) — **SUCCESS**.
- Artifact: `ANG-S11-W8-007-Atomic-Persistence`, ID `11528930146`; SHA-256 `5cf537b7ec5fcf7043c2a0fe640d3f7d9008d2e60209b712c0d81ca06a95be91`.
- **15/15** targeted fault tests PASS; **459/459** full Python tests PASS;
  **19/19** owned evidence checks PASS.
- Ruff, mypy (80 source files), import-linter, architecture, no-secrets,
  source-of-truth **70/70** and frozen UI references **42/42 SHA-256 PASS**.
- **28/28 same-HEAD workflow families SUCCESS, all attempt 1**,
  including portable Windows foundation, UI shell, timeline and E2E.
- Verified temporary create/write/sync, backup create/copy/replace and
  source replacement fault injection; preexisting source bytes exact on
  failed Save, backup always readable, orphan .tmp cleanup for recoverable
  failures, Session dirty/Save As guards and successful retry with intended
  canonical state. Snapshot save failure does not publish invalid recovery.
- **Confirmed and fixed:** pre-W8-007 code registered temp filename only
  after write/sync, leaving orphan temp on early failure. Existing repository
  serializer and ownership remain unchanged; no schema/UI changes.
- Typed `PersistenceError` stages and an actionable, redacted Indonesian
  failure projection qualified. W8-008 not implemented.

## W8-008 accepted qualification

- Accepted W8-008 implementation/regression HEAD: `6c35b70bd9122664473a69eff6635ed9b71da5cb`.
- [Windows W8-008 workflow](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37728798520) — **SUCCESS**.
- Artifact: `ANG-S11-W8-008-Stale-Result-Jobs`, ID `11529365791`,
  SHA-256 `3b622ad005a16951e040c1d590f63974304c583a13374aa87fa1bc2f6a0c1a5c`.
- Dedicated concurrency tests **12/12 PASS**, full pytest **471/471 PASS**,
  owned concurrency evidence **18/18 PASS**.
- Ruff, mypy (81 source files), import contracts, architecture, no-secrets,
  source-of-truth **70/70** and frozen UI references **42/42 SHA-256 PASS**.
- **27/27 same-HEAD regression workflows SUCCESS**, all attempt 1;
  Windows portable foundation, media/speech/UI and E2E passed.
- Verified manual edit while scan runs, closed session, new session with
  identical revision/hash, different project, same-revision semantic swap,
  cancellation with late worker completion, stale result discard and
  zero automatic project mutation.
- Existing CommandBus/ProjectRepository and frozen UI remain unchanged.
  Actual main-window UI-039/040/041 wiring remains W8-010.

## Next exact action

On owner's next `lanjutkan`, execute **SOL S11-W8-010 ONLY**:
frozen UI-039/040/041 real controller wiring + GOLDEN-03 E2E recovery/relink
regression, under locked ASTRA W8 planning. No STEP 12 in same turn.

## Provisional gates

W5 microphone physical hardware and W6/W7 live Gemini network tests remain
provisional; do not claim device/provider smoke results that were not run.




## W8-009 accepted

- W8-009 accepted code/regression HEAD: `6a4ec93d445e71dc037bcc4dc6edff2008894268`.
- Windows W8-009 run: https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37730435314 — SUCCESS.
- Artifact `ANG-S11-W8-009-Redacted-Diagnostics` ID `11529353867`;
  ZIP SHA-256 `17bc6c66063c240258f8f27fd68e8755ea8d26b63ba73a498c96e1f6e08d3b6e`.
- **11/11** targeted tests, **482/482** full Python suite, **18/18**
  owned redaction evidence checks PASS.
- Ruff, mypy **84 files**, import architecture/security,
  source-of-truth **70/70**, frozen UI SHA **42/42** PASS.
- **27/27** same-code-HEAD regression workflows SUCCESS, all attempt 1;
  Windows portable, UI shell, media, E2E regressions PASS.
- Deterministic 128KiB bounded ZIP with only manifest.json/events.json;
  excludes project paths, contents, media, exception text and credentials.
- No canonical state/schema changes or frozen UI redesign.

W8-010 READY only on owner's next explicit `lanjutkan`.

## W8-010 accepted closure — 2026-10-08 WIB

**W8-010 accepted implementation and same-HEAD regression:** `45c3294f5a8c93cee17369fa4b95122e3fca035b`.

- [Windows W8-010 UI/GOLDEN-03 run](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37732709194): **SUCCESS**.
- Artifact `ANG-S11-W8-010-UI-GOLDEN03`, ID `11530068997`, size 11,387,537 bytes.
- Artifact ZIP SHA-256: `4a24f45f3c6ef6d73924ec83d0ea2149b1490119abb766dd079d6db2a5840241`.
- **5/5** targeted Qt controller tests, **487/487** full Python suite, **23/23** owned GOLDEN-03 evidence checks PASS.
- Ruff, mypy **85 source files**, lint-imports, architecture and no-secret checks PASS; source-of-truth **70/70** PASS.
- Frozen UI-001..042 manifest **42/42 SHA-256 PASS** — no raster redesign or AAVC source changes.
- **27/27** same-code-HEAD workflow families **SUCCESS on attempt 1**, including S08 portable foundation, S09 UI shell, S10 real Windows E2E, W0-W7 and W8.
- Demonstrated live UI-041 missing referenced media BLOCKER, UI-040 bounded worker discovery and fingerprint-verified manual relink, canonical CommandBus/Undo-Redo, revalidation, save/reopen, UI-039 explicit crash snapshot restoration without silent source overwrite, and redacted diagnostic ZIP.
- Fixed a real compatibility regression: FFprobe is initialized lazily only during a media probe, so the Qt shell and fake-probe tests do not require an installed FFprobe.
- W5 physical microphone and W6/W7 live Gemini qualification remain provisional, not claimed as PASS.

**Next exact action:** SF-STEP 12 planning/contract readiness review only, after the owner's next `lanjutkan`. Do not implement STEP 12 in this W8-010 turn.


## SF-STEP 12 readiness review — 2026-10-08 WIB

- Current audit baseline: `c9154eef85f8b475630816a7c63f5e2b52bf1523` (W8-010 accepted code `45c3294...`).
- **Readiness review complete; implementation not started.** Planning source `docs/planning/12_SF_STEP12_INTEGRATION_EXPORT_READINESS_2026-10-08.txt` and matching DOCX; implementation contract `docs/project/SF12_INTEGRATION_EXPORT_READINESS_CONTRACT.md`.
- **P0:** frozen export UI advertises H.265/4K/60fps/sharpen, while `ffmpeg_slice.py` hardcodes H.264 ultrafast CRF28; `render_requested` is not a completed render pipeline. Do not claim export matrix done.
- T01 only next: capability discovery, honest enabled/disabled UI, safe output default, foundation proofs; T02+ contract/port changes require ASTRA gate when breaking. W5 physical mic and W6/W7 live Gemini remain provisional.
- **Gate:** current main CI plus ASTRA material-contract review must be verified before T01. No STEP13/14/15, no release and no coding in this review turn.


## SF12-T01 implementation checkpoint — 2026-10-08 WIB

- Code commit tested: `b0edecbb01b6eb76fb46fd1489e442bcacd589ba` on `feature/sf12-t01-export-capabilities` (stacked draft PR #2 above planning draft PR #1). Never claim merged into main.
- Windows Actions dedicated run [37734750417](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37734750417): **SUCCESS**. Targeted 6 tests and entire existing pytest suite PASS. Ruff format/check, mypy, import contracts, architecture, source-of-truth 70/70, secret check, frozen UI manifest 42/42 PASS.
- T01 result: **PASS_WITH_PROVISIONAL_NATIVE_ENCODER_INVENTORY**. Export controls fail closed: no enabled `Mulai Render` button, no claimed H.265/1440p/4K/60fps/sharpen/subtitle switch rendering. Default output directory now per-user Videos rather than a developer D: example.
- Real Windows runner inventory explicitly returned FFmpeg=false, FFprobe=false, libx264=false, libx265=false, AAC=false. This is an observed ABSENCE, not proof of missing codecs in end-user installations, and not a real H.264/H.265 export test.
- The UI receives an immutable capability snapshot but no production asynchronous capability refresh yet; current conservative default keeps render disabled. `MediaEnginePort` and `ProjectState` unchanged; no AAVC writes, no UI reference asset changes.
- **Next exact task:** SF12-T02 ExportRequest + engine-port contract ASTRA review. Do not wire or enable rendering before actual backend + output qualification; no STEP13/14/release. W5 physical mic and W6/W7 live Gemini still provisional.


## SF12-T02 acceptance — 2026-10-08 WIB

- **T02 code accepted:** `9e12498b7ed181933c1da089204e3daf234d2a35`, Windows workflow [37735699709](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37735699709) **SUCCESS**; new targeted contract tests **27/27 PASS**, full pytest PASS.
- Ruff format/check, mypy (88 files), architecture/import contracts, no-secrets, source-of-truth **70/70**, frozen UI raster SHA **42/42** PASS.
- Added typed/frozen ExportRequest, scoped enums, half-open frame selection, absolute MP4 guard, session/project/revision/semantic hash stale token and prospective additive `ExportRequestMediaPort`. Existing frozen `MediaEnginePort.export` was NOT modified; no code path writes/render MP4 through the new contract.
- Evidence: `docs/evidence/features/SF12_T02_EXPORT_REQUEST_CONTRACT.md`.
- Branch/PR: `feature/sf12-t02-export-request-contract` / draft PR #3, stacked on T01 PR #2 then planning PR #1; none merged to main.
- **Next exact task** on new owner continuation: **SF12-T03 preflight/capability negotiation only**. No STEP13, release, native engine changes or frozen UI redesign. ASTRA/ADR mandatory for breaking MediaEnginePort changes. W5 microphone and W6/W7 live Gemini remain provisional.


## SF12-T03 accepted — 2026-10-08 WIB

- **SF12-T03 Preflight & Capability Negotiation = PASS_CONTRACT_ONLY**. Code SHA `7bee32aae7248ae9023afe4b9b62bf2caf357095`; Windows [37736630766](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37736630766) **SUCCESS**.
- Tests: targeted SF12-T03 PASS, full pytest PASS; Ruff, mypy 90 files, lint-imports, architecture, no secrets, source-of-truth **70/70**, UI SHA manifest **42/42** all PASS. Evidence: `docs/evidence/features/SF12_T03_EXPORT_PREFLIGHT.md`.
- Files: `application/export_preflight.py`, `infrastructure/export_output_inspector.py`, `tests/unit/test_sf12_t03_export_preflight.py`, dedicated Windows workflow. W8 real-media validation reuse; conservative H264/1080p/30/AAC profile; protected output and disk/write probe, no output overwrite, stale checks.
- `precheck_pass` **does not authorize render**. `can_start_render=False` remains deliberate; no real FFmpeg codec-matrix/HEVC/4K proof, no engine port breaking changes, no changed UI-001..042, no AAVC writes.
- Branch `feature/sf12-t03-export-preflight` / draft PR **#4**, stacked on T02 #3, T01 #2, planning #1; **not merged into main**. Keep ownership serial to avoid collision with other agents.
- **Next exact task** on owner's next `lanjutkan`: **SF12-T04 H.264 Baseline Export Pipeline only**, real media and output safety tests, no T05+ work, no release. ASTRA/ADR mandatory for frozen port signature/native architecture changes. W5 physical mic and W6/W7 live Gemini provisional.


## SF12-T04 H.264 Baseline Export — accepted 2026-10-08 WIB

- T04 **PASS_REAL_MEDIA_BASELINE_WITH_PROVISIONAL_PRODUCTION_GATE**. Code SHA `96cf5a46ecfeea6cdb9ff767414a6dde828a2a42`; Windows CI [37737863469](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37737863469) **SUCCESS**; actual H.264+AAC 1920x1080 30fps/30 frames, 1.000000 second verified by independent FFprobe.
- Existing FFmpeg adapter gained **additive** `export_h264_baseline` with T02/T03 preflight, unique temp workspace, baseline stream check, revalidation and atomic link no-clobber; legacy port is UNCHANGED. Dedicated race test proves no overwrite of last-moment competing file.
- Entire Python suite and T04 tests PASS; Ruff, mypy 90, imports, architecture, secret checks, source-of-truth 70/70, frozen UI 42/42 PASS.
- Evidence: `docs/evidence/features/SF12_T04_H264_BASELINE.md`, GitHub artifact ANG-SF12-T04-H264-RealMedia ID 11531514655, ZIP digest `695a450672aee1962a42b961d0eccfcf8dd55f017e3d20264a6657a4ee3363e3`; MP4 SHA `fcd8f698188f5e92cf10b0b94d5cf4e8602fc53d1bbcd233cfa9523788bc32c0`.
- Production UI render stays DISABLED: T08 worker, T09 postflight, T10 packaged qualification remain outstanding. H.265/1440p/4K/60fps/selection also NOT QUALIFIED. Original source AAVC untouched.
- Branch `feature/sf12-t04-h264-baseline` **draft PR #5**, stacked on #4/#3/#2/#1; NOT merged to main. W5 physical microphone, W6/W7 live Gemini provisional.
- **Next exact task after user's next `lanjutkan`: SF12-T05 full/selection frame-accurate range mapping ONLY.** No engine port breaking change without ASTRA ADR; no STEP13/release.


## SF12-T05 — Accepted 2026-10-08 WIB

- **SF12-T05 Full/Selection Frame Mapping = PASS_REAL_MEDIA_SELECTION / UI_RENDER_DISABLED**. Accepted code SHA `9dca99397f3dcbac4d491d5d930cf8309d744271`. Windows [37738941089](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37738941089) **SUCCESS**.
- New additive synchronous `FfmpegSliceMediaEngine.export_h264_selection` uses T02/T03 selection-specific opt-in, renders original full timeline with W5 subtitle and narration, trims video with exact half-open frame indices and mixed audio with matched timestamps, re-encodes H264+AAC. T04 full path and frozen `MediaEnginePort` unchanged.
- Actual real-media Windows output: source project 4s/120f, 2 clips, subtitle 30–90 & 90–120, narration frame15. Selection [0,30), [45,75), [90,120) each produced **exact 30f/1.000000s**, H264/AAC 1080p30. Independent PSNR vs full global timeline 38.15/39.01/47.29dB, threshold 33dB. Source hashes unchanged.
- T05 targeted pytest, full pytest, Ruff, mypy 90, import/architecture/secret gates, source-of-truth 70/70 and UI reference manifest 42/42 PASS. Evidence `docs/evidence/features/SF12_T05_SELECTION_REAL_MEDIA.md`; GitHub artifact `ANG-SF12-T05-Selection-RealMedia` ID 11532743714.
- Negative tests: invalid ranges, default T03 rejection, wrong nb_frames, first/second-pass failure/cancel, existing output/no clobber. **Caveat**: 2-pass render uses full-project temporary output, not efficient for long timelines; audio alignment based on exact trim-time mapping, no independent sample-level correlation. UI remains disabled T08/T09.
- Draft stacked **PR #6** on T04 #5 / #4 / #3 / #2 / #1. NOT merged into main; no direct main changes. AAVC/UI frozen refs untouched.
- **Next exact serial task:** **SF12-T06 real codec/resolution/FPS matrix** after owner's next `lanjutkan`; one profile/cell per qualification and UI only enables proved cells after later rendering gates. ASTRA/ADR mandatory for engine switch, native dependencies/license impact or breaking port changes.


## SF12-T06 — Accepted 2026-10-08 WIB

- Gate **PASS_FOUR_REAL_MEDIA_CELLS / PRODUCT_UI_STILL_DISABLED**. Code SHA `00761740666c66c8787aec4865d3e2184a13fe7d`; Windows [37740103975](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37740103975) **SUCCESS**.
- Explicit T06 candidate matrix PASS with independently verified actual Windows FFprobe: H264 2560×1440 30fps (15f), H264 3840×2160 30fps (15f), H264 1920×1080 60fps (30f), H265/HEVC 1920×1080 30fps (15f); each 0.500000s, MP4, AAC. Source fixture unchanged.
- Additive `application/export_profiles.py`, typed matrix-candidate gate in T03 preflight (default DENY), separate `infrastructure/ffmpeg_export_profiles.py`: safe full-project compose then single conversion, strict FFprobe, postflight precheck, same-volume temporary staging, atomic no-clobber. Frozen MediaEnginePort, ProjectState, UI refs and AAVC unchanged.
- Real outputs are **upscaled 1080p→1440p/4K**, 30→60 duplicates frames. No native 4K detail, temporal detail, long-video resource or production-package HEVC claim; H265 4K60/H265 1440p30/H264 4K60 & unlisted options DENIED. UI render still disabled until T08/T09/T10.
- Dedicated T06 targeted and full pytest, Ruff, mypy **92 files**, import/architecture/secrets, source-of-truth **70/70**, frozen UI refs **42/42** PASS.
- Evidence `docs/evidence/features/SF12_T06_CODEC_MATRIX_REAL_MEDIA.md`; artifact `ANG-SF12-T06-CodecMatrix-RealMedia` ID **11533866135**, ZIP digest `04fea1ca343b133cedb838fe3a4924d50763cc01a63c67e0292080155468d1fd` (14-day retention).
- Draft stacked **PR #7**, base `feature/sf12-t05-selection-frame-mapping` / PR #6, other T01-T05 still open; **main not changed**.
- **Exact next serial task after user's next `lanjutkan`: SF12-T07 — Subtitle, Narration, Sharpen & Quality Binding ONLY.** Do not broaden to T08+ in same step. External FFmpeg licensing/package architecture changes require ASTRA/ADR; W5 physical microphone, W6/W7 live Gemini stay provisional.


## SF12-T07 — Accepted 2026-10-08 WIB

- **T07 PASS_REAL_MEDIA_STYLES / PRODUCT_RENDER_DISABLED**. Code SHA `79b24e93d4574cff0fc8a1650a6bd569e7640965`, Windows [37741355411](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37741355411) SUCCESS.
- Six exact real H264/AAC 1080p30 60-frame / 2-sec outputs: subtitle burn-in on vs off, quality high CRF28 ultrafast, youtube_clean CRF21 medium, documentary_crisp CRF18 slow; sharpen none/light/crisp (unsharp levels 0.6/1.2), all visually and codec verified. Narration begins frame 15 with 440Hz synthetic WAV.
- Objective visual mean gray pixel difference: subtitles on/off 1.1399; sharpen light 0.6486, crisp 1.0716 vs base. PCM comparison with no-narration control mean difference pre-start 4.2776, during narration 2399.3156; not subjective quality scores.
- `application/export_style_policy.py`, `infrastructure/ffmpeg_export_style.py`, opt-in T03 preflight; no ProjectState mutation, UI or MediaEnginePort breaking changes. Reuses W5 render plan, safe temp, post-check and atomic no-clobber. **Default UI render still disabled** until T08/T09/T10.
- Tests T07 + full pytest/Ruff/mypy **94 source files**/lint-imports/architecture/secrets/70 documents/42 UI reference hashes all PASS.
- Evidence `docs/evidence/features/SF12_T07_STYLE_REAL_MEDIA.md`, artifact `ANG-SF12-T07-Style-RealMedia` id **11533749234**, ZIP digest `894f7381105616d68ba27d64748713fd876127bf806ba1f4727824ff96d3c6ec`. GitHub branch `feature/sf12-t07-style-subtitles-narration` / **draft PR #8** stacked on T06 PR #7 and prior #6/#5/#4/#3/#2/#1, none merged into main.
- Disallowed options: arbitrary style permutations, quality slider, audio OFF, sidecar SRT, H265+sharpen/4K+styles, unqualified codecs. Native FFmpeg is installed only on runner, no portable bundle. W5 physical microphone and live W6/W7 Gemini tests provisional.
- **Next exact task only after next user's `lanjutkan`: SF12-T08 Nonblocking Render Job Lifecycle**, with progress, safe cancellation, timeout, stale request/close guard and tests; T09 postflight and T10 Windows packaged qualification remain separate. No frozen port/engine dependency changes without ASTRA ADR.


## SF12-T08 — Accepted 2026-10-08 WIB

- Gate **PASS_NONBLOCKING_STAGED_LIFECYCLE / PRODUCT_RENDER_DISABLED**. Implementation SHA `596a48db355878537227f193c6dee33d0ae3f24a`; Windows [37742882153](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37742882153) **SUCCESS**.
- `application/export_jobs.py` single background worker, typed QUEUED/RUNNING/READY/SUCCESS/CANCELLED/TIMED_OUT/STALE/FAILED; implicit numeric progress is intentionally NOT fabricated while FFmpeg is running (phase only). `infrastructure/export_job_adapters.py` routes verified T04–T07 profiles after original-destination W8/T03 preflight. Output held in private same-volume staged directory; owner-thread accept checks original request/session/revision/hash and publisher atomic create-if-absent; nothing auto-publishes.
- Qt QTimer heartbeat and off-thread job smoke PASS, close nonblocking, cancellation and timeout, stale after same-revision semantic swap/closed session, competing output protected, late noncooperating result never publishes, worker exceptions redacted. Real 15f / 0.5s 1080p30 H264 AAC MP4 PASS Windows FFprobe. Source unchanged; artifact ID **11534776048**, upload ZIP digest `46d8821403c4b3649eda091a09e818bcb69a11fbec4ea5a9f53bf514e2b43e35`.
- Target/full pytest PASS; Ruff, mypy 96, lint-imports, architecture, secret checks, source-of-truth 70/70, frozen UI 42/42 PASS. Code and evidence `docs/evidence/features/SF12_T08_RENDER_JOB_LIFECYCLE.md`.
- **Not wired to production Qt render button**. Strict T09 independent postflight and T10 Windows packaged smoke are pending; no constant 0–100 encoder progress, no bundled FFmpeg, and no final release. ProjectState, MediaEnginePort, AAVC, frozen UI stay untouched. Draft stacked **PR #9** on #8/#7/#6/#5/#4/#3/#2/#1; none merged to main.
- **Exact next serial task after owner's next `lanjutkan`: SF12-T09 verified strict postflight / typed errors / safe commit.** Do not silently enable real render or change native engine without ASTRA ADR.
