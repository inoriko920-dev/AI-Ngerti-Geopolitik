# AI Ngerti Geopolitik

> **STATUS: SF-STEP 11 ACTIVE — W0/W1/W2/W3/W4 PASS — W5-001/002/003/004/005 PASS — NEXT W5-006**

Repository resmi aplikasi **AI Ngerti Geopolitik**.

Baca `AGENTS.md` lalu `docs/SOURCE_OF_TRUTH_INDEX.md`.

## Current W5 status

W5 is **Subtitle + Narration**.

Completed:
- S11-W5-001 — canonical subtitle/narration model = PASS
- S11-W5-002 — SRT import + validation = PASS
- S11-W5-003 — cue editing + safe working-copy = PASS
- S11-W5-004 — subtitle style = PASS
- S11-W5-005 — render-backed animation + per-word boundary = PASS

W5-005 accepted implementation:
`293b369e74771d16dc90956bc6a7be4c71e01d1c`

Workflow:
`37575611940` — SUCCESS

Render-qualified subtitle animations:
**Fade, Pop, Slide Up, Clean Documentary**.

Unqualified legacy names remain unavailable.

Per-word timing is canonical and editable, but deterministic word distribution
is explicitly labeled **NOT speech alignment**. No ASR or transcription is
claimed or used.

Evidence verifier: **21/21 PASS**.

All W5-004/W4/W3/W2/W1/W0/S10/S09/S08 regressions are green on the same
accepted implementation HEAD.

## Next

**S11-W5-006 — Narration import + binding only.**

Microphone recording remains W5-007.
