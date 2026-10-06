# HANDOFF — AI NGERTI GEOPOLITIK

**Status dokumen:** aktif  
**Fase:** PRE-IMPLEMENTATION  
**SF-STEP terakhir:** 00 — Project Intake & Safety Gate  
**Gate:** PASS WITH RECORDED OPEN ITEMS  
**Coding:** BELUM DIIZINKAN  
**Repo target:** `inoriko920-dev/AI-Ngerti-Geopolitik`  
**STEP 00 output commit:** `bbbb084a73c7cc34e01f1472c95151ac42bae973`

## Baca sebelum melanjutkan

Mulai dari `AGENTS.md` dan ikuti `docs/SOURCE_OF_TRUTH_INDEX.md`. Verifikasi HEAD aktual sebelum bekerja.

## Yang baru selesai

SF-STEP 00 telah diselesaikan dan didokumentasikan di:

- `docs/planning/01_STEP_00_PROJECT_INTAKE_AI_NGERTI_GEOPOLITIK.docx`
- `docs/planning/01_STEP_00_PROJECT_INTAKE_AI_NGERTI_GEOPOLITIK.txt`

Hasil utama:
- project identity, input registry, source-of-truth, working agreement, capability matrix, safety boundary, risk register, acceptance checklist, dan handoff tersedia;
- repo target sudah ada tetapi **docs-only**; ini bukan bukti SF-STEP 08 selesai;
- source code aplikasi = NONE;
- repo `AI-Automatic-Video-Composer` tetap READ-ONLY;
- SF-STEP dan TECH-WAVE telah dipisahkan agar tidak salah fase;
- keputusan teknis OpenShot/libopenshot yang belum melewati discovery/license/architecture formal tetap provisional/open.

## Keputusan baru yang dikunci pada STEP 00

**D-013 — Namespace STEP**  
SF-STEP 00–15 = Software Factory governance. Roadmap Bab 31 Master Blueprint disebut TECH-WAVE 00–16. TECH-WAVE tidak boleh dipakai untuk melompati SF-STEP.

**D-014 — Repo docs-only**  
Repo proyek dibuat lebih awal atas instruksi pemilik hanya sebagai source-of-truth checkpoint. Tidak mengotorisasi coding, upstream fork/copy, CI product, build, atau release.

## Yang belum selesai

- SF-STEP 01 Product Definition;
- SF-STEP 02 formal upstream/GitHub discovery + license assessment;
- SF-STEP 03 UI/UX inventory;
- SF-STEP 04 UI prompts/generation;
- SF-STEP 05 UI freeze/reference pack;
- SF-STEP 06 architecture & technology decision final;
- SF-STEP 07 code constitution/repository architecture;
- SF-STEP 08+ implementation/CI;
- seluruh coding, build, test product, packaging, dan release.

## Exact next action

Setelah pemilik mengatakan **"lanjutkan"**, kerjakan **SF-STEP 01 — Product Definition** saja.

Gunakan:
1. Master Software Factory;
2. Master Blueprint AI Ngerti Geopolitik;
3. STEP 00 Project Intake;
4. DECISIONS_LOCKED;
5. PROJECT_STATUS.

Pada STEP 01:
- **jangan menulis ulang visi dari nol**;
- petakan/validasi blueprint yang sudah matang;
- pastikan problem statement, target user, primary workflow, input/output, mandatory vs optional features, non-goals, success criteria, dan Product Done konsisten dan dapat diuji;
- buat satu DOCX planning detail + mirror TXT;
- commit ke repo;
- update PROJECT_STATUS + HANDOFF;
- **berhenti sebelum SF-STEP 02** sampai pengguna berkata “lanjutkan”.

## Larangan penting

- Jangan mengubah `AI-Automatic-Video-Composer`.
- Jangan coding.
- Jangan generate/finalize UI pada STEP 01.
- Jangan fork/copy upstream OpenShot.
- Jangan meminta Gemini API key.
- Jangan menganggap keputusan arsitektur blueprint otomatis final sebelum STEP formal.
