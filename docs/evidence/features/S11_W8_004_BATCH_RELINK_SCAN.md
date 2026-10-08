# S11-W8-004 — BATCH DIRECTORY RELINK SCAN + CANDIDATE RANKING

**Status: PASS**  
**Latest W8-004 implementation code:** `4988e84ca6bca1e64fc5a755ff0d3287802e70f8`  
**Dedicated Windows qualification run:** [`37721840504`](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37721840504) — SUCCESS  
**Master Blueprint:** TECH-WAVE STEP 11; W8 serial contract.

## Verified implementation

- `application/relink_scan.py`: single background worker, bounded scan lifecycle,
  typed immutable proposal/snapshot, progress, cancel, project/session/revision +
  same-revision semantic-hash stale guards.
- `infrastructure/relink_scan.py`: deterministic recursive directory traversal,
  restricted to explicit root, no symlink follow, media-extension allowlist,
  max file/depth/directory bounds.
- `RelinkService.verify_candidate` reused for final re-probe before mutation;
  strict fingerprint + metadata check; duplicate asset/path selections rejected.
- Rank order: original canonical basename, saved source_name, exact SHA-256,
  metadata-only. Ranking is advisory; exact fingerprint is mandatory to enable
  selection or canonical application.
- Explicit multi-asset choices commit as one CommandBatch via existing
  RelinkAssetCommand, preserving Asset IDs/clip links and Undo/Redo.
- `presentation/asset_scan.py` projects UI-040 progress, ranked rows and
  Start/Cancel/Apply intents. Weak/unverified candidates cannot be checked.
  Full app-controller wiring is reserved for W8-010.
- Nine targeted tests defined across
  `tests/unit/test_step11_w8_004_relink_scan.py` and
  `tests/qt/test_step11_w8_004_asset_scan.py`.
- Real-media FFmpeg/ffprobe script
  `scripts/run_step11_w8_004.py` and 14-check verifier,
  `scripts/verify/verify_step11_w8_004_evidence.py`.
- Dedicated Windows pipeline:
  `.github/workflows/s11-wave8-004-batch-scan.yml`.

## Qualification and regression closure

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

Prior test failures were corrected and re-qualified at the accepted HEAD.
All 27 workflow families succeeded on their first attempt. This closure changes
no production media, no source project and no UI raster.

## Scope boundary

W8-005 autosave catalog, W8-006 crash decision and W8-009 diagnostics
have **not** been implemented by W8-004. W8-010 owns full application
controller binding of the frozen UI-040 shell.

## Next exact task

S11-W8-005 — Autosave Catalog + Retention Hardening — READY.
