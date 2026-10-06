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


## D-013 — Namespace STEP
Software Factory memakai **SF-STEP 00–15**. Roadmap implementasi teknis pada Bab 31 Master Blueprint mulai sekarang disebut **TECH-WAVE 00–16**. AI dilarang menyamakan TECH-WAVE dengan SF-STEP atau memakai TECH-WAVE untuk melompati gate Software Factory.

## D-014 — Repository docs-only sebelum SF-STEP 08
Repository AI-Ngerti-Geopolitik dibuat lebih awal atas instruksi pemilik sebagai checkpoint dokumentasi/source-of-truth. Keberadaan repository dan commit planning **tidak berarti SF-STEP 08 selesai** dan tidak mengotorisasi coding, CI product, upstream fork/copy, build, atau release.


## D-015 — UI AAVC adalah VISUAL_CONTRACT 1:1
UI `AI Ngerti Geopolitik` harus mengikuti UI repository `AI-Automatic-Video-Composer` **sama persis sedekat mungkin** sebagai target visual dan alur.

Source visual contract:
- `AI-Automatic-Video-Composer/docs/UI_FREEZE.md`
- canonical set `UI-001` sampai `UI-042`
- reference viewport 1920×1080
- Bahasa Indonesia
- light professional editor, white surfaces + restrained blue accents
- implementation screen/layout/design tokens di `src/aavc/presentation/`

Aturan:
- jangan membuat desain UI alternatif;
- jangan mengubah hierarchy/layout/panel/style/spacing/warna/flow tanpa alasan produk yang eksplisit;
- nama produk boleh diganti menjadi AI Ngerti Geopolitik;
- perubahan UI hanya boleh terjadi bila requirement ANG benar-benar berbeda atau reuse engine matang membuat kontrol lama tidak valid, dan perubahan itu harus dicatat;
- PNG referensi tidak boleh dijadikan static runtime screen; UI tetap harus berupa widget nyata;
- detail inventory/review/freeze formal tetap dijalankan pada SF-STEP 03–05 menggunakan AAVC sebagai VISUAL_CONTRACT, bukan membuat konsep baru.


## D-016 — STEP 02 adoption baseline
SF-STEP 02 menetapkan strategi **BUILD_FROM_SCRATCH_WITH_COMPONENTS**.

Makna keputusan:
- ANG membangun sendiri product shell, domain/project model, command/history, AI orchestration, validation workflow, dan UI sesuai AAVC 1:1;
- ANG **tidak** membangun media/timeline/playback/render engine umum dari nol;
- kandidat engine utama untuk spike berikutnya adalah **OpenShot/libopenshot v1.0.1** pada tag SHA `1c46200eaedeebce3fbce74b5584dc0c04d70903`;
- **MLT v7.42.0** pada tag SHA `11e84ecf42e1a7bc885953afa58ba35d228a76ad` adalah fallback/benchmark, bukan primary tanpa evidence baru;
- `openshot-qt v4.0.1` pada SHA `5b0588ca36beedebe790e9ed4f48d105a1752f18` adalah REFERENCE_ONLY; selective GPL source reuse berstatus HOLD sampai source-license strategy ANG disetujui eksplisit;
- full Shotcut/Kdenlive bukan basis aplikasi;
- OpenCut tidak dipilih sebagai basis karena current rewrite masih dalam perubahan arsitektur besar.

D-016 adalah **discovery baseline**, bukan final architecture. SF-STEP 06 tetap harus memutuskan stack/integration detail dan dapat mengganti primary engine hanya jika evidence/spike menunjukkan blocker atau pilihan yang lebih kuat.


## D-017 — STEP 03 UI inventory baseline
SF-STEP 03 menetapkan inventory UI/UX ANG berdasarkan **AAVC VISUAL_CONTRACT 1:1**.

Keputusan:
- Screen/panel/dialog/flow ANG harus dipetakan dari AAVC frozen UI + current AAVC presentation behavior, bukan didesain ulang.
- Coverage ID resmi tetap `UI-001` sampai `UI-042`.
- Pemetaan UI-001..UI-037 sudah mempunyai reference/source evidence yang memadai untuk masuk STEP 04.
- Exact old frozen mapping/assets UI-038..UI-042 masih `OPEN_NON_BLOCKING`; STEP 04 wajib mencoba recovery dari source prompt/image lama sebelum membuat substitute.
- Jika exact old reference tetap tidak ditemukan, substitute hanya boleh diturunkan dari current AAVC source/product flow dan diberi status `PROVISIONAL_REFERENCE` sampai owner review.
- Generated collage lama yang bertentangan dengan `UI_FREEZE.md` atau current AAVC source adalah secondary evidence, bukan authority.
- Requirement “1:1” tidak mengizinkan fake capability: kontrol yang benar-benar tidak supported harus dihilangkan/disabled secara transparan dan dicatat sebagai `DELTA_FROM_AAVC`, bukan dibuat seolah berfungsi.
- SF-STEP 04 adalah titik prompt/image work; setelah seluruh prompt dibuat berlaku hard stop owner sampai image review + final UI Reference DOCX selesai.


## D-018 — STEP 04 UI Bible dan reference adoption
SF-STEP 04 menetapkan **UIB-ANG-v1.0** dan mengadopsi seluruh AAVC frozen visual set `UI-001..UI-042` sebagai target ANG.

Keputusan:
- 42/42 reference AAVC berhasil direcover dan direview;
- seluruh baseline reference berstatus `REUSE_1_TO_1` dan `APPROVED_FOR_FREEZE`;
- tidak ada campaign generate ulang untuk baseline karena owner meminta UI AAVC sama persis sedekat mungkin;
- visible ANG-only delta wajib memiliki `UI-ANG-Dxx`, prompt/revision, review, dan change record;
- D-017 open item recovery UI-038..UI-042 dinyatakan RESOLVED;
- full-resolution Final UI Reference DOCX telah dibuat dan QA 43 halaman;
- repository menyimpan connector-safe reference index + SHA manifest;
- **exact full-resolution visual binary/raw pack tetap mandatory pre-coding gate** sampai benar-benar berada di repo dan diverifikasi.


## D-019 — SF-STEP 05 UI Freeze
SF-STEP 05 membekukan UI ANG pada dua level aktif:
- **FREEZE-A / SPEC_FROZEN:** shell hierarchy, screen/state IDs, design tokens, component/control semantics, copy/status language, manual/AI behavior, timeline/validation/render/recovery UX.
- **FREEZE-B / RASTER_FROZEN:** AAVC canonical `UI-001..UI-042`, 42/42, sebagai visual baseline ANG 1:1.

`FREEZE-C / IMPLEMENTATION_CONFORMED` baru dinilai pada STEP 09/13 setelah aplikasi nyata dirender dan dibandingkan terhadap FREEZE-A + FREEZE-B.

Owner correction yang dikunci:
- file/ZIP **42 prompt UI ANG** yang sempat dibuat setelah STEP 04 adalah **VOID / NON-AUTHORITATIVE / DO NOT USE**;
- baseline ANG **tidak memerlukan prompt baru dan tidak memerlukan image generation ulang** untuk UI-001..UI-042;
- prompt/gambar baru hanya boleh dibuat untuk true ANG-only visible delta yang belum memiliki reference AAVC, memakai `UI-ANG-Dxx` + change record + review;
- implementer dilarang redesign hanya karena framework/engine berbeda;
- runtime wajib real interactive widgets; PNG reference tidak boleh dijadikan static UI.

Gate STEP 05 = **PASS_WITH_PROVISIONAL**. Planning STEP 06 boleh dimulai. Production coding tetap diblokir sampai exact full-resolution UI visual/reference pack benar-benar berada di repo dan diverifikasi, selain gate STEP 06–07.


## D-020 — SF-STEP 06 Architecture baseline
SF-STEP 06 menetapkan baseline arsitektur ANG berikut.

- Desktop stack: **Python 3.12 x64 family + PySide6 / Qt 6 Widgets**. Exact patch pin dilakukan setelah build qualification.
- Arsitektur: modular monolith dengan dependency direction `presentation -> application -> domain`; adapter eksternal mengimplementasikan port ke arah dalam.
- Source-of-truth edit: **ANG-owned ProjectState**, bukan Qt, Gemini, libopenshot/MLT, atau FFmpeg.
- Native project format: versioned UTF-8 JSON **`.angproj`** dengan atomic save, autosave/recovery terpisah, dan migration pipeline.
- Canonical time: rational/frame-aware; float seconds bukan persisted source-of-truth.
- Semua mutasi manual/AI: semantic **CommandBus / CommandBatch** dengan validation, expected revision, grouped Undo/Redo, dan stale-plan rejection.
- Media boundary **MediaEnginePort** adalah FROZEN. **libopenshot v1.0.1** menjadi primary qualification candidate, bukan unconditional final engine; **MLT 7.42** adalah fallback bila primary gagal qualification yang didefinisikan.
- Preview harus engine-derived dari semantic graph yang sama; jangan membangun hand-written preview compositor kedua.
- Render memakai immutable ProjectState snapshot dan isolated child worker; temp output diverifikasi sebelum final move.
- Gemini berada di belakang `AIProviderPort` memakai official `google-genai` family + structured EditPlan/tool calls. AI dilarang mutate ProjectState langsung.
- Credential pool 1–100 memakai `CredentialPort` + Windows generic credential storage/keyring backend; raw secret tidak masuk project/settings/log/repo. Wajib ada 100-slot qualification test.
- Windows distribution: standalone multi-file portable folder -> ZIP. `pyside6-deploy`/Nuitka preferred; PyInstaller onedir fallback bila evidence packaging native lebih kuat.
- Exact bundled dependency/license manifest + THIRD_PARTY_NOTICES + SHA-256 required for release.

### Material license gate
`libopenshot` sendiri LGPL-3.0-or-later, tetapi audio dependency `libopenshot-audio` adalah GPLv3 dan upstream juga menyebut opsi commercial license. Karena ANG membutuhkan narration/audio, actual Windows dependency tree dan source/distribution license strategy **wajib** diselesaikan sebelum engine-dependent distribution. `openshot-qt` tetap REFERENCE_ONLY dan tidak boleh dicopy sebagai shortcut.

D-020 adalah architecture baseline. Exact dependency versions, final packager, exact preview isolation mechanics, dan final libopenshot-vs-MLT production adoption ditetapkan berdasarkan qualification evidence tanpa mengubah ProductState/port/UI freeze contracts.
