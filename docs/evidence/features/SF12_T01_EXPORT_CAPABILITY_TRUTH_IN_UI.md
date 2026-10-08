# SF12-T01 — Export Capability Truth-in-UI

**Date:** 8 October 2026 WIB. **Status:** CODE-VERIFIED / PASS_WITH_PROVISIONAL_NATIVE_ENCODER_INVENTORY.
**Baseline:** `ef7e5e1` (STEP12 planning). Scope is T01 only.

- Added immutable app-level toolchain flags. Detected executables/encoders do not imply real rendering.
- Added read-only bounded FFmpeg/FFprobe encoder inventory for CLI/CI. It is never run on the Qt thread; it does not write machine paths or secret output.
- Disabled unqualified export dialog controls including H.265, 1440p/4K, 60fps, quality, sharpen, and subtitle toggle. Render button remains disabled until backend wiring and actual media qualification.
- Replaced example D: export directory with current user's Videos directory. Dialog does not create it.
- Preserved UI routes/layout and existing raster references. No MediaEnginePort, ProjectState, engine changes, actual export-matrix work, or AAVC writes.
- Added contract and Qt guard tests, and a Windows same-head CI workflow.
- Windows run 37734750417 on code SHA b0edecbb: SUCCESS. 6/6 targeted tests, full pytest, Ruff format/check, mypy, import contracts, architecture, secrets, source-of-truth 70/70, frozen UI refs 42/42 PASS. No production package qualification in this task.
- Real runner toolchain inventory: ffmpeg=false; ffprobe=false; libx264=false; libx265=false; AAC=false. Actual encode/performance/distribution remains PROVISIONAL. Never confuse fixture tests with real encoder proof.
- Next serial task after T01 gate: T02 typed ExportRequest and port-contract ASTRA review.
