# AI Ngerti Geopolitik

> **STATUS: SF-STEP 11 ACTIVE — W7 CLOSED PROVISIONAL LIVE GEMINI — W8-001..003 PASS — W8-004 PASS — NEXT W8-005**

Repository resmi aplikasi **AI Ngerti Geopolitik**.

Baca `AGENTS.md`, `docs/SOURCE_OF_TRUTH_INDEX.md` dan `HANDOFF.md`.

## W8 — Validation / Recovery / Diagnostics

Completed:
- W8-001 Canonical Validation Contracts + Baseline Rules = **PASS**;
- W8-002 Real Media Integrity + Validation Center Projection = **PASS**;
- W8-003 Single Asset Relink Command + Exact Identity Preservation = **PASS**;
- W8-004 Batch Directory Relink Scan + Candidate Ranking = **PASS**.

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

**Accepted W8-004 implementation/regression HEAD:** `4988e84ca6bca1e64fc5a755ff0d3287802e70f8`  
**Dedicated Windows workflow:** [37721840504](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37721840504) — SUCCESS  
**Artifact:** `ANG-S11-W8-004-Batch-Directory-Relink`, ID `11525753140`  
**Artifact SHA-256:** `75f33b72c4cf147d37b151e17bb7ae6bddc84982941f9f0aa8847c97d4fe4fb4`  
**Tests:** targeted 9/9 PASS; full pytest 420/420 PASS; real-media evidence 14/14 PASS  
**Gates:** Ruff, mypy (75 modules), import contracts, architecture, no-secret, source-of-truth 70/70, UI SHA 42/42 PASS  
**Full same-HEAD regression:** 27/27 workflow families SUCCESS, all attempt 1.

Verified: bounded worker scan, cancellation, stale project/session/revision/hash safety,
rank 1–4, SHA-256 verified explicit selection only, ambiguous candidate review,
one atomic CommandBatch, stable asset/clip IDs, exact Undo/Redo, save/reopen and
real-media validation. UI-040 projects intents; controller wiring remains W8-010.

Evidence: `docs/evidence/features/S11_W8_004_BATCH_RELINK_SCAN.md`.

**Next:** S11-W8-005 Autosave Catalog + Retention Hardening — READY.
UI-001..UI-042 remain frozen; AAVC is read-only.
