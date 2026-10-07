# W6 UI REFERENCE CORRECTION — PHYSICAL FROZEN RASTER MAPPING

Status: ACTIVE SOURCE-OF-TRUTH CORRECTION
Date: 2026-10-07
Scope: S11-W6-009 only

## Reason

A 42/42 visual contact-sheet audit found that the historical W6 planning labels
`UI-010/011/012/013/014/023` do not match the actual visual content of the frozen
PNG files stored under `docs/ui_reference/raw/`.

The raw frozen files are valid and their SHA-256 identities are unchanged. The
problem is the historical semantic-number association in planning text, not the
binary reference pack.

## Physical frozen raster mapping for W6

| W6 semantic state | Physical frozen raster |
| --- | --- |
| AI Director / AI Otomatis | `UI-020.png` |
| AI Agent — Ready / Chat | `UI-021.png` |
| AI Agent — Rencana Aksi | `UI-022.png` |
| AI Agent — Perubahan Diterapkan | `UI-023.png` |
| AI Agent — Provider Tidak Tersedia | `UI-024.png` |
| Provider & API Key Manager | `UI-033.png` |

## Enforcement

- Do not rename, regenerate, rewrite, or replace the 42 frozen PNGs.
- Do not change their approved SHA-256 values.
- W6-009 actual-vs-reference evidence must compare semantic states against the
  physical raster IDs above.
- Historical planning documents remain historical records. When they mention the
  stale W6 numbers, this correction takes precedence for W6-009 visual evidence.
- Runtime UI remains real PySide6 widgets; frozen screenshots are reference/evidence
  only and are never used as runtime UI.
- Gemini remains the only V1 AI provider in W6.
