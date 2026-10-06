# ARCHITECTURE — ANG-SF-STEP06-ARCH-TECH-v1.0

Canonical detail: `docs/planning/07_STEP_06_ARCHITECTURE_TECHNOLOGY_DECISION_AI_NGERTI_GEOPOLITIK.*`.

Dependency direction:

`presentation -> application -> domain`

`infrastructure -> application ports + domain contract types`

`bootstrap -> all` for construction only.

ProjectState is canonical truth. Manual and AI mutations must share semantic CommandBus/CommandBatch. Concrete media/provider/persistence/security dependencies stay behind adapters. Media engine remains behind `MediaEnginePort`; libopenshot is only the primary qualification candidate and MLT is fallback.
