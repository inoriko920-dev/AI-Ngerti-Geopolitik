# ASTRA INT-01 — Keamanan FFmpeg eksternal: desain siap, implementasi diblokir

**Status:** `DESIGN_PASS / NATIVE_RUNTIME_NOT_IMPLEMENTED / OWNER_D1_PENDING`  
**Tanggal:** 2026-10-08 WIB, planning ASTRA only.

Source audit found real potential hazards in existing export_capability_probe.py and ffmpeg_slice.py: mutable PATH lookup between detection and engine construction; unverified encoder list; lack of cancellation/timeouts on FfprobeMediaProbe.raw_probe; subprocess pipe deadlock potential when Popen poll waits before communicate; existing stdout/stderr includes paths at infrastructure level. These are code-level hazards, NOT proof of exploitation or runtime incident. They require controlled Windows tests and typed mitigation in the later SOL task.

The complete 16-case Windows matrix, typed proposed identity contract, six implementation subtasks, and D1–D4 decision status are in `docs/planning/14_ASTRA_INT01_EXTERNAL_FFMPEG_SECURITY_DESIGN_2026-10-08.md`, TXT mirror and DOCX. No engine/UI/port/release changes during this planning task. `main` remains unchanged; parent is ASTRA planning PR #12; next step requires **explicit Pilot A approval**, then SOL INT-01A, not full release authorization.
