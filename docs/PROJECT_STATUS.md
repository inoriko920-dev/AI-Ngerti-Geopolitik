# PROJECT STATUS — AI NGERTI GEOPOLITIK

**Current STEP:** SF-STEP 11 — Feature Implementation Waves  
**Last completed wave:** **W3 — PASS**  
**Accepted W3 implementation HEAD:** `79217e687a9930087260e7dd3203b6ab8492b477`  
**Accepted W3 run:** `37545032247` — SUCCESS  
**Next exact wave:** **W4 — Titles / Transitions / Effects**

## W3 proven

Canonical properties:
- inspector context binding: project / track / asset / clip;
- clip video position, scale, rotation, opacity;
- crop/basic composition;
- audio volume, pan, fade-in/fade-out;
- brightness, exposure, contrast, saturation, temperature, tint;
- uniform speed 25%–400%;
- speed-aware timeline duration and source-frame mapping;
- ripple of later clips after speed duration change;
- all property mutations through CommandBus;
- cross-property Undo/Redo;
- .angproj persistence + old-schema safe defaults.

Runtime/UI:
- real PySide6 property inspector emits semantic intents;
- Reverse is visibly disabled, not faked.

Real media evidence:
- baseline preview and property preview differ;
- real W3 export = 1920×1080, 30 fps, 180 frames;
- canonical timeline = 180 frames;
- audio stream present;
- evidence verifier PASS 8/8.

Evidence:
`docs/evidence/features/S11_W3_PROPERTIES_VIDEO_AUDIO_COLOR_SPEED.md`.

Artifact:
- ID `11449982099`;
- digest
  `sha256:81077bc180eb29506aca3b4a7d1720675082e09759650de829083bca3ecb8533`.

## Regression lock

On accepted W3 implementation HEAD:
- W3: `37545032247` — SUCCESS;
- W2: `37545032183` — SUCCESS;
- W1: `37545031989` — SUCCESS;
- W0: `37545032172` — SUCCESS;
- S10: `37545032214` — SUCCESS;
- S09: `37545032107` — SUCCESS;
- S08: `37545032095` — SUCCESS.

## Engine direction

Unchanged:
- MLT = primary production-engine implementation candidate;
- ProjectState + CommandBus + MediaEnginePort remain canonical;
- FFmpeg W3 is a real qualification adapter, not an engine switch;
- final production MLT property mapping/native DLL closure remains a later
  hardening/release gate.

## Reverse

Reverse remains intentionally **disabled** because it has not passed safe W3
backend qualification. Do not expose it as functional until real evidence
exists.

## Exact next action

On owner **"lanjutkan"**, execute **W4 only — Titles / Transitions / Effects**.

Do not enter W5, W8/Gemini, SF-STEP 12, or final release work until W4 is
completed or explicitly gated.
