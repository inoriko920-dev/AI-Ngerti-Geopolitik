# PLAN — CURRENT IMPLEMENTATION PHASE

**SF-STEP 11 W8 closed / PASS. W7 is CLOSED. SF-STEP 12 is READY but NOT STARTED.**

## W8 — Validation / Recovery / Diagnostics Hardening

**Status:** CONTRACT_LOCKED / W8-001..010 PASS / W8 CLOSED  
**Master Blueprint:** TECH-WAVE STEP 11

## Accepted W8 tasks

- W8-001 — canonical deterministic validation; 9/9 targeted, 395/395 full,
  evidence 22/22 and regression 27/27 PASS.
- W8-002 — real media integrity + frozen UI-041; 7/7 targeted,
  402/402 full, evidence 18/18 and regression 27/27 PASS.
- W8-003 — canonical verified single-asset relink preserving exact identity.

W8-003 accepted implementation/regression HEAD:
`25e5f6cefbbef5f554bd17e64d50a61db948bf13`

W8-003 workflow: [37689420848](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37689420848) — SUCCESS.

W8-003 gates:
- 9/9 targeted, 411/411 full pytest, 23/23 real-media evidence PASS;
- exact Undo/Redo/save-reopen, type/fingerprint/metadata/path conflict rejection;
- frozen UI 42/42, security, architecture, lint, mypy PASS;
- regression 27/27 workflow families SUCCESS, all attempt 1.

See `docs/evidence/features/S11_W8_003_SINGLE_ASSET_RELINK.md`.

## Serial order

1. W8-001 — **PASS**
2. W8-002 — **PASS**
3. W8-003 — **PASS**
4. W8-004 Batch Directory Relink Scan + Candidate Ranking — **PASS**
5. W8-005 Autosave Catalog + Retention Hardening — **PASS**
6. W8-006 Crash Marker + Startup Recovery Decision — **PASS**
7. W8-007 Atomic Persistence Failure Injection + Remediation — **PASS**
8. W8-008 Stale Result Hardening — **PASS**
9. W8-009 Structured Diagnostics + Redacted Diagnostic Bundle — **PASS**
10. W8-010 Frozen UI Wiring + GOLDEN-03 Closure + Regression Lock — **PASS**

## W8-004 accepted

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

## W8-007 accepted

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

## Accepted W8-008

- Code/regression HEAD: `6c35b70bd9122664473a69eff6635ed9b71da5cb`.
- Windows workflow `37728798520` SUCCESS, artifact `11529365791`.
- 12/12 targeted, 471/471 full pytest, 18/18 evidence, 27/27
  regression workflow families SUCCESS, all first attempt.
- No UI redesign, canonical schema change, or second ProjectState store.

## Exact next action

On owner's explicit `lanjutkan`, **SOL W8-009 only**. W8-010 remains blocked.

## W8-009 accepted

W8-009 accepted code HEAD `6a4ec93d445e71dc037bcc4dc6edff2008894268`.
Windows `37730435314` SUCCESS, artifact `11529353867`,
ZIP SHA-256 `17bc6c66063c240258f8f27fd68e8755ea8d26b63ba73a498c96e1f6e08d3b6e`.
Targeted **11/11**, full pytest **482/482**, evidence **18/18**,
frozen UI **42/42**, same-HEAD regression **27/27 SUCCESS**, all attempt 1.
Deterministic 128KiB max redacted ZIP contains fixed manifest/events only.
No raw paths, private content, credentials or media bytes.

**Next:** On owner's next `lanjutkan`, SOL W8-010 only, no STEP 12.

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


## T03 acceptance and next serial handoff — 2026-10-08 WIB

SF12-T03 preflight code SHA `7bee32aae7248ae9023afe4b9b62bf2caf357095`, Windows workflow `37736630766` SUCCESS. Conservative profile gate and output safety checks are implemented and tested; **real render not enabled**. Exact next after explicit owner continuation: **SF12-T04 H264 baseline export only**, with genuine codec and media evidence, no API-breaking engine change without ASTRA/ADR.
