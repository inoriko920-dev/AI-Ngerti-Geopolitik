# S11 W7-005 — L2 PACING QUALIFICATION: DURATION + SPEED

**Status:** PASS  
**Accepted implementation HEAD:** `e00ad734833ceac4f32f42e5363f5b8b5c203212`  
**Accepted workflow:** `37653613643` — SUCCESS  
**Artifact:** `ANG-S11-W7-005-L2-Pacing`  
**Artifact ID:** `11498316525`  
**Artifact size:** 30,314,627 bytes  
**Artifact SHA-256:** `9e1799c549709fbb74a8a9ec171b527f451dfe98c99b6c5a3ba520f6dc9e2644`

## Scope

W7-005 qualifies real pacing behavior for the W7 L2 duration and speed command
families. It does not add a new provider, mutation owner, UI, approval path, or
transform/transition qualification.

The path under qualification is:

`AutoEditPlanVerifier → canonical manual pacing command → immutable candidate state → real FFmpeg qualification adapter`.

Canonical committed ProjectState and CommandBus history remain untouched.

## Owned real-media fixture

The workflow generates an owned 1920×1080 / 30 fps / 8-second H.264 + AAC
fixture through `scripts/generate_step10_fixture.py`.

Qualification project:
- three contiguous clips;
- each baseline clip uses 60 source/timeline frames;
- starts at 0 / 60 / 120;
- baseline timeline = 180 frames.

## Duration qualification

Proposal:
`DurationEditProposal("C001", 90)`.

Verified translation:
- `SetClipDurationCommand`;
- `ripple=True` is application-owned.

Candidate:
- C001 duration = 90 frames;
- C001 source_out = 90;
- C002 start = 90;
- C003 start = 150;
- timeline end = 210 frames;
- speed remains 100%.

Real output:
`duration_150pct_210f.mp4`.

Independent ffprobe timing matches the 210-frame canonical timeline within the
existing ±3-frame output tolerance and audio is present.

## Speed qualification

### 200%

Proposal:
`SpeedEditProposal("C001", 200)`.

Candidate:
- source range remains 60 frames;
- speed = 200%;
- C001 timeline duration = 30;
- C002 start = 30;
- C003 start = 90;
- timeline end = 150;
- timeline offset 15 maps to source frame 30.

Real output:
`speed_200pct_150f.mp4`.

### 50%

Proposal:
`SpeedEditProposal("C001", 50)`.

Candidate:
- source range remains 60 frames;
- speed = 50%;
- C001 timeline duration = 120;
- C002 start = 120;
- C003 start = 180;
- timeline end = 240;
- timeline offset 15 maps to source frame 7.

Real output:
`speed_50pct_240f.mp4`.

Baseline timeline offset 15 maps to source frame 15.

The baseline, 200%, and 50% preview PNGs have three distinct SHA-256 hashes.

## Safety proof

- every candidate semantic hash matches the W7-004 verifier proof;
- `VerifiedAutoEditPlan.candidate_revision` remains equal to base revision;
- candidate states do not commit a revision;
- canonical ProjectState semantic JSON/hash is unchanged;
- CommandBus has no Undo/Redo history added by qualification;
- input video SHA-256 before/after is identical;
- all baseline/duration/fast/slow exports retain audio;
- provider profile unchanged;
- runtime UI unchanged;
- canonical AI apply not started;
- W7-006 transform qualification not started.

## Evidence bundle

11 files:
1. `00_w7_005_pacing_report.json`
2. `01_duration_qualification.json`
3. `02_speed_qualification.json`
4. `03_baseline_and_boundaries.json`
5. `preview_baseline_frame15.png`
6. `preview_speed_200_frame15.png`
7. `preview_speed_50_frame15.png`
8. `baseline_180f.mp4`
9. `duration_150pct_210f.mp4`
10. `speed_200pct_150f.mp4`
11. `speed_50pct_240f.mp4`

Verifier: **11/11 files PASS**.

## Quality gates

- FFmpeg qualification toolchain PASS;
- uv lock/frozen sync PASS;
- Ruff format/check PASS;
- mypy PASS — 68 source files;
- import contracts PASS;
- architecture PASS;
- source-of-truth PASS;
- no-secret PASS;
- frozen UI references 42/42 PASS;
- targeted W7-005 tests **6/6 PASS**;
- full pytest PASS;
- real-media evidence PASS;
- artifact upload PASS.

## Regression lock

All **26/26 workflows** triggered on accepted W7-005 HEAD are SUCCESS, all
attempt 1:

- W7-005 `37653613643`
- W6-010 `37653613592`
- W6-009 `37653613392`
- W6-008 `37653613516`
- W6-007 `37653613694`
- W6-006 `37653613363`
- W6-005 `37653613477`
- W6-004 `37653613589`
- W6-003 `37653613843`
- W6-002 `37653613722`
- W6-001 `37653613509`
- W5-010 `37653613691`
- W5-009 `37653613412`
- W5-008 `37653613502`
- W5-007 `37653613474`
- W5-006 `37653613641`
- W5-005 `37653613559`
- W5-004 `37653613421`
- W4 `37653613704`
- W3 `37653613446`
- W2 `37653613463`
- W1 `37653613627`
- W0 `37653613397`
- S10 `37653613605`
- S09 `37653613492`
- S08 `37653613644`

S08 portable build/smoke PASS.  
S09 portable UI shell PASS.  
S10 real-media + packaged smoke PASS.  
W0 engine qualification PASS.

## Gate

**S11-W7-005 = PASS.**

Next exact task after owner says `lanjutkan`:
**S11-W7-006 — Transform qualification only.**
