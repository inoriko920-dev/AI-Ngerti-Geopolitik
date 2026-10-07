# PROJECT STATUS — AI NGERTI GEOPOLITIK

**Current STEP:** SF-STEP 11 — Feature Implementation Waves  
**Current wave:** **W5 — Subtitle + Narration**  
**W5 progress:** **S11-W5-001/002/003/004 PASS**  
**Accepted W5-004 implementation HEAD:** `687d31585d476541711978d5f69e5e7eafe72245`  
**Accepted W5-004 workflow:** `37574406573` — SUCCESS  
**Next exact task:** **S11-W5-005 — Render-backed subtitle animation + per-word boundary**

## W5-004 proven

Canonical mutation/history:
- added semantic `SetSubtitleStyleCommand`;
- style mutation requires an existing canonical SubtitleTrack;
- mutation flows through CommandBus/CommandBatch;
- Undo restores the prior style;
- Redo restores the styled state.

Persistence:
- font family/size, fill, outline, shadow, background box/opacity,
  alignment and margin persist in .angproj;
- save/reopen semantic hash remains stable;
- legacy W5 defaults remain compatible.

Working-copy integration:
- dirty cue edits stay local;
- changing project subtitle style does not discard the cue working copy;
- later Save Copy carries the latest project style forward instead of reverting
  to the working-copy baseline metadata;
- source SRT remains unchanged.

Render qualification:
- FFmpeg remains a qualification adapter only;
- preview renders the cue active at the requested canonical timeline frame;
- export applies subtitle cues after canonical timeline composition;
- every enabled style dimension received an independent real preview variant:
  font family, font size, fill, outline, shadow, background box/opacity,
  alignment and safe vertical margin;
- every preview variant differed from the baseline image;
- final styled export is valid and retains audio.

Render-qualified font-family boundary for this adapter:
- Arial;
- Segoe UI.

Other font-family strings may remain canonical data but are explicitly rejected
by this qualification adapter until independently proven. Future UI must not
advertise unqualified fonts as available.

Animation boundary:
- SubtitleAnimation remains `none` only;
- W5-004 does not enable Fade/Pop/Slide Up/Clean Documentary;
- animation qualification remains W5-005.

Evidence:
`docs/evidence/features/S11_W5_004_SUBTITLE_STYLE.md`.

Artifact:
- `ANG-S11-W5-004-Subtitle-Style`;
- ID `11461154582`;
- size 10,534,700 bytes.

## W5-004 quality/evidence gate

Workflow `37574406573`:
- Ruff format PASS;
- Ruff check PASS;
- mypy PASS;
- import contracts PASS;
- architecture PASS;
- source-of-truth 70/70 PASS;
- secret scan PASS;
- targeted W5-004 tests: **6/6 PASS**;
- full pytest PASS;
- real W5-004 evidence PASS;
- evidence verifier: **18/18 PASS**.

## Regression lock on accepted W5-004 HEAD

All SUCCESS:
- W5-004: `37574406573`;
- W4: `37574406598`;
- W3: `37574406680`;
- W2: `37574406711`;
- W1: `37574406582`;
- W0: `37574406562`;
- S10: `37574406568`;
- S09: `37574406585`;
- S08: `37574406553`.

This includes MLT W0/W2 qualification, W3/W4 real-output evidence, S10
real-media vertical slice, packaged real-media smoke, portable UI regression,
and S08/S09 portable regressions.

## Exact next action

On owner **"lanjutkan"**, execute **S11-W5-005 only**.

W5-005 must qualify actual subtitle animation behavior and the per-word timing
boundary. Do not start narration import, microphone recording, frozen UI parity,
Gemini/provider work or later W5 tasks in the same turn.
