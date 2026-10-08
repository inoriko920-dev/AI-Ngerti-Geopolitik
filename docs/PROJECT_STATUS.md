# PROJECT STATUS — AI NGERTI GEOPOLITIK

**Current STEP:** SF-STEP 11 — Feature Implementation Waves  
**Last completed wave:** **W8 — Validation / Recovery / Diagnostics Hardening — PASS**  
**W8 status:** **CLOSED / W8-001..010 PASS**  
**W8 runtime:** **QUALIFIED / CLOSED**  
**Accepted W8-003 implementation/regression HEAD:** `25e5f6cefbbef5f554bd17e64d50a61db948bf13`  
**Accepted W8-003 workflow:** `37689420848` — SUCCESS  
**Last completed task:** **S11-W8-009 — Structured Diagnostics + Redacted Diagnostic Bundle — PASS**  
**Master Blueprint mapping:** **TECH-WAVE STEP 11**

## W8-003 proven

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

W8-001 and W8-002 remain PASS. This closure does not implement W8-004,
recovery, diagnostics, new UI or STEP 12 export.

## Gates

- targeted **9/9 PASS**;
- full pytest **411/411 PASS**;
- Ruff, mypy, import contracts, architecture, source-of-truth and no-secret PASS;
- UI references **42/42 PASS**;
- real-media evidence **23/23 PASS**;
- artifact ID `11513225118`;
- regression **27/27 workflow families SUCCESS, all attempt 1**.

Prior W5 microphone physical hardware and W6/W7 live Gemini remain provisional.

## W8-004 acceptance

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

## Accepted W8-005

- Accepted W8-005 implementation/regression HEAD: `43cb1d04b5d519c26f843714c4b7cd9793054fe9`.
- Windows autosave qualification: [37724812333](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37724812333) **SUCCESS**.
- Artifact `ANG-S11-W8-005-Autosave-Catalog`, ID `11526779061`; ZIP SHA-256 `c9a305ccc6cee9744e271e7520df4722192fa27a2a44544cf8ab68c717cf556c`.
- Dedicated catalog tests **9/9 PASS**; full pytest **429/429 PASS**; owned evidence **12/12 PASS**.
- Ruff, mypy (76 files), lint-imports, architecture, no-secrets, source-of-truth **70/70**, frozen UI **42/42 SHA-256 PASS**.
- Full same-HEAD regression **27/27 workflow families SUCCESS, all attempt 1**; Windows portable foundation PASS.
- New and legacy autosave filename compatibility, deterministic timestamp ordering, validated per-project catalog, maximum **20** managed valid snapshots, corrupt/foreign isolation and write/unlink failure guards qualified.
- Source `.angproj` and `.bak` are never retention/prune targets; source bytes unchanged in evidence. UI-039 recovery is deferred to W8-006.

## W8-006 acceptance

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

## W8-007 accepted proof

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

## Exact next action

**S11-W8-009 — Structured Diagnostics + Redacted Diagnostic Bundle — IN_VERIFICATION.**
W8-010 remains serial-blocked. W5 physical microphone and W6/W7 live Gemini
tests remain provisional; no physical/provider smoke success is invented.
No W8-009 implementation was started during W8-008 closure.

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

## Exact next action

**S11-W8-010 — Frozen UI Wiring + GOLDEN-03 Recovery/Relink Closure +
Regression Lock — PASS.** W8-010 implementation and all regressions accepted at `45c3294f5a8c93cee17369fa4b95122e3fca035b`.
W5 physical microphone and W6/W7 live Gemini remain provisional.

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

## Post-W8 quality fix — project-open malformed JSON (2026-10-08 WIB)

- Branch `fix/project-open-corrupt-json-fail-closed-20261008` from unchanged `main`: non-native bugfix for `JsonProjectRepository.load`, safe handling of corrupt nested track records, fixed-path-free `ProjectFormatError`, and preservation of existing session on failed open.
- Evidence: `docs/evidence/quality/PROJECT_OPEN_CORRUPTION_2026-10-08.md` and dedicated Windows full regression. Source commit `24af2d67` **PASS Windows** on [CI #37772403305](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37772403305): targeted/full pytest, Ruff, mypy, architecture, source-of-truth and UI manifest. Documentation update requires verification at its own HEAD. D1 Pilot A and product render unchanged; no portable or release.

## Project reopen integrity follow-up — strict JSON booleans (2026-10-08 WIB)

- On Draft PR #20, ensure invalid JSON strings/numbers/null cannot silently flip enabled/muted/locked/visible flags on reopen; source-of-truth v1 schema and frozen UI unchanged.
- Evidence: `docs/evidence/quality/PROJECT_OPEN_CORRUPTION_2026-10-08.md`. Windows CI on new HEAD pending before PASS. No native FFmpeg or portable work.

## PR #20 — Project load Unicode/atomicity hardening (8 Oct 2026 WIB)

- Unpaired Unicode surrogate escapes in a valid JSON file could pass decode then fail `semantic_hash` after `ProjectSession.open_project` began replacing the active session. Validate canonical hashing inside repository load and hash before session mutation; add synthetic-invalid-repository and valid-existing-project regression tests. Evidence in `docs/evidence/quality/PROJECT_OPEN_CORRUPTION_2026-10-08.md`.
- **PENDING current-head Windows CI**, source schema/UI/main/FFmpeg execution unchanged; PR #20 remains Draft, portable last.

## PR #20 — Save As / autosave recovery atomicity check (2026-10-08 WIB)

- `ProjectSession.save` now computes semantic identity before any repository write or path rebind; `recover_snapshot` verifies source/snapshot semantic identities before adopting a recovered session. Regression tests simulate a returning-invalid repository and a saving adapter that would write before hash validation. No project schema change, UI change, native FFmpeg execution, release or main merge.
- Evidence in `docs/evidence/quality/PROJECT_OPEN_CORRUPTION_2026-10-08.md`. **Current-head Windows CI pending**; earlier PR #20 CI alone does not qualify this change.

## Post-W8 GUI open preinspection regression (2026-10-08 WIB)

- Existing saved editor project no longer closes before asynchronous recovery inspection of another chosen `.angproj`. Malformed/missing targets leave the active session/marker intact; duplicate open of same path ignored. Qt targeted+full Windows tests added on PR #20; status **PENDING latest-head CI**. No visual UI change; Pilot A D1 pending, no main merge or portable.
## PR #20 — Qt staged project replacement (2026-10-08 WIB)

- Cross-project switch now stages final RecoveryManager source/snapshot decision and crash marker on a temporary candidate session BEFORE retiring the current live project. Stale offers and failed marker write cannot remove the active editor state; successful candidate promotion closes the prior session and marker. New Qt tests: staleness, marker denial, successful switch. **Current-head Windows CI PENDING**; no UI structural change, Pilot A D1 still pending, no main merge/release.

## PR #20 — Guard crash-marker close before in-memory session release (2026-10-08 WIB)

- Fix `RecoveryManager.close_clean` ordering: validate dirty-state, persist clean marker, then release memory; if marker write fails, original project remains open. An unexpected close failure attempts marker rollback. New unit+Qt fault-injection tests; current-head Windows CI pending. No new visual UI, `main` merge or FFmpeg pilot authority.

## W8 project opening from Home navigates into existing editor (2026-10-08 WIB)

- PR #20 corrects the successful `.angproj` open/recovery flow to enter existing Editor Overview `UI-010`. Failed opens remain on `UI-002`. Two Qt regression tests cover success/failure without changing any frozen UI art/layout. **New-head CI PENDING**; `main` untouched and no Pilot A FFmpeg production work.

## PR #20 — Prevent phantom project creation through UI-003 wizard (2026-10-08 WIB)

- UI-003 Continue previously navigated to editor while runtime ignored the `NEW_PROJECT` intent. It now passes a selected DOCX path to runtime and refuses to open a fictitious editor session until a true DOCX scene/asset importer is built. Status is explicit and file-project state remains intact. Two Qt regressions added. **Current-HEAD Windows CI pending**; no design/engine/main changes.
