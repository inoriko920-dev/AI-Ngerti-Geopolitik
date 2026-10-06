# AGENTS.md — WAJIB DIBACA SEBELUM BEKERJA

Dokumen ini adalah **entry gate wajib** untuk AI, agent, model, atau sesi baru yang akan melanjutkan proyek **AI Ngerti Geopolitik**.

## 1. Jangan langsung coding

Sebelum membuat, mengubah, memindahkan, atau menghapus source code, AI **WAJIB** membaca dan memahami, berurutan:

1. `AGENTS.md` ini.
2. `docs/software_factory/00_MASTER_SOFTWARE_FACTORY_PROMPT.txt`.
3. `docs/software_factory/PANDUAN_PENGGUNAAN_SOFTWARE_FACTORY_ASTRA_SOL.docx`.
4. Seluruh file di `docs/planning/`.
5. `HANDOFF.md`.
6. `docs/PROJECT_STATUS.md`.
7. `docs/DECISIONS_LOCKED.md`.
8. `docs/REPOSITORY_RULES.md`.
9. Struktur repository dan source/test yang sudah ada pada saat itu.
10. Evidence/gate STEP aktif jika sudah tersedia.

Jika ada dokumen baru yang kemudian ditetapkan sebagai planning/reference/source-of-truth, dokumen itu juga wajib dibaca.

## 2. Source-of-truth precedence

Jika ada konflik, gunakan urutan berikut:

1. Instruksi eksplisit terbaru dari pemilik proyek.
2. Aturan platform/safety yang berlaku.
3. Prompt STEP Software Factory yang sedang aktif.
4. Master Software Factory.
5. Master Blueprint AI Ngerti Geopolitik dan dokumen planning/reference terbaru yang masih berlaku.
6. `DECISIONS_LOCKED.md`.
7. `PROJECT_STATUS.md` dan `HANDOFF.md`.
8. Source code/test/evidence aktual.

Jangan memilih diam-diam jika dua source-of-truth proyek bertentangan. Catat konflik dan hentikan perubahan yang berisiko sampai konflik terselesaikan.

## 3. Aturan STEP

- Kerjakan **satu STEP aktif** pada satu waktu.
- Jangan melompat STEP.
- Jangan mengulang planning final yang sudah disetujui tanpa alasan/evidence baru.
- Jangan menjalankan STEP berikutnya hanya karena pekerjaan terasa mudah.
- Setelah STEP selesai, update status, evidence, gate, handoff, dan next exact action.
- Planning dipimpin ASTRA; implementasi dipimpin SOL sesuai Software Factory.

## 4. Gate sebelum coding

Coding production **DILARANG** sampai:
- seluruh DOCX planning/reference yang diwajibkan pada tahap pra-coding sudah berada di repo;
- UI reference/freeze yang diwajibkan Software Factory sudah lengkap pada STEP-nya;
- keputusan arsitektur dan repository architecture sudah cukup matang;
- status STEP secara eksplisit mengizinkan implementasi.

Adanya repository GitHub **bukan** izin untuk coding.

## 5. Repo lama adalah read-only

Repository:
`inoriko920-dev/AI-Automatic-Video-Composer`

boleh dibaca sebagai referensi fitur/perilaku/evidence, tetapi **DILARANG DIUBAH** oleh pekerjaan proyek ini kecuali pemilik secara eksplisit memerintahkan perubahan pada repo lama dalam tugas terpisah.

Jangan push, commit, edit issue, branch, release, workflow, atau file apa pun ke repo lama.

## 6. Prinsip implementasi

Saat nanti coding sudah diizinkan:
- jangan membangun ulang timeline/playback/render engine dari nol bila fondasi matang yang sudah dipilih dapat digunakan;
- perubahan AI harus melalui command/transaction yang dapat divalidasi dan di-Undo;
- jangan menyimpan secret/API key plaintext;
- jangan hardcode path lokal;
- jangan menaruh business logic besar di UI/MainWindow;
- jangan membuat placeholder/fake feature yang terlihat selesai tetapi tidak bekerja;
- jangan menyebut fitur selesai tanpa test/evidence yang sesuai;
- jangan menghapus test gagal hanya untuk membuat CI hijau.

## 7. Sebelum sesi berakhir

AI wajib memperbarui minimal:
- `docs/PROJECT_STATUS.md`
- `HANDOFF.md`

bila sesi membuat perubahan bermakna pada status, keputusan, code, test, build, atau blocker.

Handoff harus menyatakan:
- STEP aktif;
- baseline/HEAD yang dikerjakan;
- apa yang sudah selesai;
- apa yang belum;
- keputusan baru;
- test/evidence;
- blocker/known issue;
- next exact action.

## 8. Bahasa laporan

Gunakan Bahasa Indonesia sederhana kepada pemilik proyek. Jangan membebani pemilik dengan detail teknis rutin yang dapat dianalisis sendiri oleh AI.

**Jika aturan ini belum dibaca, jangan bekerja.**
