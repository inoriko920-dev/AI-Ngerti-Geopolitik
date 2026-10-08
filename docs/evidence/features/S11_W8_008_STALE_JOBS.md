# S11-W8-008 — Stale Result Hardening for W8 Background Jobs

**Status: PASS**  
**Accepted code/regression HEAD:** `6c35b70bd9122664473a69eff6635ed9b71da5cb`  
**Dedicated Windows workflow:** [37728798520](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37728798520) — SUCCESS  
**Scope:** W8-008 only; W8-009 remains blocked.

## Implementation
- `ProjectSession.session_id` rotates at each New/Open/Recover and clears on Close.
- `ProjectJobToken` verifies canonical project ID, lifecycle session ID, revision and semantic SHA-256.
- `ReadOnlyProjectJobs` runs validation and recovery inspection in a bounded read-only worker. Stale/cancelled results cannot be resolved.
- `RelinkScanJobService` reuses the shared token and treats closed sessions as stale.
- No duplicate project store, CommandBus, serializer or UI redesign.
- 12 owned unit tests exercise manual edits during scans, close/open same and different project, cancellation with late worker completion, validation acceptance and recovery-result discard.
- Owned concurrency evidence runner and strict verifier are checked on Windows CI.

## QA gate
Ruff, mypy, lint-imports, architecture, source-of-truth, 42 frozen UI SHA-256 references, targeted/full pytest, owned evidence and all previous workflow families at the same accepted code HEAD must PASS.

## W8-008 acceptance

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

## Next exact task

S11-W8-009 — Structured Diagnostics + Redacted Diagnostic Bundle — READY.
W8-010 remains blocked. No UI bitmap redesign, schema change or AAVC mutation.

