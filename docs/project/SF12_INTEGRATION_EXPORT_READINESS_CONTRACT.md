# SF12 — Integration & Export Readiness Contract (planning only)

Proyek: AI Ngerti Geopolitik | Tanggal: 8 Oktober 2026 (WIB) | Peran: SOL audit/readiness, ASTRA review untuk perubahan kontrak besar
Status dokumen: READINESS REVIEW COMPLETE / IMPLEMENTATION NOT STARTED / CONTRACT DRAFT
Baseline yang diaudit: main c9154eef85f8b475630816a7c63f5e2b52bf1523. W8-010 accepted code: 45c3294f5a8c93cee17369fa4b95122e3fca035b.

## 1. Maksud dan peta dua nomor STEP
SF-STEP 12 pada Software Factory = Integrations & External Services. TECH-WAVE STEP 12 pada Master Blueprint = Export Matrix. Dokumen ini merekonsiliasi keduanya: integrasi FFmpeg/FFprobe dan engine, kontrak ekspor, capability discovery, validation, job lifecycle, serta bukti nyata H.264/H.265 dan preset ekspor. Nomor TECH-WAVE bukan izin melompati gerbang SF-STEP.
Hasil giliran ini hanyalah audit kesiapan dan rencana kontrak. Tidak ada pengembangan fitur, pemutakhiran skema proyek, perubahan MediaEnginePort, UI redesign, atau klaim pengujian codec baru.

## 2. Bukti dasar dan batas klaim
W8-001..010 ditutup PASS dalam source-of-truth; W8-010 melaporkan 487/487 pytest, 23/23 evidence, 42/42 UI SHA, dan 27/27 workflow families sukses pada accepted HEAD 45c3294. Run Windows W8-010: 37732709194, SUCCESS. Commit main c9154ee merupakan tindak lanjut dokumen; status semua CI pada c9154ee harus diperiksa tersendiri sebelum mengunci gate implementasi.
W5 microphone physical hardware = PROVISIONAL (runner tidak punya perangkat DirectShow). W6/W7 live Gemini network = PROVISIONAL (belum ada kredensial provider live untuk smoke). Bukti simulasi provider, perangkat palsu, atau FFmpeg saja tidak boleh dinyatakan sebagai validasi live.
Aturan: AAVC read-only, UI-001..042 frozen, ProjectState sumber tunggal, CommandBus/CommandBatch untuk mutasi state, presentation tidak mengimpor infrastructure, engine konkret tetap di balik MediaEnginePort, dan tidak menambah fitur tanpa render-backed evidence.

## 3. Audit implementasi saat ini (berbasis file nyata)
- application/ports.py: MediaEnginePort.export(state, output_path, cancellation) belum menerima kontrak ExportRequest/preset/selection. ExportResult hanya menyimpan revision, path, duration frames, width, height, fps; belum memuat codec/audio/verification evidence.
- application/vertical_slice.py: VerticalSliceSession.export() meneruskan panggilan langsung ke media_engine.export(); belum merupakan job antrean ekspor yang benar-benar non-blocking.
- infrastructure/ffmpeg_slice.py: FfmpegSliceMediaEngine.export() membangun video+audio+subtitle kemudian memakai libx264, preset ultrafast, CRF 28, AAC 96k; config engine tidak dipilih dari dialog. Probe output hanya memeriksa width>0, height>0, duration_frames>0 sebelum os.replace.
- presentation/dialogs.py: dialog menawarkan H.265, 1440p, 4K, 60fps, preset kualitas, sharpen, subtitle off, tetapi action render_requested hanya mengirim format dan preset. Tidak ada binding nilai resolusi/FPS/quality/sharpen/subtitle ke ExportRequest yang tervalidasi. Default directory masih contoh D:\Video Projects\Liburan ke Bromo\Hasil Akhir; ini tidak boleh dipakai sebagai path produksi.
- presentation/main_window.py: aksi Export membuka route/dialog; tidak sama dengan pembuktian bahwa klik Mulai Render benar-benar menulis MP4.
- W8 ValidationService/RealMediaIntegrityRule telah tersedia; ekspor perlu mengonsumsi blocker yang current (bukan cached/stale) dan melengkapi pemeriksaan output writable/disk/codec/provider native dependency.
- ffmpeg_subtitles.py dan ffmpeg_narration.py sudah mempunyai render plan untuk kasus W5; ini harus direuse, bukan diduplikasi oleh export layer baru.
Temuan P0: UI dapat mengiklankan fitur yang belum didukung. Sampai kontrak benar-benar teruji, pilihan unsupported wajib disabled/label NOT AVAILABLE; hindari output palsu dan klaim render sukses dari sekadar mengirim intent.

## 4. Keputusan yang dikunci untuk tahap perencanaan
1) Perlu satu ExportRequest typed/immutable pada application layer: scope FULL/SELECTION, codec yang tersedia, width/height/FPS, quality profile, subtitle policy, sharpen, audio, destination, expected project/session/revision hash, dan cancellation. Definisi skema final harus ASTRA-reviewed bila mengubah signature MediaEnginePort.
2) Capability registry dibangun dari engine yang benar-benar terpasang dan binary encoder yang tersedia pada build target, tidak hanya hard-coded daftar UI. Unsupported option tidak bisa dipilih/diapply.
3) Pilihan default pertama: MP4 H.264 1920x1080 30fps dengan AAC melalui jalur qualified; H.265/1440p/4K/60fps dan sharpen tetap PROVISIONAL sampai dites satu per satu pada runner Windows target.
4) ProjectState tidak diubah demi preset sementara; request ekspor merupakan snapshot read-only. Tidak boleh ada CommandBus mutation ketika render dimulai atau ketika gagal.
5) Preflight harus fail-closed untuk referenced media hilang/rusak, subtitle/narration invalid, selection range kosong, file tidak writable, ruang disk tak cukup, codec tidak ada, dan output sama dengan source.
6) Job render berjalan off Qt UI thread, supports timeout/cancel/progress; cancel/error tidak mengganti output existing. Output menulis ke temporary path unik, probe lengkap, baru atomic promote.
7) Result verifier minimal mengecek container MP4, requested codec, width/height, fps rational, duration tolerance, audio AAC bila terpilih, subtitle burn-in sample proof, file nonzero, dan output path benar.
8) Legacy AAVC read-only, frozen UI 42/42 checksum tetap; tidak membuat panel baru tanpa gate ASTRA/UI.
9) MLT tetap kandidat produksi dan FFmpeg jalur qualification; perubahan strategi engine, dependency native, lisensi, MediaEnginePort breaking, atau schema format wajib ASTRA/ADR sebelum coding.

## 5. Matriks kemampuan: status faktual / bukti dibutuhkan
MP4/H.264 + AAC | TERBUKTI pada limited W3/W5/W7/W8 real-media fixtures | test ulang pada request typed dan packaged Windows.
MP4/H.265 | HANYA MUNCUL DI UI | encoder discovery, codec choice, actual hevc stream, packaged licensing check.
1920x1080/30 | TERUJI DI BEBERAPA FIXTURES | matrix golden baseline, duration, subtitle dan audio.
2560x1440 / 3840x2160 | BELUM TERBUKTI sebagai preset terhubung | real output dimensions, resource ceiling, honest UI.
60fps | BELUM TERBUKTI | rational timebase, audio sync, no frame mapping drift.
Full project | JALUR DASAR ADA | explicit validated request and output postflight.
Selection In/Out | BELUM ADA dalam MediaEnginePort.export() | precise start/end frame clipping and audio/subtitle offsets, reject invalid selection.
Quality profile / CRF | UI ADA, RENDER TERKUNCI CRF28 ULTRAFAST | mapping typed presets, actual ffmpeg params and probe.
Sharpen | UI ADA, JALUR EKSPOR BELUM TERBUKTI | bounded filter, before/after golden and cost.
Subtitle include/exclude | W5 render plan ADA; UI toggle BELUM TERHUBUNG | explicit policy, off makes no subtitles, on proof.
Narration/AAC | jalur W5 ADA | assert stream presence, mixed audio and duration.
Background progress/cancel/timeout | cancellation token dasar ADA; live UI JOB belum terbukti | thread affinity/progress/cancel, no partial file.
Output verification | checks MINIMAL >0 ADA | exact codec/container/resolution/fps/audio/duration/size/probe and negative cases.

## 6. Task yang direncanakan secara serial (BELUM AUTHORISED UNTUK CODING)
SF12-T01 — Capability & Truth-in-UI Baseline. Owner SOL. Audit binary FFmpeg/ffprobe/engine di packaged Windows; buat registry izin nyata; disable H.265/4K/60/sharpen yang unqualified; ubah placeholder path menjadi directory aman dan jangan memunculkan fake render. Exit: UI/engine capability parity tests + 42/42 frozen ref unchanged. Tidak mengubah engine API saat ini.
SF12-T02 — Export Request + Port Contract. Owner SOL setelah ASTRA review jika signature breaking. Typed request/response, selection scope, codec/quality/subtitle/audio/sharpen, stable snapshots and explicit errors. Exit: negative DTO/unit contracts; unknown/out-of-range rejects; no ProjectState mutation.
SF12-T03 — Preflight & Capability Negotiation. Owner SOL. Consume W8 ValidationService; file permissions, output collisions, media fingerprint, disk margin, codec probe, selection range; no expensive work on Qt thread. Exit: fail-closed tests for missing media, path traversal/collision, unwritable, low disk and unavailable encoder.
SF12-T04 — H.264 Baseline Export Pipeline. Owner SOL. Map accepted request to existing FFmpeg qualification adapter; safe temp and atomic result promotion; quality/preset/0-to-100 slider mapping documented or disabled if ambiguous. Exit: golden MP4 probe, source unchanged, no duplicates.
SF12-T05 — Full and Selected Range Mapping. Owner SOL. Clip-accurate in/out, correct duration, source offset, narration mix and subtitle offset. Exit: trims beginning/middle/end, rejects empty/locked/missing and proves audio/subtitle alignment.
SF12-T06 — Codec/Resolution/FPS Matrix. Owner SOL. Detect actual Windows native encoder availability. Implement/qualify H.265, 1440p, 4K, 60fps separately; hardware/software support no false promises. Exit: exact ffprobe codec/profile, width, height, rational FPS, bounded performance report.
SF12-T07 — Subtitle, Narration, Sharpen & Quality Binding. Owner SOL. True UI on/off policy, subtitle burn-in and optional sidecar only if contract admits, narration AAC, actual sharpen pixel-diff proof. Exit: golden on/off frames and audio stream assertions.
SF12-T08 — Nonblocking Render Job Lifecycle. Owner SOL. Thread-safe immutable snapshot, cancel, timeout, progress, stale session/close guard; legacy source and existing output preserved on failure. Exit: Qt responsiveness/slow cancel fault tests.
SF12-T09 — Postflight Verification + Errors. Owner SOL. Typed diagnostics redacted, probe compare exact requested fields, corrupt/zero/wrong codec/timebase rejected before publish. Exit: verifier fixture table, existing output untouched after failure.
SF12-T10 — Windows Full Matrix + UI Regression Closure. Owner SOL, ASTRA review for risk changes. Full direct packaged smoke, golden pixel parity where applicable, run all workflow families, UI SHA42, evidence archive, status/handoff update. Exit: success only for proven cells; unproven declared PROVISIONAL and disabled.

## 7. Gate sebelum memulai T01 dan sebelum release
DoR T01: main commit unchanged or reconciled; review PR/other-agent conflict; W8-010 evidence confirmed; CI of latest main checked (no assumption c915 all PASS); software factory and 70 source-of-truth gates; UI manifest 42/42 checksum; CLI FFmpeg/ffprobe environment inventory; no plaintext credentials. T01 is reversible and needs no paid Gemini or physical microphone.
Gate for changing MediaEnginePort or native dependency: ASTRA ADR approval mandatory. No full T02/T06 implementation before this decision, cannot silently change production engine.
Gate for matrix result PASS: every advertised preset maps to verified real output or is disabled. Unit/contracts, Qt UI, real-media render/evidence, Windows portable smoke, source security, lint/type/arch, 42 UI refs and same-HEAD regression all green. Save actual CI run IDs, commit SHA, artifact digest, codec build signature and exact command sanitised.
Gate STEP12 closure: test error/cancel/timeout, concurrent double click, stale revisions, disk fault, corrupt files, untrusted project, safe output path, no partial promoted file, privacy/no secrets. Provisional physical mic/live Gemini do not count as provider PASS.

## 8. Risiko, eskalasi dan larangan
P0—Fake export options currently in UI: user sees H.265/4K/60fps/sharpen without a verified execution path. Fix capability truth-in-UI first.
P0—Incomplete render_requested payload and dispatch means button action is not proof of export.
P1—Output verifier currently minimal, so wrong codec/resolution/audio could pass. Implement strict postflight.
P1—Export sync call could freeze Qt if wired on UI thread; must design job lifecycle and cancellation.
P1—Hardcoded example output directory is not a suitable production default; use safe per-user path / explicit dialog choice.
P1—Native FFmpeg/MLT selection and codec/licence/distribution review required before claiming H.265 or final Windows release.
Do not broaden into STEP13 hardening/release, change AAVC, rename UI reference assets, bypass CommandBus for state writes, store plaintext API keys, or describe unit/mocked capability as physical/live proof.

## 9. Ready decision and handoff
Audit result: SF-STEP12 READINESS_REVIEW COMPLETE / CONTRACT_DRAFT / BUILD NOT STARTED. Product still NOT FINAL. Implementation exact next task after contract review: SF12-T01 Capability & Truth-in-UI Baseline ONLY; each later task requires prior gate PASS and user continuation.
Files proposed: docs/planning/12_SF_STEP12_INTEGRATION_EXPORT_READINESS_2026-10-08.{txt,docx}; docs/project/SF12_INTEGRATION_EXPORT_READINESS_CONTRACT.md; HANDOFF.md and project state entries.
Source links: github repo tree at baseline c9154ee; HANDOFF.md; Software Factory 00_MASTER and guide; Master Blueprint section 20 and technical STEP 12; source application/ports.py, application/vertical_slice.py, infrastructure/ffmpeg_slice.py, presentation/dialogs.py, application/validation.py.
Do not use this review as evidence that T01 or any codec matrix testing has already been implemented.
## SF12-T02 additive export request boundary — 2026-10-08 WIB

- Typed immutable request in `application/export_request.py`; exact format/quality/subtitle/audio/sharpen enums, resolution 1080p/1440p/4K, fps 30/60, FULL/SELECTION half-open frame range.
- Output path must be absolute MP4, no parent traversal. No filesystem write/probe in DTO. Stable project ID, session ID, revision, semantic hash; stale session or same-revision semantic swap fail closed.
- `ExportRequestMediaPort` is a *prospective additive protocol only*, not an adopted production MediaEnginePort change. Current frozen `MediaEnginePort.export(state, path, cancellation)` is unchanged. ASTRA/ADR review is required before replacing/breaking its signature or choosing native dependencies.
- Valid DTO represents intent, **not qualified encoder availability, GUI enablement, render success or verified receipt**. T03 preflight and T09 postflight own those gates; T02 does not start a worker or write an MP4.
- Selection bounds validate against current timeline; selection frame policy needs T05 real-media qualification.


## SF12-T04 acceptance (2026-10-08 WIB)

T04 additive `FfmpegSliceMediaEngine.export_h264_baseline` performed real Windows H.264/1080p30 + AAC export with safe unique staging and atomic no-clobber publish. Same-code Windows run `37737863469`, code SHA `96cf5a46ecfeea6cdb9ff767414a6dde828a2a42` PASS. T09 owns full postflight, T08 worker, T10 packaged qualification; GUI remains disabled. Frozen `MediaEnginePort.export` unchanged. Next T05 selection frame mapping only; selection remains blocked until proven.


## SF12-T05 acceptance — 2026-10-08 WIB

T05 engine-side selection [start,end) is now qualified on Windows synthetic H264/AAC 1080p30 at 3 intervals (start/cross-clip/end) with subtitles and narration. Code SHA `9dca99397f3dcbac4d491d5d930cf8309d744271`, workflow `37738941089` SUCCESS. Two-pass full-composition-plus-trim preserves global cue/narration timeline but doubles encoding; not a final performance path. T03 default still rejects unqualified selection unless explicitly invoked by T05 method. No GUI render enablement, no codec/4K claims. T06 matrix is next serial task.


## SF12-T06 qualified profile evidence (2026-10-08 WIB)

Windows real-media run `37740103975`, accepted code `00761740666c66c8787aec4865d3e2184a13fe7d`, PASS for exactly **four H.264/H.265/1440p/4K/60fps combinations**: H264 1440p30, H264 4K30, H264 1080p60, H265 1080p30. Each MP4+Aac verified by FFprobe on 0.5s owned synthetic 1080p30 input. Output scaling/duplication does not increase source resolution/motion detail. T03 default deny persists; only the dedicated T06 qualification exporter can provide a typed allowlisted candidate; no UI/port replacement. Remaining matrix combinations still DENIED; full long-media performance, bundle/licenses and T08 worker/T09 postflight/T10 packaging remain provisional. Next T07 subtitle/narration/sharpen/quality policy.
