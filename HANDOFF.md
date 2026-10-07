# HANDOFF — AI NGERTI GEOPOLITIK

**Current phase:** SF-STEP 11  
**Current wave:** W5 — Subtitle + Narration  
**Last completed task:** S11-W5-009 — PASS  
**Accepted W5-009 HEAD:** `afcdd20c74f3870aee589ad83bf20cdae3861fea`  
**Accepted W5-009 run:** `37581393310` — SUCCESS  
**Next exact task:** S11-W5-010 — Failure paths + evidence + regression lock

## Read first

Follow `AGENTS.md` and `docs/SOURCE_OF_TRUTH_INDEX.md`.

Read:
- W0–W4 evidence;
- W5 contract;
- W5-001 through W5-009 evidence;
- current PLAN/TASKS/PROJECT_STATUS.

## W5-009 real combined qualification

Owned fixture:
- 1920×1080 / 30 fps;
- base 880 Hz video audio;
- 440 Hz narration;
- owned source SRT;
- canonical 180-frame timeline.

Canonical flow:
1. import video;
2. import source SRT;
3. edit subtitle text/timing in SubtitleWorkingCopy;
4. Save Copy to a new SRT and commit;
5. apply qualified subtitle style;
6. bind narration at frame 60;
7. qualify static subtitle+narration;
8. qualify Fade/Pop/Slide Up/Clean Documentary;
9. commit final Slide Up;
10. save/reopen project;
11. verify source SRT and narration media unchanged.

## Proven evidence

Subtitle:
- source SRT unchanged;
- edited copy = 1500..4500 ms;
- edited text survives;
- frame 30 no subtitle;
- frame 51 subtitle visible;
- style visible;
- style survives reopen.

Animations:
- all four UI-enabled presets differ from static preview;
- all four differ from static export frame;
- all four exported files retain audio and duration tolerance.

Narration:
- preview WAV audible;
- frame-60 offset measurable through 440 Hz spectral evidence;
- same combined export contains subtitle image evidence + narration audio
  evidence.

Persistence/output:
- save/reopen semantic hash match;
- subtitle and narration both present;
- final output 1920×1080 / 30 fps / audio;
- duration within ±3 frames.

Artifact:
`ANG-S11-W5-009-Combined-Qualification`
ID: `11464149053`
Size: 49,935,397 bytes.

Verifier:
**26/26 PASS**.

## Critical boundaries for W5-010

- W5-010 is closure/regression only; do not add new product scope.
- Test malformed SRT and dirty-working-copy guards.
- Test missing/corrupt narration without fake success.
- Test failed recording preserves existing narration.
- Prove subtitle/narration Undo/Redo.
- Prove old W4 project loads with safe W5 defaults.
- Re-run quality, architecture, UI, security and full pytest.
- Build deterministic W5 closure evidence/verifier.
- Lock W4/W3/W2/W1/W0/S10/S09/S08 regressions.
- Carry microphone hardware qualifier forward honestly if no physical device is
  available.
- Do not start later waves or SF-STEP 12.

## Next exact action

After owner says `lanjutkan`, execute **S11-W5-010 only**.
