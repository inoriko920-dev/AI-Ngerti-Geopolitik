# AI Ngerti Geopolitik

> **STATUS: SF-STEP 11 ACTIVE — W0/W1/W2/W3/W4 PASS — W5-001 PASS — NEXT W5-002**

Repository resmi aplikasi **AI Ngerti Geopolitik**.

Baca `AGENTS.md` lalu `docs/SOURCE_OF_TRUTH_INDEX.md`.

## Current W5 status

W5 is **Subtitle + Narration**.

**S11-W5-001 — Canonical subtitle/narration model = PASS.**

Accepted implementation:
`b5bf8543554bcf38d22a65510fe0376195676d46`

Accepted workflow:
`37571740654` — SUCCESS

W5-001 adds canonical subtitle/narration entities, frame-aware validation,
CommandBus mutation, .angproj persistence and backward-compatible defaults.
No parser/UI/recorder/AI work was started.

All W4/W3/W2/W1/W0/S10/S09/S08 regressions are green on the same accepted
implementation HEAD.

## Next

**S11-W5-002 — SRT import + validation only.**

It must parse/validate SRT into the W5-001 canonical model without rewriting
the source file. Cue editing UI belongs to W5-003, not W5-002.
