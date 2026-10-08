# PLAN — CURRENT IMPLEMENTATION PHASE

**SF-STEP 11 remains active. W7 is CLOSED. W8 is ACTIVE.**

## W8 — Validation / Recovery / Diagnostics Hardening

**Status:** CONTRACT_LOCKED / W8-001..003 PASS / W8-004 IN_VERIFICATION  
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
4. W8-004 Batch Directory Relink Scan + Candidate Ranking — **IN_VERIFICATION**
5. W8-005 Autosave Catalog + Retention Hardening — **BLOCKED**
6. W8-006 Crash Marker + Startup Recovery Decision — **BLOCKED**
7. W8-007 Atomic Persistence Failure Injection + Remediation — **BLOCKED**
8. W8-008 Stale Result Hardening — **BLOCKED**
9. W8-009 Structured Diagnostics + Redacted Diagnostic Bundle — **BLOCKED**
10. W8-010 Frozen UI Wiring + GOLDEN-03 Closure + Regression Lock — **BLOCKED**

## Exact next action

Code `4988e84ca6bca1e64fc5a755ff0d3287802e70f8` implements W8-004 but the CI/evidence/regression gate has
not been accepted. Dedicated latest Windows workflow: `37721840504` (pending).
Finish W8-004 verification first; **do not start W8-005**.
