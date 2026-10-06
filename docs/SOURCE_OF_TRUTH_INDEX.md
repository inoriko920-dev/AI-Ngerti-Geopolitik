# SOURCE OF TRUTH INDEX

Dokumen ini membantu AI/sesi baru menemukan sumber kebenaran proyek tanpa mengandalkan histori chat.

## Urutan baca wajib

1. `/AGENTS.md`
2. `/docs/software_factory/00_MASTER_SOFTWARE_FACTORY_PROMPT.txt`
3. `/docs/software_factory/PANDUAN_PENGGUNAAN_SOFTWARE_FACTORY_ASTRA_SOL.docx`
   - mirror machine-readable: `PANDUAN_PENGGUNAAN_SOFTWARE_FACTORY_ASTRA_SOL.txt`
4. Seluruh `/docs/planning/`, urut:
   - `00_MASTER_BLUEPRINT_AI_NGERTI_GEOPOLITIK.docx/.txt`
   - `01_STEP_00_PROJECT_INTAKE_AI_NGERTI_GEOPOLITIK.docx/.txt`
   - `02_STEP_01_PRODUCT_DEFINITION_AI_NGERTI_GEOPOLITIK.docx/.txt`
   - `03_STEP_02_EXISTING_SOLUTION_GITHUB_DISCOVERY_AI_NGERTI_GEOPOLITIK.docx/.txt`
   - `04_STEP_03_UI_UX_INVENTORY_AI_NGERTI_GEOPOLITIK.docx/.txt`
   - `05_STEP_04_UI_DESIGN_REFERENCE_ADOPTION_AI_NGERTI_GEOPOLITIK.docx/.txt`
   - `06_STEP_05_UI_FREEZE_PRODUCT_BLUEPRINT_AI_NGERTI_GEOPOLITIK.docx/.txt`
   - `07_STEP_06_ARCHITECTURE_TECHNOLOGY_DECISION_AI_NGERTI_GEOPOLITIK.docx/.txt`
   - `08_STEP_07_CODE_CONSTITUTION_REPOSITORY_ARCHITECTURE_AI_NGERTI_GEOPOLITIK.docx/.txt`
5. UI reference:
   - `/docs/ui_reference/UI_REFERENCE_MANIFEST.md`
   - `/docs/ui_reference/05_UI_REFERENCE_FINAL_AI_NGERTI_GEOPOLITIK_REPO_INDEX.docx`
   - exact raw references: `/docs/ui_reference/raw/UI-001.png..UI-042.png`
6. STEP 08 evidence:
   - `/docs/evidence/ui/S08_T01_UI_REFERENCE_GATE.md`
7. `/HANDOFF.md`
8. `/docs/PROJECT_STATUS.md`
9. `/docs/DECISIONS_LOCKED.md`
10. `/docs/REPOSITORY_RULES.md`
11. Source/test/evidence aktual jika implementasi sudah ada.

## Aturan mirror TXT

DOCX tetap disimpan sebagai artefak planning/reference. TXT adalah salinan isi terurai untuk lingkungan AI/GitHub yang tidak dapat membaca binary DOCX secara langsung.

Jika runtime dapat membaca DOCX, baca DOCX. Jika binary DOCX tidak dapat dibaca, gunakan mirror TXT dan jangan menganggap dokumen tidak tersedia.

## Status sekarang

- SF-STEP 00–07 planning: present in repo.
- SF-STEP 08 / S08-T01: **PASS**.
- exact UI raw GitHub references: **42/42 PRESENT + REMOTE IDENTITY VERIFIED**.
- application feature code: NONE.
- next exact task: **S08-T02 — Repository Skeleton, Toolchain & Architecture Fitness**.
- UI baseline prompt regeneration: VOID / DO NOT USE.
- old AAVC repo: read-only.
