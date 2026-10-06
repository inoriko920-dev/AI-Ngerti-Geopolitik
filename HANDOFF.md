# HANDOFF — AI NGERTI GEOPOLITIK

**Current phase:** SF-STEP 11  
**Last completed wave:** W2 — PASS  
**Accepted W2 implementation HEAD:** `4486da29883bc42e9cd12d5d13a7784f347dc2d3`  
**Accepted W2 run:** `37542485728` — SUCCESS  
**Next exact wave:** W3 — Properties: Video, Audio, Color & Speed

## Read first

Follow `AGENTS.md` and `docs/SOURCE_OF_TRUTH_INDEX.md`.

Read:
- STEP 08–10 evidence;
- `docs/evidence/features/S11_W0_BASELINE_AND_ENGINE_QUALIFICATION.md`;
- `docs/evidence/features/S11_W1_PROJECT_MEDIA_PERSISTENCE.md`;
- `docs/evidence/features/S11_W2_TIMELINE_PLAYBACK_CORE.md`.

## W2 outcome

Verified:
- video-track CRUD/order/lock/mute/visibility;
- clip move/duplicate/delete/selection with stable IDs;
- ripple/collision policy;
- split and left/right trim;
- Undo/Redo through CommandBus;
- playback play/pause/seek/scrub;
- marker, IN/OUT, snap, zoom, follow;
- Qt keyboard/context actions routed semantically;
- save/reopen of W2 state;
- real MLT Windows playback/render projection;
- 1000-clip deterministic stress fixture.

W2 core artifact:
- ID `11449376822`;
- digest
  `sha256:1c7a5812b7d249caf51af294f14ce734cc3e58bc314cdf76b5a45ab543641e83`.

MLT artifact:
- ID `11448897281`;
- digest
  `sha256:c27584b57760121eff068040345aedf95ebd6bfe36a49af691030cfe9b8a3846`.

## Regression IDs on accepted W2 implementation HEAD

- W2: `37542485728`;
- W1: `37542485911`;
- W0: `37542485906`;
- S10: `37542485819`;
- S09: `37542485810`;
- S08: `37542485951`.

All are SUCCESS.

## Locked interpretation carried forward

- ProjectState remains canonical truth.
- All canonical mutation remains CommandBus/CommandBatch.
- MLT remains the primary production-engine implementation candidate.
- MediaEnginePort stays the boundary.
- Presentation does not mutate engine/project objects directly.
- AAVC UI-001..UI-042 remains frozen 1:1.
- W2 canonical tracks are video-track semantics; richer audio/property behavior
  is not falsely backfilled into W2.
- MLT W2 evidence is a real canonical V1 projection, not final arbitrary
  multitrack production support.

## Next exact action

Execute **W3 only — Properties: Video, Audio, Color & Speed** after owner says
`lanjutkan`.

W3 should cover serially:
1. inspector binding by selected object type;
2. video position/scale/rotation/opacity;
3. crop/basic composition;
4. audio volume/pan/fade in/out;
5. brightness/exposure/contrast/saturation/WB/tint policy;
6. uniform speed + duration recompute;
7. reverse only if engine qualification is safe, otherwise explicitly disabled;
8. cross-property Undo/Redo + project reload + preview/output evidence.

Do not start W4 or STEP 12.
