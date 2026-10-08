# S11-W8-003 — SINGLE ASSET RELINK + EXACT IDENTITY PRESERVATION

**Status:** PASS  
**Verified implementation/regression HEAD:** `25e5f6cefbbef5f554bd17e64d50a61db948bf13`  
**W8-003 workflow:** [37689420848](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37689420848) — SUCCESS  
**Artifact:** `ANG-S11-W8-003-Single-Asset-Relink`  
**Artifact ID:** `11513225118`  
**Artifact digest:** `sha256:706922cf4040fd0c4ead504571c2fadca7ee5088b56d7f186d866990d0300d72`  
**Artifact retention:** 14 days; canonical long-lived record is this repository evidence note.

## Scope implemented

`RelinkAssetCommand` changes only the canonical Asset binding, retaining the stable
`asset_id` and every clip/narration reference. `RelinkService` verifies a user-selected
candidate through `MediaProbePort`, rejects a candidate already bound to another asset,
and commits only after strict type/fingerprint/metadata checks via the existing
`CommandBus` / `CommandBatch`.

No silent filename-based replacement or automatic scanning is introduced. The selection
and verification path is implemented at application level; interactive UI-040 batch
discovery is deliberately deferred to subsequent W8 tasks.

## Qualification and failures

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

Real-media qualification uses an owned FFmpeg-generated video, moves it to a renamed
`relocated/` location, observes missing status on the original binding, probes the
replacement, applies a single relink, runs real-media validation, saves/reopens,
then checks one exact Undo and Redo. Original media contents are not rewritten.

## Tests and evidence

- Targeted `tests/unit/test_step11_w8_003_relink.py`: **9/9 PASS**.
- Repository-wide `uv run pytest -q`: **411/411 PASS**.
- `scripts/verify/verify_step11_w8_003_evidence.py`: **23/23 PASS**.
- `ruff format --check`, `ruff check`, `mypy`, `lint-imports`,
  architecture, source-of-truth, no-secret, UI SHA-256 42/42: **PASS**.
- GitHub Actions W8-003 real-media workflow `37689420848`: **SUCCESS**.
- Full same-HEAD regression: **27/27 workflow families SUCCESS (attempt 1)**,
  including S08/S09/S10/W0 and W1–W7.

Evidence artifact `11513225118` contains the relink report, identity/path
diagnostics, and a reopened `.angproj` proof project. These temporary CI paths are
test-only, not developer-machine assumptions.

## Boundaries and remaining work

W8-003 does **not** implement batch-directory scanning, candidate ranking, progress,
cancellation, crash recovery, diagnostics or new UI layout. W6/W7 live Gemini remains
provisional without production provider credentials; microphone physical-hardware
qualification also remains provisional.

## Next exact task

**S11-W8-004 — Batch Directory Relink Scan + Candidate Ranking — READY.**

Do not implement W8-004 in the W8-003 closure turn.
