# PROJECT STATUS — AI NGERTI GEOPOLITIK

**Current STEP:** SF-STEP 11 — Feature Implementation Waves  
**Current wave:** **W5 — Subtitle + Narration**  
**W5 progress:** **S11-W5-001..006 PASS / W5-007 PASS_WITH_PROVISIONAL_MIC_HARDWARE / W5-008 PASS / W5-009 PASS**  
**Accepted W5-009 implementation HEAD:** `afcdd20c74f3870aee589ad83bf20cdae3861fea`  
**Accepted W5-009 workflow:** `37581393310` — SUCCESS  
**Next exact task:** **S11-W5-010 — Failure paths + evidence + regression lock**

## W5-009 combined real-media proof

The qualification uses one deterministic owned real-media project:
- 1920×1080 / 30 fps video fixture;
- base video audio at 880 Hz;
- narration WAV at 440 Hz;
- owned SRT source;
- canonical 180-frame project timeline.

Subtitle import/edit:
- original SRT imports through the accepted strict W5-002 path;
- working copy changes text to `EDITED COMBINED W5-009`;
- canonical timing changes to frame 45..135;
- Save Copy writes a new edited SRT;
- original source SRT SHA-256 remains unchanged;
- edited copy parses back to 1500..4500 ms with the edited text.

Subtitle timing preview proof:
- frame 30 is before the edited cue and matches the no-subtitle baseline;
- frame 51 is inside the edited cue and differs from the no-subtitle baseline.

Style proof:
- qualified Segoe UI style with visible fill/outline/background/top-center
  positioning is applied through canonical state;
- styled preview differs from the default-style preview;
- style survives .angproj save/reopen.

Animation matrix:
- Fade;
- Pop;
- Slide Up;
- Clean Documentary.

All four:
- produce preview output different from static subtitle;
- produce export frame output different from static subtitle;
- retain narration audio in their exported MP4;
- keep output duration within tolerance.

Narration:
- 440 Hz narration starts at canonical frame 60;
- real narration preview WAV is audible;
- final export proves substantially stronger 440 Hz energy after the offset than
  before the offset;
- final export also proves narration above the 880-Hz-only baseline;
- narration source SHA-256 remains unchanged.

Combined coexistence:
- the same Slide Up MP4 contains visible subtitle output and measurable narration
  audio;
- output is 1920×1080 / 30 fps with audio;
- project duration remains within ±3 frames of the canonical timeline.

Persistence:
- final project uses Slide Up animation;
- edited text/timing, style, animation, narration binding and frame offset all
  survive save/reopen;
- reopened preview matches the accepted Slide Up preview.

Boundaries preserved:
- no ASR;
- no speech-alignment claim;
- microphone hardware qualifier remains PROVISIONAL;
- FFmpeg remains qualification adapter only.

## W5-009 gates

Workflow `37581393310`:
- Ruff format PASS;
- Ruff check PASS;
- mypy PASS — 52 source files;
- import contracts PASS;
- architecture PASS;
- source-of-truth 70/70 PASS;
- secret scan PASS;
- frozen UI references 42/42 PASS;
- targeted W5-009 tests: **3/3 PASS**;
- full pytest PASS;
- combined real-media qualification PASS;
- evidence verifier **26/26 PASS**.

Artifact:
- `ANG-S11-W5-009-Combined-Qualification`;
- ID `11464149053`;
- size 49,935,397 bytes.

Same-HEAD foundation checks:
- W5-009 `37581393310` — SUCCESS;
- S09 `37581393138` — SUCCESS;
- S08 `37581393297` — SUCCESS.

Full W5 regression lock is intentionally reserved for W5-010.

## Hardware qualifier carried forward

W5-007 remains **PASS_WITH_PROVISIONAL_MIC_HARDWARE** because CI exposes no
real DirectShow microphone input. W5-009 does not alter that status.

## Exact next action

On owner **"lanjutkan"**, execute **S11-W5-010 only**.

W5-010 must execute failure-path coverage, history/backward-compatibility checks,
the deterministic W5 closure verifier, and the full W4/W3/W2/W1/W0/S10/S09/S08
regression lock.

Do not begin later waves, Gemini/provider work, SF-STEP 12, or release work in
the same turn.
