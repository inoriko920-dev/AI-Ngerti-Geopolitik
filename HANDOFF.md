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

## Post-W8 quality-only branch (2026-10-08 WIB)

- Branch `fix/project-open-corrupt-json-fail-closed-20261008`: scoped project-open malformed nested JSON regression and privacy-safe typed failure. Verify same-head Windows CI and maintain one bugfix scope; keep `main` unchanged.
- This branch is independent of stacked INT-01B Draft PR #19 and does NOT authorize native FFmpeg process work. Owner D1 remains pending; portable remains last.
- Source code and targeted/full Windows regression **PASS** on `24af2d67`, [CI #37772403305](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37772403305). Treat a later HEAD as fully verified only after its CI also passes.

## PR #20 project-open follow-up: strict boolean flags

- Load must fail closed instead of coercing malformed `"false"` strings to True in canonical project flags. New tests cover 10 fields / 50 invalid values plus valid roundtrip. Confirm Windows full CI on exact latest head before marking PASS; no `main` merge.

## PR #20 Unicode project-load follow-up (8 Oct 2026 WIB)

- Inspect exact current-head Windows CI for unpaired-surrogate malformed JSON, safe exception mapping and project-session atomicity; prior `a3bebefa` PASS is not evidence for new changes. Keep PR Draft, no main merge. Pilot A remains pending.

## PR #20 subsequent Save As / recovery atomicity regression (2026-10-08 WIB)

- Verify same-head Windows CI for the pre-write hash guard and pre-recovery adoption validation. Tests must prove invalid repository responses cannot change the project path, project session or existing source bytes. Keep Draft; D1 Pilot A FFmpeg still pending; no portable, no main merge.

## PR #20 UI open preinspection gate (2026-10-08 WIB)

- Verify Qt regressions for invalid target keeping current project alive and same-path open being a no-op; check same-head full Windows CI. Stale candidate after valid inspection remains a separate guarded decision risk, so do not claim fully transactional cross-project switching. No owner Pilot A permission/merge.
## PR #20 staged recovery acceptance (2026-10-08 WIB)

- Audit exact-head Windows CI of the staged `W8RuntimeController._decide` replacement, including Qt stale/marker-failure/valid-switch regressions, before PASS. `main` must remain unchanged; owner D1 Pilot A remains pending. Do not claim complete rollback if prior close_clean fails after session.close.

## PR #20 — previous clean-marker close fault gate (2026-10-08 WIB)

- Check exact current-head Windows CI for marker-write denial preserving previous editor, dirty guard rejecting clean marker, unexpected close rollback, and Qt old/candidate marker ownership. Keep PR Draft; D1 Pilot A still pending; portable remains last.

## PR #20 — Home-to-Editor runtime navigation fix (2026-10-08 WIB)

- Verify Qt: open saved project from UI-002 reaches UI-010 only on accepted session; corrupt target stays UI-002 with no opened project. Confirm W8-010 targeted and full Windows tests at current PR head. No frozen reference image/layout changes, no main merge and no Pilot A authorization.

## PR #20 — UI-003 New Project fail-closed regression (2026-10-08 WIB)

- Qt tests: Browse→Continue with selected .docx must not navigate to UI-010 without an actual ProjectSession, and a missing DOCX must not affect existing active project. Next feature milestone is a strictly validated Prompt-1 scene/Asset-ID DOCX importer; do not assume it exists, and do not create fake editor state. Current-head CI required, no D1 Pilot A FFmpeg work, no main merge.
## Scene DOCX Parser Step — Source-first handoff (8 Oct 2026 WIB)

- Source: `application/scene_docx_contract.py` and `infrastructure/scene_docx_reader.py`. Test: `tests/unit/test_scene_docx_import_contract.py`. Check exact-head Windows workflow including parser and full pytest before qualifying.
- Requirements from Master Blueprint 8.1: global asset IDs Axxx, scene headers N:1/2, source context; next phase requires folder asset scan/bind + real ProjectState creation/atomic save before enable wizard Continue. Do not bypass with a fake project, fake media metadata or opening an empty editor. Frozen UI and Pilot A boundaries remain.
## UI-003 read-only DOCX preflight (2026-10-08 WIB)

- Verified parser source: `scene_docx_contract.py` and `scene_docx_reader.py`. W8 worker now returns SceneDocxPlan to Qt only on success; broken ZIP/structure fails safely. Inspect same-head Windows CI before marking PASS. No canonical asset binding, no .angproj creation yet; avoid saying new-project workflow complete.
## Scene Axxx folder binding engine (8 Oct 2026 WIB)

- Implemented pure candidate matcher in application and bounded Qt image-aware folder scanner in infrastructure. Scan is read-only and a duplicate match must block rather than choose a random image. Next: GUI folder-picker hookup after valid DOCX preflight (no UI artwork/layout edits), then canonical scene/asset timeline mapping and atomic project save. Windows CI verification required before PASS.
