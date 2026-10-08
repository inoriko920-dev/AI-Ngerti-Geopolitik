# W8 — VALIDATION / RECOVERY / DIAGNOSTICS HARDENING CONTRACT

**Status:** CONTRACT_LOCKED / W8-001..003 PASS / W8-004..005 PASS / W8-006 PASS / W8-007 PASS / W8-008 PASS / W8-009 PASS / W8-010 READY  
**Runtime:** ACTIVE  
**Master Blueprint mapping:** TECH-WAVE STEP 11  
**Planning date:** 2026-10-08  
**Planning baseline:** `a39c6c6d5941f69a2b5b662f26df94d82b7f94ac`  
**Accepted W7 implementation/regression HEAD:** `ca6dd582a4916caa4b0ac4affe4c3119e9ad2049`

Planning sources:
- `docs/planning/11_S11_W8_VALIDATION_RECOVERY_DIAGNOSTICS_HARDENING_CONTRACT_PLAN_2026-10-08.docx`
- `docs/planning/11_S11_W8_VALIDATION_RECOVERY_DIAGNOSTICS_HARDENING_CONTRACT_PLAN_2026-10-08.txt`

## Purpose

W8 hardens the existing product against missing/relocated/corrupt media, stale
background results, persistence failures, crash recovery and support diagnostics.
It adds no new editing family and does not enter Master Blueprint STEP 12 export work.

## Canonical owners

- `ProjectState`: canonical project truth.
- `CommandBus / CommandBatch`: only committed mutation/history owner.
- `ProjectSession`: lifecycle/dirty/open/save/autosave owner.
- `JsonProjectRepository`: atomic project persistence owner.
- `ValidationService`: non-mutating typed issue aggregation — **qualified W8-001**.
- `RelinkAssetCommand`: qualified canonical relink mutation preserving asset_id (W8-003).
- `RelinkService`: qualified verified candidate + canonical command construction (W8-003).
- planned `RelinkScanJobService`: background scan/hash/probe with stale token.
- planned `RecoveryCatalogService / RecoveryManager`: snapshot discovery/validation/retention/decision.
- planned `DiagnosticBundleService`: redacted diagnostics orchestration.
- presentation: projection/intent only; no direct infrastructure/project mutation.

No parallel project store, history owner, serializer, media identity or AI stale owner is allowed.

## Validation contract — W8-001 qualified

`ValidationIssue` and `ValidationResult` are transient frozen application DTOs,
never new ProjectState fields.

Severity:
- BLOCKER
- ERROR
- WARNING
- INFO

Scopes:
PROJECT, MEDIA, TIMELINE_SCENE, SUBTITLE, NARRATION, AI, RENDER, RUNTIME.

Result is bound to project ID + revision + semantic SHA-256.
Different project, changed revision or same-revision semantic replacement is STALE.

Canonical `Asset.availability` remains `online/offline/missing`.
CORRUPT/DUPLICATE remain derived validation/media-health projections; W8-002 real-media integrity is qualified.

Baseline:
- ProjectState.validate() remains structural authority;
- referenced missing = BLOCKER;
- referenced offline = ERROR;
- unreferenced missing = WARNING;
- unreferenced offline = INFO;
- validation is deterministic and non-mutating.

Accepted W8-001:
- HEAD `fd319947ea8ce2579de4918b5c4b49c046851609`;
- workflow `37681708473` SUCCESS;
- targeted 9/9 PASS;
- full pytest 395/395 PASS;
- evidence 22/22 PASS;
- regression 27/27 SUCCESS, all attempt 1;
- artifact `ANG-S11-W8-001-Validation-Contracts` / ID `11509960710`.

Evidence:
`docs/evidence/features/S11_W8_001_CANONICAL_VALIDATION_CONTRACTS.md`.

## Relink contract

Candidate ranking remains locked:
1. exact canonical Axxx basename + compatible probe;
2. exact source_name + compatible media/metadata;
3. exact SHA-256 fingerprint;
4. compatible metadata candidate = manual choice only.

Filename similarity alone never auto-applies. Relink preserves Asset ID and clip references.

## Recovery contract

Autosave never silently overwrites source. Default managed retention max 20 validated
snapshots/project. Source .angproj and .bak are never prune targets. Recovery remains explicit.

## Diagnostics contract

Structured diagnostics must redact credentials/private content and remain bounded.
Diagnostic bundle implementation is deferred to W8-009.

## Frozen UI reuse

No new UI image-generation gate:
- UI-039 — Pemulihan Project;
- UI-040 — Asset Scan;
- UI-041 — Validation Center.

## Serial implementation contract

- **W8-001 — Canonical Validation Contracts + Baseline Rules — PASS**
- **W8-002 — Real Media Integrity + Validation Center Projection — PASS**
- **W8-003 — Single Asset Relink Command + Exact Identity Preservation — PASS**
- W8-004 — Batch Directory Relink Scan + Candidate Ranking — PASS
- W8-005 — Autosave Catalog + Retention Hardening — PASS
- W8-006 — Crash Marker + Startup Recovery Decision — PASS
- W8-007 — Atomic Persistence Failure Injection + Remediation — PASS
- W8-008 — Stale Result Hardening for Validation/Relink/Recovery Jobs — PASS
- W8-009 — Structured Diagnostics + Redacted Diagnostic Bundle — PASS
- W8-010 — Frozen UI Wiring + GOLDEN-03 Recovery/Relink Closure + Regression Lock — IN_VERIFICATION

## Exact next action

Accepted W8-002:
- HEAD `c73a38d8fd6d3796f988769ca43354185eb66a6d`;
- workflow `37684517658` SUCCESS;
- targeted 7/7 PASS;
- full pytest 402/402 PASS;
- real ffprobe missing/zero/probe-failure/duplicate evidence PASS;
- frozen UI-041 projection + stale gating PASS;
- evidence 18/18 PASS;
- regression 27/27 SUCCESS, all attempt 1;
- artifact `ANG-S11-W8-002-Real-Media-Validation` / ID `11510448492`.

Evidence:
`docs/evidence/features/S11_W8_002_REAL_MEDIA_VALIDATION_CENTER.md`.

Accepted W8-003:
- HEAD `25e5f6cefbbef5f554bd17e64d50a61db948bf13`;
- workflow `37689420848` SUCCESS;
- targeted 9/9 PASS; full pytest 411/411 PASS;
- real relocated-media/Undo-Redo/save-reopen proof PASS; evidence 23/23 PASS;
- regression 27/27 SUCCESS, all attempt 1;
- artifact `ANG-S11-W8-003-Single-Asset-Relink` / ID `11513225118`.

Evidence:
`docs/evidence/features/S11_W8_003_SINGLE_ASSET_RELINK.md`.

Accepted W8-004:

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

## Accepted W8-005 evidence

- W8-005 accepted implementation/regression HEAD: `43cb1d04b5d519c26f843714c4b7cd9793054fe9`.
- Windows qualification workflow: `37724812333` — SUCCESS.
- Artifact: `ANG-S11-W8-005-Autosave-Catalog` ID `11526779061`;
  SHA-256 `c9a305ccc6cee9744e271e7520df4722192fa27a2a44544cf8ab68c717cf556c`.
- Targeted autosave tests **9/9 PASS**, full pytest **429/429 PASS**,
  owned evidence verifier **12/12 PASS**, frozen UI **42/42 PASS**.
- Ruff/mypy/imports/architecture/security/source-of-truth PASS.
- Same-HEAD regression **27/27 workflow families SUCCESS, all attempt 1**.
- Maximum 20 validated managed autosaves/project, legacy compatibility,
  corrupt isolation and writer/unlink failure injection PASS.
- Never prune source `.angproj`, `.bak`, or foreign project snapshots.

Next: **SOL S11-W8-006 only**. W8-007 remains blocked.

## W8-006 accepted

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

## Next

SOL S11-W8-007 only. W8-008 remains blocked. No unapproved UI redesign.

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

## Accepted W8-008

- Code HEAD `6c35b70bd9122664473a69eff6635ed9b71da5cb`; Windows `37728798520` SUCCESS.
- 12/12 targeted, 471/471 full pytest, 18/18 evidence, 27/27
  same-HEAD workflow regressions SUCCESS.
- Exact project/session/revision/hash guarding and cancellation safe,
  with no automatic canonical mutation or duplicate history.

## Next

**SOL S11-W8-009 only**. W8-010 remains blocked.

## W8-009 accepted

W8-009 accepted code HEAD `6a4ec93d445e71dc037bcc4dc6edff2008894268`.
Windows `37730435314` SUCCESS, artifact `11529353867`,
ZIP SHA-256 `17bc6c66063c240258f8f27fd68e8755ea8d26b63ba73a498c96e1f6e08d3b6e`.
Targeted **11/11**, full pytest **482/482**, evidence **18/18**,
frozen UI **42/42**, same-HEAD regression **27/27 SUCCESS**, all attempt 1.
Deterministic 128KiB max redacted ZIP contains fixed manifest/events only.
No raw paths, private content, credentials or media bytes.

**Next:** SOL S11-W8-010 only, after owner's `lanjutkan`.

## W8-010 implementation QA (pending)

Bootstrap product launch now binds typed UI-039/040/041 dialogs to real
ProjectSession, background validation and folder-scan workers, verified
manual CommandBus relink and explicit recovery. Fixture-mode screenshots
remain unchanged, preserving all 42 frozen reference images.

Five Qt runtime-wiring tests and a real Windows FFprobe GOLDEN-03 script cover
missing -> BLOCKER -> verified relink -> clean validation -> save/reopen,
crash snapshot recovery without source overwrite, and redacted diagnostic ZIP.
Dedicated workflow: `.github/workflows/s11-wave8-010-ui-golden03.yml`.
**Gate: IN_VERIFICATION, not PASS.** No STEP 12 implementation.
