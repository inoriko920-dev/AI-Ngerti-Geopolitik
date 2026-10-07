# HANDOFF — AI NGERTI GEOPOLITIK

**Current phase:** SF-STEP 11  
**Current wave:** W5 — Subtitle + Narration  
**Last completed task:** S11-W5-001 — PASS  
**Accepted W5-001 HEAD:** `b5bf8543554bcf38d22a65510fe0376195676d46`  
**Accepted W5-001 run:** `37571740654` — SUCCESS  
**Next exact task:** S11-W5-002 — SRT import + validation

## Read first

Follow `AGENTS.md` and `docs/SOURCE_OF_TRUTH_INDEX.md`.

Read:
- W0–W4 evidence in order;
- `docs/project/W5_SUBTITLE_NARRATION_CONTRACT.md`;
- `docs/evidence/features/S11_W5_001_CANONICAL_SUBTITLE_NARRATION.md`;
- current PLAN/TASKS/PROJECT_STATUS.

## W5-001 canonical model now available

Domain:
- SubtitleTrack;
- SubtitleCue;
- SubtitleStyle;
- SubtitleAnimation;
- WordTiming;
- NarrationTrack.

ProjectState:
- `subtitle: SubtitleTrack | None`;
- `narration: NarrationTrack | None`.

Commands:
- `SetSubtitleTrackCommand`;
- `SetNarrationTrackCommand`.

Persistence:
- W5-001 state round-trips through .angproj;
- old files missing W5 fields load with safe None defaults;
- schema remains version 1.

Important constraint:
`SubtitleAnimation` currently accepts only `none`. This is intentional.
Do not enable Fade/Pop/Slide Up/Clean Documentary until W5-005 real-render
qualification.

## W5-001 regression lock

All are SUCCESS on the accepted implementation HEAD:
- W5-001 `37571740654`
- W4 `37571740680`
- W3 `37571740678`
- W2 `37571740732`
- W1 `37571741010`
- W0 `37571740664`
- S10 `37571740757`
- S09 `37571740743`
- S08 `37571740660`

## Next exact action

After owner says `lanjutkan`, execute **S11-W5-002 only**.

W5-002 scope:
- SRT UTF-8 / UTF-8 BOM parsing;
- timestamp/range/text validation;
- multiline text preservation;
- overlap/order detection with actionable typed failure;
- map valid parsed cues into the existing canonical SubtitleCue model;
- never overwrite/rewrite the source SRT during import.

Do not implement cue editor/working-copy save flow (W5-003) yet.
