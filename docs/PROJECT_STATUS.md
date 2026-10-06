# PROJECT STATUS — AI NGERTI GEOPOLITIK

**Last known phase:** PRE-IMPLEMENTATION  
**Formal Software Factory completed:** SF-STEP 02 — Existing Solution / GitHub / Upstream Discovery  
**Gate:** PASS_WITH_PROVISIONAL  
**Adoption decision:** BUILD_FROM_SCRATCH_WITH_COMPONENTS  
**Preferred engine candidate:** libopenshot v1.0.1 @ `1c46200eaedeebce3fbce74b5584dc0c04d70903`  
**Fallback/benchmark:** MLT v7.42.0 @ `11e84ecf42e1a7bc885953afa58ba35d228a76ad`  
**Formal Software Factory next:** SF-STEP 03 — UI/UX Inventory & User Flow  
**Code status:** NONE  
**UI implementation:** NONE  
**Build:** NONE  
**Release:** NONE

## STEP 02 evidence

Canonical discovery report:
- `docs/planning/03_STEP_02_EXISTING_SOLUTION_GITHUB_DISCOVERY_AI_NGERTI_GEOPOLITIK.docx`
- machine-readable mirror: `docs/planning/03_STEP_02_EXISTING_SOLUTION_GITHUB_DISCOVERY_AI_NGERTI_GEOPOLITIK.txt`

Key result:
- tidak ditemukan EXACT_BASE yang memenuhi product + UI AAVC 1:1;
- product shell/domain/UI/AI tetap ANG-owned;
- media engine tidak dibangun dari nol;
- libopenshot menjadi primary COMPONENT_SOURCE candidate;
- MLT menjadi fallback/benchmark;
- openshot-qt/Shotcut/Kdenlive adalah reference-only untuk scope STEP 02;
- OpenCut ditahan sebagai future reference karena rewrite;
- ANG engine integration/runtime/portable build **BELUM DIUJI**.

## Progress

| Area | Status | Keterangan |
|---|---|---|
| SF-STEP 00 | PASS | selesai |
| SF-STEP 01 | PASS WITH PROVISIONAL | Product Definition baseline |
| SF-STEP 02 | PASS WITH PROVISIONAL | Discovery/adoption baseline selesai |
| AAVC UI contract | LOCKED | VISUAL_CONTRACT 1:1 |
| Primary engine candidate | PROVISIONAL SELECTED | libopenshot v1.0.1 |
| Engine fallback | HOLD | MLT v7.42.0 |
| openshot-qt client source reuse | HOLD | GPL gate / SF-STEP 06 |
| UI inventory | NEXT | SF-STEP 03 |
| UI prompt/reference formal | BELUM | SF-STEP 04 |
| UI freeze | BELUM | SF-STEP 05 |
| Architecture final | BELUM | SF-STEP 06 |
| Coding | DILARANG | no source implementation yet |

## Exact next action

Setelah pengguna berkata **"lanjutkan"**, jalankan **SF-STEP 03 — UI/UX Inventory & User Flow** saja.

STEP 03 wajib memakai AAVC UI sebagai VISUAL_CONTRACT 1:1:
- inventaris UI-001..UI-042 dan implementation screens/states AAVC;
- map Product MUST ke screen/panel/dialog/state;
- buat Screen IDs, state IDs, flow map, interaction inventory, dan UI image/reference coverage matrix;
- jangan redesign;
- perbedaan wajib diberi label `DELTA_FROM_AAVC`;
- belum coding;
- berhenti sebelum SF-STEP 04 setelah DOCX + TXT + status/handoff selesai.
