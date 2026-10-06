# HANDOFF — AI NGERTI GEOPOLITIK

**Status dokumen:** aktif  
**Fase:** PRE-IMPLEMENTATION / SOURCE-OF-TRUTH BOOTSTRAP  
**Coding:** BELUM DIIZINKAN  
**Repo target:** `inoriko920-dev/AI-Ngerti-Geopolitik`

## Baca sebelum melanjutkan

Mulai dari `AGENTS.md`. Jangan mulai dari source code.

## Posisi proyek saat ini

Proyek baru dibuat untuk menggantikan pendekatan editor custom yang terasa kurang matang pada `AI-Automatic-Video-Composer`. Repo lama hanya menjadi referensi read-only.

Master Blueprint produk sudah selesai dibuat dan menjelaskan:
- masalah produk yang ingin diselesaikan;
- feature parity yang harus dipertahankan;
- arah OpenShot/libopenshot sebagai fondasi matang;
- AI command/transaction model;
- subtitle, narration, animation, Gemini credential pool, render/export;
- testing, packaging, migration, risiko, tahapan implementasi, dan Definition of Done.

Software Factory asli juga disimpan di repo sebagai aturan proses.

## Yang sudah selesai

- Repo `AI-Ngerti-Geopolitik` tersedia.
- Master Blueprint produk selesai.
- Baseline matang yang direkomendasikan telah diidentifikasi: OpenShot/libopenshot.
- Aturan bahwa repo lama tidak boleh diubah telah dikunci.
- Source-of-truth dan handoff foundation sedang/ telah dimasukkan ke repo.
- Belum ada source code aplikasi.

## Yang belum selesai

Formal Software Factory masih harus dijalankan disiplin terhadap evidence yang sudah ada. Dokumen blueprint yang sudah dibuat adalah evidence awal dan tidak otomatis berarti semua STEP formal sudah PASS.

Belum dilakukan/di-freeze secara formal:
- STEP 00 Project Intake gate proyek ini;
- STEP 01 Product Definition mapping/gate;
- STEP 02 Existing Solution/GitHub Discovery validation formal;
- STEP 03 UI/UX inventory;
- STEP 04 prompt + generate seluruh UI yang diwajibkan;
- STEP 05 UI freeze;
- STEP 06 architecture/technology decision final;
- STEP 07 repository architecture/code constitution final;
- STEP 08 foundation implementation/CI;
- STEP 09+ implementation.

## Next exact action

**Kerjakan hanya STEP 00 Software Factory untuk AI Ngerti Geopolitik**, dengan memakai Master Blueprint dan repo ini sebagai input/evidence. Jangan coding.

Jika pemilik berkata “lanjutkan”, AI berikutnya harus:
1. baca seluruh urutan wajib di `AGENTS.md`;
2. verifikasi status aktual repo;
3. jalankan STEP 00 saja;
4. buat output planning/evidence STEP 00;
5. update status + handoff;
6. berhenti sebelum STEP 01 sampai diizinkan.

## Larangan penting

- Jangan mengubah `AI-Automatic-Video-Composer`.
- Jangan mengulang Master Blueprint dari nol.
- Jangan langsung fork/copy OpenShot sebelum license gate dan architecture STEP formal memutuskan cara reuse.
- Jangan coding sebelum gate pra-implementasi mengizinkan.
