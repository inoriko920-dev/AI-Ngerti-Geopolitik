# PROJECT STATUS — AI NGERTI GEOPOLITIK

**Current STEP:** SF-STEP 11 — Feature Implementation Waves  
**Current wave:** **W5 — Subtitle + Narration**  
**W5 progress:** **S11-W5-001/002/003/004/005/006 PASS**  
**Accepted W5-006 implementation HEAD:** `77770cd98210dbed18cbe1715111a935f2135b77`  
**Accepted W5-006 workflow:** `37577639655` — SUCCESS  
**Next exact task:** **S11-W5-007 — Microphone recording**

## W5-006 proven

Canonical import/binding:
- narration import uses the existing canonical media probe and asset identity rules;
- import + NarrationTrack binding is committed in one CommandBatch;
- a failed non-audio import does not leave a partial asset or narration binding;
- one canonical NarrationTrack remains the project source of truth;
- binding an already-imported audio asset is also supported.

Narration controls:
- frame-aware timeline start/offset;
- gain 0..400%;
- mute;
- fade-in;
- fade-out;
- fade validation is bounded by the actually audible narration segment inside
  the project timeline, not merely the source-file duration.

History/persistence:
- narration import/binding is Undo/Redo safe;
- narration control edits are Undo/Redo safe;
- .angproj save/reopen preserves narration source, offset and controls;
- narration source file remains unchanged.

Real runtime qualification:
- added FFmpeg narration projection behind the existing qualification adapter;
- narration source is trimmed to the audible project range;
- gain/mute/fades compile to real audio filters;
- canonical timeline offset compiles to real delay;
- narration mixes with the canonical timeline audio without replacing it;
- export duration remains governed by the base project timeline.

Preview:
- added a real narration-preview WAV excerpt rendered from canonical timeline
  position/range;
- preview evidence contains measurable 440 Hz narration energy.

Export:
- real video fixture base audio uses 880 Hz;
- real narration fixture uses 440 Hz;
- band-pass/volume evidence proves the 440 Hz narration is absent/low before
  its offset and present after the offset;
- real export evidence proves gain changes level, mute removes narration energy,
  and fade-in changes level near narration start;
- narrated export remains a valid MP4 with audio.

Microphone boundary:
- **no microphone/device capture implementation was started in W5-006**;
- microphone work remains exclusively W5-007.

Evidence:
`docs/evidence/features/S11_W5_006_NARRATION_IMPORT_BINDING.md`.

Artifact:
- `ANG-S11-W5-006-Narration`;
- ID `11462194359`;
- size 28,535,901 bytes.

## W5-006 quality/evidence gate

Workflow `37577639655`:
- Ruff format PASS;
- Ruff check PASS;
- mypy PASS;
- import contracts PASS;
- architecture PASS;
- source-of-truth 70/70 PASS;
- secret scan PASS;
- targeted W5-006 tests: **5/5 PASS**;
- full pytest PASS;
- real W5-006 audio evidence PASS;
- evidence verifier: **11/11 PASS**.

## Regression lock on accepted W5-006 HEAD

All SUCCESS:
- W5-006: `37577639655`;
- W5-005: `37577639727`;
- W5-004: `37577639737`;
- W4: `37577639656`;
- W3: `37577639667`;
- W2: `37577639693`;
- W1: `37577639687`;
- W0: `37577639704`;
- S10: `37577639665`;
- S09: `37577639668`;
- S08: `37577639634`.

This includes MLT W0/W2 qualification, W3/W4 real output, W5 subtitle
qualification, S10 real-media + packaged smoke + portable UI, and S08/S09
portable regressions.

## Exact next action

On owner **"lanjutkan"**, execute **S11-W5-007 — Microphone recording only**.

Do not start frozen UI parity, combined W5 qualification/closure,
Gemini/provider work, or later tasks in the same turn.
