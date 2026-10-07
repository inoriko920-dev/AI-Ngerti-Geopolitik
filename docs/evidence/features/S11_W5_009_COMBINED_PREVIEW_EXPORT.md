# S11 W5-009 — Combined Subtitle + Narration Preview/Export Qualification

**Status:** PASS  
**Accepted implementation HEAD:** `afcdd20c74f3870aee589ad83bf20cdae3861fea`  
**Accepted workflow:** `37581393310` — SUCCESS  
**Artifact:** `ANG-S11-W5-009-Combined-Qualification`  
**Artifact ID:** `11464149053`

## Scope

W5-009 qualifies the previously implemented canonical subtitle and narration
systems together in one deterministic real-media project.

It does not add new product features and does not begin W5-010 closure.

## Owned fixture

Video:
- 1920×1080;
- 30 fps;
- base audio sine = 880 Hz;
- canonical project clip = 180 frames.

Narration:
- PCM WAV;
- 48 kHz;
- sine = 440 Hz;
- canonical start = frame 60;
- gain = 80%;
- fade in/out = 15 frames.

Subtitle source:
- owned UTF-8 SRT;
- original cue initially 1000..4000 ms;
- SHA-256 captured before workflow mutation.

## Canonical subtitle edit flow

The source SRT imports through W5-002.

SubtitleWorkingCopy then edits:
- text -> `EDITED COMBINED W5-009`;
- IN -> frame 45;
- OUT -> frame 135.

SubtitleWorkingCopyService writes:
`source_original.edited.srt`.

The original source SRT is not overwritten.

The saved edited copy parses back as:
- 1500 ms;
- 4500 ms;
- edited text retained.

## Timing proof

Preview evidence uses the exact same video source frame with and without
subtitle state.

At frame 30:
- edited cue has not started;
- combined-state preview matches the no-subtitle baseline.

At frame 51:
- edited cue is active;
- combined-state preview differs from the no-subtitle baseline.

This proves the edited canonical IN boundary is respected.

## Style proof

Qualified style:
- Segoe UI;
- font size 80;
- fill #FFD166;
- outline #003049;
- outline width 5 px equivalent;
- shadow 3 px equivalent;
- background box 60%;
- top-center alignment;
- margin 90.

The styled preview differs from the default-style preview.

The same style survives save/reopen.

## Animation matrix

UI-enabled/render-qualified presets:
- Fade;
- Pop;
- Slide Up;
- Clean Documentary.

For every preset:
- real preview PNG differs from the static subtitle preview;
- real exported MP4 frame differs from the static subtitle export frame;
- exported MP4 retains audio;
- exported duration is within ±3 frames of the canonical timeline;
- narration 440 Hz energy remains present.

Final persisted animation:
**Slide Up**.

## Narration synchronization

Narration preview:
- real PCM WAV rendered from canonical timeline;
- 440 Hz energy passes the audible qualification threshold.

Final combined export:
- 440 Hz energy is materially lower before the frame-60 narration offset;
- 440 Hz energy is materially stronger after the offset;
- 440 Hz energy is materially stronger than the 880-Hz-only baseline.

Narration source SHA-256 remains unchanged.

## Same-export coexistence

The final Slide Up export simultaneously has:
- visual subtitle evidence;
- measurable narration 440 Hz evidence;
- base video;
- audio present.

Output qualification:
- 1920×1080;
- 30 fps;
- audio present;
- duration within ±3 frames.

This directly proves subtitle + narration coexist in the same real export.

## Persistence

After committing final Slide Up:
- project saved as `.angproj`;
- reopened semantic hash matches;
- edited text survives;
- frame 45..135 timing survives;
- style survives;
- Slide Up survives;
- narration binding survives;
- narration frame-60 offset survives;
- reopened preview equals accepted Slide Up preview.

## Boundaries

W5-009 uses:
- no ASR;
- no transcription;
- no speech-alignment claim.

Microphone hardware status remains:
**PROVISIONAL**.

FFmpeg remains a qualification adapter and does not replace the production
engine priority decision.

## Tests and gates

Target:
`tests/unit/test_step11_w5_009_combined.py`

Targeted result:
**3/3 PASS**.

Workflow `37581393310`:
- Ruff format PASS;
- Ruff check PASS;
- mypy PASS — 52 source files;
- import contracts PASS;
- architecture PASS;
- source-of-truth 70/70 PASS;
- secret scan PASS;
- UI reference integrity 42/42 PASS;
- targeted W5-009 tests PASS;
- full pytest PASS;
- owned real-media fixture PASS;
- combined qualification PASS;
- evidence verifier **26/26 PASS**.

## Artifact

- name: `ANG-S11-W5-009-Combined-Qualification`;
- ID: `11464149053`;
- size: 49,935,397 bytes.

The artifact includes:
- original + edited SRT;
- 440 Hz narration WAV;
- baseline/static/animated preview PNGs;
- narration preview WAV;
- Fade/Pop/Slide Up/Clean Documentary MP4s;
- extracted export frames;
- final .angproj;
- JSON evidence reports.

## Same-HEAD foundation checks

On accepted W5-009 HEAD:
- W5-009: `37581393310` — SUCCESS;
- S09: `37581393138` — SUCCESS;
- S08: `37581393297` — SUCCESS.

The complete historical regression lock belongs to W5-010.

## Next

**S11-W5-010 — Failure paths + evidence + regression lock only.**
