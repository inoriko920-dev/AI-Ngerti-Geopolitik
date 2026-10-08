# SF12-T02 — Typed Export Request Contract: Windows Acceptance

**Date:** 8 October 2026 (WIB)  
**Status:** **PASS — CONTRACT_ONLY / RENDER_UNQUALIFIED**  
**Verified code SHA:** `9e12498b7ed181933c1da089204e3daf234d2a35`  
**Windows GitHub Actions run:** [37735699709](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37735699709) — **SUCCESS**

## Scope shipped in the T02 branch

- Added immutable, typed `ExportRequest`, selection `ExportFrameRange`, explicit scoped enums and a prospective application-owned `ExportRequestMediaPort` in `application/export_request.py`.
- Output is an absolute MP4 path only; traversal, null bytes and wrong extensions are rejected without accessing the file system.
- Binds project ID, session ID, revision and semantic SHA-256 fingerprint; rejects newly-opened sessions and same-revision content swaps.
- Half-open selection intervals are validated against active timeline bounds. Full project rejects stray selection intervals.
- Rejects untyped/free-form option strings, Python bool as integer, unsupported FPS or size, malformed identity and hash.
- Preserves `MediaEnginePort`, `ProjectState`, current export adapter, frozen UI and original AAVC unchanged. No renderer/UI dispatch activated.

## Accepted evidence

- T02 targeted **27/27 pytest cases PASS**.
- Full repository `uv run pytest -q` **SUCCESS** on the same code SHA.
- `ruff format --check`, `ruff check`, `mypy` (**88 source files**), `lint-imports`, architecture verifier, secrets check: **PASS**.
- `verify_source_of_truth`: **70/70 PASS**.
- `verify_ui_reference_manifest`: **42/42 SHA-256 PASS**.
- First iterations failed due formatting, incorrect use of the timeline end property, and a missing media fingerprint in the test fixture; these defects were corrected before the accepted green run.
- No FFmpeg/FFprobe H.264/H.265 render, physical microphone, or live Gemini smoke took place in T02. Codec availability and T03/T09 safety gates stay pending.

## Gate / handoff

The written DTO and optional prospective protocol are **additive**. A future signature change to the frozen `MediaEnginePort`, native engine selection, or licensing/distribution strategy **requires ASTRA ADR review** before adoption. No new service or production implementation was introduced.

**Next exact serial task:** **SF12-T03 — export preflight and capability negotiation**, after the owner's next `lanjutkan`. Consume W8 validation, verify writable output and collision/source safety, selection/media dependency checks, disk-space safety, and native encoder readiness. Keep render disabled until T04/T08/T09 production job and verification gates are actually qualified.

**GitHub review:** Draft PR #3 (stacked on T01 PR #2, which is stacked on STEP12 planning PR #1). Not merged to main.
