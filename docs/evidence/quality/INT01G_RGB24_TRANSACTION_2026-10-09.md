# INT-01G — Synthetic transactional RGB24 handoff

Date: 2026-10-09 WIB  
Branch: PR #20 Draft  
Native FFmpeg Pilot A: **NOT APPROVED**

## Scope
Implement a cooperative timeout for the already-qualified RGB24 sink and
a mockable two-phase sink lifecycle. Once a transfer is complete, the sink may
publish only when its full byte count has been accepted and checked. Any
cancellation, elapsed time budget, source failure, or publish failure
must request staged-data discard. No file/MP4 creation or native executable
is introduced.

## Guarantees and limitations
- Time budget 0 < seconds <= 86400; monotonic clock injected in deterministic tests.
- Checks before and after writes and callbacks, including slow but eventually
  returning writes. **Cannot interrupt an indefinitely blocked synchronous
  write**; production process-level termination remains an external Pilot A gate.
- Transaction interface supports publish/discard, while tests use in-memory
  fakes only; future implementations must prove actual atomic publication.
- On any failure, best-effort discard runs and the original exception is
  retained. A broken discard callback cannot prove cleanup; fail closed.
- No FFmpeg, codec invocation, MP4 postflight, UI change, main merge or portable.

## Evidence
CI adds dedicated transactional regressions and keeps all previous RGB24,
image, Qt, lint, architecture, security and 42 frozen reference tests.
Mark this complete only after exact-current-HEAD Windows CI SUCCESS.
