# AI Ngerti Geopolitik

> **STATUS: SF-STEP 11 ACTIVE — W0/W1/W2/W3/W4 PASS — W5-001..006 PASS — W5-007 PASS_WITH_PROVISIONAL_MIC_HARDWARE — NEXT W5-008**

Repository resmi aplikasi **AI Ngerti Geopolitik**.

Baca `AGENTS.md` lalu `docs/SOURCE_OF_TRUTH_INDEX.md`.

## Current W5 status

Completed:
- W5-001 canonical subtitle/narration model = PASS
- W5-002 SRT import + validation = PASS
- W5-003 cue editing + safe working-copy = PASS
- W5-004 subtitle style = PASS
- W5-005 render-backed animation + per-word boundary = PASS
- W5-006 narration import + binding = PASS
- W5-007 microphone recording software path = PASS
- W5-007 physical microphone hardware gate =
  **PASS_WITH_PROVISIONAL_MIC_HARDWARE**

W5-007 accepted implementation:
`be4daa667bf5030ba3810460cc6841a2e8be4fee`

Workflow:
`37578572691` — SUCCESS

Microphone flow now has:
- real device enumeration boundary;
- staging WAV;
- cancellation;
- validation before canonical mutation;
- collision-safe finalization;
- canonical narration bind through W5-006;
- failure safety preserving existing narration.

The GitHub Windows runner exposed **0 DirectShow audio input devices**, so no
physical microphone recording is falsely claimed. A real Windows hardware
smoke is still required to remove the provisional qualifier.

Targeted W5-007 tests: **6/6 PASS**.  
Full pytest: **PASS**.

All accepted regressions through S08 remain green.

## Next

**S11-W5-008 — Frozen UI parity only.**
