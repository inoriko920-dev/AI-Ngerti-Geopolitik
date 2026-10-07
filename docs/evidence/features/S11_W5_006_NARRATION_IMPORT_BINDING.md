# S11 W5-006 — Narration Import + Binding

**Status:** PASS  
**Accepted implementation HEAD:** `77770cd98210dbed18cbe1715111a935f2135b77`  
**Accepted workflow:** `37577639655` — SUCCESS  
**Artifact:** `ANG-S11-W5-006-Narration`  
**Artifact ID:** `11462194359`

## Scope

W5-006 implemented first-class narration import/binding and qualified the
canonical narration controls against real audio output.

It did not implement microphone recording, frozen UI parity, W5 final combined
qualification or Gemini/provider behavior.

## Application import/binding

Added:
`src/ai_ngerti_geopolitik/application/narration.py`.

`NarrationImportService.import_and_bind(...)`:
- probes the source through the existing MediaProbePort;
- rejects non-audio sources before canonical mutation;
- creates an Asset using the existing W1 media identity rules;
- creates a canonical NarrationTrack;
- commits ImportAssetCommand + SetNarrationTrackCommand in one CommandBatch.

This makes import/binding atomic:
- success adds both the audio asset and narration binding in one revision;
- Undo removes both;
- Redo restores both;
- invalid/non-audio input leaves the project unchanged.

`bind_existing(...)` binds an already-canonical audio asset without
duplicating it.

## Canonical narration controls

Qualified:
- timeline_start in canonical frames;
- gain_percent;
- muted;
- fade_in_frames;
- fade_out_frames.

Domain validation now bounds fades against the narration segment that is
actually audible inside the project timeline:
`min(source_duration, timeline_end - narration_start)`.

This prevents a fade from validating merely because it fits the source file
when the project itself cuts the narration earlier.

## FFmpeg qualification projection

Added:
`src/ai_ngerti_geopolitik/infrastructure/ffmpeg_narration.py`.

The qualification plan compiles:
- source trim to audible range;
- gain via real volume filter;
- mute via zero gain;
- fade in;
- fade out;
- frame offset to real audio delay.

`FfmpegSliceMediaEngine.export(...)` now:
- keeps the existing canonical timeline audio;
- adds narration as a separate real input;
- applies the narration plan;
- mixes base audio + narration using an explicit audio mix;
- keeps output duration controlled by the base project timeline.

FFmpeg remains a qualification adapter, not a production-engine selection
change.

## Narration preview evidence

Added qualification method:
`preview_narration_audio(...)`.

It renders a real PCM WAV excerpt for a requested canonical timeline frame/range
using the same narration source/timing/control projection.

The evidence preview contains measurable narration-band energy.

This is audio qualification, not the frozen W5 UI implementation; UI wiring
remains W5-008.

## Real evidence design

Video fixture:
- 1920×1080 / 30 fps;
- existing base audio sine: **880 Hz**.

Narration fixture:
- WAV / 48 kHz;
- sine: **440 Hz**.

Using different frequencies allows objective band-pass measurement of narration
without confusing it with the base video audio.

Evidence proves:
- before canonical narration offset, 440 Hz band energy remains low;
- after narration offset, 440 Hz energy becomes materially stronger;
- narration preview WAV has audible/measurable 440 Hz energy;
- boosted gain produces stronger 440 Hz level than 70% gain;
- mute removes/reduces narration-band energy;
- fade-in produces lower narration level near its start than at its steady
  section;
- narrated export remains valid and retains audio;
- source narration WAV SHA-256 remains unchanged.

Evidence includes:
- baseline MP4;
- narrated MP4;
- muted MP4;
- boosted-gain MP4;
- narration preview WAV;
- source narration WAV;
- project .angproj;
- binding, measurements and history/persistence JSON reports.

## History and persistence

Proven:
- atomic import+bind Undo removes the imported narration asset and binding;
- Redo restores them;
- narration control mutation is reversible;
- project save/reopen preserves the narration track;
- semantic hash survives reopen;
- source media remains untouched.

## Microphone boundary

W5-006 intentionally does not:
- enumerate recording devices;
- request microphone permissions;
- capture microphone audio;
- create RecorderPort;
- claim microphone hardware support.

Those belong only to W5-007.

## Tests and gates

Target:
`tests/unit/test_step11_w5_006_narration.py`

Targeted result:
- **5/5 PASS**.

Workflow `37577639655`:
- Ruff format PASS;
- Ruff check PASS;
- mypy PASS — 49 source files;
- import contracts PASS;
- architecture PASS;
- source-of-truth 70/70 PASS;
- secret scan PASS;
- targeted W5-006 tests PASS;
- full pytest PASS;
- real W5-006 audio evidence PASS;
- evidence verifier **11/11 PASS**.

## Artifact

- name: `ANG-S11-W5-006-Narration`;
- ID: `11462194359`;
- size: 28,535,901 bytes.

## Regression lock

All workflows on the accepted W5-006 implementation HEAD are SUCCESS:
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

This includes MLT playback qualification, real media output, packaged media
smoke, portable UI regression and Windows foundation regression.

## Next

**S11-W5-007 — Microphone recording only.**

A real hardware gate applies. Never fake physical microphone evidence.
