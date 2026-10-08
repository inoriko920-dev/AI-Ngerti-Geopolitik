# ASTRA INT-01 — Rancangan Keamanan dan Kualifikasi FFmpeg Eksternal

Status: DESIGN READY / OWNER PILOT A APPROVAL MISSING / SOL IMPLEMENTATION BLOCKED.
Tanggal: 8 Oktober 2026 WIB.
Basis: ASTRA INT-00 commit de0b771a652a7b31ae411c14922fa350339cfc7c; main c9154eef85f8b475630816a7c63f5e2b52bf1523.
Paket dasar: T10 berhasil menguji dua ZIP terpisah (UI shell dan media test CLI), sembilan MP4 melalui FFmpeg di Windows CI, tetapi belum ada tombol render aplikasi yang berfungsi.
Peran dokumen: rancangan INT-01 yang dapat dieksekusi SOL setelah pilot A DISETUJUI SECARA EKSPLISIT, bukan izin mengubah sistem saat ini.

## 1. Tujuan dan ruang lingkup

Tujuan INT-01 adalah memastikan program tidak salah mengenali, salah menjalankan, atau bergantung diam-diam pada executable FFmpeg dan FFprobe eksternal yang belum diverifikasi. Output INT-01 nantinya berupa identitas native toolchain bertipe tetap, alasan penolakan yang jelas, preflight runtime nonblocking, serta tes negatif Windows.

Tidak termasuk INT-01: menghubungkan tombol Mulai Render, mengubah desain UI-001 sampai UI-042, mengganti engine produksi ke libopenshot, membundel GPL encoder, menginstal FFmpeg, mengubah pilihan lisensi proyek, menggabungkan semua PR ke main, ataupun merilis aplikasi.

Semua pilihan distribusi final, lisensi, dan engine produksi tetap PENDING sesuai D1 sampai D4 pada ADR sebelumnya. Kata “lanjutkan” dalam percakapan tidak dianggap menyetujui keempat keputusan ini.

## 2. Sumber yang diaudit pada commit dasar

- src/ai_ngerti_geopolitik/infrastructure/export_capability_probe.py: detect_export_toolchain menerima ffmpeg_binary, ffprobe_binary dan Runner, memakai shutil.which bila tidak diberikan, lalu menjalankan ffprobe -version dan ffmpeg -hide_banner -encoders dengan timeout 8 detik. Hasil mengindikasikan keberadaan encoder berdasarkan teks output, bukan verifikasi identitas atau encode sungguhan.
- src/ai_ngerti_geopolitik/application/export_capabilities.py: ExportToolchain memiliki lima Boolean. ExportCapabilities.can_start_render membutuhkan baseline terdeteksi, h264_export_qualified dan render_handler_wired. Tidak ada identitas pasangan binary, fingerprint atau provenance.
- src/ai_ngerti_geopolitik/infrastructure/ffmpeg_slice.py: _tool memilih shutil.which saat konstruksi FfmpegSliceMediaEngine dan FfprobeMediaProbe. Karena dipanggil terpisah dari capability detection, executable bisa berubah jika PATH berubah atau file diganti sebelum job berjalan.
- FfmpegProcessRunner.run menggunakan subprocess.Popen dengan stdout dan stderr berupa PIPE, kemudian melakukan poll sebelum communicate. Output yang memenuhi buffer pipe dapat membuat proses menunggu tanpa selesai. Tidak ada batas wall-clock umum jika token tidak diberikan.
- FfprobeMediaProbe.raw_probe menjalankan subprocess.run tanpa timeout, lalu membaca JSON secara penuh. Pada file rusak atau tool yang tidak responsif, operasi dapat menggantung di luar batas waktu UI.
- T08 ExportJobService dapat membatalkan job render; tetapi operasi raw_probe tidak menerima cancellation token secara langsung. Kegagalan harus tetap aman jika FFprobe tidak merespons.
- T09 telah melakukan independent full decode dan pemeriksaan metadata MP4, tetapi bukti integritas output bukan bukti kepercayaan binary yang menjalankan pemeriksaan.
- bootstrap/main.py masih membangun UI W8 dan belum menghubungkan T08/T09 ke tombol render. Jangan mengubah hal ini sebelum langkah integrasi yang disetujui.

## 3. Temuan audit terukur: prioritas dan sumber risiko

R01 / P0 — PATH binary mismatch. Probe dan engine bisa menggunakan dua lokasi executable berbeda, khususnya jika PATH atau konfigurasi berubah. Solusi: paket identitas absolut yang dipakai konsisten untuk discovery, probe, engine dan postflight; revalidate sebelum job.

R02 / P0 — binary spoofing. Output string -version dan -encoders dapat dipalsukan executable lain. Solusi: identitas path nyata, hash, metadata/provenance, sumber yang dipilih pengguna; tanda tangan sistem bila tersedia sebagai sinyal tambahan, bukan satu-satunya bukti. Jangan menjanjikan keamanan terhadap penyerang yang mengendalikan PC.

R03 / P0 — tombol render dapat keliru dianggap qualified. Encoder ditemukan dalam daftar belum menjamin encoding atau decoding berjalan. Solusi: tes encode kecil terikat waktu menggunakan data yang dibangkitkan sendiri, lalu FFprobe dan decode independen. Tes ini menjadi gate untuk profil yang diizinkan saja.

R04 / P0 — operasi native blocking. Popen dengan PIPE tanpa drain paralel berpotensi deadlock; raw_probe tidak memiliki timeout. Solusi: bounded process runner dengan drain stdout/stderr, batas waktu, cancel/kill process tree, pembatasan output dan pembersihan deterministik.

R05 / P0 — cancellation tidak konsisten. Render memiliki cancellation token, raw_probe belum. Solusi: kontrak cancellable probe di adapter aditif tanpa mengubah MediaEnginePort; testing cancel setiap fase.

R06 / P1 — metadata dan versi binary bisa berubah di antara probe dan render. Solusi: fingerprint stat/sha256, file identity, re-probe/re-hash saat job dimulai; jika berubah, tolak dan minta pengguna memilih binary yang dipercaya ulang.

R07 / P1 — identitas FFmpeg dan FFprobe kurang berpasangan. Tools bisa berasal dari vendor/versi berbeda. Solusi: simpan kedua path dan versi, periksa kompatibilitas fungsional, tidak mengharuskan keduanya berasal dari direktori yang sama bila tes lulus dan provenance dipercaya.

R08 / P1 — output/diagnostik bisa membocorkan path pengguna. Tool mengeluarkan stderr berisi jalur file. Solusi: stable error code untuk UI, log redacted, tidak menampilkan stdout/stderr mentah atau environment secrets.

R09 / P1 — binary atau media disimpan pada UNC/network drive, symlink, reparse point atau direktori tidak terpercaya. Solusi: kebijakan sumber binary yang dapat dikonfigurasi secara eksplisit dan dinilai owner; fail closed untuk lokasi yang tidak diizinkan saat pilot.

R10 / P1 — operasi teknis menyebabkan resource exhaust. Solusi: tiny synthetic qualification fixture, timeout, batas ukuran output dan frekuensi scan, throttle lifecycle, tidak menjalankan tes berat secara terus-menerus.

## 4. Kontrak aplikasi yang diusulkan, belum dikodekan

Model NativeToolchainIdentity bersifat immutable dan tidak menyimpan kunci atau token, memuat absolute_ffmpeg_path, absolute_ffprobe_path, file_identity, sha256, version_string_safe, encoder_caps, checked_at, provenance_hint dan qualification_signature.

Model NativeCapabilityReport menyimpan status FAIL_CLOSED, DETECTED_UNVERIFIED, QUALIFYING, QUALIFIED_PILOT_ONLY atau REVALIDATION_REQUIRED. Tidak satu pun status mengaktifkan UI produk sebelum INT-02 sampai INT-05 lulus.

Error code bertipe: NATIVE_NOT_FOUND, NATIVE_PATH_UNTRUSTED, NATIVE_PAIR_MISMATCH, NATIVE_VERSION_REJECTED, NATIVE_PROBE_TIMEOUT, NATIVE_OUTPUT_TOO_LARGE, NATIVE_ENCODER_MISSING, NATIVE_QUALIFICATION_FAILED, NATIVE_FINGERPRINT_CHANGED, NATIVE_PROCESS_CANCELLED dan NATIVE_PROBE_INTERNAL_ERROR.

Laporan untuk UI tidak boleh menyertakan path lengkap, user profile, codec stderr, environment variables, API key atau lokasi file sumber. Diagnostik developer disimpan hanya dengan opt-in dan redaksi.

Semua object diberi batas maksimal panjang string; tidak ada static global mutable path. Cache report harus terikat hash binary dan TTL terbatas, serta diinvalidasi jika berkas atau konfigurasi berubah.

## 5. Algoritma pemilihan dan identitas executable

Langkah A: input lokasi eksplisit pengguna atau konfigurasi runtime yang memang telah dipilih. PATH detection boleh menampilkan kandidat, tidak otomatis memberikan status terpercaya.

Langkah B: normalisasi lokasi ke path absolut Windows, periksa file biasa, ekstensi executable, kebijakan jaringan/reparse point, hak baca/eksekusi, dan metadata. Tolak folder tanpa file, path kosong, path relative ambiguous, dan binary tak terduga.

Langkah C: baca hash SHA-256 secara streaming dan catat file identity. Versi dan buildconf diproses sebagai atribut yang tidak dipercaya hingga qualification sukses.

Langkah D: jalankan query FFmpeg/FFprobe dengan exact absolute path, argument list, shell=False dan timeout. Jangan menaruh argumen berbasis input pengguna ke interpreter perintah. Jangan mengeksekusi hasil output sebagai perintah.

Langkah E: verifikasi hasil CLI dengan parser terbatas, bukan substring tunggal. Check libx264, libx265 dan aac terpisah. Keberadaan H265 tidak berarti semua preset H265 mendukung fitur tambahan.

Langkah F: encode tiny owned synthetic fixture untuk H264 baseline dan AAC hanya jika pilot disetujui; probe output dan full-decode. H265 qualification terpisah bila direncanakan dan engine mendukungnya.

Langkah G: hasil qualification dikaitkan ke identity fingerprint. Sebelum pekerjaan ekspor baru dimulai, engine dan postflight menerima pasangan path absolut dari report yang sama. Bila identitas berubah, tolak eksekusi; jangan fallback diam-diam ke PATH.

## 6. Desain bounded process runner yang diusulkan

Gunakan satu pelaksana proses native bersama pada lapisan infrastructure, dengan batas startup/probe/encode yang berbeda dan diturunkan dari kebijakan. Jangan mengubah MediaEnginePort.export yang dibekukan.

Reader stdout/stderr harus melakukan drain secara aman dan bounded. Jika output melebihi batas, hentikan proses dan laporkan NATIVE_OUTPUT_TOO_LARGE tanpa memori tak terbatas.

Untuk timeout dan cancellation, hentikan process tree seaman mungkin pada Windows, tunggu batas grace pendek, lalu lakukan forced termination bila perlu. Semua handle/temporary files/process/thread harus dibersihkan bahkan ketika exception.

Jangan mengasumsikan terminate() selalu membunuh seluruh child process. Tambahkan tes proses anak di Windows; proses tidak boleh tertinggal setelah worker timeout atau aplikasi ditutup.

Keluaran error tidak boleh menyertakan stderr mentah. Logging privacy-safe mencatat request ID acak, phase, kategori error, durasi, nama capability dan versi yang sudah disanitasi saja.

FfprobeMediaProbe.raw_probe harus dapat menerima bounded execution via additive runner atau adaptor baru, tanpa memaksa perubahan kontrak port yang frozen.

## 7. Matriks pengujian wajib pada Windows 11 dan CI

P01 — FFmpeg dan FFprobe valid pada lokasi eksplisit berisi spasi/Unicode: deteksi aman, terikat identity dan sukses tiny H264+AAC round trip.

P02 — PATH tidak memiliki binary: aplikasi UI shell masih bisa dibuka; report NATIVE_NOT_FOUND; tombol tetap disabled.

P03 — PATH mengandung fake ffmpeg.exe yang mencetak encoder palsu: tidak QUALIFIED hanya dari teks output; test encode gagal dan UI disabled.

P04 — FFmpeg valid tetapi ffprobe.exe berbeda atau tidak ada: fail closed, tidak fallback silently.

P05 — Native binary hang pada -encoders atau -version: timeout, cleanup child process, tidak membekukan Qt.

P06 — FFprobe hang pada media rusak: bounded timeout+cancel; worker berhenti; output final tidak tercipta.

P07 — FFmpeg stderr/stdout mengalir banyak lebih dari batas: reader drain terus, laporkan NATIVE_OUTPUT_TOO_LARGE, tidak deadlock.

P08 — Binary berubah checksum setelah initial qualification: revalidation menolak job, tidak menggunakan executable pengganti secara diam-diam.

P09 — Tutup aplikasi atau ganti project saat qualification: cancel, no stale signal, no output.

P10 — Tidak ada libx264 atau AAC pada FFmpeg valid: NATIVE_ENCODER_MISSING, tombol disabled.

P11 — Ada libx264 pada -encoders tetapi tiny actual encode gagal: NATIVE_QUALIFICATION_FAILED, no false success.

P12 — Permission denied/reparse point/UNC/not file/wrong extension: typed rejection, tidak menjalankan binary.

P13 — Error dari proses memuat C:\Users\Sensitive\video.mp4 atau token: UI/log summary tidak membocorkan string privat.

P14 — Probe ulang dengan binary fingerprint yang sama dan TTL sah: tidak ada proses duplikat; cache invalidasi bila path/hash berubah.

P15 — Engine, media probe dan independent postflight memakai ffmpeg/ffprobe exact absolute path yang berasal dari identitas report yang sama.

P16 — Existing frozen UI-001..042 dan semua test T02–T10 tetap PASS; tidak ada renderer product enabled pada tahap INT-01.

## 8. Kriteria penerimaan PASS/FAIL

PASS hanya bila semua P0 diuji secara nyata pada Windows, source checkout dan CI di commit yang sama berhasil, static tests, mypy, lint-imports, architecture, security, 42 reference UI dan source-of-truth checks lulus.

FAIL bila PATH spoof dapat memberi status siap, timeout menghasilkan proses zombie, stdout/stderr unbounded, FFprobe menggantung, binary berbeda antara probe dan engine, atau media bisa dipublikasikan tanpa T09 whole-decode.

PROVISIONAL bila hanya mock/fake runner tests tersedia dan belum ada actual Windows CLI qualification. Jangan label PASS_REAL_MEDIA bila alat native tidak dieksekusi.

Selesai INT-01 tidak memberi izin mengaktifkan btn_export_render. Status maksimum adalah NATIVE_QUALIFIED_PILOT_ONLY dan langkah berikutnya tetap INT-02 setelah owner-approved pilot ADR.

## 9. Rencana pembagian tugas SOL sesudah persetujuan

Task 01A: buat typed identity dan diagnostic contract pada application. Wajib tanpa perubahan DTO ProjectState dan MediaEnginePort.

Task 01B: buat secure bounded native runner, memisahkan output decoder dan callback cancellation. Uji deadlock/timeout pada Windows.

Task 01C: resolver path+fingerprint dan explicit approval source strategy di infrastructure. Cegah PATH lookup saat runtime render memakai path terverifikasi.

Task 01D: qualification tiny owned H264+AAC dan optional H265 capability, checked actual encode/probe/decode. Fail-closed on all exceptions.

Task 01E: wiring additive runtime identity ke engine/ffprobe/adapters melalui bootstrap, tanpa menyentuh Qt render activation.

Task 01F: negatif tests P01–P16, documented evidence dan draft PR, full test Windows, no release.

Setiap task 01A–F menjadi subtask teknis di bawah INT-01, bukan izin otomatis menjalankan semuanya dalam satu giliran. Bekerja satu gate per perintah setelah owner memberi D1.

## 10. Keputusan dan pembatas tegas

D1 external FFmpeg Pilot A: NOT APPROVED. Implementasi tidak dimulai. D2 final bundled vs external encoder: PENDING. D3 source project license/legal notices: PENDING. D4 libopenshot primary production candidate vs alternative: PENDING. Usulan ini bukan keputusan owner.

Jangan jalankan kode baru atas dasar dokumen ini saja. Jangan mengubah main, menggabungkan Draft PR, atau membundel FFmpeg. Hak pengguna untuk menyetujui Pilot A harus dinyatakan eksplisit.

Permintaan persetujuan yang memadai: “Saya setuju Pilot A, gunakan FFmpeg eksternal untuk pengujian integrasi UI. Jangan bundel FFmpeg, jangan ubah UI, dan jangan rilis aplikasi final.”

## 11. Referensi dan jejak handoff

Repo: https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik
Run T10: https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37746818497
Run ASTRA: https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37748770423
T10 blockers: docs/project/SF12_T10_RELEASE_BLOCKERS.md
ADR: docs/project/ASTRA_ADR_2026_10_08_RENDER_NATIVE_PACKAGING_PROPOSAL.md
Master plan: docs/planning/13_ASTRA_POST_T10_INTEGRATION_AND_NATIVE_LICENSE_PLAN_2026-10-08.docx
Official Python subprocess: https://docs.python.org/3/library/subprocess.html
Official FFmpeg license: https://www.ffmpeg.org/legal.html
