# SOL INT-01B/B2 — Controlled Python Subprocess Prequalification

**Tanggal:** 8 Oktober 2026 WIB  
**Technical gate:** `PASS_PYTHON_SYNTHETIC_PROCESS_ONLY / REAL_FFMPEG_RUNNER_NOT_STARTED`  
**Implementation commit:** `7e36ccae6e1215e22608ff9e5a7eeb842f2aa55a`  
**Windows CI:** [37755635788](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37755635788) — **SUCCESS** at that same code SHA.  
**Review:** [Draft PR #17](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/pull/17), stacked on Draft PR #16. Earlier #1–#16 remain unmerged. `main` unchanged from `c9154eef85f8b475630816a7c63f5e2b52bf1523`.

## What was implemented — isolated experiment only

- New `src/ai_ngerti_geopolitik/infrastructure/synthetic_process_qualification.py` exposes `run_synthetic_fixture(fixture, NativeProcessPolicy, cancellation=Event)`. The function accepts only an allowlisted `SyntheticFixture` enum and executes **only `sys.executable -I -c` with a fixed internally authored Python program**. It does not accept a user-supplied command, script, file path, executable, codec or FFmpeg argument and is not referenced by bootstrap, Qt or the media engine.
- Uses `subprocess.Popen` with `shell=False`, `stdin=DEVNULL`, and **two concurrent reader threads** that consume stdout and stderr without buffering or exposing either stream to application code. Counts bytes and marks overflow against hard caps from B1 `NativeProcessPolicy`.
- Applies a `time.monotonic()` deadline, optional `threading.Event` cancellation, bounded polling and terminate/kill fallback to the synthetic child process. All outcomes reuse immutable `NativeProcessOutcome` with typed `NativeIssueCode`, exit status, duration and byte counters. No stdout, stderr, paths, tokens or argv in public outcomes.
- Existing `FfmpegProcessRunner`, `FfprobeMediaProbe.raw_probe`, T04–T09 adapters, `MediaEnginePort.export`, Qt render button, frozen UI and production binary discovery were **not changed**. FFmpeg/FFprobe binaries were **not executed or bundled** by this task.

## Windows acceptance evidence

GitHub Actions 37755635788, success on source commit `7e36ccae...`:
- Targeted Windows `tests/unit/test_sol_int01b_b2_synthetic_subprocess.py` **PASS**. Tests use fixed Python child fixtures for:
  - stdout-only flooding past 1 MiB cap;
  - stderr-only flooding past 1 MiB cap;
  - simultaneous flooding of stdout and stderr without deadlock;
  - successful short child with no private captured text;
  - child sleeping beyond 1-second deadline (timeout);
  - cancellation before start and while child is running;
  - failure emitting a synthetic private path/token, publicly redacted;
  - invalid fixture/arguments rejected before child spawn.
- Full Python repository pytest **PASS**. Ruff format/check, mypy **101 source files**, lint-imports, architecture verification, secrets check, source-of-truth **70/70** and frozen UI SHA256 **42/42** **PASS**.
- Dedicated static safety guard confirms harness points only to `sys.executable`, not `FfmpegProcessRunner`, Qt render or production job controller.

## Limitations — DO NOT declare production B2 pass

1. This is a **synthetic Python subprocess**, not external FFmpeg qualification; no user-provided binary, codec, ffprobe parser or production worker was exercised.
2. **Windows process-tree containment is not established**. This harness terminates the owned immediate child only. B3 needs Windows child-tree/job-object testing before treating it as a robust general-purpose runner.
3. The reader threads continue draining after cap and store only counters, not raw bytes; the child is then terminated. The input is hardcoded and controlled, so this does not establish all adversarial-output bounds for an arbitrary executable.
4. The race window between process termination and stream drain is bounded by joins but not formally proved safe under every process/OS failure. Full B2 production semantics, B3 child trees, B4 ffprobe timeout, B5 integration and B6 real external FFmpeg smoke remain open.
5. **Pilot A D1 still not explicitly approved**; this isolated synthetic Python test does not select libopenshot/FFmpeg as production engine, approve GPL codec distribution or allow release. D2–D4 remain pending.
6. No new DOCX is needed for this implementation-only substep: planning authority remains `docs/planning/15_ASTRA_INT01B_BOUNDED_PROCESS_RUNNER_2026-10-08.docx`.

**Next gated task:** Only after explicit owner approval of Pilot A, implement a bounded external/native runner with exact-path validation and real Windows child-tree cleanup (B2/B3), then separately wire FFprobe and FFmpeg (B4/B5) and run native smoke (B6). Do not activate `btn_export_render` until later UI integration gates pass.
