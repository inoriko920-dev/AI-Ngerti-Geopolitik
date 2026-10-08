# S11-W8-007 — Atomic Persistence Failure Injection + Remediation

**Status:** IN_VERIFICATION — not PASS  
**Planning:** locked ASTRA W8 planning §10.7  
**Dedicated Windows CI:** `.github/workflows/s11-wave8-007-atomic-persistence.yml`

## Bug observed by source inspection

Previous `JsonProjectRepository._write` registered `temp_path`
**after** payload write, flush and fsync. An interrupted partial write
or fsync could therefore create an untracked and unremoved `.tmp` file.

## Minimal remediation

- Retain existing `ProjectRepositoryPort`, `JsonProjectRepository`
  serializer, `ProjectState`, `ProjectSession` and `CommandBus` ownership.
- Register newly opened source temp immediately; restore guaranteed
  cleanup on write/sync/backup/replace exceptions.
- Preserve source bytes exactly on failed Save; retain a readable `.bak`.
- Failures are represented by application-level typed `PersistenceError`
  with safe, actionable Indonesian projection — no OS path or secret leak.
- Invalid extension is rejected before creating target directories.
- Incomplete commits leave `ProjectSession.dirty` set; retry persists
  intended state, with source backup of prior canonical bytes.
- `save_snapshot` is tested independently to avoid phantom recovery data.
- Inject 7 failure stages with parametrized tests plus lifecycle/fault tests
  (15 planned targeted cases in total). Deterministic evidence asserts
  source integrity and successful retry.

## QA gate (pending)

Windows: Ruff, mypy, import contracts, architecture, source-of-truth,
no-secrets, frozen UI SHA-256 manifest, targeted/full pytest,
owned failure evidence verifier, and all previous workflow families at one
accepted implementation HEAD. W8-008 remains blocked.
