# HANDOFF — AI NGERTI GEOPOLITIK

**Current phase:** SF-STEP 11 — Feature Implementation Waves  
**Current wave:** W8 — Validation / Recovery / Diagnostics Hardening  
**Last completed task:** S11-W8-004 — PASS  
**Accepted implementation/regression HEAD:** `25e5f6cefbbef5f554bd17e64d50a61db948bf13`  
**Accepted W8-003 workflow:** [37689420848](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37689420848) — SUCCESS  
**Current implementation:** S11-W8-004 — PASS
**Next exact task:** S11-W8-005 — Autosave Catalog + Retention Hardening — READY

## Read-first constraints

Read `AGENTS.md`, the Software Factory guide, planning DOCX/TXT, frozen UI manifest,
W8 contract, current task list, evidence and source before writing. AAVC remains
read-only. UI-001..042 frozen. All canonical mutations require CommandBus; no
presentation-to-infrastructure shortcuts. One serial W8 task per continuation.

## W8 accepted progress

- W8-001 canonical deterministic validation: PASS.
- W8-002 real media integrity + frozen UI-041 validation projection: PASS.
- W8-003 verified single asset relink: PASS.
- W8-004 batch directory relink scan + candidate ranking: PASS.

## W8-003 qualification

- validated manual single-asset relink through canonical CommandBatch / CommandBus;
- exact Asset ID and clip references preserved;
- wrong media type, fingerprint, duration, dimensions and audio metadata fail safely with zero mutation;
- path already owned by another asset is rejected;
- missing source -> renamed relocated media -> verified rebind -> validation clears;
- one revision on apply, exact Undo and Redo, exact .angproj save/reopen;
- no batch scan, ranking, recovery flow or frozen UI redesign in W8-003;
- targeted tests **9/9 PASS**, full pytest **411/411 PASS**;
- real-media evidence verifier **23/23 PASS**;
- Windows CI lint, mypy, architecture, source-of-truth, secret and UI 42/42 gates PASS;
- full main-HEAD regression **27/27 workflow families SUCCESS**, all attempt 1.

**Workflow:** `37689420848`  
**Artifact:** `ANG-S11-W8-003-Single-Asset-Relink` / ID `11513225118`  
**Long-lived evidence:** `docs/evidence/features/S11_W8_003_SINGLE_ASSET_RELINK.md`.

## W8-004 accepted evidence

**Accepted W8-004 implementation/regression HEAD:** `4988e84ca6bca1e64fc5a755ff0d3287802e70f8`  
**Dedicated Windows workflow:** [37721840504](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37721840504) — SUCCESS  
**Artifact:** `ANG-S11-W8-004-Batch-Directory-Relink`, ID `11525753140`  
**Artifact SHA-256:** `75f33b72c4cf147d37b151e17bb7ae6bddc84982941f9f0aa8847c97d4fe4fb4`  
**Tests:** targeted 9/9 PASS; full pytest 420/420 PASS; real-media evidence 14/14 PASS  
**Gates:** Ruff, mypy (75 modules), import contracts, architecture, no-secret, source-of-truth 70/70, UI SHA 42/42 PASS  
**Full same-HEAD regression:** 27/27 workflow families SUCCESS, all attempt 1.

Verified: bounded worker scan, cancellation, stale project/session/revision/hash safety,
rank 1–4, SHA-256 verified explicit selection only, ambiguous candidate review,
one atomic CommandBatch, stable asset/clip IDs, exact Undo/Redo, save/reopen and
real-media validation. UI-040 projects intents; controller wiring remains W8-010.

## Next exact action

On the next owner's `lanjutkan`, implement **SOL W8-005 only** using the locked
ASTRA W8 planning. Never prune `.angproj`, source `.bak` or unrelated projects;
catalog must validate snapshot content and isolate corrupt records. W8-006 remains
blocked until W8-005 passes all gates.

## Provisional gates

W5 microphone physical hardware and W6/W7 live Gemini network tests remain
provisional; do not claim device/provider smoke results that were not run.
