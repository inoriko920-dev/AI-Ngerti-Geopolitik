# S11 W5-010 — History, Failure Paths and Regression Closure

**Task result:** PASS  
**Final W5 result:** PASS_WITH_PROVISIONAL_MIC_HARDWARE  
**Accepted implementation HEAD:** `cb54b544dd8c6977d117bb71e137117830feb061`  
**W5-010 workflow:** `37583174352` — SUCCESS  
**Artifact:** `ANG-S11-W5-010-Closure`  
**Artifact ID:** `11466065855`

## Closure scope

W5-010 adds no new product features.

It closes:
- history guarantees;
- pre-W5 backward compatibility;
- failure safety;
- source preservation;
- deterministic closure evidence;
- full regression lock.

## History

A deterministic canonical project was walked through:
1. video-only state;
2. subtitle-bound state;
3. subtitle+narration state;
4. Undo narration;
5. Undo subtitle;
6. Redo subtitle;
7. Redo narration.

Semantic state hashes returned to the expected state at every transition.

Result:
**subtitle + narration Undo/Redo PASS**.

## Pre-W5 W4 backward compatibility

Fixture:
`tests/fixtures/step11_w4_pre_w5.angproj`

The fixture intentionally contains W4 creative state but no W5 fields.

Loaded result:
- `subtitle is None`;
- `narration is None`;
- title `GEOPOLITIK` preserved;
- `fade_black` transition preserved;
- `Rise` effect preserved.

Result:
**safe W5 defaults without breaking W4 state PASS**.

## Malformed SRT

A malformed timestamp using a dot separator is rejected by the strict UTF-8 SRT
parser/import path.

After rejection:
- canonical semantic hash unchanged;
- no replacement subtitle state is committed.

Result:
**PASS**.

## Dirty working-copy guard

An unsaved subtitle text edit is created in SubtitleWorkingCopy.

A reload without explicit discard raises the typed dirty-working-copy failure.

After rejection:
- working copy remains dirty;
- unsaved edit remains present;
- ProjectState remains unchanged.

Result:
**PASS**.

## Missing and corrupt narration

Actual FFprobe qualification is used.

Missing narration file:
- probe/import rejected;
- no new asset/narration commit;
- canonical state unchanged.

Corrupt `.wav` payload:
- FFprobe rejected the file;
- no fake audio success;
- canonical state unchanged.

Result:
**PASS**.

## Missing bound narration runtime

A valid narration is first imported/bound, then its source file is temporarily
removed from the expected path.

Real narration preview is attempted.

Expected result:
- FFmpeg path fails visibly;
- no fake preview output file remains;
- canonical state remains unchanged.

The valid narration source is restored afterward and SHA-256 remains unchanged.

Result:
**PASS**.

## Failed microphone capture preservation

A deterministic recorder adapter exposes a device and then fails during capture.

Expected result:
- MicrophoneRecordingError surfaced;
- previously-bound narration remains bound;
- canonical semantic hash unchanged;
- no successful recording is claimed.

Result:
**PASS**.

## Source safety

Both remain byte-identical after closure:
- source SRT;
- valid narration WAV.

Result:
**PASS**.

## W5-010 gates

Accepted workflow `37583174352`:
- Ruff format PASS;
- Ruff check PASS;
- mypy PASS — 52 source files;
- import contracts PASS;
- architecture PASS;
- source-of-truth 70/70 PASS;
- secret scan PASS;
- frozen UI references 42/42 PASS;
- targeted closure tests **6/6 PASS**;
- full pytest PASS;
- deterministic closure evidence PASS;
- verifier **9/9 PASS**.

Artifact size:
6,856 bytes.

## Final same-HEAD regression lock

All final runs use accepted implementation HEAD
`cb54b544dd8c6977d117bb71e137117830feb061`.

SUCCESS:
- W5-010: `37583174352`;
- W5-009: `37583174359`;
- W5-008: `37583174310`;
- W5-007: `37583174255`, attempt 2;
- W5-006: `37583174384`, attempt 2;
- W5-005: `37583174296`;
- W5-004: `37583174275`;
- W4: `37583174301`;
- W3: `37583174280`;
- W2: `37583174363`, attempt 2;
- W1: `37583174318`;
- W0: `37583174261`;
- S10: `37583174258`, attempt 2;
- S09: `37583174265`;
- S08: `37583174297`.

W0 includes the MLT Windows playback qualification.

S10 includes:
- real-media vertical slice;
- packaged real-media smoke;
- portable UI regression.

### External CI incident

The initial W5-007, W5-006, W2-core and S10 attempts encountered an external
Chocolatey community-feed HTTP 504 while installing FFmpeg.

Those failed jobs were rerun on the **same commit SHA** with no product-code
changes.

The reruns completed SUCCESS.

Therefore the final regression result is not masking a code fix between
attempts.

## Final hardware qualifier

Hosted Windows CI exposes zero DirectShow audio-input devices.

The deterministic recording software path, staging, atomic binding and failure
preservation are proven.

A physical microphone recording was not available to test.

Therefore the only honest final W5 status is:

**PASS_WITH_PROVISIONAL_MIC_HARDWARE**

—not full PASS.

## Next

No W6 contract currently exists in repository source-of-truth.

Do not invent the next wave.

On the next owner `lanjutkan`, derive and lock the actual next SF-STEP 11 wave
from the frozen Product/Master Blueprint before implementation.
