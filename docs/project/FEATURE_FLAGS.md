# STEP 11 FEATURE / READINESS FLAGS

This document mirrors the runtime registry in
`src/ai_ngerti_geopolitik/application/feature_flags.py`.

| Key | State at W0 entry | Meaning |
| --- | --- | --- |
| canonical_editing_backbone | VERIFIED | STEP 10 E2E is real and green |
| production_media_engine | QUALIFYING | W0 must choose/qualify Windows production direction |
| continuous_playback | QUALIFYING | transport semantics exist; native playback evidence pending |
| libopenshot_direct_binding | BLOCKED | current Windows/package/license evidence is insufficient |
| gemini_service | RESERVED | real service wiring belongs to STEP 12 |

Rules:
- no UI may claim a QUALIFYING/BLOCKED feature is production-ready;
- a state changes only with evidence;
- Gemini remains outside STEP 11 real-network acceptance.
