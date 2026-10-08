# AI Ngerti Geopolitik

> **STATUS: SF-STEP 11 ACTIVE — W7 CLOSED PROVISIONAL LIVE GEMINI — W8-001..003 PASS — W8-004..005 PASS — W8-006 PASS — W8-007 PASS — NEXT W8-008**

Repository resmi aplikasi **AI Ngerti Geopolitik**.

Baca `AGENTS.md`, `docs/SOURCE_OF_TRUTH_INDEX.md` dan `HANDOFF.md`.

## W8 — Validation / Recovery / Diagnostics

Completed:
- W8-001 Canonical Validation Contracts + Baseline Rules = **PASS**;
- W8-002 Real Media Integrity + Validation Center Projection = **PASS**;
- W8-003 Single Asset Relink Command + Exact Identity Preservation = **PASS**;
- W8-004 Batch Directory Relink Scan + Candidate Ranking = **PASS**;
- W8-005 Autosave Catalog + Retention Hardening = **PASS**.

Verified W8-003 implementation/regression:
`25e5f6cefbbef5f554bd17e64d50a61db948bf13`

Workflow:
[37689420848](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37689420848) — SUCCESS.

Proof:
- stable asset identity, exact clip references;
- verified candidate, rejected incompatible media/path conflict;
- exact Undo/Redo, save/reopen and real-media relink validation;
- targeted 9/9 tests, full 411/411 tests and evidence 23/23 PASS;
- 27/27 workflow regression families SUCCESS on the same HEAD.

Evidence: `docs/evidence/features/S11_W8_003_SINGLE_ASSET_RELINK.md`.  
Artifact: `ANG-S11-W8-003-Single-Asset-Relink` / ID `11513225118`.

## W8-004 accepted

W8-004 validated scanner, verified explicit relink and UI-040 projection remain
accepted. Full evidence: `docs/evidence/features/S11_W8_004_BATCH_RELINK_SCAN.md`.

## W8-005 accepted

- Accepted W8-005 implementation/regression HEAD: `43cb1d04b5d519c26f843714c4b7cd9793054fe9`.
- Windows autosave qualification: [37724812333](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37724812333) **SUCCESS**.
- Artifact `ANG-S11-W8-005-Autosave-Catalog`, ID `11526779061`; ZIP SHA-256 `c9a305ccc6cee9744e271e7520df4722192fa27a2a44544cf8ab68c717cf556c`.
- Dedicated catalog tests **9/9 PASS**; full pytest **429/429 PASS**; owned evidence **12/12 PASS**.
- Ruff, mypy (76 files), lint-imports, architecture, no-secrets, source-of-truth **70/70**, frozen UI **42/42 SHA-256 PASS**.
- Full same-HEAD regression **27/27 workflow families SUCCESS, all attempt 1**; Windows portable foundation PASS.
- New and legacy autosave filename compatibility, deterministic timestamp ordering, validated per-project catalog, maximum **20** managed valid snapshots, corrupt/foreign isolation and write/unlink failure guards qualified.
- Source `.angproj` and `.bak` are never retention/prune targets; source bytes unchanged in evidence. UI-039 recovery is deferred to W8-006.

Evidence: `docs/evidence/features/S11_W8_005_AUTOSAVE_CATALOG.md`.

**Next:** S11-W8-008 — Stale Result Hardening for W8 Background Jobs — READY.
W8-007 remains BLOCKED. UI-001..UI-042 frozen, AAVC read-only.

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

Evidence: `docs/evidence/features/S11_W8_006_CRASH_RECOVERY.md`.

**Next:** SOL S11-W8-007 only, when owner says `lanjutkan`.
W8-008 remains blocked; source `.angproj` and `.bak` are protected.

## W8-007 — Atomic Persistence Fault Injection — PASS

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

Evidence: `docs/evidence/features/S11_W8_007_ATOMIC_PERSISTENCE.md`.

**Next:** S11-W8-008 — Stale Result Hardening for W8 Background Jobs —
READY. W8-009 remains blocked. UI-001..042 frozen and AAVC read-only.
