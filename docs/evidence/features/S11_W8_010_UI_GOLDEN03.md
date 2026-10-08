# S11-W8-010 — Live UI Wiring + GOLDEN-03 Closure

**Status: IN_VERIFICATION — NOT PASS**  
**Dedicated Windows CI:** `.github/workflows/s11-wave8-010-ui-golden03.yml`

## Implemented (waiting for QA)
- Frozen UI-039 recovery, UI-040 Asset Scan and UI-041 Validation Center
  project-bound MainWindow rendering adapters without changing UI raster references.
- Product-only bootstrap `W8RuntimeController` uses existing
  ProjectSession, ValidationService, RelinkScanJobService and RecoveryManager.
- Nonblocking UI validation via W8-008 stale-token worker, scan progress/cancel,
  manually approved SHA-confirmed relink through canonical CommandBus.
- Startup project-open inspects validated autosaves in background;
  explicit source/restore/ignore, dirty recovered working state until Save.
- Five Qt controller tests and real FFprobe GOLDEN-03 script with captured
  Qt images, clean save/reopen and Undo/Redo, crash recovery and diagnostic ZIP.

## Mandatory acceptance (pending)
Ruff, mypy, imports, architecture, no-secret and 42/42 frozen UI references;
targeted/full pytest; real-media evidence verifier; exact saved project,
no silent overwrite; Windows portable; all previous workflow families
on one code HEAD. No STEP 12 and no AAVC mutation.

## Formatter qualification

Pinned Ruff 0.16.10 auto-format completed successfully and the temporary
format workflow was removed. The scoped Windows W8-010 quality, Qt and
real GOLDEN-03 proof remains pending; this is NOT a PASS assertion.
