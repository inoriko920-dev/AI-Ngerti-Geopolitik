# REPOSITORY RULES & STRUCTURE

## Tujuan struktur

Repository harus mudah dilanjutkan AI lain tanpa membaca histori chat lengkap.

## Struktur pra-coding

```text
/
├─ AGENTS.md                         # pintu masuk wajib AI
├─ HANDOFF.md                        # posisi terakhir + next exact action
├─ README.md
└─ docs/
   ├─ PROJECT_STATUS.md
   ├─ DECISIONS_LOCKED.md
   ├─ REPOSITORY_RULES.md
   ├─ software_factory/
   │  ├─ 00_MASTER_SOFTWARE_FACTORY_PROMPT.txt
   │  └─ PANDUAN_PENGGUNAAN_SOFTWARE_FACTORY_ASTRA_SOL.docx
   └─ planning/
      └─ 00_MASTER_BLUEPRINT_AI_NGERTI_GEOPOLITIK.docx
```

Planning/reference berikutnya harus ditempatkan secara konsisten, bukan tersebar acak di root.

## Aturan nama

- Planning STEP: prefix numerik/STEP yang jelas.
- Status/handoff: satu file canonical, diperbarui; jangan membuat puluhan salinan “final_final”.
- Evidence besar: tempatkan dalam folder evidence per STEP ketika mulai diperlukan.
- UI reference: gunakan ID stabil UI-xxx sesuai Software Factory.
- Jangan rename file source-of-truth tanpa memperbarui seluruh referensi.

## Aturan perubahan

- Satu perubahan harus memiliki tujuan jelas.
- Jangan mencampur redesign, refactor besar, dan fitur baru dalam perubahan yang sama tanpa alasan.
- Cari modul/helper yang sudah ada sebelum membuat duplikat.
- Jaga module ownership dan dependency direction setelah STEP 07 menetapkannya.
- Jangan commit secret, token, API key, credential, file user private, atau output media besar yang tidak perlu.
- Jangan hardcode path Windows milik satu komputer.

## State proyek

Setelah pekerjaan bermakna, update:
- PROJECT_STATUS;
- HANDOFF;
- DECISIONS_LOCKED bila keputusan berubah;
- evidence/gate STEP yang sesuai.

## Definition of “lanjutkan”

Perintah “lanjutkan” berarti lanjut dari **next exact action** yang tercatat dan hanya STEP yang diizinkan. Itu bukan izin untuk melewati seluruh roadmap.
