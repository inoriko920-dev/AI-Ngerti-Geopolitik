# PLAN — CURRENT IMPLEMENTATION PHASE

**SF-STEP 11 remains active. W7 is CLOSED. W8 is ACTIVE.**

## W8 — Validation / Recovery / Diagnostics Hardening

**Status:** CONTRACT_LOCKED / W8-001..006 PASS / W8-007 READY  
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
7. W8-007 Atomic Persistence Failure Injection + Remediation — **READY**
8. W8-008 Stale Result Hardening — **BLOCKED**
9. W8-009 Structured Diagnostics + Redacted Diagnostic Bundle — **BLOCKED**
10. W8-010 Frozen UI Wiring + GOLDEN-03 Closure + Regression Lock — **BLOCKED**

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

## Exact next action

W8-005 accepted:
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

## Exact next action

On owner's **lanjutkan**, SOL S11-W8-007 only. W8-008 remains blocked.
