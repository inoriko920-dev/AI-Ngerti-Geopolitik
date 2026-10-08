# PLAN — CURRENT IMPLEMENTATION PHASE

**SF-STEP 11 remains active. W7 is CLOSED. W8 is ACTIVE.**

## W8 — Validation / Recovery / Diagnostics Hardening

**Status:** CONTRACT_LOCKED / W8-001..003 PASS / W8-004 READY  
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
4. W8-004 Batch Directory Relink Scan + Candidate Ranking — **READY**
5. W8-005 Autosave Catalog + Retention Hardening — **BLOCKED**
6. W8-006 Crash Marker + Startup Recovery Decision — **BLOCKED**
7. W8-007 Atomic Persistence Failure Injection + Remediation — **BLOCKED**
8. W8-008 Stale Result Hardening — **BLOCKED**
9. W8-009 Structured Diagnostics + Redacted Diagnostic Bundle — **BLOCKED**
10. W8-010 Frozen UI Wiring + GOLDEN-03 Closure + Regression Lock — **BLOCKED**

## Exact next action

Wait for a new owner `lanjutkan`, then execute **SOL S11-W8-004 only**.
Do not begin W8-005 in the same turn.
