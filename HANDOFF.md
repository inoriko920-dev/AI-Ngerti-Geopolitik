# HANDOFF — AI NGERTI GEOPOLITIK

**Current phase:** SF-STEP 11 — Feature Implementation Waves  
**Current wave:** W8 — Validation / Recovery / Diagnostics Hardening  
**Last completed task:** S11-W8-008 — PASS  
**Accepted implementation/regression HEAD:** `130407dc728b6417c30dbbc935ecd9b04d37ba43`  
**Accepted W8-003 workflow:** [37689420848](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37689420848) — SUCCESS  
**Current implementation:** S11-W8-005 — PASS
**Last implementation:** S11-W8-006 — Crash Marker + Startup Recovery Decision — PASS
**Last implementation:** S11-W8-007 — Atomic Persistence Failure Injection + Remediation — PASS
**Last implementation:** S11-W8-008 — Stale Result Hardening for W8 Background Jobs — PASS
**Next exact task:** S11-W8-009 — Structured Diagnostics + Redacted Diagnostic Bundle — READY

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

When owner explicitly says `lanjutkan`, execute **SOL S11-W8-009 ONLY**
under locked ASTRA W8 planning: structured diagnostics + bounded redacted
ZIP manifest, private content/credentials never bundled by default.
W8-010 remains blocked. Do not enter W8-010 within W8-009.

## Provisional gates

W5 microphone physical hardware and W6/W7 live Gemini network tests remain
provisional; do not claim device/provider smoke results that were not run.



