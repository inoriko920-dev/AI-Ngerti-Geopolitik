# PLAN — CURRENT IMPLEMENTATION PHASE

**SF-STEP 11 is active. W0 = PASS.**

W0 accepted:
- HEAD `f54993851f85aa5672f0d86dcb7e5ea3a49c7ae6`;
- run `37533447729`;
- regression and native-engine qualification green.

Engine implementation priority now follows evidence:
- MLT primary candidate for STEP 11;
- libopenshot direct binding blocked;
- architecture boundaries unchanged.

## Active next wave

**W1 — Project, Media & Persistence Foundation**

Implementation remains serial and regression-safe. W1 must harden the project
lifecycle and media model before W2 expands timeline/playback behavior.

Required W1 outcomes:
- no accidental state loss on project lifecycle;
- safe atomic save/save-as;
- stable video/audio/image asset IDs and metadata;
- explicit offline/missing media state;
- queryable media-bin model;
- persisted project settings;
- autosave snapshots that never overwrite the canonical project silently.

Do not begin W2 until W1 evidence is green.
