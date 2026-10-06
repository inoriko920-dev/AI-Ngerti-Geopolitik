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


## D-021 — SF-STEP 07 Code Constitution & Repository Architecture
SF-STEP 07 menetapkan **CC-ANG-v1.0** dan **REPO-ANG-v1.0**.

Locked constitution:
- canonical Python package: `src/ai_ngerti_geopolitik/`;
- main boundaries: `domain`, `application`, `presentation`, `infrastructure`, `bootstrap`;
- dependency direction: presentation -> application -> domain; infrastructure implements application ports; bootstrap construction only;
- one concern has one canonical owner; generic god managers/services are forbidden;
- all ProjectState mutation goes through semantic CommandBus/CommandBatch;
- presentation may not call concrete media/provider/persistence/credential adapters;
- domain may not depend on Qt, libopenshot/MLT, FFmpeg, Gemini SDK, keyring, subprocess, or filesystem I/O;
- worker results must revalidate session/project revision before apply;
- generated/build/cache/user data is not manual source;
- docs/PROJECT_STATUS.md remains canonical live project-state document; do not create a competing PROJECT_STATE.md;
- architecture changes, engine switch, breaking ports/schema, frozen UI deltas, secret backend changes, new native dependencies, and packaging-model changes require ASTRA/ADR review.

STEP 08 task order is locked:
1. `S08-T01` Source-of-Truth & Exact UI Reference Gate;
2. `S08-T02` Repository Skeleton, Toolchain & Architecture Fitness;
3. `S08-T03` Windows CI & Portable Packaging Scaffold.

The exact full-resolution UI-001..UI-042 raw/reference set must be committed and hash-verified in S08-T01 **before production source coding**. STEP 07 does not claim source/test/CI/build implementation.


## D-021 — Verified STEP 08 Windows toolchain baseline
S08-T03 Windows CI verifies the foundation toolchain baseline:
- CPython 3.12.10 x64;
- uv 0.12.21 with committed resolver-generated `uv.lock`;
- PySide6 6.11.1;
- Ruff 0.16.10;
- mypy 2.4.0;
- Import Linter 2.15;
- pytest 9.1.1 + pytest-qt 4.5.0;
- detect-secrets 1.5.0 + pip-audit 2.10.1;
- PyInstaller 6.22.3 onedir for the **foundation packaging scaffold**.

This locks the STEP 08 foundation toolchain, not the final media-engine/native dependency set. A material toolchain switch requires evidence and review.


## D-022 — STEP 09 AAVC runtime parity baseline
SF-STEP 09 menerima implementasi UI ANG berdasarkan instruksi eksplisit owner bahwa UI harus mengikuti AAVC sedekat mungkin / 1:1 tanpa redesign.

Aturan acceptance:
- frozen `UI-001..UI-042` tetap visual/design authority dan tidak boleh diganti;
- actual runtime screenshot AAVC dari repo read-only dipakai sebagai **implementation-parity supplement**, karena tujuan owner adalah menyalin UI aplikasi AAVC yang nyata, bukan menciptakan desain baru;
- baseline runtime AAVC yang dipakai: CI run `37498549910`, commit `7d77fc9f724d359c7da6c4796dffce5104740952`, artifact `step09-ui-actual` ID `11429380147`;
- baseline ANG STEP 09 yang diterima: Windows CI run `37520166438`, commit `61225eca38115a636e062d3e795f7884049d19d4`;
- representative anchor states yang diuji: UI-002, UI-003, UI-010, UI-013, UI-014, UI-027, UI-035, UI-041;
- runtime ANG harus memakai widget Qt nyata; frozen PNG tidak boleh dipasang sebagai static runtime screen;
- perbedaan branding, rasterization/font antialiasing, capture environment, dan minor fixture dapat diterima bila hierarchy/flow AAVC dipertahankan dan tidak ada redesign;
- acceptance **tidak berarti pixel-identical** terhadap seluruh 42 raster;
- AAVC tetap read-only.

Keputusan ini hanya menetapkan interpretasi acceptance STEP 09. Ia tidak mengizinkan perubahan UI diam-diam pada STEP berikutnya.


## D-023 — STEP 10 media qualification boundary
SF-STEP 10 membuktikan canonical editing backbone memakai **real system FFmpeg/ffprobe qualification adapter** di belakang `MediaEnginePort`.

Keputusan yang dikunci:
- adapter STEP 10 adalah real backend untuk qualification/evidence, bukan fake;
- adapter ini **tidak mengganti D-020** dan tidak otomatis menjadi production media engine ANG;
- libopenshot tetap primary production qualification candidate dan MLT tetap fallback sampai STEP 11 menghasilkan evidence Windows yang cukup;
- presentation tidak boleh memanggil FFmpeg/libopenshot/MLT langsung;
- ProjectState + CommandBus tetap source-of-truth dan engine-agnostic;
- STEP 10 boleh ditutup PASS_WITH_PROVISIONAL karena UI→state→persistence→preview/export→packaged smoke sudah real dan verified;
- provisional yang wajib diprioritaskan pada STEP 11 adalah continuous production playback serta final engine/native dependency/license qualification;
- packaged STEP 10 media-smoke executable adalah qualification artifact, bukan final user-facing distribution.

Accepted STEP 10 baseline:
- commit `852610f55a6e99dc98234114c3cf099ed85dfd42`;
- S10 run `37527851180` SUCCESS;
- S09 regression `37527851222` SUCCESS;
- S08 regression `37527851230` SUCCESS.


## D-024 — STEP 11 W0 engine qualification decision
SF-STEP 11 Wave 0 replaces the **implementation-priority ordering** in D-020
with fresh Windows runtime evidence, while preserving all architecture
boundaries.

Accepted evidence:
- W0 run `37533447729` on
  `f54993851f85aa5672f0d86dcb7e5ea3a49c7ae6` — SUCCESS;
- actual tested MLT package:
  `mingw-w64-x86_64-mlt 7.40.0-2`;
- runtime `melt.exe 7.40.0`;
- Python binding `mlt7`;
- exact seek samples at 0, 10, 50 and 98 frames;
- SDL2 continuous/seek/edited-playlist transport smoke;
- MLT avformat H.264/AAC render;
- regression artifact `11444509597`;
- MLT artifact `11444689616`.

Locked interpretation:
- **MLT is the primary production-engine implementation candidate for STEP 11
  W1/W2 onward**;
- direct libopenshot production binding is BLOCKED until Windows build/package
  and libopenshot-audio licensing evidence becomes materially stronger;
- STEP 10 FFmpeg remains a qualification/reference adapter and does not become
  the editor source-of-truth;
- ANG-owned ProjectState, CommandBus/CommandBatch, MediaEnginePort, Qt UI freeze
  and semantic edit architecture remain unchanged.

Important version truth:
D-016/D-020 research tracked MLT 7.42.0, but the actual MSYS2 Windows package
available and verified in W0 was **7.40.0-2**. Do not claim 7.42.0 was runtime
tested unless a later qualification proves it.

Remaining release gate:
W0 does not approve a final distributable MLT DLL bundle. The exact native DLL
closure, required plugin subset, codec/license obligations, notices/source
obligations and clean-machine package smoke remain mandatory before release.
