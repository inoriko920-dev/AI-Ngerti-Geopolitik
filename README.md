# AI Ngerti Geopolitik

> **STATUS: SF-STEP 08 / S08-T01 BLOCKED — EXACT UI BINARY BELUM MASUK GITHUB — PRODUCT CODING DILARANG**

Repository resmi untuk aplikasi **AI Ngerti Geopolitik**.

## WAJIB UNTUK AI / SESI BARU

Baca `AGENTS.md`, lalu ikuti `docs/SOURCE_OF_TRUTH_INDEX.md`.

## Current gate

Planning STEP 00–07 sudah ada di repo. Exact AAVC UI-001..UI-042 sudah direcover dan diverifikasi lokal **42/42 SHA PASS**, tetapi binary raw pack belum berhasil ditulis ke GitHub melalui connector yang tersedia.

Evidence:
- `docs/evidence/ui/S08_T01_UI_REFERENCE_GATE.md`
- `docs/ui_reference/UI_REFERENCE_MANIFEST.md`

S08-T01 tetap **BLOCKED**. Jangan mulai S08-T02 atau coding product sampai exact raw UI pack benar-benar committed dan remote hash verification PASS.

## Core frozen decisions

- UI = AAVC visual/workflow contract 1:1.
- VOID ANG 42-prompt regeneration must not be used.
- UI framework family = PySide6 / Qt Widgets.
- ProjectState + semantic CommandBus/Undo are ANG-owned.
- Media behind MediaEnginePort; libopenshot primary qualification candidate, MLT fallback.
- Gemini only through validated EditPlan/commands.
- Target release = Windows portable multi-file ZIP.
