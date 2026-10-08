# S11-W8-006 — Crash Marker + Startup Recovery Decision

**Status:** IN_VERIFICATION — not yet PASS.
**Planning:** locked W8 ASTRA planning §10.6.
**Dedicated CI:** `.github/workflows/s11-wave8-006-crash-recovery.yml`.

## Implemented, pending Windows qualification

- An atomic local crash marker with `clean`/`unclean` status binds to
  the resolved source path digest and project ID; corrupt markers fail closed.
- Startup `RecoveryManager.inspect` reads source via the existing repository,
  uses the W8-005 validated autosave catalog and offers only newer candidates.
- Choices are **OPEN_SOURCE**, **RECOVER_SNAPSHOT**, **IGNORE**, each explicitly
  executed. Ignore changes nothing. Selected recovery is revalidated by SHA-256,
  semantic hash, revision, and source identity before adoption.
- `ProjectSession.recover_snapshot` adopts a working CommandBus state bound
  to the original source path, forcibly dirty until a user explicitly saves.
  It does **not** call source persistence, rewrite `.angproj` or `.bak`.
- Clean close must pass the existing unsaved-change guard before an atomic
  marker status update.
- UI-039 recovery projection/dialog emits only semantic intents and requires
  explicit selection before a restore button is enabled. Full controller
  integration remains W8-010, not W8-006.
- 12 unit tests and 3 Qt tests cover abnormal termination, valid-fallback
  with corrupt newest, wrong-project isolation, stale source/snapshot,
  explicit Ignore/Open/Restore choices, clean close, and input validation.
- Owned crash simulation and strict evidence verifier provide source-byte proof.

## Gate

Ruff, mypy, import/architecture/security gates, 15 dedicated tests, full
pytest, owned crash evidence and same-HEAD regression must pass. **Do not
start W8-007 before W8-006 is formally accepted.**

## Formatting qualification

Pinned Ruff 0.16.10 formatting completed and temporary formatter removed.
Dedicated Windows QA and same-code regression are still pending; this note is NOT a PASS.
