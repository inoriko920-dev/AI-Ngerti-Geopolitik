# S11-W8-004 — BATCH DIRECTORY RELINK SCAN + CANDIDATE RANKING

**Status: IN_VERIFICATION — NOT PASS**  
**Latest W8-004 implementation code:** `4988e84ca6bca1e64fc5a755ff0d3287802e70f8`  
**Dedicated Windows qualification run:** [`37721840504`](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37721840504) — pending  
**Master Blueprint:** TECH-WAVE STEP 11; W8 serial contract.

## Implemented (source-level, awaiting final CI)

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

## QA history and pending gate

- Pre-fix run `37721605589` passed lint/mypy/imports but failed targeted Qt
  weak-candidate checkbox, after 8/9 tests succeeded.
- This defect was corrected on `4988e84ca6bca1e64fc5a755ff0d3287802e70f8` by explicitly removing Qt's
  default user-checkable flag for unverified candidates.
- Latest `37721840504` must pass targeted and full pytest, real relocation,
  evidence verifier, security/architecture/UI manifest and all prior workflow
  families on a single accepted commit before W8-004 can become PASS.
- No production real-media or full-regression PASS is claimed yet.

## Next exact task

Finish W8-004 gates and write a closure evidence record with workflow IDs, exact
test counts, artifact ID and scope. Do not start W8-005.
