# AI Ngerti Geopolitik

> **STATUS: SF-STEP 11 ACTIVE — W0/W1/W2/W3/W4 PASS — W5-001..006 PASS — W5-007 PASS_WITH_PROVISIONAL_MIC_HARDWARE — W5-008 PASS — NEXT W5-009**

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
- W5-007 microphone software path = PASS
- W5-007 physical microphone = PASS_WITH_PROVISIONAL_MIC_HARDWARE
- W5-008 frozen subtitle/narration UI parity = PASS

W5-008 accepted implementation:
`b65bf585510ee442584a7ebbe8db8c3d40ac1533`

Workflow:
`37579815809` — SUCCESS

W5-008 now provides real PySide6 controls for subtitle cue editing, style,
animation, manual/per-word timing boundary, narration controls and device-gated
recording.

Only qualified features are enabled.

Frozen UI reference integrity:
**42/42 PASS**.

W5-008 Qt tests:
**6/6 PASS**.

Evidence:
**14/14 PASS**.

All accepted regressions through S08 are green on the same implementation HEAD.

## Next

**S11-W5-009 — Real subtitle/narration preview/export qualification only.**
