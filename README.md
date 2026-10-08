# AI Ngerti Geopolitik

> **STATUS: SF-STEP 11 ACTIVE — W7 CLOSED PROVISIONAL LIVE GEMINI — W8-001..003 PASS — W8-004 IN_VERIFICATION**

Repository resmi aplikasi **AI Ngerti Geopolitik**.

Baca `AGENTS.md`, `docs/SOURCE_OF_TRUTH_INDEX.md` dan `HANDOFF.md`.

## W8 — Validation / Recovery / Diagnostics

Completed:
- W8-001 Canonical Validation Contracts + Baseline Rules = **PASS**;
- W8-002 Real Media Integrity + Validation Center Projection = **PASS**;
- W8-003 Single Asset Relink Command + Exact Identity Preservation = **PASS**.

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

## Next

W8-004 bounded asynchronous directory scan, deterministic proposal ranking,
explicit-only verified batch relink, stale protection and UI-040 progress projection
are implemented. Code: [`4988e84c`](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/commit/4988e84ca6bca1e64fc5a755ff0d3287802e70f8).
**Gate: IN_VERIFICATION, not PASS**. Current dedicated Windows run:
[`37721840504`](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37721840504).
See `docs/evidence/features/S11_W8_004_BATCH_RELINK_SCAN.md`.

**Next:** finish W8-004 Windows tests, real-media evidence and regression closure.
Do not start W8-005. UI-001..UI-042 remain frozen; AAVC is read-only.
