# SF12-T03 — Export Preflight & Capability Negotiation

**Date:** 8 October 2026 WIB  
**Status:** **PASS_CONTRACT_ONLY — RENDER_NOT_ENABLED / NATIVE_MATRIX_PROVISIONAL**  
**Accepted CODE SHA:** `7bee32aae7248ae9023afe4b9b62bf2caf357095`  
**Windows CI:** [37736630766](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37736630766) — **SUCCESS**  
**Base:** T02 accepted SHA `603d2173a9ff7211a09f1750c537117591e30931`

## Implemented in this isolated T03 task

- `application/export_preflight.py`: read-only `ExportPreflightService`, typed/redacted failure codes, explicit `precheck_pass`, and `can_start_render=False` hard boundary. Accepts immutable `ExportRequest`, active session and full `ProjectState`.
- Reuses W8 `ValidationService` + `RealMediaIntegrityRule` via existing `MediaIntegrityInspectorPort`, treating BLOCKER/ERROR on referenced media or invalid canonical state as export rejection, while allowing warnings on unused media.
- Detects stale session, project ID, revision and semantic hash; validates nonempty timeline; refuses selection until separate T05 render qualification.
- Conservative negotiation: only requests for H.264, 1920x1080, 30fps, HIGH quality, no sharpen, burn-in subtitle, AAC, FULL scope are considered for *precheck*. FFmpeg, FFprobe, libx264, AAC presence must be observed through the prior T01 immutable `ExportToolchain` snapshot. Encoder discovery alone never authorizes render.
- `infrastructure/export_output_inspector.py`: rejects missing output parent, output already present, source/project protected path collisions (including resolved alias), insufficient disk reserve, or denied directory write. Uses a random temporary probe file with automatic cleanup, never writes to target or the project's source. No exception string or raw path is exposed in `ExportPreflightResult`.
- Conservative disk-space guard: maximum of 256 MiB and (128 MiB + 2 MB per timeline second). This is a screening margin, *not* guaranteed real output size. Remaining hard disk/permission/race conditions must still be rechecked during T04/T08 before atomic publication.
- No export job invoked; no new GUI hook, no mutable project storage, no new engine dependency, no frozen `MediaEnginePort` signature changes.

## Verified Windows same-code-HEAD gates

- CI run `37736630766`, code SHA `7bee32a`: **SUCCESS**.
- New targeted preflight unit/negative tests: **PASS**, including referenced missing/zero/probe error, stale session and semantic swap, missing encoder, H.265/4K/60fps/selection denial, existing/collision output, missing parent, disk low/failure, write denied, unused missing media nonblocker, no temp artifacts, and no private-path error leakage.
- Existing complete `uv run pytest -q`: **PASS**.
- Ruff format/check, mypy (**90 source files**), import contracts, architecture boundaries, no-secret gate: **PASS**.
- Source-of-truth **70/70 PASS**; frozen UI references **42/42 SHA-256 PASS**.
- Earlier CI red due formatting and alias-import ordering; corrected on branch before green accepted SHA.
- W5 physical mic and W6/W7 live Gemini remain PROVISIONAL. T01 runner did not have FFmpeg/FFprobe installed; this workflow uses controlled test doubles and local filesystem tests, NOT production H.264/HEVC media encode proof.

## Limits / handoff

- A clean *preflight* means inputs/conditions passed at inspection time, NOT that a video was rendered, that an encoder actually succeeded, or that a final output is valid.
- Filesystem is subject to TOCTOU; T04 must recheck collisions/space/permissions in the worker and preserve existing output with safe temp/atomic promote.
- T04 must add real FFmpeg H.264 Windows fixture qualification with known dependency/licensing strategy before enabling any feature flags. T05 selection, T06 4K/60fps/H.265, T08 render worker/cancellation, T09 postflight are separate serial gates.
- **Exact next task after owner's next `lanjutkan`: SF12-T04 H.264 Baseline Export Pipeline only.** Review repository source-of-truth/ASTRA ADR if changing frozen port/engine design. Do not merge stacked draft PRs or change AAVC without appropriate review.
- Draft PR stack: #4 T03 -> #3 T02 -> #2 T01 -> #1 STEP12 planning -> main. PR #4 is not merged; main is unchanged by this task.
