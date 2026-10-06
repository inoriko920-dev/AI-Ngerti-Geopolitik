# DECISIONS LOCKED — AI NGERTI GEOPOLITIK

Dokumen ini mencatat keputusan yang **tidak boleh diubah diam-diam** oleh AI lain.

## D-001 — Nama proyek
Nama aplikasi/repository: **AI Ngerti Geopolitik**.

## D-002 — Repo target
Semua pekerjaan proyek baru diarahkan ke:
`inoriko920-dev/AI-Ngerti-Geopolitik`.

## D-003 — Repo lama read-only
`inoriko920-dev/AI-Automatic-Video-Composer` adalah referensi. Jangan mengubahnya sebagai bagian proyek baru.

## D-004 — Masalah utama
Repo baru dibuat karena produk lama memiliki banyak fitur tetapi fondasi editor custom belum sematang editor video yang telah lama dipakai. Target baru adalah mempertahankan workflow/fitur penting sambil memakai fondasi editor yang lebih matang.

## D-005 — Arah fondasi teknis
Arah utama yang direkomendasikan adalah **OpenShot + libopenshot**, bukan membangun ulang timeline/playback/render engine custom dari nol.

Baseline research yang telah dicatat:
- OpenShot openshot-qt v4.0.1
- libopenshot v1.0.1

Keputusan cara integrasi/fork/linking/copy tetap harus melewati **license gate dan STEP 06** sebelum coding besar.

## D-006 — V1 feature parity
V1 harus mempertahankan kemampuan inti repo lama yang relevan, termasuk:
- Scene DOCX + canonical Axxx;
- SINGLE/DOUBLE;
- timeline editing yang diperlukan workflow;
- manual/random/AI animation + lock;
- undo/redo/recovery;
- validation/relink;
- subtitle editor/style/animation;
- narration;
- Gemini provider + sampai 100 credential slots;
- render/export H.264/H.265 dan selection render;
- workflow otomatis yang deterministik dan dapat diuji.

Rincian authoritative ada di Master Blueprint.

## D-007 — AI tidak boleh mengedit state sembarangan
AI natural-language harus menghasilkan **Edit Plan/Command** yang:
- tervalidasi;
- deterministic pada eksekusi;
- memakai command engine yang sama dengan edit manual;
- dapat masuk undo/redo transaction;
- dapat ditolak bila invalid/stale.

AI tidak boleh menulis project JSON/state arbitrarily sebagai shortcut.

## D-008 — Fokus produk
Aplikasi adalah editor/otomasi khusus workflow geopolitik/dokumenter, bukan target menjadi clone penuh Filmora/Premiere.

## D-009 — Windows
Target utama V1 adalah desktop Windows dengan distribusi portable multi-file ZIP sesuai Software Factory, kecuali pemilik memutuskan lain.

## D-010 — Gemini
Gemini adalah provider AI V1 yang direncanakan. Credential tidak boleh disimpan plaintext setelah import.

## D-011 — No fake capability
UI/README tidak boleh mengklaim fitur yang belum benar-benar bekerja dan belum memiliki evidence/test sesuai risikonya.

## D-012 — Planning before code
Seluruh planning/reference DOCX wajib berada di repo sebelum coding. AI lain wajib membaca source-of-truth, status STEP, keputusan, struktur repo, pekerjaan selesai/belum, dan next action sebelum bekerja.

## Cara mengubah keputusan locked
Perubahan hanya boleh dilakukan jika:
1. pemilik proyek meminta/menyetujui perubahan secara eksplisit; atau
2. evidence teknis/legal menunjukkan keputusan tidak dapat dipertahankan, lalu AI menjelaskan dampaknya dan mencatat keputusan pengganti.

Setiap perubahan harus memperbarui Master/decision log/status/handoff yang relevan.
