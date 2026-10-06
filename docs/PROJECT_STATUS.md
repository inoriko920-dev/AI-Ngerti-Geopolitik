# PROJECT STATUS — AI NGERTI GEOPOLITIK

**Last known phase:** PRE-IMPLEMENTATION  
**Formal Software Factory completed:** SF-STEP 01 — PRODUCT DEFINITION  
**Gate:** PASS WITH PROVISIONAL  
**Product Definition:** v1.0 — BASELINE_CONFIRMED untuk WHAT; provisional teknis non-blocking  
**Formal Software Factory next:** SF-STEP 02 — Existing Solution / GitHub / Upstream Discovery  
**Code status:** NONE  
**UI implementation:** NONE  
**Build:** NONE  
**Release:** NONE

## STEP 01 evidence

Canonical Product Definition:
- `docs/planning/02_STEP_01_PRODUCT_DEFINITION_AI_NGERTI_GEOPOLITIK.docx`
- machine-readable mirror: `docs/planning/02_STEP_01_PRODUCT_DEFINITION_AI_NGERTI_GEOPOLITIK.txt`

STEP 01 memvalidasi Master Blueprint, bukan menulis visi baru dari nol.

Hasil utama:
- problem statement, target user, outcomes/JTBD, primary + supporting workflows telah diformalkan;
- feature inventory dipisah MUST / SHOULD / COULD / OUT_OF_SCOPE;
- functional requirements, NFR, product I/O, persistence, AI contract, constraints, non-goals, release target, success criteria, open questions, conflict register, dan traceability tersedia;
- **UI AAVC dikunci sebagai VISUAL_CONTRACT 1:1** melalui owner decision / D-015;
- konflik lama “AAVC hanya inspirasi” vs “sama persis” berstatus RESOLVED mengikuti keputusan owner terbaru;
- core product scope tidak mempunyai blocker untuk discovery;
- pertanyaan teknis seperti upstream/license/integration strategy tetap sengaja provisional dan dialokasikan ke STEP berikutnya.

## Source of Truth saat ini

| Prioritas | Dokumen | Status |
|---|---|---|
| 1 | Instruksi eksplisit pemilik terbaru | Aktif |
| 2 | `AGENTS.md` | Aktif |
| 3 | Master Software Factory + prompt STEP aktif | Aktif |
| 4 | Master Blueprint ANG DOCX/TXT | Baseline awal |
| 5 | STEP 00 Project Intake DOCX/TXT | Gate intake formal |
| 6 | STEP 01 Product Definition DOCX/TXT | Canonical WHAT baseline |
| 7 | `docs/DECISIONS_LOCKED.md` | Aktif, termasuk D-015 UI 1:1 |
| 8 | `HANDOFF.md` | Exact next action |
| 9 | Source/test/evidence aktual | Belum ada code |

## Progress

| Area | Status | Keterangan |
|---|---|---|
| SF-STEP 00 Project Intake | PASS | Selesai |
| SF-STEP 01 Product Definition | PASS WITH PROVISIONAL | Core WHAT confirmed |
| Product scope | BASELINE_CONFIRMED | Tidak ada blocker discovery |
| AAVC UI reference role | LOCKED | VISUAL_CONTRACT 1:1; no redesign |
| Mature foundation research | PRIOR EVIDENCE | Harus diverifikasi formal SF-STEP 02 |
| License/reuse strategy | OPEN | SF-STEP 02/06 |
| UI inventory | BELUM | SF-STEP 03, berdasarkan AAVC UI |
| UI prompt/reference formal | BELUM | SF-STEP 04 |
| UI freeze | BELUM | SF-STEP 05 |
| Architecture formal | BELUM FINAL | SF-STEP 06 |
| Repository architecture | BELUM | SF-STEP 07 |
| Coding | BELUM / DILARANG | Menunggu gates pra-implementasi |
| Test/CI/product build | BELUM | Tidak ada source aplikasi |
| Packaging/release | BELUM | Tidak ada artifact |

## Exact next action

Setelah pengguna mengatakan **"lanjutkan"**, jalankan **SF-STEP 02 — Existing Solution / GitHub / Upstream Discovery** saja.

STEP 02 harus:
- verifikasi ulang OpenShot/openshot-qt dan libopenshot baseline terkini yang dipilih sebagai kandidat;
- audit activity/maintainability, license, Windows compatibility, Python bindings, timeline/playback/export primitives dan packaging implications;
- bandingkan kandidat relevan secukupnya;
- klasifikasikan kandidat sebagai EXACT_BASE / STRONG_BASE / COMPONENT_ONLY / REFERENCE_ONLY / BUILD_FROM_SCRATCH;
- tentukan apa yang boleh direuse dan apa yang tetap milik ANG;
- menjaga **AAVC UI VISUAL_CONTRACT 1:1** sebagai requirement produk;
- tidak coding, tidak fork/copy upstream, tidak membuat UI;
- membuat DOCX planning STEP 02 + mirror TXT, commit, update status/handoff, lalu berhenti sebelum SF-STEP 03.
