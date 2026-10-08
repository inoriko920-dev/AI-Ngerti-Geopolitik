# HANDOFF — AI NGERTI GEOPOLITIK

**Current phase:** SF-STEP 11 — Feature Implementation Waves  
**Current wave:** W8 — Validation / Recovery / Diagnostics Hardening  
**Last completed task:** S11-W8-003 — PASS  
**Accepted implementation/regression HEAD:** `25e5f6cefbbef5f554bd17e64d50a61db948bf13`  
**Accepted W8-003 workflow:** [37689420848](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37689420848) — SUCCESS  
**Current implementation:** S11-W8-004 — IN_VERIFICATION (not yet PASS)
**Next exact task:** W8-004 Windows CI + real-media closure; W8-005 remains blocked

## Read-first constraints

Read `AGENTS.md`, the Software Factory guide, planning DOCX/TXT, frozen UI manifest,
W8 contract, current task list, evidence and source before writing. AAVC remains
read-only. UI-001..042 frozen. All canonical mutations require CommandBus; no
presentation-to-infrastructure shortcuts. One serial W8 task per continuation.

## W8 accepted progress

- W8-001 canonical deterministic validation: PASS.
- W8-002 real media integrity + frozen UI-041 validation projection: PASS.
- W8-003 verified single asset relink: PASS.

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

## Next exact action

W8-004 implementation has landed on main (latest code HEAD `4988e84ca6bca1e64fc5a755ff0d3287802e70f8`). Do not
redo implementation. Wait for the verified latest-HEAD Windows W8-004 run
[`37721840504`](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37721840504), inspect failures,
fix only W8-004, and then qualify real-media evidence plus all prior regression
families before closing W8-004. The prior W8-004 attempt passed 8/9 targeted
tests but exposed a default Qt checkbox on unverified candidates; this is fixed
in the latest code, not yet re-qualified. **Never claim W8-004 PASS until CI succeeds.**
Do not start W8-005 in the same turn.

## Provisional gates

W5 microphone physical hardware and W6/W7 live Gemini network tests remain
provisional; do not claim device/provider smoke results that were not run.
