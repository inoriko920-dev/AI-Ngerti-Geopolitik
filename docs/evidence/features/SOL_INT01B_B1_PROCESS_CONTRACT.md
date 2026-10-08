# SOL INT-01B/B1 — Kontrak Batas Proses dan Outcome Aman

**Tanggal:** Kamis, 8 Oktober 2026 WIB  
**Status teknis:** **PASS_PURE_CONTRACT / NO_SUBPROCESS_EXECUTION / NO_GUI_EXPORT**  
**Commit implementasi yang diuji:** `bfa20eb942ddda10d6daf9ab34b1265991356e42`  
**Windows CI:** [37754131337](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37754131337) — **SUCCESS**  
**GitHub:** Draft stacked [PR #16](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/pull/16), base planning PR #15; `main` tetap `c9154eef85f8b475630816a7c63f5e2b52bf1523`.

## Implementasi B1 yang benar-benar selesai

- `src/ai_ngerti_geopolitik/application/native_process_contract.py` menambah `NativeProcessPolicy` berjenis frozen/slots. Batas terverifikasi: timeout total **1–1800 detik**, stdout/stderr masing-masing **1 sampai 1 MiB**, interval polling **10–100 ms**, grace terminasi **0,1–5 detik**, maksimum **128 argumen** dan **32.768 karakter argv**. Angka negatif, tak hingga/NaN, Boolean yang menyamar sebagai angka, tipe salah dan batas terlampaui **ditolak dengan kode tetap**.
- `NativeProcessStatus` bertipe `SUCCESS`, `FAILED`, `TIMED_OUT`, `CANCELLED`, `OUTPUT_LIMIT` dan `START_FAILED`. `NativeProcessOutcome` membatasi exit code, hitungan byte dan durasi; sukses wajib exit code 0 tanpa issue, gagal wajib membawa `NativeIssueCode` yang sesuai. Ketidaksesuaian status/issue/exit code **ditolak**.
- Outcome hanya mencatat informasi aman: status, kode, durasi dan hitungan byte. **Tidak ada field atau akses untuk stdout, stderr, argv, environment, sumber video atau path pengguna.**
- Kedua properti `product_render_authorized` tetap selalu **False**. Ini bukan izin memakai executable atau mengaktifkan tombol render.
- `tests/unit/test_sol_int01b_b1_process_contract.py` mencakup nilai valid, immutability, status sukses/gagal, error mismatch, nilai NaN/inf, output cap, privasi, dan berbagai input bertipe salah. `.github/workflows/sol-int01b-b1-process-contract-windows.yml` menguji file baru plus seluruh repository dan mengecek **tidak ada** import subprocess, eksekusi native atau kontrol UI dalam modul B1.

## Evidence dan gate Windows

Run **37754131337**, pada commit implementasi `bfa20eb...`, berstatus **SUCCESS** dan meluluskan:
- uv frozen lock, Ruff formatting/lint, mypy **100 source files**, lint-imports/architecture, source-of-truth **70/70**, no-secrets, manifest UI **42/42 SHA-256**.
- Pytest khusus B1 dan pytest lengkap di repository.
- Audit statis B1: no subprocess, native execution atau GUI activation.

**Pembatas klaim:** belum ada native binary FFmpeg yang dijalankan B1. Kontrak ini *tidak* menyelesaikan potensi deadlock runner lama, batas waktu pada FFprobe, Windows child-tree cleanup, spoofing/TOCTOU executable, maupun integrasi tombol render. Semua masalah tersebut tetap memerlukan B2–B6 dan INT-01C setelah persetujuan pemilik.

## Handoff dan keputusan owner

- Keputusan D1 penggunaan FFmpeg eksternal **Pilot A masih belum disetujui secara eksplisit**. Status B1 ini adalah kontrak murni, tidak mengasumsikan izin tersebut.
- D2 cara distribusi portable final, D3 lisensi/third-party notices dan D4 pemilihan engine produksi masih PENDING.
- Belum ada paket baru, encoder bundled, perubahan `MediaEnginePort.export`, revisi frozen UI, merge `main`, maupun rilis.
- **Tugas berikutnya sesudah Pilot A disetujui:** SOL **INT-01B/B2** — runner bounded yang menguras stdout/stderr paralel, deadline monotonic, cancellation dan typed errors; lanjutkan B3 (Windows child tree), B4 (FFprobe timeout), B5 (adapter), dan B6 (real Windows FFmpeg) **secara serial**, tidak langsung dinyatakan PASS bersama.


## B1 acceptance hardening — unexpected huge integer input, 2026-10-08 WIB

- A code review found that `math.isfinite(value)` could raise **OverflowError** when `NativeProcessPolicy(timeout_seconds=10**1000)` or `terminate_grace_seconds=10**1000` is supplied, rather than returning the required typed fixed error code.
- Corrected `_seconds_between` to call `math.isfinite` **only for float** values; ordinary int values use range comparison directly. This retains fail-closed behavior for bool, NaN/Infinity, negative and over-limit values.
- Added parametrized regression tests for excessively large positive/negative integers in the timeout and termination grace, and 10**1000 into outcome counters. These tests verify rejection as `NativeProcessContractError`, not OverflowError or untrusted text.
- Hardened implementation SHA `7b95beebc3c277590371e8499acca81616d99aa4`; Windows [37756572639](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37756572639) **SUCCESS**. Target B1 tests and complete repository pytest PASS; Ruff/mypy/architecture/security/source-of-truth/UI frozen all PASS.
- The native runner **is not wired**, external FFmpeg **is not executed** by this new contract, and `can_start_product_render` stays False. Original B1 qualifications still hold; this is a stricter input validation edge-case gate only.
- **Next B2 actual subprocess engine remains blocked on explicit owner Pilot A authorization**. No engine/license, native bundling, UI binding, main merge or release permission follows from this green result.
