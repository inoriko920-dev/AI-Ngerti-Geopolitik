# HANDOFF — AI NGERTI GEOPOLITIK

**Fase:** PRE-IMPLEMENTATION  
**SF-STEP terakhir:** 03 — UI/UX Inventory & User Flow  
**Gate:** PASS_WITH_PROVISIONAL  
**Coding:** BELUM DIIZINKAN  
**Next exact action:** SF-STEP 04 — UI Design System & All UI Prompts

## STEP 03 selesai

Canonical outputs:
- `docs/planning/04_STEP_03_UI_UX_INVENTORY_AI_NGERTI_GEOPOLITIK.docx`
- `docs/planning/04_STEP_03_UI_UX_INVENTORY_AI_NGERTI_GEOPOLITIK.txt`

Inventory mencakup:
- SCR-001 Home
- SCR-002 New Project Wizard
- SCR-003 Main Editor / Overview
- SCR-004 Subtitle Workspace
- SCR-005 Animation Workspace / Inspector
- SCR-006 Narration / Audio Workspace
- SCR-007 Preview Focus / Playback
- SCR-008 Legacy Compatibility Report (SHOULD / provisional)

Global surfaces mencakup Scene/Aset/Inspector/Preview/Timeline/Layout/Animation/AI Agent/Subtitle/History/Audio/Background, Validation Center, Export, render jobs, recovery, relink, credential manager, narration recording, unsaved guard, and help.

## UI authority

**AAVC UI = VISUAL_CONTRACT 1:1. No redesign.**

Authority order untuk STEP 04:
1. owner decision terbaru / D-015;
2. AAVC `docs/UI_FREEZE.md`;
3. exact frozen image/prompt asset jika berhasil direcover;
4. current AAVC PySide6 presentation source + USER_GUIDE;
5. STEP 03 registry/coverage;
6. generated collage lama hanya secondary evidence dan tidak boleh mengalahkan frozen/source contract.

Known frozen contract:
- 42 IDs UI-001..UI-042;
- reference viewport 1920x1080;
- Indonesian;
- light professional editor;
- white surfaces + restrained blue;
- existing AAVC design tokens preserved.

## Reference gap

Exact old frozen mapping/assets UI-038..UI-042 belum sepenuhnya berhasil direcover.

Ini **tidak memberi izin untuk berkreasi**.
STEP 04 harus:
- search/recover exact prompt/reference first;
- bila masih unavailable, derive only from current AAVC source/product flow;
- label substitute `PROVISIONAL_REFERENCE`;
- owner review required before it can be final UI reference.

## Flows yang wajib tercakup

- FLOW-001 create project
- FLOW-002 open existing project
- FLOW-003 manual edit/timeline
- FLOW-004 random animation
- FLOW-005 AI edit/plan/apply/undo
- FLOW-006 subtitle edit
- FLOW-007 narration
- FLOW-008 validation/relink
- FLOW-009 export
- FLOW-010 recovery

## Do not invent

- No new visual style.
- No OpenShot/Shotcut/Kdenlive UI.
- No new product scope.
- No fake/unsupported controls.
- No coding.
- No source copy/fork.

## Exact next action

Jika owner berkata **"lanjutkan"**, jalankan **SF-STEP 04 — UI Design System & All UI Prompts**.

STEP 04 output must include:
- AAVC-preserved design system;
- exact per-ID reference recovery register;
- stable image/prompt list;
- prompt batches;
- prompt text for every image that actually requires generation/reconstruction;
- review criteria.

## NON-NEGOTIABLE HARD STOP

Setelah **semua prompt gambar UI selesai dibuat**, STOP.

Jangan menjalankan SF-STEP 05 hanya karena owner berkata “lanjutkan”.

Proses baru boleh diteruskan setelah:
1. semua gambar yang dibutuhkan sudah dibuat/recovered;
2. semuanya diperiksa;
3. yang salah direvisi/regenerate;
4. seluruh gambar final dimasukkan ke satu **DOCX UI Reference final**.

Sampai empat kondisi itu selesai, state proyek tetap berada pada SF-STEP 04 / UI IMAGE REVIEW.
