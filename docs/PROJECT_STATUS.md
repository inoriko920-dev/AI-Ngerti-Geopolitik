# PROJECT STATUS — AI NGERTI GEOPOLITIK

**Last known phase:** PRE-IMPLEMENTATION  
**Formal Software Factory completed:** SF-STEP 03 — UI/UX Inventory & User Flow  
**Gate:** PASS_WITH_PROVISIONAL  
**UI contract:** AAVC UI = VISUAL_CONTRACT 1:1  
**Formal Software Factory next:** SF-STEP 04 — UI Design System & All UI Prompts  
**Code status:** NONE  
**UI implementation:** NONE  
**UI image generation for ANG:** NOT STARTED  
**Build:** NONE  
**Release:** NONE

## STEP 03 evidence

Canonical planning:
- `docs/planning/04_STEP_03_UI_UX_INVENTORY_AI_NGERTI_GEOPOLITIK.docx`
- machine-readable mirror: `docs/planning/04_STEP_03_UI_UX_INVENTORY_AI_NGERTI_GEOPOLITIK.txt`

STEP 03 inventory hasil:
- 8 screen/view entries;
- 14 panel/inspector entries;
- dialog/overlay/message/permission registry;
- 11 navigation edges;
- 10 critical P0 user flows;
- 28 critical actions;
- state matrix untuk ready/dirty/working/error/stale/permission/recovery;
- Product MUST → UI traceability;
- frozen coverage contract UI-001..UI-042;
- STEP 04 batch recommendation A–E.

## Reference status

AAVC `UI_FREEZE.md` mengunci 42 reference ID: UI-001..UI-042.

Recovered/reconciled evidence:
- UI-001..UI-037: dapat dipetakan dari frozen-generation batches/source evidence yang tersedia;
- UI-038..UI-042: exact old source-image/title mapping belum direkonsiliasi sepenuhnya;
- current AAVC PySide6 source + UI Freeze + User Guide tetap memberi structural contract;
- STEP 04 wajib mencoba recovery exact reference/prompt lebih dulu dan **dilarang mengarang desain baru** bila reference lama hilang.

## Locked interpretation

- Owner decision D-015 tetap berlaku: UI ANG harus sama dengan AAVC sedekat mungkin.
- Nama produk boleh berubah menjadi AI Ngerti Geopolitik.
- Inconsistent old generated collage bukan authority bila konflik dengan frozen UI/source.
- Unsupported/fake control tidak boleh dibuat aktif hanya demi screenshot parity; setiap visible deviation harus `DELTA_FROM_AAVC`.
- Tidak ada OpenShot/Shotcut/Kdenlive UI yang boleh menggantikan AAVC visual contract.

## Progress

| Area | Status | Keterangan |
|---|---|---|
| SF-STEP 00 | PASS | selesai |
| SF-STEP 01 | PASS WITH PROVISIONAL | Product Definition |
| SF-STEP 02 | PASS WITH PROVISIONAL | Discovery |
| SF-STEP 03 | PASS WITH PROVISIONAL | UI/UX inventory complete |
| AAVC UI visual contract | LOCKED | 1:1 |
| UI-001..037 mapping | RECONCILED | reference/source evidence available |
| UI-038..042 exact old mapping | OPEN_NON_BLOCKING | recover in STEP 04 before generating substitutes |
| UI prompts | NEXT | SF-STEP 04 |
| UI images ANG | BELUM | SF-STEP 04 |
| UI freeze ANG | BELUM | SF-STEP 05 |
| Architecture final | BELUM | SF-STEP 06 |
| Coding | DILARANG | no implementation yet |

## Exact next action

Setelah pengguna mengatakan **"lanjutkan"**, jalankan **SF-STEP 04 — UI Design System & All UI Prompts** saja.

STEP 04 wajib:
1. membaca STEP 03 coverage matrix;
2. recover/reuse AAVC frozen references dan prompt package sebanyak mungkin;
3. mempertahankan design tokens/layout/hierarchy AAVC 1:1;
4. membuat prompt hanya untuk state/reference yang memang perlu dibuat atau direkonstruksi;
5. menjaga stable IDs UI-001..UI-042;
6. tidak coding.

### HARD STOP OWNER RULE
Setelah seluruh prompt gambar UI STEP 04 selesai disusun, **WAJIB BERHENTI**. Bahkan bila pengguna langsung berkata “lanjutkan”, jangan masuk SF-STEP 05 sampai:
- seluruh gambar UI yang diperlukan benar-benar tersedia;
- seluruh gambar diperiksa;
- gambar salah direvisi/regenerate sampai sesuai;
- seluruh gambar final dikumpulkan ke **1 DOCX UI Reference final**.

Baru setelah kondisi tersebut terpenuhi SF-STEP 05 boleh dimulai.
