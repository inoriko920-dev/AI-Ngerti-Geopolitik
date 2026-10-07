# AI Ngerti Geopolitik

> **STATUS: SF-STEP 11 ACTIVE — W0/W1/W2/W3/W4 PASS — W5-001/W5-002/W5-003 PASS — NEXT W5-004**

Repository resmi aplikasi **AI Ngerti Geopolitik**.

Baca `AGENTS.md` lalu `docs/SOURCE_OF_TRUTH_INDEX.md`.

## Current W5 status

W5 is **Subtitle + Narration**.

Completed:
- **S11-W5-001 — Canonical subtitle/narration model = PASS**
- **S11-W5-002 — SRT import + validation = PASS**
- **S11-W5-003 — Cue editing + safe working-copy flow = PASS**

W5-003 accepted implementation:
`d8db4d18cb42b71d91a9b727868b25340961702f`

Accepted workflow:
`37573388357` — SUCCESS

The subtitle workflow now supports local cue editing, insert/delete,
split/merge, explicit sort/index normalization, dirty reload protection and
safe no-clobber SRT save-copy with an undoable canonical commit.

The original SRT is not overwritten by W5-003.

All W4/W3/W2/W1/W0/S10/S09/S08 regressions are green on the same accepted
implementation HEAD.

## Next

**S11-W5-004 — Subtitle style only.**

Subtitle animation, narration and recording remain later tasks.
