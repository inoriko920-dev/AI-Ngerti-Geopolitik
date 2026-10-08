# S11-W8-010 — Live UI Wiring + GOLDEN-03 Closure

**Status:** PASS / W8 CLOSED / SF-STEP 11 FEATURE WAVES CLOSED
**Accepted implementation/regression HEAD:** `45c3294f5a8c93cee17369fa4b95122e3fca035b`
**Dedicated Windows CI:** [37732709194](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37732709194) — SUCCESS
**Artifact:** `ANG-S11-W8-010-UI-GOLDEN03` / ID `11530068997`
**Artifact ZIP SHA-256:** `4a24f45f3c6ef6d73924ec83d0ea2149b1490119abb766dd079d6db2a5840241`

## Qualified implementation

- Frozen UI-039 recovery, UI-040 Asset Scan and UI-041 Validation Center
  bound to real project and media state in the existing MainWindow.
- Product bootstrap W8RuntimeController routes UI intents to existing
  ProjectSession, ValidationService, RelinkScanJobService and RecoveryManager.
- Media validation occurs in background stale-checked jobs; worker progress
  is reflected on UI-040 without freezing the Qt event loop.
- Asset relinking requires explicit selection of an exact SHA-256-verified
  candidate; canonical changes go through CommandBus, with Undo/Redo.
- Crash recovery offers original, validated newer snapshot, or ignore;
  it never saves recovered source automatically. Original project bytes
  remain untouched until an explicit Save.
- Support diagnostic ZIP is bounded and redacted; frozen UI manifests
  and AAVC repo unchanged.
- FFprobe is resolved lazily only for real probe calls, preventing missing
  FFprobe from blocking Qt app startup and pure fake-probe unit/Qt tests.

## Windows qualification and regression evidence

**W8-010 accepted implementation and same-HEAD regression:** `45c3294f5a8c93cee17369fa4b95122e3fca035b`.

- [Windows W8-010 UI/GOLDEN-03 run](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37732709194): **SUCCESS**.
- Artifact `ANG-S11-W8-010-UI-GOLDEN03`, ID `11530068997`, size 11,387,537 bytes.
- Artifact ZIP SHA-256: `4a24f45f3c6ef6d73924ec83d0ea2149b1490119abb766dd079d6db2a5840241`.
- **5/5** targeted Qt controller tests, **487/487** full Python suite, **23/23** owned GOLDEN-03 evidence checks PASS.
- Ruff, mypy **85 source files**, lint-imports, architecture and no-secret checks PASS; source-of-truth **70/70** PASS.
- Frozen UI-001..042 manifest **42/42 SHA-256 PASS** — no raster redesign or AAVC source changes.
- **27/27** same-code-HEAD workflow families **SUCCESS on attempt 1**, including S08 portable foundation, S09 UI shell, S10 real Windows E2E, W0-W7 and W8.
- Demonstrated live UI-041 missing referenced media BLOCKER, UI-040 bounded worker discovery and fingerprint-verified manual relink, canonical CommandBus/Undo-Redo, revalidation, save/reopen, UI-039 explicit crash snapshot restoration without silent source overwrite, and redacted diagnostic ZIP.
- Fixed a real compatibility regression: FFprobe is initialized lazily only during a media probe, so the Qt shell and fake-probe tests do not require an installed FFprobe.
- W5 physical microphone and W6/W7 live Gemini qualification remain provisional, not claimed as PASS.

## Scope and remaining provisional qualifications

W8 is CLOSED. All W8-001..010 tasks are PASS. SF-STEP 12 has not started;
W5 hardware microphone and W6/W7 live Gemini qualification remain
provisional. No unsupported provider/device PASS is implied.

## Next exact task

SF-STEP 12 — read the locked Software Factory STEP 12 contract and determine
one serial task only on owner's next explicit `lanjutkan`.
