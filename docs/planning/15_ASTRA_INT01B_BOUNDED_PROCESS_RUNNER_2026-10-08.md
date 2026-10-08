# ASTRA INT-01B — Spesifikasi Runner Proses FFmpeg yang Aman untuk Windows

**Tanggal:** 8 Oktober 2026 WIB  
**Peran:** ASTRA, desain dan handoff saja  
**Status:** `DESIGN_READY / PILOT_A_APPROVAL_PENDING / NO_NATIVE_EXECUTION_IMPLEMENTED`  
**Basis:** SOL INT-01A SHA `743883731ef47a67e91b2ea8c26f16b58e7a0aa0`, Draft PR #14; `main` SHA `c9154eef85f8b475630816a7c63f5e2b52bf1523`.  
**Sumber pengikat:** `docs/planning/14_ASTRA_INT01_EXTERNAL_FFMPEG_SECURITY_DESIGN_2026-10-08.docx`; usulan native ADR di `docs/project/ASTRA_ADR_2026_10_08_RENDER_NATIVE_PACKAGING_PROPOSAL.md`.

## 00 — Keputusan dan scope

INT-01B kelak menangani **subprocess aman dan terbatas waktu**, bukan memilih FFmpeg sebagai engine produksi final. Desain ini boleh disusun sekarang; implementasi yang menjalankan binary FFmpeg eksternal masih **menunggu persetujuan eksplisit Pilot A**.

Tidak ada perubahan pada `MediaEnginePort.export`, model `ProjectState`, UI-001..UI-042, tombol `btn_export_render`, codec yang dibundel, lisensi proyek atau merge PR #1–#14. Kontrak INT-01A tetap kelas value-object tanpa eksekusi native. Kode proses harus terisolasi di lapisan `infrastructure`, dipanggil hanya oleh worker non-UI melalui bootstrap setelah gate disetujui.

## 01 — Temuan kode yang perlu dibuktikan/diperbaiki

1. Pada `src/ai_ngerti_geopolitik/infrastructure/ffmpeg_slice.py`, `FfmpegProcessRunner.run()` memanggil `subprocess.Popen(stdout=PIPE, stderr=PIPE)`, lalu `poll()` berulang dan baru `communicate()` sesudah proses berhenti. Bila output pipe penuh, parent menunggu child exit sementara child menunggu parent menguras output: **potensi deadlock**.
2. Runner tersebut tidak memiliki timeout keseluruhan; bila token cancel tidak diset, proses dapat berjalan tanpa batas.
3. Jika token cancellation diset, runner melakukan `terminate()` dan `kill()` pada process utama saja, belum membuktikan semua proses turunan Windows ikut mati.
4. Kegagalan `MediaToolError` dan `MediaOperationCancelled` saat ini dapat memasukkan potongan `stderr`/nama file mentah ke pesan error; jalur user atau token dalam output native bisa bocor ke UI/log jika diteruskan.
5. `FfprobeMediaProbe.raw_probe()` memakai `subprocess.run(..., capture_output=True)` **tanpa timeout dan tanpa batas output**, lalu mem-parsing JSON dan mencantumkan `stderr` saat error.
6. `export_capability_probe._run()` sudah memakai `timeout=8` untuk `-encoders`, tetapi output ditampung tanpa cap byte; ini belum dipakai sebagai satu runner produksi umum.
7. INT-01A telah menambah nilai bertipe `NativeExecutableIdentity`, `NativeToolchainIdentity`, `NativeIssueCode`; itu **klaim data**, bukan validasi hash executable sebenarnya atau izin render.

Penilaian di atas adalah inspeksi kode, **bukan bukti serangan atau hasil fuzzing**. Jangan mengklaim sudah memperbaiki deadlock selama belum ada implementasi, regression test dan Windows native smoke.

## 02 — Arsitektur proses yang disarankan

### 02.1 Port dan dependensi

Rencanakan kelas internal `BoundedNativeProcessRunner` di infrastructure dan port/adaptor independen bernama `BoundedNativeProcessPort` (jika memang diperlukan). Tugas tunggal: jalankan **path absolute binary terpilih**, argv sebagai sequence tanpa shell, drain output secara bounded, kembali dengan hasil terbatas atau kode error privasi-aman.

Aturan:
- `shell=False`, tidak ada string command hasil gabungan `user_input`, tidak menyuntik ke PowerShell/CMD.
- Path executable berasal dari identitas INT-01A yang diverifikasi lebih dahulu oleh INT-01C, bukan `PATH` yang dicari ulang setiap job.
- Batas konfigurasi immutable: `timeout_seconds` antara 1 dan 1800, `max_stdout_bytes` dan `max_stderr_bytes` di bawah batas kebijakan (contoh pilot: 1 MiB masing-masing), `poll_interval_ms` maksimum 100. Nilai final tidak dipilih diam-diam; tetapkan lewat acceptance dan benchmark.
- Penulis output sebaiknya memakai dedicated reader threads/async reader atau temporary spool yang dibatasi, **menguras kedua pipe bersamaan sejak proses dimulai**. Jangan melakukan blocking `wait()` sebelum drain.
- Setiap argumen harus bertipe str, tidak NUL; cegah command log memuat user input/path. Maksimum arg count dan panjang total diaudit.
- `CancellationToken` dipantau tanpa menunggu output native; deadline memakai `time.monotonic()`.

### 02.2 Hasil dan kesalahan bertipe

Kontrak `NativeProcessResult`: `exit_code`, `stdout`, `stderr` jika memang boleh digunakan **secara internal hanya**; `duration_ms`, `bytes_seen_stdout`, `bytes_seen_stderr`, `truncated` dan penyebab. Representasi umum di luar infrastructure harus menampilkan **hanya** error code terdaftar `NativeIssueCode`.

Bedakan `NATIVE_PROBE_TIMEOUT`, `NATIVE_PROCESS_CANCELLED`, `NATIVE_OUTPUT_TOO_LARGE`, `NATIVE_QUALIFICATION_FAILED`, `NATIVE_PROBE_INTERNAL_ERROR`, `NATIVE_FINGERPRINT_CHANGED`. Tidak boleh menambah kode baru tanpa test dan dokumen yang relevan.

Jangan mengembalikan `stderr` langsung sebagai `str(error)`. Untuk developer diagnostic, simpan hanya metadata yang aman serta boleh diaktifkan secara eksplisit; rekaman tanpa password, path user, token atau environment.

### 02.3 Algoritma deadline, timeout dan cancel

1. Sebelum `Popen`, validasi parameter bounded dan token cancel; `cancelled=True` = batal tanpa menjalankan executable.
2. Jalankan child dengan `stdin=DEVNULL`, stdout/stderr dikuras paralel.
3. Pantau `monotonic deadline` dan cancellation selama child berjalan dan selama proses penutupan.
4. Pada cancel/deadline/output lebih batas: hentikan process group/tree semampunya. Pada Windows, rencanakan `CREATE_NEW_PROCESS_GROUP`, sinyal/grace period jika efektif, dan fallback `taskkill /T /F` **hanya terhadap PID proses yang dibuat sendiri** dengan arguments list, tidak shell, disertai audit proses turunan. Implementasi akhir boleh memakai Windows Job Objects jika diperlukan, tetapi butuh tes nyata di Windows 11; jangan mengasumsikan `taskkill` atau `terminate` selalu cukup.
5. Tutup semua pipe, reader thread dan handle proses. Pembersihan memiliki deadline. Jika child tidak bisa dihentikan, laporkan fail-closed dan tandai resource cleanup sebagai gagal; jangan menyembunyikannya.
6. Kesalahan returncode abnormal = failed, tidak ada file hasil yang dipublikasikan; tahap media T08/T09 tetap memiliki staging serta verifikasi mandiri.
7. Cancel/timeout termasuk saat `ffprobe -show_streams -show_format` dan saat full-decode T09; jangan hanya menambahkan guard pada render utama.

### 02.4 Format dan ukuran output

- `ffprobe` JSON: stream dibatasi ukuran byte, diverifikasi bentuk object, jumlah stream dibatasi, parser tidak menerima output arbitrer berukuran besar.
- `ffmpeg` progress: jika dibutuhkan nanti, parse kanal `-progress pipe:1` yang bounded; jangan gunakan teks stderr sebagai sumber progres palsu atau persen asumsi.
- Encoder output file besar bukan `stdout`; output utama ditulis pada staging path privat seperti T08/T09. Pembatasan output pipe tidak membatasi ukuran file MP4.
- Tidak boleh membuang seluruh stderr secara tak terkendali: tetap drain penuh lalu hanya simpan jumlah byte/fragmen aman bila dibutuhkan. Jika cap terlampaui, hentikan proses dan laporkan output-too-large.

## 03 — Rencana implementasi SOL setelah owner menyetujui Pilot A

**B1 — Kontrak internal proses:** tulis typed immutable `NativeProcessPolicy`, `NativeProcessOutcome`, dan pemetaan error ke `NativeIssueCode`; validasi batas dan privasi, tanpa koneksi UI. Unit test pure.

**B2 — Bounded runner:** implemen drain paralel stdout/stderr, absolute argv, monotonic deadlines dan cancellation. Unit test dengan Python child fixture buatan sendiri, tanpa memerlukan FFmpeg.

**B3 — Windows child-tree lifecycle:** gunakan fixture Python child yang membuat proses turunan, menjalankan output besar, menolak berhenti, atau sleep tanpa batas; verifikasi tidak ada child tersisa setelah cancel/timeout. Kode lintas platform harus punya fallback aman dan tidak menghentikan PID orang lain.

**B4 — FFprobe adapter:** ubah path native scan/raw_probe menjadi bounded tanpa mengubah `MediaProbePort` atau `MediaEnginePort` yang frozen. Pastikan media hilang/rusak tidak membuat UI macet; beri kode error yang tidak mengandung path.

**B5 — FFmpeg qualification wiring:** lewat adapter injeksi, jalur media lama memakai runner baru hanya setelah lulus regression; tidak mengganti codec, tidak mengubah format output, tidak mengaktifkan render produk.

**B6 — CI Windows + real native QA:** uji FFmpeg/FFprobe eksternal hanya pada runner CI, termasuk kontrol versi, timeout nyata, ketiadaan binary, cancel saat encode, corrupted/large output, dan full T02-T10 regression. Tidak ada executable FFmpeg di ZIP yang didistribusikan.

**Gate serial:** B1 dahulu, kemudian B2–B6 masing-masing terpisah bila pengguna memberi perintah lanjut setelah approval. Tidak boleh mengerjakan semuanya seolah satu langkah sudah melewati gate.

## 04 — Matriks penerimaan Windows dan failure mode

| ID | Fixture/test | Hasil yang wajib |
|---|---|---|
| B01 | Child menulis stdout jauh melebihi ukuran OS pipe | Tidak deadlock; gagal aman/berhasil jika di bawah cap |
| B02 | Child menulis stderr besar tanpa stdout | Kedua pipe terkuras; tidak deadlock |
| B03 | stdout+stderr bergantian cepat | Tidak deadlock, akuntansi byte konsisten |
| B04 | Child sleep tanpa output | Deadline menghentikan job dan child |
| B05 | Cancel sebelum start | Tidak menjalankan binary sama sekali |
| B06 | Cancel saat child sibuk | Respon terbatas waktu dan staging aman |
| B07 | Child membuat proses turunan yang sleep | Child tree tidak dibiarkan berjalan |
| B08 | Child mengabaikan terminasi halus | Bounded forced cleanup, typed error |
| B09 | Proses output melebihi batas yang diizinkan | `NATIVE_OUTPUT_TOO_LARGE`; memory bounded |
| B10 | stderr berisi path user & token rahasia sintetis | UI/error publik tidak membocorkan substring |
| B11 | Nama binary/penggalan argv mengandung spasi/Unicode | Argumen tetap utuh tanpa shell |
| B12 | NUL, salah tipe, jumlah argumen ekstrem | Fail closed sebelum subprocess |
| B13 | `ffprobe` hang pada corrupt media | Timeout/cancel dan file staging bersih |
| B14 | `ffprobe` mengembalikan JSON tidak valid/terlalu besar | Typed fail dan tidak mengirim data mentah |
| B15 | FFmpeg exit code nonzero setelah output parsial | Final output tidak dipublikasikan |
| B16 | User mengubah project saat proses berlangsung | T08 stale guard menahan publikasi |
| B17 | FFmpeg/ffprobe diganti sesudah probe awal | Revalidation INT-01C diperlukan; tidak fallback PATH |
| B18 | Banyak job diklik serentak | T08 one-worker policy tetap berlaku |
| B19 | FFmpeg tidak ada di komputer pengguna | UI tetap terbuka, render dinonaktifkan |
| B20 | Windows CI tanpa admin dan ZIP tanpa FFmpeg bundled | Audit ZIP lulus, dependency eksternal jelas |

**Klasifikasi:** B01–B10, B13–B16 = P0; sisanya = P1. B17 sebagian besar bergantung INT-01C dan tidak boleh dinyatakan PASS pada INT-01B saja.

## 05 — Pembatas kinerja dan observabilitas

- Benchmark waktu cancel/timeout pada Windows Actions dan Windows 11 x64; jangan menjanjikan milidetik tertentu sebelum pengukuran.
- Maksimal stdout/stderr harus terukur dengan `bytes_seen`; error public hanya kode. Ukur peak process memory, leak handle, lingering process, cancel latency.
- Bounded stdout diperlukan untuk FFprobe JSON dan video progress; source media SHA serta output no-clobber diverifikasi lewat existing T08/T09.
- Jangan merekam commandline lengkap, environment, query, API key, path user, atau stdout/stderr raw di GitHub artifacts.

## 06 — Kondisi FAIL dan stop rules

- FAIL jika runner masih menunggu `poll()` tanpa drain pipe atau tidak ada bounded deadline.
- FAIL jika cancel membiarkan proses anak hidup, atau timeout membiarkan output MP4 parsial menjadi final.
- FAIL jika user-facing exception/log memuat token sintetis atau file path.
- FAIL jika implementasi mengganti `MediaEnginePort.export` signature, mengubah UI/ProjectState, menyalakan `btn_export_render`, atau membundel codec.
- PROVISIONAL jika hanya mock/synthetic child unit test di Linux; tidak ada Windows native child-tree proof.
- PASS_INT01B baru sah setelah semua kasus P0 dan regression Windows pada commit yang sama lulus, dengan bukti log dan status khusus. Rilis produk tetap BLOCKED.

## 07 — Gate keputusan owner

- D1: Pilot A penggunaan FFmpeg eksternal **belum disetujui secara eksplisit**. Dokumen ini tidak memberikan otorisasi menyentuh runner produksi.
- D2: Distribusi encoder di ZIP final vs pemasangan terpisah **pending**.
- D3: LICENSE proyek dan native dependency notices/legal review **pending**.
- D4: libopenshot sebagai kandidat mesin akhir tetap mengikuti keputusan sebelumnya; pergantian engine **tidak diotorisasi**.

Setelah pemilik mengatakan “Saya setuju Pilot A untuk pengujian dengan FFmpeg eksternal, tanpa bundling FFmpeg, tanpa perubahan desain UI, tanpa rilis final”, barulah ASTRA memperbarui ADR owner-approved dan SOL boleh memulai B1. **Perintah “lanjutkan” umum tidak otomatis memberikan persetujuan lisensi/distribusi.**

## 08 — Pustaka referensi dan evidence

- Python subprocess API, deadlock dan timeout: https://docs.python.org/3/library/subprocess.html
- FFmpeg legal/redistribution: https://www.ffmpeg.org/legal.html
- Repo T10 Windows evidence: https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37746818497
- INT-01A CI: https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37750922504
- Source inspected: `src/ai_ngerti_geopolitik/infrastructure/ffmpeg_slice.py` and `src/ai_ngerti_geopolitik/infrastructure/export_capability_probe.py` on commit 743883731ef47a67e91b2ea8c26f16b58e7a0aa0.
