# HANDOFF — AI NGERTI GEOPOLITIK

**Current phase:** SF-STEP 11  
**Last completed wave:** W4 — PASS  
**Accepted W4 implementation HEAD:** `3e3cd376189e9f183e70ca537ad25f037e25bcd7`  
**Accepted W4 run:** `37570612799` — SUCCESS  
**Next exact wave:** W5 — derive exact scope before coding

## Read first

Follow `AGENTS.md` and `docs/SOURCE_OF_TRUTH_INDEX.md`.

Read STEP 08–10 evidence, then:
- `S11_W0_BASELINE_AND_ENGINE_QUALIFICATION.md`;
- `S11_W1_PROJECT_MEDIA_PERSISTENCE.md`;
- `S11_W2_TIMELINE_PLAYBACK_CORE.md`;
- `S11_W3_PROPERTIES_VIDEO_AUDIO_COLOR_SPEED.md`;
- `S11_W4_TITLES_TRANSITIONS_EFFECTS.md`.

## W4 outcome

Verified canonical W4 behavior:
- per-clip title overlay state;
- real `fade_black` transition plus `none`;
- nine render-backed AAVC effects: Fade, Pop, Breathe, Stomp, Tumble,
  Tectonic, Rise, Pan and Drift;
- effect enter/exit, bounded intensity and lock;
- semantic Qt creative intents;
- CommandBus Undo/Redo;
- persistence and old-schema default compatibility;
- preview reflects W4 state;
- real export reflects W4 state and retains audio.

W4 evidence report:
- `status = PASS`;
- title overlay = true;
- fade_black transition = true;
- render-backed effects = true;
- unsupported legacy effects hidden = true;
- crossfade claimed = false;
- Undo/Redo = true;
- save/reopen = true;
- preview changed = true;
- export valid = true;
- export has audio = true;
- verifier PASS 8/8.

W4 artifact:
- name `ANG-S11-W4-Creative`;
- ID `11460641864`;
- digest
  `sha256:06e87e681e0407b6e576b0ab8247eee3c900c50af7bfe2f38f81015bea64630e`.

## Locked interpretation carried forward

- ProjectState remains canonical truth.
- W4 mutation remains CommandBus/CommandBatch.
- Presentation may emit intents but not mutate concrete engines.
- MLT remains the primary production-engine implementation candidate.
- FFmpeg remains a real qualification adapter behind MediaEnginePort.
- AAVC UI-001..UI-042 remains frozen 1:1.
- Reverse remains unsupported and visibly disabled.
- `fade_black` is fade-through-black, not dissolve/crossfade.
- Do not expose Wipe, Blur, Succession, Baseline, Neon, Scrapbook, Brush, Ink,
  Digital, Spray Paint, Sketch or Gradient as functional W4 effects.
- W4 does not claim that final distributable MLT DLL/mapping is done.

## Regression IDs on accepted W4 implementation HEAD

- W4: `37570612799`;
- W3: `37570612705`;
- W2: `37570612673`;
- W1: `37570612719`;
- W0: `37570612737`;
- S10: `37570612830`;
- S09: `37570612683`;
- S08: `37570612789`.

All are SUCCESS.

## Next exact action

After owner says `lanjutkan`, execute **W5 only**.

Before implementing W5, derive and record its exact serial task contract from
the frozen Product/UI/Architecture source-of-truth. Do not infer a W5 scope
only from legacy code.

Do not jump to Gemini/AI coverage, SF-STEP 12, or final release packaging.
