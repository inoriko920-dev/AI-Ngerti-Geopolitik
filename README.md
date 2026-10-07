# AI Ngerti Geopolitik

> **STATUS: SF-STEP 11 ACTIVE — W0/W1/W2/W3/W4 PASS — W5-001/W5-002 PASS — NEXT W5-003**

Repository resmi aplikasi **AI Ngerti Geopolitik**.

Baca `AGENTS.md` lalu `docs/SOURCE_OF_TRUTH_INDEX.md`.

## Current W5 status

W5 is **Subtitle + Narration**.

Completed:
- **S11-W5-001 — Canonical subtitle/narration model = PASS**
- **S11-W5-002 — SRT import + validation = PASS**

W5-002 accepted implementation:
`d4349c925cc0f475cfa94b0db55347320954e1cf`

Accepted workflow:
`37572463564` — SUCCESS

The app now has a strict read-only UTF-8/BOM SRT parser, typed validation,
canonical frame mapping, CommandBus subtitle import and source-file preservation.

All W4/W3/W2/W1/W0/S10/S09/S08 regressions are green on the same accepted
implementation HEAD.

## Next

**S11-W5-003 — Cue editing + safe working-copy flow only.**

Style, subtitle animation, narration and recording remain later tasks.
