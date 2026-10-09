# ANG INT-01C — PNG-to-encoder integrity handoff

Date: 2026-10-09 WIB  
Status: IMPLEMENTED ON DRAFT PR #20; WINDOWS CI PENDING ON EXACT COMMIT

## Scope

The existing image-only project export writes immutable-looking, bounded
\`frames-all\` PNG batches and nested SHA-256 manifests. Before any future
MP4 encoder consumes that directory, an independent **read-only verifier**
must check actual bytes against both manifests and the saved canonical project.

Added:

- \`infrastructure/still_sequence_verification.py\` offers
  \`verify_complete_still_sequence(state, root)\`, returning a typed, ordered
  \`VerifiedStillSequence\` only after every check succeeds.
- Checks exact zero-based contiguous frame ranges, canonical filenames/batch
  directory names, declared FPS/project identity/semantic SHA, per-batch
  manifest SHA-256, per-frame file size/SHA-256 and PNG header dimensions.
- Enforces explicit bounds (18,000 frames, 8 GiB), strict integer types and
  rejects path traversal attempts by deriving paths rather than using names
  from untrusted manifests. Rejects symlinks, absent frames and extra files.
- Re-checks every original scene source image at clip boundaries against
  the persisted project fingerprint before handing off ordered frame paths.
- \`scripts/verify_still_frames.py --project film.angproj --frames frames\`
  reports PASS/FAIL in Indonesian. It does **not** encode an MP4 or execute
  any native process, write to the project, alter UI or overwrite frames.

## Acceptance

Tests: \`tests/unit/test_still_sequence_verification.py\` plus full Windows
Ruff, mypy, lint-imports, architecture/source-of-truth/secrets, frozen 42 UI
checks, Qt and pytest regressions. Do not mark final PASS until CI on exact
latest HEAD finishes successfully.

## Outstanding and explicit permissions

The frame directory is **not** yet an MP4. Audio mix, subtitles, transition
parity, image animation, MLT/FFmpeg process execution, output postflight and
end-user UI Export are NOT qualified. The external FFmpeg Pilot A D1 requires
separate owner permission before execution.

PR #20 must remain Draft. Do not merge into \`main\` without owner approval.
Final Windows portable packaging remains last.
