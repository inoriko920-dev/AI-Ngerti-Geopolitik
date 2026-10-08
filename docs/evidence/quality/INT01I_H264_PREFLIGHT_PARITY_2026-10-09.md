# INT-01I — Align dry-run preflight with RGB24 decoder ceilings

Date: 2026-10-09 WIB
PR #20 Draft; main unchanged.

## Verified implementation defect
Before this patch, INT-01D returned `DRY RUN PASS` for dimensions
that exceeded INT-01E's hard maximum of 8192 pixels on either axis
(even when total pixels stayed within 16 million). It likewise did
not reject source PNG sizes exceeding INT-01E's per-frame 128 MiB
limit. Such plans would fail only at the later RGB24 streaming stage.

## Fix
- Silent H.264 planning now enforces 8192 pixels per axis and an
  encoded PNG maximum of 128 MiB per frame, consistently with the
  stream's actual input contract.
- The planner checks per-frame digest and byte-count tuple lengths
  before advertising a qualified future encode plan.
- Regression tests inject verified-sequence metadata representing
  oversized axis dimensions, oversized compressed frame size, and
  truncated checksum metadata. All must fail closed before encoding.
- No codec executable is chosen; no FFmpeg run or MP4 write occurs.

## Still blocked
The owner-controlled Pilot A native FFmpeg/FFprobe run is not
authorized, so MP4 generation, native process termination, output
postflight, audio/subtitle/effects, release and portable packaging
remain pending. Do not merge the Draft PR without explicit consent.

Gate: Windows targeted tests + full pytest + Ruff, mypy, architecture,
source-of-truth, secrets and 42 frozen UI references.
