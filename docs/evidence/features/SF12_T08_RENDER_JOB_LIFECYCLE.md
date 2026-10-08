# SF12-T08 — Nonblocking Render Lifecycle: Windows Acceptance

**Date:** 8 October 2026 WIB  
**Gate:** **PASS_NONBLOCKING_STAGED_LIFECYCLE / GUI_RENDER_STILL_DISABLED**  
**Accepted implementation SHA:** `596a48db355878537227f193c6dee33d0ae3f24a`  
**Windows GitHub Actions:** [37742882153](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37742882153) — **SUCCESS**.  
**Draft review:** [PR #9](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/pull/9), stacked on #8 T07 → #7 T06 → #6 T05 → #5 T04 → #4 T03 → #3 T02 → #2 T01 → #1 planning; none merged to `main`.

## Implemented and frozen boundaries

- New `application/export_jobs.py`: exactly **one background ThreadPoolExecutor worker**, typed lifecycle **QUEUED → RUNNING → READY → SUCCESS**, and terminal **CANCELLED/TIMED_OUT/STALE/FAILED**. Identical request IDs and concurrent double-click requests are rejected. The canonical ProjectState and immutable ExportRequest remain unmodified.
- Output is **always first staged privately** in a same-volume unique `.ang-export-job-*` directory; job success is not file publication. A result becomes READY only after the delegated existing T04–T07 adapter returns the expected revision/output staging path and a nonempty artifact. Only an explicit **owner-thread `accept()`**, after rechecking session, project identity, revision and semantic hash, publishes via an atomic **hard-link create-if-absent**. Existing destinations, media sources and optional .angproj source paths must not be overwritten.
- `infrastructure/export_job_adapters.py`: worker-side T03 preflight checks the **original output destination**, routes only qualified baseline, selection, matrix or style requests to existing FFmpeg adapters using a cloned **private output path**, and accepts cancellation token. The earlier immutable `MediaEnginePort.export` signature, production-engine choice, CommandBus, AAVC and frozen UI-001..042 were **not modified**.
- `shutdown(wait=False)` sets cancellation without blocking the Qt thread; running FFmpeg polls cancellation and terminates. A noncooperating fake worker cannot publish a late result. `snapshot()` invalidates stale session/revision/same-revision semantic swaps and can expire a request. After the worker ends, intermediate staging is removed in the background. Errors exposed to UI are stable codes without paths, stderr or credentials.
- Progress is **truthful lifecycle phases**, not a fictional percentage: `QUEUED`, `PREFLIGHT_AND_ENCODING`, `AWAITING_ACCEPTANCE`, `PUBLISHED`; numeric `progress_percent=None` while encoding and **100 only after final publication**. **No claim of continuous FFmpeg 0–100% progress**.
- Worker port and lifecycle can be polled from Qt, but **no production Qt Export dialog event binding or render button activation in T08**. That remains blocked on comprehensive T09 postflight and T10 packaged Windows qualification. T08's `accept` is a qualification-only acceptance mechanism, not approval of every output quality property.

## CI and real Windows evidence

- Same-code-HEAD Windows workflow **37742882153 = SUCCESS**, accepted source SHA `596a48db355878537227f193c6dee33d0ae3f24a`.
- Reused the owned synthetic video generator and external Windows FFmpeg + FFprobe, **not bundled** in repository. Real baseline H264 + AAC, **1920×1080 / 30 fps, 15 frames / 0.5 seconds** rendered in background. The chosen output **did not exist before main-thread acceptance**, then was atomically published, independently probed, and hashed.
- Final MP4 SHA256: `26972e24078169c3ad11b15e3ca978241ff417121427517ad1db9c531283c201`. Source MP4 remained byte-identical: SHA256 `a19bf794db3d8c519caffe4bf2ea29799756986dea8c9c4c4eb7dd78ee4b2ec5`. No project semantic mutation and no remaining staging directories.
- Tests: Qt event loop heartbeat at 10ms intervals while a fake render worker is blocked, nonblocking close (<0.5 s in tested fixture), duplicate-job guard, early/READY cancellation, paused noncooperating late worker, timeout, same-revision semantic change and session closure, wrong-owner-thread acceptance, existing competing output and source collision, exception privacy redaction, source hash preservation. Fake tests establish lifecycle behavior; they do not establish native FFmpeg cancellation latency under every Windows stress case.
- Targeted T08 unit + Qt tests and **complete Python repository pytest PASS**; Ruff, mypy (**96 source files**), import lint, architecture verifier, secret scan, source-of-truth **70/70**, frozen UI SHA manifest **42/42** PASS.
- Artifact `ANG-SF12-T08-Worker-RealMedia` GitHub ID **11534776048**, **607,154 bytes**, uploaded ZIP SHA256 `46d8821403c4b3649eda091a09e818bcb69a11fbec4ea5a9f53bf514e2b43e35`; retention 14 days. Includes `worker_lifecycle.json` and real MP4.

## Explicit unresolved gates

- The worker delegates T04–T07 output probes but **does not implement independent strict T09 postflight for all combinations before accepting**; `accept` is not yet production-authorized. A fake test worker can return nonempty bytes, deliberately proving this distinction. Main UI render action remains disabled and unwired.
- Continuous FFmpeg completion percentage, packaged Windows native codecs/licensing, true output matrix across large source files, forced timeout with unresponsive native process, full resource/disk stress and real UI close hook are **not proven**. Worker-side single threaded execution and phase progress are proven.
- Prior W5 microphone physical proof and W6/W7 live Gemini integration remain provisional.
- **Exact next task upon owner next `lanjutkan`: SF12-T09 — strict independent MP4/audio/subtitle postflight, redacted typed diagnostics, and safe publication gating.** Do not jump to T10 or enable Qt render until T09/T10 explicitly pass, and do not change frozen MediaEnginePort/engine binary/license policy without ASTRA ADR.
