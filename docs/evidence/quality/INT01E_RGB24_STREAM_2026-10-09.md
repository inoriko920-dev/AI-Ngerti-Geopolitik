# INT-01E — CPU-only verified PNG to bounded RGB24 chunks

Date: 2026-10-09 WIB
Scope: Draft PR #20. No main merge, no native engine, no UI or portable.

The INT-01D H.264 plan now feeds a pure in-memory RGB888 converter.
The qualified PNG sequence carries a verified SHA-256 and encoded byte count
for every frame. Each frame is rehashed immediately before decoding from an
in-memory QByteArray, avoiding silent reuse of files changed after planning.
Pixel values are emitted in exact frame order as tightly packed RGB24 blocks;
Qt row stride padding is deliberately excluded.

The scanline generator returns up to 64 rows in a block and holds at most one
decoded frame in memory at once. Per-input limits: 128 MiB PNG, 16 million
pixels, even dimensions from 2 through 8192, and exactly 30 or 60 FPS.
Output MP4 files are not written, and FFmpeg is never executed.

Tests render real SINGLE red and DOUBLE green/blue frames, then validate
the exact byte stream against reference colors and scene boundaries.
Additional regressions test corrupt/missing/reordered PNGs, late changes,
and invalid row limits. New targeted Windows job plus existing full pytest,
Ruff, mypy, architecture/source-of-truth/secrets and 42 frozen UI
reference gates are required before INT-01E is marked PASS.

Remaining: external FFmpeg Pilot A approval, real RGB pipe writer, subprocess
cancellation and timeout, staged MP4 publication, independent codec/frame
postflight, audio/subtitle/effects parity, GUI export, portable release.
The runner will need to recheck the project and sources during its
own authorized execution. Frame blocks already yielded cannot be revoked.
