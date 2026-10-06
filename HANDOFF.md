# HANDOFF — AI NGERTI GEOPOLITIK

**Current phase:** SF-STEP 11  
**Last completed wave:** W3 — PASS  
**Accepted W3 implementation HEAD:** `79217e687a9930087260e7dd3203b6ab8492b477`  
**Accepted W3 run:** `37545032247` — SUCCESS  
**Next exact wave:** W4 — Titles / Transitions / Effects

## Read first

Follow `AGENTS.md` and `docs/SOURCE_OF_TRUTH_INDEX.md`.

Read STEP 08–10 evidence, then:
- `S11_W0_BASELINE_AND_ENGINE_QUALIFICATION.md`;
- `S11_W1_PROJECT_MEDIA_PERSISTENCE.md`;
- `S11_W2_TIMELINE_PLAYBACK_CORE.md`;
- `S11_W3_PROPERTIES_VIDEO_AUDIO_COLOR_SPEED.md`.

## W3 outcome

Verified canonical W3 behavior:
- inspector binding to project/track/asset/clip;
- video position/scale/rotation/opacity;
- crop/basic composition;
- audio volume/pan/fades;
- basic color controls;
- speed 25%–400% with duration recompute/ripple;
- semantic Qt property intents;
- CommandBus Undo/Redo;
- persistence and old-schema default compatibility;
- preview reflects property change;
- real export reflects W3 state and retains audio.

Real evidence export:
- 1920×1080;
- 30 fps;
- 180 canonical frames = 180 probed frames;
- SHA-256
  `faf166bb5d78e997d264d104fcc76bb72f4f5415081511b1a4a14376afb3b48b`.

W3 artifact:
- ID `11449982099`;
- digest
  `sha256:81077bc180eb29506aca3b4a7d1720675082e09759650de829083bca3ecb8533`.

## Locked interpretation carried forward

- ProjectState remains canonical truth.
- Property mutation remains CommandBus/CommandBatch.
- Presentation may emit intents but not mutate concrete engines.
- MLT remains the primary production-engine implementation candidate.
- FFmpeg remains a real qualification adapter behind MediaEnginePort.
- AAVC UI-001..UI-042 remains frozen 1:1.
- Reverse is **not supported** in W3 and must remain visibly disabled until a
  later real backend qualification proves it safe.
- W3 does not claim that final distributable MLT DLL/property mapping is done.

## Regression IDs on accepted W3 implementation HEAD

- W3: `37545032247`;
- W2: `37545032183`;
- W1: `37545031989`;
- W0: `37545032172`;
- S10: `37545032214`;
- S09: `37545032107`;
- S08: `37545032095`.

All are SUCCESS.

## Next exact action

After owner says `lanjutkan`, execute **W4 only — Titles / Transitions /
Effects**.

Do not start W5, AI/Gemini coverage, SF-STEP 12, or final release packaging.
