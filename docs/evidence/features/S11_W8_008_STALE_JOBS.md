# S11-W8-008 — Stale Result Hardening for W8 Background Jobs

**Status: IN_VERIFICATION — NOT PASS**  
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

**Next:** complete W8-008 qualification. Do NOT start W8-009.
