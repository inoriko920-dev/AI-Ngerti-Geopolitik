# SOL INT-01B/B2-prep — Independent bounded stdout/stderr collector

**Tanggal:** 2026-10-08 WIB  
**Gate:** `PASS_PURE_BUFFER_COMPONENT / NO_SUBPROCESS_EXECUTION / PILOT_A_OWNER_PENDING`  
**Accepted implementation SHA:** `ef8b06a4a1262134509d9d6a9df98feea00062af`  
**Windows GitHub Actions:** [37757835429](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37757835429) — **SUCCESS**, code SHA match.  
**GitHub:** [Draft stacked PR #18](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/pull/18), base B1 PR #16 branch; no source UI, binary distribution, production process runner or `main` changes.

## Why this restricted change exists

B1 already PASSED and was hardened against `math.isfinite(10**1000)` overflow; latest documented branch SHA `6bf5c0213a9419ef758f99458989dd579ff17195` Windows [37757021414](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37757021414) SUCCESS. The full B2 runner is **blocked** by absent explicit approval of external-FFmpeg Pilot A.

As a safe preparatory step, this PR adds only `src/ai_ngerti_geopolitik/infrastructure/native_bounded_capture.py`, an isolated in-memory **collector of already-available bytes**. It does **not** find, spawn, terminate, probe, or otherwise execute FFmpeg, FFprobe, Python subprocesses or any external binaries. It does not replace existing `FfmpegProcessRunner` or `FfprobeMediaProbe`.

## Functionality proved in isolated tests

- Reuses frozen `application.NativeProcessPolicy` limits (1 to 1,048,576 bytes per stream). `NativeBoundedCapture.append(stream, chunk)` enforces independent stdout and stderr caps and accounts each accepted byte without copying chunks larger than the remaining limit.
- `threading.Lock` protects both streams when synthetic readers call the collector concurrently. A correct future runner **must drain both OS pipes in parallel** and must stop the child on any cap failure. This collector alone does not drain OS pipes or cancel child processes.
- On first overflow the collector securely discards both private buffers, marks itself overflowed, and throws only `NATIVE_OUTPUT_TOO_LARGE`; no path or original byte content is echoed in errors. Subsequent writes and handoffs fail closed. `discard()` permanently seals and clears buffers.
- `take_private_buffers()` allows a **single internal parser handoff** after readers have finished, returns raw bytes only to infrastructure, and seals/clears internal buffers. Raw native outputs must never be sent to UI/logs; they may contain sensitive data. `NativeCaptureMetrics` is frozen, contains only byte counters/overflow/sealed, and is safe to pass outward.
- Pure test suite `tests/unit/test_sol_int01b_b2_prep_bounded_capture.py`: exact caps and one-time handoff, stdout/stderr independent one-byte overflow, huge secret-bearing byte chunks, invalid inputs, zero-byte chunks, cancel-equivalent discard, two synthetic concurrent writer threads, immutable metrics, wrong policy type.
- Windows workflow `.github/workflows/sol-int01b-b2-prep-windows.yml` includes Ruff format/lint, mypy **101 source files**, lint-imports, architecture, no secrets, source-of-truth **70/70**, frozen UI SHA **42/42**, B2-prep unit tests, complete repository pytest, and explicit static guard for **no subprocess execution or Qt export activation**. Every job step PASSED.

## Explicit limitations, honest nonclaims and future work

- **B2 actual native subprocess runner is NOT implemented or qualified.** The pre-existing `FfmpegProcessRunner` PIPE deadlock risk, lack of global deadline, `raw_probe` timeout/cancellation gaps, process-tree cleanup, FFmpeg trusted-executable identity checks, and external executable redistribution/licensing questions are all still OPEN. No Windows child-process or native FFmpeg execution is claimed for this new component.
- Concurrent **in-memory** synthetic writers prove synchronization, not concurrent OS pipe draining. No proof of process termination, bounded memory beyond cap accounting in the entire application, or Windows process-tree orphan cleanup.
- **Pilot A owner decision D1 is not accepted by saying only `lanjutkan`.** Native/process-executing B2 must wait for explicit scoped owner approval. D2 final portable FFmpeg bundling, D3 LICENSE/notices and D4 final libopenshot/engine also remain PENDING.
- No modifications to frozen `MediaEnginePort.export`, ProjectState, UI-001..042, user render button, or binary packaging. `main` remains unchanged and all PRs remain drafts.
- **Next serial task only after owner approval:** SOL INT-01B/B2 native process runner combining safe OS-pipe parallel draining, monotonic timeout and cancellation with this collector. Later B3 Windows child-tree verification, B4 bounded FFprobe, B5 FFmpeg adapter and B6 real-media Windows gate remain separate tasks.

**Conclusion:** `B2_PREP_PASS` does not equal `B2_PASS`, `Pilot_A_Approved`, or `Product_Release_Allowed`.
