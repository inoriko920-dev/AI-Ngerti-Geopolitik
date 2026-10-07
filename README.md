# AI Ngerti Geopolitik

> **STATUS: SF-STEP 11 ACTIVE — W0/W1/W2/W3/W4 PASS — W5-001/002/003/004 PASS — NEXT W5-005**

Repository resmi aplikasi **AI Ngerti Geopolitik**.

Baca `AGENTS.md` lalu `docs/SOURCE_OF_TRUTH_INDEX.md`.

## Current W5 status

W5 is **Subtitle + Narration**.

Completed:
- S11-W5-001 — canonical subtitle/narration model = PASS
- S11-W5-002 — SRT import + validation = PASS
- S11-W5-003 — cue editing + safe working-copy = PASS
- S11-W5-004 — subtitle style = PASS

W5-004 accepted implementation:
`687d31585d476541711978d5f69e5e7eafe72245`

Workflow:
`37574406573` — SUCCESS

The app now has canonical subtitle styling with Undo/Redo and persistence plus
real preview/export qualification for font family/size, fill, outline, shadow,
background box/opacity, alignment and vertical margin.

For the current FFmpeg qualification adapter, render-proven fonts are **Arial**
and **Segoe UI** only.

Evidence verifier: **18/18 PASS**.

All W4/W3/W2/W1/W0/S10/S09/S08 regressions are green on the same accepted
implementation HEAD.

## Next

**S11-W5-005 — Render-backed subtitle animation + per-word boundary only.**

Narration and recording remain later tasks.
