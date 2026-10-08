# ASTRA INT-01B — Handoff dan bukti audit

**Status:** `READ_ONLY_PROCESS_AUDIT_PASS / CODE_NOT_CHANGED / PILOT_A_APPROVAL_BLOCKED`.

INT-01A typed native identity has passed Windows CI [37750922504](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37750922504). The project remains at pre-unified renderer architecture: FFmpeg and UI packaged test binaries are separate, product render stays disabled.

Current `FfmpegProcessRunner.run()` starts a child with stdout/stderr PIPE, polls before communicate, and has no global timeout; `FfprobeMediaProbe.raw_probe()` captures unbounded output and lacks a timeout. These code-level patterns pose deadlock, hanging and privacy risks. Source audit does not establish that a runtime deadlock has already occurred.

The detailed blueprint, 20 test cases, six serialized tasks B1–B6, stop conditions and release/ADR boundaries are in `docs/planning/15_ASTRA_INT01B_BOUNDED_PROCESS_RUNNER_2026-10-08.md` (TXT and DOCX mirrors). No source, GUI, architecture, native library, or release state changes are authorized by this document. Next action remains explicit owner approval for Pilot A, followed by B1 contract implementation under SOL.
