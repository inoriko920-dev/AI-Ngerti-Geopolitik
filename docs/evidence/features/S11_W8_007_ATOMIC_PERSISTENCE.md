# S11-W8-007 — Atomic Persistence Failure Injection + Remediation

**Status:** PASS  
**Accepted implementation/regression HEAD:** `130407dc728b6417c30dbbc935ecd9b04d37ba43`  
**Windows CI:** [37727525574](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37727525574) — SUCCESS  
**Artifact:** `ANG-S11-W8-007-Atomic-Persistence`, ID `11528930146`  
**Artifact SHA-256:** `5cf537b7ec5fcf7043c2a0fe640d3f7d9008d2e60209b712c0d81ca06a95be91`

## Actual defect and narrow remediation

Before W8-007, `JsonProjectRepository._write` registered `temp_path`
only after payload write, flush and fsync. Injected early disk/write failures
could leave orphan `.tmp` files.

The existing serializer/repository ownership is retained. The fix registers
the temporary file immediately and cleans source and backup staging temp
files on failure. The source remains atomically published only after the
backup has been prepared. If the file is not committed, `ProjectSession`
keeps dirty state and retains its original canonical source binding.

The application provides typed `PersistenceError` stages and
`persistence_error_projection`: safe actionable Indonesian messages with
no raw absolute paths/OS error strings. Invalid extensions are rejected
before destination directories are created.

## Qualified fault matrix

- Temporary file creation failure and partial payload write failure.
- Temporary write/sync/fsync failure and cleanup of orphan temp files.
- Backup stage temporary creation, copy failure and backup replace failure.
- Atomic source replacement failure with byte-identical pre-existing source.
- Failed initial Save / Save As: no fake project file or session path rebind.
- Old backup bytes or current-source backup remain readable through failures.
- Failed `save_snapshot`: no phantom recovery output or source change.
- Unlink cleanup denied: typed failure rather than false success.
- Intended state survives in session, and retry saves exact new data with
  previous canonical version in `.bak`.
- No scope expansion into W8-008 stale-result orchestration.

## Windows acceptance

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

## Follow-up

S11-W8-008 — Stale Result Hardening for W8 Background Jobs — READY.
W8-009..010 remain blocked. No UI-001..UI-042 structural delta,
ProjectState schema change, or AAVC repo mutation.
