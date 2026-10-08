# MASTER PLAN ASTRA: POST-T10 UI RENDER INTEGRATION AND NATIVE LICENSE, 2026-10-08 WIB

**Status: PLANNING COMPLETE / OWNER APPROVAL PENDING / NO SOL CODING.**
**Primary source:** docs/project/ASTRA_ADR_2026_10_08_RENDER_NATIVE_PACKAGING_PROPOSAL.md.
**Planning baseline:** GitHub T10 866464471e5926d7f9a782e56f2030ed2425e7a2 and Windows run https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37746818497.
**Platform:** Windows 11 x64, Python 3.12.10, PySide6, PyInstaller onedir, UI-001..042 frozen, AAVC read-only.

## 00 — Objective and non-goals
Objective is to move from TWO working test ZIPs (UI-only and separately packaged media CLI) to ONE tested actual Windows desktop editor with qualified render, while preserving the frozen design and enforcing legal and native engine gates. The T10 technical package PASS must not be marketed as a release. Not in scope here: changing the production engine, adding GPL codecs to releases, merging PRs #1–#11, redesigning the GUI or starting coding prior to approval.

## 01 — Evidence-backed current state
- T01-T03: typed export intent, current media integrity, output collision and disk safety; GUI widgets do not yet construct a renderable request.
- T04-T07: FFmpeg qualification for baseline H264, selection, H265, 1440p/4K/60fps, subtitle and quality/sharpen, plus W5 narration in selected tests. Profile permutations are not automatically authorized.
- T08: one background worker, no fake progress percent, cancel/timeout/stale/close guard, private staging, owner-thread accept.
- T09: independent FFprobe metadata and full video+AAC decode required before READY; typed privacy-safe error codes and stage receipt. Conservative no-clobber hardlink promotion.
- T10: three Windows jobs success on final head, 9 true MP4 cells rendered from packaged CLI with EXTERNAL FFmpeg, standalone UI shell startup, 42/42 reference SHA256, 70/70 docs, full pytest/Ruff/mypy. CI packages are not ONE desktop editor.
- Main remains at W8 baseline; all #1-#11 PRs are stacked drafts. No approved user release. W5 physical mic and W6/W7 live Gemini are provisional.

## 02 — Concrete code owners and reuse
- Existing export Qt dialog in presentation/dialogs.py: current btn_export_render remains disabled; resolution, FPS, quality/sharpen/subtitle controls cannot silently become enabled without capability truth and actual connected worker.
- application/export_request.py: canonical immutable request with project/session/revision/semantic_hash and no ProjectState mutation.
- application/export_capabilities.py and infrastructure/export_capability_probe.py: native detection, no hardcoded availability assumptions.
- application/export_preflight.py and infrastructure/export_output_inspector.py: referenced asset fingerprint, disk/permissions/source collision and collision-free output target.
- application/export_jobs.py: one background rendering job, phase snapshot, cancellation, owner-thread acceptance and private stage.
- infrastructure/export_job_adapters.py: dispatch verified profile cells and T04-T07 adapter reuse, preserve fixed H265 routing.
- application/export_postflight.py and infrastructure/export_postflight.py: exact MP4/codec/FPS/frame count/audio plus independent whole decode and verification receipt.
- bootstrap/main.py: dependency construction; only existing application ports flow outward to presentation.
- scripts/package/build_step09_ui.ps1 and build_step10_media_smoke.ps1: existing independent packages are baselines, NOT final merged editor. No new packaging model without ADR.

## 03 — Strategy choices and licence risk
**Choice A: EXTERNAL FFmpeg pilot — RECOMMENDED, PENDING OWNER.** One existing onedir UI package can eventually wire approved workers. Toolchain remains a declared prerequisite installed/supplied externally. A pilot with an external FFmpeg path is not zero-dependency portable. Validate identity, codec availability, executable path and safety; do not download silently or inject shell commands.
**Choice B: BUNDLED FFmpeg/x264/x265 — BLOCKED.** GPL-enabled FFmpeg distribution requires source/build/notice/legal compliance plus codec/patent policies, security maintenance and approval. Do not copy binaries into ZIP.
**Choice C: libopenshot final engine — PROVISIONAL.** Aligned with D-005, but require Windows engine bind/exports/undo/cancel/parity, dependencies FFmpeg/JUCE licenses, and approved ADR before native adoption.
**Choice D: MLT fallback — PROVISIONAL.** Only independently qualified after C evidence insufficient.

Official references: https://www.ffmpeg.org/legal.html ; https://www.openshot.org/libopenshot/ ; https://doc.qt.io/qtforpython-6.8/commercial/index.html ; https://github.com/pyinstaller/pyinstaller/blob/develop/COPYING.txt . This analysis is not legal advice.

## 04 — Target PILOT architecture after explicit approval
(1) User launches one packaged Qt executable. Native probe discovers FFmpeg/FFprobe OFF the UI thread. No encoder → edit shell opens, render unavailable and truthful reason shown. No admin/auto-install.
(2) Existing Qt widgets map to stable typed enum IDs and exact T04-T07 qualified combinations; do not parse arbitrary labels into engine parameters or turn on unsupported quality slider.
(3) Existing controller passes an immutable request to application port, preserving current canonical project identity/session/revision/hash. No duplicate session state or second CommandBus.
(4) Preflight checks missing MP4/SRT, corruption, output target, disk, stale project, codec support and selection in/out.
(5) Background worker processes render to private same-volume staging. Progress is honest phase only (QUEUED/RUNNING/POSTFLIGHT/READY); numeric 100 only after committed success. Qt QTimer/event signals cannot block.
(6) Owner-thread completion rechecks request and project, T09 full decode/receipt, and atomically publishes only to a new output file; errors cannot overwrite source/existing data.
(7) Qt close/cancel/reopen callbacks revoke stale jobs, no post-close UI update, cleanup intermediate artifacts.
(8) If progress needs a new panel/modal, STOP and request UI approval; no new artwork or frozen UI structure without owner permission.

## 05 — Serial task cards for SOL AFTER owner D1-D4

### INT-00 — Approved ADR and git baseline reconciliation (ASTRA/owner)
Inputs: proposal, decisions D1–D4, PR stack #1–#11, accepted T10 head. Output: accepted ADR with explicit chosen pilot and license scope, dependency matrix, GitHub handoff and stop/go. No code before owner acceptance. PASS only if no conflict with D-005/media contract/UI freeze. FAIL if legal decision unclear. Next INT-01.

### INT-01 — Native executable trust & capability inventory
Inputs: existing export probe, target Windows runner binary version/config. Output: additive runtime native locator invoked off GUI thread, explicit configured path/lookup safety, ffmpeg+ffprobe encoder/version test, typed availability. Tests: no binary, fake binary, wrong codecs, path spoofing, AV quarantine, changed installed binaries mid-session, path with spaces/Unicode. Gate: invalid binary never enables render or executes arbitrary shell; source/GitHub actions proof. Next INT-02.

### INT-02 — Qt intent → typed ExportRequest bridge
Input: existing Qt combo/field IDs and application immutable request. Output: controller mapping using stable option IDs, target-safe absolute MP4 path, selection, narration/subtitles, snapshot/session token, no state mutation. Tests: unsupported enum, malformed/empty filename, NUL/traversal, no timeline, stale revision, double click and same-revision semantic swap. Gate: UI can build only valid request, still DISABLED. Next INT-03.

### INT-03 — Frozen UI capability and feedback projection
Input: UI-001..42, dialog objectNames, export capability registry. Output: existing widgets enabled/disabled truthfully by exact allowlist, error/progress text reuse without structure change. Tests: native absent/present, H264 baseline, H265 with/without libx265, nonqualified permutations, screenshot representative anchors and 42 reference SHA. Gate: no accidental UI redesign; progress slider not falsely 0-100. Next INT-04.

### INT-04 — Qt lifecycle binding and close/cancel
Input: T08 job service and T09 full postflight. Output: bootstrap-controlled worker start/poll/cancel/window-close callbacks in existing Qt owner thread, redacted stable errors, job ownership. Tests: heartbeat, cancel while encoder busy, timeout, app/window close, reopen, queued double click, stale project, output remains old/unmodified on failure. Gate: no UI freeze/stale publish. Next INT-05.

### INT-05 — Controlled REAL click-to-MP4 pilot
Inputs: INT01–04 PASS and approved pilot scope. Output: feature-flag-guarded btn_export_render enabled only for qualified H264 1080p30/AAC full project after all preflight and native probes pass; T09 full decode and no-clobber required. Tests: actual Qt click, source-owned project with SRT and narration, exact FPS/codec/duration, file path, Cancel, corrupt media, no encoder case, project changed while rendering. Gate: no final capability claims, H265/4K style only after individual connected-UI evidence. Next INT-06.

### INT-06 — One Windows onedir pilot with unbundled FFmpeg
Inputs: existing PyInstaller UI shell, tested bootstrap changes. Output: one UI executable ZIP that imports render and managed worker components, excludes FFmpeg/x264/x265 binaries, hashes/version/notice and explicit dependency prerequisites; preserve original two test ZIPs for regression. Tests: unzip, cold launch on vanilla Windows11, no installed Python, missing FFmpeg messaging, successful controlled external FFmpeg export, integrity/source manifest. Gate: technically pilot only. Next INT-07.

### INT-07 — Windows 11 GUI end-to-end and failure/stress
Input: integrated GUI pilot. Positive: MP4 import, SRT+audio, timeline, save/reopen, correct H264 full/selection, audio sync, subtitles visual verification, cancel/restart, clip and 60fps mapping only when approved. Negative: absent/corrupt required input, symlink/existing target, disk full, wrong codec, timeout, unexpected FFmpeg exit, long 1/10-minute media, 4K memory ceiling, UI close. Evidence: real screenshot diff, FFprobe streams and independent whole decode, source SHA, packaged ZIP SHA, runtime timing, test environment details. Gate: no missing P0. Next INT-08.

### INT-08 — Legal/provenance/third-party manifest
Input: owner D2–D3, actual packaged files and ffmpeg native config, PySide6/Qt, PyInstaller, libopenshot if used. Output: SPDX/SBOM, full copyright/source/notice records, build dependency provenance and CVE updates, explicit user license, legal review. Must distinguish external codecs from bundled obligations, document possible patents and region-specific distribution. Gate: blocked without owner/legal permission; no source LICENSE silently added. Next INT-09.

### INT-09 — Same-head integration and release gate
Input: approved all prior gates. Run 27 historical workflow families against SAME HEAD, all 42 reference hashes, 70 source-of-truth, real packaged GUI, signed/hashed artifact and clean Windows11 user machine smoke. Owner checks full UX, unsupported controls stay disabled, no secret leaks, permission, third-party notices, links and version. Output: release candidate only if every P0 PASS, explicit owner signoff; otherwise status BLOCKED and separate bug cards. Do not represent a pilot as final version.

## 06 — Risk and acceptance matrix
P0 fake render controls: must stay disabled if native absent/wrong or feature not proven.
P0 GPL/native distribution: do not bundle FFmpeg at all in pilot; release option B requires approved legal/notice/source obligations.
P0 binary execution security: explicit trusted executable path, no shell interpolation/hidden installs, deny unknown codec.
P0 save corruption: current source project cannot be overwritten; atomic publish no-clobber; stale result discarded.
P0 Qt freeze/close: worker always off UI thread, bounded shutdown and generation guard.
P1 T09 stage stat-only after SHA verification: isolate temporary folder and future strengthen receipt to prevent adversarial tamper.
P1 CPU/RAM/long-form: decode overhead and 4K/HEVC can be expensive; measure realistic files before final enable.
P1 physical microphone and Gemini live provisional: keep separately labelled, never count mocked QA as live.
P1 same-head 27 workflows incomplete: do not claim acceptance prior to rerun.

## 07 — Exact required owner decisions
D1: Approve pilot external FFmpeg (yes/no).
D2: Final portable product must include encoders in ZIP (yes/no); if yes, legal compliance prerequisite.
D3: Decide software/source license + reviewer of FFmpeg/libopenshot/Qt/PyInstaller notices and rights.
D4: Maintain libopenshot primary production qualification candidate in D-005 (yes, recommended) or open separate engine ADR.

**No D1–D4 approval has been given.** Generic subsequent CONTINUE does not constitute licensing approval. STOP before SOL coding or toggling the UI.

## 08 — Evidence and sources
GitHub T10: https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37746818497.
Repo records: AGENTS.md, docs/DECISIONS_LOCKED.md, docs/project/ARCHITECTURE.md, docs/project/SF12_T10_RELEASE_BLOCKERS.md, docs/evidence/packaging/SF12_T10_WINDOWS_PACKAGED_E2E.md.
Official: https://www.ffmpeg.org/legal.html ; https://www.openshot.org/libopenshot/ ; https://doc.qt.io/qtforpython-6.8/commercial/index.html ; https://github.com/pyinstaller/pyinstaller/blob/develop/COPYING.txt.
