# AI Ngerti Geopolitik

> **STATUS: PRE-IMPLEMENTATION / UI HARD STOP — SF-STEP 04 PASS WITH PROVISIONAL — BELUM BOLEH CODING**

Repository resmi untuk aplikasi **AI Ngerti Geopolitik**.

Tujuan repo ini adalah membangun editor video desktop Windows yang stabil untuk workflow video geopolitik/dokumenter, dengan fondasi editor matang dan lapisan otomasi/AI yang terkontrol.

## WAJIB UNTUK AI / SESI BARU

Sebelum mengubah apa pun, baca **AGENTS.md** di root repository dan ikuti urutan baca yang ditetapkan di sana.

AI tidak boleh langsung coding hanya karena repository sudah tersedia.

## Source of Truth

Dokumen perencanaan, Software Factory, status STEP, keputusan terkunci, dan handoff disimpan di repository ini agar proyek dapat dilanjutkan lintas AI/sesi tanpa mengandalkan ingatan chat.

## Repo lama

`inoriko920-dev/AI-Automatic-Video-Composer` adalah **READ-ONLY REFERENCE** untuk proyek ini. Jangan mengubah repository lama sebagai bagian dari pekerjaan AI Ngerti Geopolitik.

## Kondisi saat ini

- Repository baru telah dibuat.
- Master blueprint produk telah dibuat.
- Belum ada source code aplikasi.
- Belum ada implementasi UI.
- Belum ada build/release.
- SF-STEP 00 selesai. SF-STEP 01 Product Definition selesai dengan PASS WITH PROVISIONAL. Exact next action: SF-STEP 02 Existing Solution / GitHub / Upstream Discovery setelah perintah pengguna.

Lihat `HANDOFF.md` dan `docs/PROJECT_STATUS.md` untuk posisi terakhir.


## UI contract

UI target untuk AI Ngerti Geopolitik adalah UI AI-Automatic-Video-Composer sebagai **VISUAL_CONTRACT 1:1**. SF-STEP 03–05 akan memetakan dan membekukannya secara formal; tidak ada redesign kreatif.


## Discovery baseline

SF-STEP 02 selesai dengan `BUILD_FROM_SCRATCH_WITH_COMPONENTS`: libopenshot v1.0.1 menjadi primary engine candidate, MLT v7.42.0 fallback/benchmark, dan full editor upstream hanya reference kecuali keputusan lisensi baru.


## SF-STEP 03 UI inventory

UI/UX inventory selesai. AAVC tetap **VISUAL_CONTRACT 1:1**, dengan coverage `UI-001..UI-042`. Exact legacy mapping UI-038..042 masih provisional/recovery target; missing reference tidak boleh menjadi alasan redesign.


## UI inventory baseline

SF-STEP 03 registers 17 major surfaces, 15 states, 16 core flows, and **42/42 AAVC canonical UI references**. The 42 existing AAVC references are reused 1:1; no new baseline visual design is requested.


## SF-STEP 04 UI reference adoption

UIB-ANG-v1.0 selesai. Semua 42 AAVC frozen references diadopsi 1:1 dan berstatus APPROVED_FOR_FREEZE. Full visual reference DOCX telah lulus render QA 43 halaman. Repo menyimpan connector-safe reference index + SHA manifest. Exact full-resolution visual binary/raw pack tetap merupakan mandatory pre-coding gate.
