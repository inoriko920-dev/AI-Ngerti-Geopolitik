# SOL INT-01A — Typed Native Executable Identity Contract

**Tanggal:** 8 Oktober 2026 WIB  
**Status:** **PASS_PURE_APPLICATION_CONTRACT / PILOT_A_UNAPPROVED / GUI_RENDER_DISABLED**  
**Accepted implementation SHA:** `51a51eb8de4841d6800ebf63e6220eafafa42541`  
**Windows CI:** [37750580743](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37750580743) **SUCCESS**.
**GitHub:** [Draft PR #14](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/pull/14), based on ASTRA planning PR #13; PR #1–#13 still draft stacked. The `main` baseline remains unchanged.

## Additive implementation

- `src/ai_ngerti_geopolitik/application/native_toolchain_identity.py` is a **pure application-layer value-object contract**. It does not import infrastructure, call `shutil.which`, run `subprocess`, read the filesystem, dynamically load executables, or modify any GUI. These responsibilities remain deliberately outside INT-01A.
- `NativeExecutableIdentity` is a frozen/slots snapshot of a syntactically absolute ffmpeg.exe or ffprobe.exe path, lower-case SHA-256 claim, positive byte size, nonnegative modification timestamp, short printable sanitized version label, and typed source category (explicit user or PATH candidate). The path does not appear in dataclass `repr`; all validation exceptions use stable string codes.
- `NativeToolchainIdentity` holds exactly one correctly typed ffmpeg and ffprobe identity, a strictly allowlisted immutable encoder tuple, a positive inspection timestamp, and optional SHA-256 qualification digest plus typed tested profiles. Duplicate, wrong-type, missing AAC or mismatched profile claims fail closed. The qualification digest is a **data field**, not cryptographic proof or trusted attestation.
- `NativeCapabilityReport` holds fail-closed state from `NativeCapabilityStatus` with typed redacted `NativeIssueCode`; unexpected strings, missing identities and missing failure reasons are invalid. The `can_start_product_render` property **ALWAYS returns False**, including for `QUALIFIED_PILOT_ONLY`. This prevents a forged or merely constructed DTO from enabling render.
- `tests/unit/test_sol_int01a_native_identity.py` exercises immutable behavior, privacy-safe representation, invalid paths, malformed digests/timestamps/version strings, typed claims, codec/encoder mismatch, absent identity, wrong status, duplicate values, stable issue codes, and deliberate product render denial.
- `.github/workflows/sol-int01a-native-identity-windows.yml`: Windows runner Python 3.12.10, frozen UV lock, Ruff format/lint, mypy **99 source files**, import contracts, architecture, no secrets, source-of-truth **70/70**, frozen UI hashes **42/42**, targeted tests, complete Python regression and a static guard ensuring the new module has no native process calls or UI enablement.

## Security and product limitations

This step introduces **only data validation**. A SHA-256 string provided to the constructor is not proof that the executable on disk has that hash. The path is not canonicalized, symlink/junction/reparse-point checked, authenticode verified, or protected against replacement. Those checks belong to future implementation and Windows negative testing for INT-01B–01F. No actual external executable was launched by the new tests. Windows CI success does not establish a secure native runner.

The prior FFmpeg PATH TOCTOU, unbounded stdout/stderr/deadlock risk, raw FFprobe timeout, and cancellation concerns identified by ASTRA are **NOT FIXED** here; they remain in `docs/planning/14_ASTRA_INT01_EXTERNAL_FFMPEG_SECURITY_DESIGN_2026-10-08.docx`.

**Owner decision:** Pilot A integration and engine/license choices D1–D4 **still have not been explicitly approved**. This isolated, architecture-neutral DTO/test change does not record or imply such approval. No FFmpeg distribution/bundling, no Qt button activation, no editing UI-001..042, no change to `MediaEnginePort`, no merge to `main`, and no release.

**Next after scoped owner approval:** INT-01B — bounded/cancellable, privacy-safe subprocess runner design and implementation with real Windows negative tests. Do not treat INT-01A green as product readiness.
