# S11-W8-002 — REAL MEDIA INTEGRITY + VALIDATION CENTER PROJECTION

**Status:** PASS  
**Accepted implementation HEAD:** `c73a38d8fd6d3796f988769ca43354185eb66a6d`  
**Accepted workflow:** `37684517658` — SUCCESS  
**Artifact:** `ANG-S11-W8-002-Real-Media-Validation`  
**Artifact ID:** `11510448492`  
**Artifact size:** 11,328,702 bytes  
**Artifact SHA-256:** `9575986fab94e5d510ac53f48ed2aac76ccc1de771fe6a3cd32a80436a7221cb`

## Scope

W8-002 adds real ffprobe-backed media integrity inspection and projects canonical validation
results onto the existing frozen UI-041 Validation Center. It does not implement relink mutation,
recovery, diagnostics bundle, directory scanning or UI redesign.

## Qualified real-media integrity

- clean owned video + ffprobe => zero integrity issue;
- referenced physical file missing => `MEDIA_FILE_MISSING` / BLOCKER;
- zero-byte media => `MEDIA_ZERO_BYTE`;
- unreadable/non-media file => `MEDIA_PROBE_FAILED`;
- media-type mismatch => typed derived issue;
- fingerprint mismatch => typed derived issue;
- duplicate real fingerprint across stable asset IDs => INFO only;
- all integrity inspection is non-mutating.

`Asset.availability` remains canonical `online/offline/missing`. Integrity observations are
derived validation state, not a second project truth.

## UI-041 projection

Existing `dlg_validation_center` is reused at the same 650×900 geometry and minimum width 600.
The summary card, Validasi Ulang control, QTabWidget and Project/Media/Scene/AI/Render grouping
remain in place.

Live projection adds:
- real counts and typed issue rows;
- visible severity text, not color alone;
- exact safe issue title/message;
- semantic remediation action;
- exact stable target IDs in the emitted UiIntent.

No new screen or reference image was created.

## Stale safety

Projection is stale when project ID, revision or semantic hash no longer matches the validation
result. In stale state:
- issue remediation buttons are disabled;
- Validasi Ulang stays enabled;
- stale issue action cannot be emitted.

## Gates

Workflow `37684517658`:
- FFmpeg toolchain PASS;
- uv lock/frozen sync PASS;
- Ruff format/check PASS;
- mypy PASS — 71 source files;
- import contracts 4/4 PASS;
- architecture PASS;
- source-of-truth 70/70 PASS;
- no-secret PASS;
- UI references 42/42 SHA-256 PASS;
- targeted unit + Qt tests **7/7 PASS**;
- full pytest **402/402 PASS**;
- owned real-media fixture PASS;
- real ffprobe evidence PASS;
- evidence verifier **18/18 PASS**;
- artifact upload PASS.

## Regression lock

On accepted implementation HEAD
`c73a38d8fd6d3796f988769ca43354185eb66a6d`:

- **27/27 workflow families SUCCESS**;
- all 27 succeeded on attempt 1;
- S08 portable foundation PASS;
- S09 Windows UI shell PASS;
- S10 packaged real-media E2E PASS;
- W0 engine qualification PASS;
- W1–W7 and W8-001 regressions PASS.

## Boundary

W8-003 relink mutation is not started by this task.

## Next

**S11-W8-003 — Single Asset Relink Command + Exact Identity Preservation — READY.**

Do not start W8-004 in the same turn.
