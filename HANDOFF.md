# HANDOFF — AI NGERTI GEOPOLITIK

**Fase:** PRE-IMPLEMENTATION  
**SF-STEP terakhir:** 01 — Product Definition  
**Gate:** PASS WITH PROVISIONAL  
**Product Definition:** v1.0 / BASELINE_CONFIRMED untuk WHAT  
**Coding:** BELUM DIIZINKAN  
**Repo target:** `inoriko920-dev/AI-Ngerti-Geopolitik`

## Baca sebelum melanjutkan

Mulai dari `AGENTS.md` dan `docs/SOURCE_OF_TRUTH_INDEX.md`. Verifikasi HEAD aktual sebelum bekerja.

## Yang baru selesai

SF-STEP 01 telah menyusun Product Definition canonical:

- `docs/planning/02_STEP_01_PRODUCT_DEFINITION_AI_NGERTI_GEOPOLITIK.docx`
- `docs/planning/02_STEP_01_PRODUCT_DEFINITION_AI_NGERTI_GEOPOLITIK.txt`

Core produk dinilai cukup jelas untuk discovery. Tidak ada blocker product-definition.

## Definisi satu kalimat

AI Ngerti Geopolitik adalah aplikasi desktop Windows untuk creator/editor video geopolitik/dokumenter yang menyusun draft edit otomatis dari input terstruktur, tetapi tetap menyediakan manual correction dan export stabil, dengan AI yang hanya bekerja melalui command tervalidasi/undoable.

## MUST product decisions

- Windows 11 x64; portable multi-file ZIP release.
- Scene DOCX + canonical Axxx asset binding.
- SINGLE/DOUBLE workflow.
- Timeline/editor manual yang benar-benar dapat dikoreksi.
- Undo/Redo untuk perubahan manual/AI.
- Motion manual + random deterministic + lock.
- Subtitle SRT workspace + style/animation.
- Narration import + microphone recording.
- Validation/relink/recovery.
- Gemini V1; hingga 100 secure credential slots.
- AI bounded Edit Plan/command; no arbitrary state mutation.
- Preview/playback yang dapat dipercaya terhadap export.
- H.264/H.265 export dan selection render sesuai support yang terbukti.
- Windows portable clean-machine behavior.
- Feature parity praktis AAVC untuk capability yang sudah dikunci.
- **UI AAVC = VISUAL_CONTRACT 1:1 sedekat mungkin; tidak ada redesign kreatif.**

## UI owner decision terbaru

AAVC UI sebelumnya sempat diperlakukan sebagai inspiration/reference. Keputusan owner terbaru mengalahkan interpretasi itu:

**Untuk ANG, AAVC UI adalah VISUAL_CONTRACT 1:1.**

Yang boleh berubah hanya:
- branding/nama menjadi AI Ngerti Geopolitik;
- control/state yang memang wajib berubah karena requirement ANG atau karena control lama tidak valid pada engine baru;
- perubahan tersebut harus dicatat dan tidak boleh menjadi redesign diam-diam.

SF-STEP 03–05 tetap dijalankan untuk inventory, coverage, review, dan freeze; bukan untuk menciptakan gaya baru.

## Provisional/open non-blocking

- exact OpenShot/libopenshot reuse strategy;
- license/source-license/distribution obligations;
- exact Windows native dependency strategy;
- exact project schema/file extension;
- exact mapping 21 legacy effects ke supported engine primitives;
- exact benchmark numbers untuk 100–300 scene;
- scope akhir legacy AAVC project importer;
- exact Gemini model/runtime behavior yang harus diverifikasi saat tahap relevan.

## Exact next action

Jika owner berkata **"lanjutkan"**, kerjakan **SF-STEP 02 — Existing Solution / GitHub / Upstream Discovery** saja.

Discovery questions:
1. Apakah OpenShot/openshot-qt masih kandidat editor infrastructure yang paling cocok untuk UI/workflow ANG tanpa memaksa produk menjadi clone OpenShot?
2. Apakah libopenshot menyediakan primitives timeline/playback/keyframe/audio/render yang cukup matang pada Windows dan Python binding?
3. Apa license obligations aktual dari openshot-qt, libopenshot, FFmpeg, Qt/PySide dan dependency yang relevan?
4. Apakah reuse sebaiknya full fork, selective reuse, component-only engine, atau reference-only?
5. Repo/library alternatif mana yang layak dibandingkan agar keputusan tidak bias?
6. Bagaimana mempertahankan AAVC UI 1:1 di atas foundation matang?
7. Bagian feature parity apa yang engine dukung langsung, perlu adapter, atau tetap ANG-specific?

Discovery tidak boleh:
- mengubah nama/tujuan produk;
- mengubah AAVC UI VISUAL_CONTRACT 1:1;
- mengubah Gemini-only V1;
- memperluas produk menjadi general-purpose NLE;
- coding/fork/copy upstream;
- menyentuh repo AAVC selain membaca evidence.

Setelah STEP 02 selesai: buat DOCX + TXT, commit, update state/handoff, lalu berhenti sebelum SF-STEP 03.
