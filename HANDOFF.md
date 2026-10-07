# HANDOFF — AI NGERTI GEOPOLITIK

**Current phase:** SF-STEP 11  
**Current wave:** W5 — Subtitle + Narration  
**Last completed task:** S11-W5-004 — PASS  
**Accepted W5-004 HEAD:** `687d31585d476541711978d5f69e5e7eafe72245`  
**Accepted W5-004 run:** `37574406573` — SUCCESS  
**Next exact task:** S11-W5-005 — Render-backed subtitle animation + per-word boundary

## Read first

Follow `AGENTS.md` and `docs/SOURCE_OF_TRUTH_INDEX.md`.

Read:
- W0–W4 evidence in order;
- W5 contract;
- W5-001 / W5-002 / W5-003 / W5-004 evidence;
- current PLAN/TASKS/PROJECT_STATUS.

## W5-004 implementation now available

Application/domain path:
- existing canonical SubtitleStyle;
- new `SetSubtitleStyleCommand`;
- CommandBus Undo/Redo;
- .angproj persistence/reopen.

Qualification renderer:
- `infrastructure/ffmpeg_subtitles.py`;
- preview chooses the canonical active cue;
- export applies cue timing windows after timeline composition;
- render-qualified font families: Arial and Segoe UI.

Qualified style surface:
- font family;
- font size;
- fill color;
- outline color/width;
- shadow;
- background box/opacity;
- top/center/bottom-center alignment;
- safe vertical margin.

Working-copy interaction:
- style changes do not discard dirty cue edits;
- Save Copy carries current project style into the newly bound copied SRT;
- source SRT protection from W5-003 remains intact.

## W5-004 evidence

Workflow:
`37574406573` — SUCCESS

Evidence verifier:
18/18 PASS.

Artifact:
`ANG-S11-W5-004-Subtitle-Style`
ID: `11461154582`

## Critical boundaries carried forward

- FFmpeg is qualification, not a production-engine switch.
- SubtitleAnimation is still canonical `none` only.
- Do not advertise unqualified fonts.
- W5-005 may enable only animations with real preview/export proof.
- No ASR/transcription/automatic word alignment claims.
- Deterministic word distribution, if added, must be explicitly labeled
  **not speech alignment**.
- Do not start narration/recording/Gemini work.

## Regression lock on W5-004 accepted HEAD

All SUCCESS:
- W5-004 `37574406573`
- W4 `37574406598`
- W3 `37574406680`
- W2 `37574406711`
- W1 `37574406582`
- W0 `37574406562`
- S10 `37574406568`
- S09 `37574406585`
- S08 `37574406553`

## Next exact action

After owner says `lanjutkan`, execute **S11-W5-005 only**:
qualify supported subtitle animation presets with real preview/export evidence,
then implement the explicit per-word timing boundary without claiming speech
alignment.

Do not start W5-006 or later tasks.
