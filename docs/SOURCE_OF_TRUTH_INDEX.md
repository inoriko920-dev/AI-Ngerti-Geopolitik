# SOURCE OF TRUTH INDEX

Dokumen ini membantu AI/sesi baru menemukan sumber kebenaran proyek tanpa mengandalkan histori chat.

## Urutan baca wajib

1. `/AGENTS.md`
2. `/docs/software_factory/00_MASTER_SOFTWARE_FACTORY_PROMPT.txt`
3. `/docs/software_factory/PANDUAN_PENGGUNAAN_SOFTWARE_FACTORY_ASTRA_SOL.docx`
   - mirror machine-readable: `PANDUAN_PENGGUNAAN_SOFTWARE_FACTORY_ASTRA_SOL.txt`
4. Seluruh `/docs/planning/`
   - saat ini: `00_MASTER_BLUEPRINT_AI_NGERTI_GEOPOLITIK.docx`
   - mirror machine-readable: `00_MASTER_BLUEPRINT_AI_NGERTI_GEOPOLITIK.txt`
5. `/HANDOFF.md`
6. `/docs/PROJECT_STATUS.md`
7. `/docs/DECISIONS_LOCKED.md`
8. `/docs/REPOSITORY_RULES.md`
9. Source/test/evidence aktual jika implementasi sudah ada.

## Aturan mirror TXT

DOCX tetap disimpan sebagai artefak planning/reference. TXT adalah salinan isi terurai untuk lingkungan AI/GitHub yang tidak dapat membaca binary DOCX secara langsung.

Jika runtime dapat membaca DOCX, baca DOCX. Jika runtime tidak dapat membaca DOCX binary, gunakan mirror TXT dan **jangan menganggap dokumen tidak tersedia**.

## Status saat index dibuat

- fase: pre-implementation;
- code aplikasi: belum ada;
- next exact action: Software Factory STEP 00;
- repo lama AI-Automatic-Video-Composer: read-only reference.
