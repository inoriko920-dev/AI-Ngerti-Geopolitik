# AI Ngerti Geopolitik

> **STATUS: SF-STEP 11 ACTIVE — W0/W1/W2/W3/W4 PASS — W5-001/002/003/004/005/006 PASS — NEXT W5-007**

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
- S11-W5-006 — narration import + binding = PASS

W5-006 accepted implementation:
`77770cd98210dbed18cbe1715111a935f2135b77`

Workflow:
`37577639655` — SUCCESS

Narration now supports canonical:
- audio import/binding;
- frame-aware timeline offset;
- gain;
- mute;
- fade in/out;
- Undo/Redo;
- save/reopen;
- real narration-preview WAV;
- real narration mix in MP4 export.

Real evidence uses separate 880 Hz base audio and 440 Hz narration so
offset/gain/mute/fade behavior is measured rather than assumed.

Evidence verifier: **11/11 PASS**.

All W5-005/W5-004/W4/W3/W2/W1/W0/S10/S09/S08 regressions are green on the
same accepted implementation HEAD.

## Next

**S11-W5-007 — Microphone recording only.**

Frozen UI parity remains W5-008.
