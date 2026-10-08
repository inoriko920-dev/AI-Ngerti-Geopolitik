# INT-01H — Pre-publication Cancellation / Deadline Audit

Date: 2026-10-09 WIB
Scope: Fix one observed gap in Draft PR #20's synthetic RGB24
transaction; no external FFmpeg Pilot A authorization granted.

## Defect
INT-01G returned a complete RGB24 transfer receipt and then called
the synthetic stage.publish() without checking cancellation or its
monotonic deadline again at the commit boundary. Completion of a byte
stream is not authorization to commit a result if the caller cancels
or the time budget expires in the receipt-to-publication interval.

## Fix
- Retain the original transaction monotonic clock and read its start
  before stream transfer.
- Perform one final cancellation probe and one final monotonic deadline
  test immediately before stage.publish().
- Redact callback / clock exceptions into typed errors rather than
  emitting private source paths.
- Any failing pre-publish gate enters existing best-effort discard().
  No complete result receipt is returned and stage.publish() is not
  invoked.
- Tests deterministically flip the cancel condition or deadline
  only at the last probe after all bytes are accepted. Additional
  regression verifies private-path callback errors are redacted.

## Limits
This is a **synthetic in-memory** publish gate only. It cannot interrupt
a blocked synchronous write, cannot guarantee an arbitrary sink is
transactional, and cannot replace codec postflight. Explicit Pilot A
approval is still required for native FFmpeg/FFprobe execution.
No GitHub merge, UI redesign, or Windows portable packaging.
