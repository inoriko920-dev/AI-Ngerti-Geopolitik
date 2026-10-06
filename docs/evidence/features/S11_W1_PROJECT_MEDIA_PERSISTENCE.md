# SF-STEP 11 WAVE 1 — PROJECT, MEDIA & PERSISTENCE FOUNDATION

Status: **PASS**

Accepted implementation HEAD:
`1f354cddc68eb9f129ba22d0410480964c6b1b85`.

Primary W1 workflow:
- name: `S11 W1 Project Media Persistence`;
- run ID: `37536861625`;
- run number: 5;
- conclusion: **SUCCESS**.

Artifact:
- ID: `11446054538`;
- name: `ANG-S11-W1-Project-Media-Persistence`;
- size: 4,059 bytes;
- digest:
  `sha256:24fb98071bd1a1ee86cc1e4e2552fa2eb424cf4200a02fe3700b01241dc3e6b9`.

## W1 task results

| Task | Result | Evidence |
| --- | --- | --- |
| S11-W1-001 project new/open/close + dirty state | VERIFIED | ProjectSession lifecycle + unsaved close guard |
| S11-W1-002 atomic Save/Save As + backup/replace | VERIFIED | atomic temp/replace, Save As, previous-save .bak |
| S11-W1-003 video/audio/image import + metadata/offline | VERIFIED | real ffprobe on generated MP4/WAV/PNG |
| S11-W1-004 media-bin search/sort/filter/selection | VERIFIED | stable-ID query/selection tests + evidence |
| S11-W1-005 project settings persistence | VERIFIED | resolution/FPS/aspect round-trip |
| S11-W1-006 autosave snapshot foundation | VERIFIED | separate .ang-autosave snapshot; canonical untouched |
| S11-W1-007 missing/offline state, no silent deletion | VERIFIED | missing media keeps A001 and C001 relationship |

## Quality and architecture

The W1 run passed:
- Ruff format;
- Ruff lint;
- mypy — **32 source files, 0 issues**;
- Import Linter — **4 contracts kept, 0 broken**;
- custom architecture verifier;
- source-of-truth verifier — 70/70;
- frozen UI reference verifier — 42/42 SHA-256;
- committed-secret verifier;
- complete pytest suite.

The W1 suite contains **39 tests** after adding eight W1-focused tests.

## Real media evidence

The Windows W1 workflow generated owned deterministic fixtures:
- H.264/AAC MP4 video;
- PCM WAV audio;
- PNG image.

The real `FfprobeMediaProbe` classified and imported all three media families with
stable IDs:
- A001 = video;
- A002 = audio;
- A003 = image.

Persisted metadata includes canonical duration frames, dimensions where
applicable, audio sample rate, file size, fingerprint, source name, and explicit
availability state.

## Project lifecycle and persistence guarantees

Verified:
- a newly created unsaved project is dirty;
- dirty close is blocked unless discard is explicit;
- Save establishes a clean canonical path;
- Save As establishes a new canonical path;
- subsequent Save preserves the previous successful project as
  `<project>.angproj.bak`;
- writes use same-directory temporary files + `os.replace`;
- autosave writes a separate revision/hash-addressed snapshot under
  `.ang-autosave`;
- autosave does not clear dirty state;
- autosave does not overwrite either the original Save file or current Save As
  file.

Project schema remains version 1 with backward-compatible additive defaults for:
- project settings;
- source name / file size / sample rate;
- media availability.

Older schema-v1 project files without those additive keys remain loadable.

## Missing/offline media semantics

W1 explicitly separates media identity from file availability.

Verified:
- when A001's file disappears, A001 becomes `missing`;
- C001 remains present and continues referencing A001;
- no clip is silently deleted;
- autosave persists the missing state;
- the prior canonical Save remains unchanged;
- `offline` is also a valid persisted state for intentionally unavailable
  media.

This establishes the recovery/relink-compatible state required by later waves.

## Media-bin semantics

Verified:
- query by text;
- filter by media family;
- filter by availability;
- stable sorting;
- stable selection by Asset ID;
- selection does not mutate ProjectState.

Search is intentionally scoped to asset identity/display metadata rather than
arbitrary parent-directory text.

## Regression lock on W1 accepted HEAD

The same accepted W1 HEAD also passed all prior implementation regressions:

- S11 W0 engine qualification: `37536861597` — SUCCESS;
- S10 Windows E2E vertical slice: `37536861677` — SUCCESS;
- S09 Windows UI shell: `37536861608` — SUCCESS;
- S08 Windows foundation: `37536861662` — SUCCESS.

Therefore W1 did not obtain green by weakening earlier gates.

## Remaining boundaries

W1 does **not** implement:
- real-time Qt playback/timeline engine integration;
- full timeline editing behavior;
- transitions/effects/motion;
- subtitle/audio production wave;
- Gemini editing;
- final native MLT bundle/license closure.

Those remain later waves.

## Gate

**W1 = PASS.**

Next exact wave after owner says `lanjutkan`:
**W2 — Timeline, Playback & Core Editing.**

Do not start W3 or STEP 12 before W2 is green.
