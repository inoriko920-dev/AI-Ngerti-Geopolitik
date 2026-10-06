# HANDOFF — AI NGERTI GEOPOLITIK

**Fase:** PRE-IMPLEMENTATION  
**SF-STEP terakhir:** 02 — Existing Solution / GitHub / Upstream Discovery  
**Gate:** PASS_WITH_PROVISIONAL  
**Adoption:** BUILD_FROM_SCRATCH_WITH_COMPONENTS  
**Coding:** BELUM DIIZINKAN

## Discovery decision

Tidak ada EXACT_BASE yang layak dijadikan aplikasi utama tanpa membawa UI/scope/license debt.

**Primary engine candidate**
- OpenShot/libopenshot v1.0.1
- tag SHA: `1c46200eaedeebce3fbce74b5584dc0c04d70903`
- role: COMPONENT_SOURCE
- license screening: LGPL-3.0-or-later
- alasan: Timeline/Clip/KeyFrame/QtPlayer/FFmpeg/audio + Python binding + UI freedom

**Fallback / benchmark**
- MLT v7.42.0
- tag SHA: `11e84ecf42e1a7bc885953afa58ba35d228a76ad`
- role: COMPONENT_SOURCE fallback
- license screening: LGPL-2.1 framework; modules must be inventoried

**Reference client**
- openshot-qt v4.0.1
- tag SHA: `5b0588ca36beedebe790e9ed4f48d105a1752f18`
- GPL-3.0-or-later
- role: REFERENCE_ONLY
- selective source reuse: HOLD sampai license decision explicit

**Other references**
- Shotcut v26.9.27 — GPLv3 / MLT production + Windows ZIP evidence
- Kdenlive 26.08.1 — GPLv3 / MLT large-editor evidence
- OpenCut current rewrite — MIT but architecture still being redesigned

## Critical interpretation

BUILD_FROM_SCRATCH_WITH_COMPONENTS **bukan** berarti membuat media engine sendiri.

ANG-owned:
- AAVC 1:1 UI shell
- Scene DOCX / Axxx / SINGLE-DOUBLE
- semantic project model
- command/history/Undo-Redo
- AI Edit Plan + validation
- validation/relink/recovery workflow
- product-specific subtitle/narration/animation workflow

Engine-owned candidate:
- timeline/clip/layers
- keyframes/compositing
- playback/frame generation
- audio mixing
- codec/read/write/render primitives

## What is NOT proven

Belum ada:
- ANG + libopenshot Windows build;
- portable clean-machine run;
- Python binding load in ANG package;
- 100–300 scene stress;
- preview/export golden parity;
- final 21-effect compatibility mapping.

Jangan menyebut engine stabil untuk ANG sampai evidence implementasi nanti lulus.

## UI constraint for next STEP

**AAVC UI = VISUAL_CONTRACT 1:1.**

SF-STEP 03 bukan tempat desain baru. Gunakan:
- AAVC `docs/UI_FREEZE.md`;
- UI-001..UI-042;
- AAVC current PySide6 screens/widgets/design tokens;
- existing workflow behavior.

Setiap perbedaan harus diberi label `DELTA_FROM_AAVC`.

## Exact next action

Jika owner berkata **"lanjutkan"**, jalankan **SF-STEP 03 — UI/UX Inventory & User Flow** saja.

Output STEP 03:
- detailed planning DOCX + TXT mirror;
- screen IDs;
- state IDs;
- flow map;
- interaction inventory;
- UI reference/image coverage matrix;
- Product MUST → UI surface mapping;
- status/handoff update.

Setelah STEP 03 selesai, **STOP sebelum STEP 04** sampai owner berkata lanjutkan.

Larangan:
- no coding;
- no fork/copy upstream;
- no UI implementation;
- no redesign AAVC;
- no SF-STEP 04 dalam sesi yang sama.
