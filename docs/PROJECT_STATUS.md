# PROJECT STATUS — AI NGERTI GEOPOLITIK

**Current STEP:** SF-STEP 11 — Feature Implementation Waves  
**Last completed wave:** **W4 — PASS**  
**Accepted W4 implementation HEAD:** `3e3cd376189e9f183e70ca537ad25f037e25bcd7`  
**Accepted W4 run:** `37570612799` — SUCCESS  
**Current wave:** **W5 — Subtitle + Narration**  
**W5 state:** **CONTRACT_LOCKED / IMPLEMENTATION_NOT_STARTED**  
**Next exact task:** **S11-W5-001 — Canonical subtitle/narration model**

## W5 scope decision

W5 is definitively Subtitle + Narration.

Source-of-truth basis:
- Master Blueprint Subtitle System + Narration/Audio chapters;
- recommended TECH-WAVE 08 = Subtitle + Narration;
- product F-010/F-011/F-012 and FR-011/FR-012 = MUST parity;
- frozen UI SCR-008, SCR-009, UI-017, UI-018, UI-033..UI-036,
  WIN-001 and WIN-003;
- architecture requires ProjectState ownership and dependency adapters.

Full locked contract:
`docs/project/W5_SUBTITLE_NARRATION_CONTRACT.md`.

## W5 closure boundary

W5 must prove:
- canonical/persisted subtitle and narration state;
- SRT import/edit/timing safety;
- render-backed style/animation only;
- narration audible and synchronized;
- microphone recording cannot destroy an existing narration on failure;
- preview/export evidence;
- full regression lock.

A real microphone smoke is required for a full W5 PASS when a Windows capture
device is available. If only deterministic port/adapter tests are possible, W5
must be labeled `PASS_WITH_PROVISIONAL_MIC_HARDWARE`.

## Carried W4 baseline

W4 evidence remains accepted:
- implementation HEAD `3e3cd376189e9f183e70ca537ad25f037e25bcd7`;
- W4 `37570612799` SUCCESS;
- W3 `37570612705` SUCCESS;
- W2 `37570612673` SUCCESS;
- W1 `37570612719` SUCCESS;
- W0 `37570612737` SUCCESS;
- S10 `37570612830` SUCCESS;
- S09 `37570612683` SUCCESS;
- S08 `37570612789` SUCCESS.

## Locked non-scope

Do not start:
- Gemini credential/provider work;
- AI Auto Edit;
- ASR/transcription/speech alignment;
- final export matrix/release packaging;
- unsupported subtitle animations;
- Reverse enablement;
- W4 unsupported effects/crossfade.

## Exact next action

On owner **"lanjutkan"**, implement **S11-W5-001 only**.

Do not start W5-002 until W5-001 has its own tests/gate and status report.
