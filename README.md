# AI Ngerti Geopolitik

> **STATUS: SF-STEP 08 — S08-T01 PASS — NEXT S08-T02 — PRODUCT FEATURES BELUM DIMULAI**

Repository resmi untuk aplikasi **AI Ngerti Geopolitik**.

## WAJIB UNTUK AI / SESI BARU

Baca `AGENTS.md`, lalu ikuti `docs/SOURCE_OF_TRUTH_INDEX.md`.

## Current gate

Planning STEP 00–07 sudah ada di repo dan exact AAVC `UI-001..UI-042` sekarang sudah committed di:
`docs/ui_reference/raw/`.

S08-T01 verification:
- raw files present: **42/42**;
- canonical local SHA-256 vs manifest: **42/42 PASS**;
- remote byte-size parity: **42/42 PASS**;
- remote Git-object identity parity: **42/42 PASS**.

Evidence:
- `docs/evidence/ui/S08_T01_UI_REFERENCE_GATE.md`
- `docs/ui_reference/UI_REFERENCE_MANIFEST.md`

**Next exact task: S08-T02 — Repository Skeleton, Toolchain & Architecture Fitness.**

## Core frozen decisions

- UI = AAVC visual/workflow contract 1:1.
- VOID ANG 42-prompt regeneration must not be used.
- UI framework family = PySide6 / Qt Widgets.
- ProjectState + semantic CommandBus/Undo are ANG-owned.
- Media behind MediaEnginePort; libopenshot primary qualification candidate, MLT fallback.
- Gemini only through validated EditPlan/commands.
- Target release = Windows portable multi-file ZIP.
