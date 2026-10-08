# ASTRA ADR-2026-10-08: Native Engine, Licensing and Unified Windows Editor

**Status: PROPOSED / NOT APPROVED / NO SOL CODING AUTHORITY.**
**Basis audit:** T10 code head 866464471e5926d7f9a782e56f2030ed2425e7a2, successful Windows Actions 37746818497. **D-005 remains unchanged.**
**Scope:** architecture proposal after T10, not a production binary decision.

## Facts
1. Two distinct ZIPs exist: a PySide6 UI shell with the Export button disabled, and a separately packaged media test executable. A combined editor with usable render is NOT present.
2. Nine real MP4 profile cells passed on Windows when the packaged media executable called external FFmpeg and FFprobe. These native codec executables were NOT included in the delivered ZIP.
3. Existing application layer owns typed ExportRequest, current preflight, worker cancellation/phase/status and strict independent postflight. The new UI binding has NOT been made.
4. Locked D-005 says libopenshot is a primary candidate, MLT fallback. This does not mean a chosen or adopted production engine.
5. THIRD_PARTY_NOTICES.md is a foundation scaffold. No top-level LICENSE file was found. A legal release decision remains open.

## Options and ASTRA recommendation
**A — Pilot with externally provided FFmpeg.** Reuse T02-T09 in one UI onedir test package; user must separately supply trusted FFmpeg/FFprobe. No download or bundling of GPL codec binary. This is the preferred *limited pilot* because it needs the least disruption to frozen UI, source, and the MediaEnginePort. It is NOT a self-contained offline portable final product and is NOT automatically free of any license obligations.

**B — Bundle GPL-enabled FFmpeg, libx264/libx265.** Easiest end-user ZIP, but GPL-source/build traceability, accompanying copyright notices, dependency auditing, patent concerns, distribution source, and provenance need explicit owner/legal sign-off. Not approved.

**C — Adopt libopenshot for final product.** Follows D-005 strategic candidate; libopenshot is LGPLv3 or commercial. Windows binary parity, FFmpeg/JUCE and other native obligations, frame/undo/render/cancellation behavior, and 9 tested cells require new real qualification. It does NOT bypass codec licensing. Not approved.

**D — MLT fallback.** Remains a fallback requiring independent Windows/source/license/feature parity evidence. Not approved.

**ASTRA proposal:** approve only option A as a narrow engineering pilot after owner consent; keep C as the previously locked final-engine evaluation candidate, not an automatic engine switch. Do not publish a final editor on this ADR alone.

## Official license references
- FFmpeg licensing and legal checklist: https://www.ffmpeg.org/legal.html
- FFmpeg license source: https://ffmpeg.org/doxygen/trunk/md_LICENSE.html
- libopenshot LGPLv3 vs commercial and dependency warning: https://www.openshot.org/libopenshot/
- Qt for Python LGPL/GPL/commercial: https://doc.qt.io/qtforpython-6.8/commercial/index.html
- PyInstaller bootloader exception: https://github.com/pyinstaller/pyinstaller/blob/develop/COPYING.txt

These references require dependency-specific review. This is technical planning, NOT legal advice. Calling an external executable is different from bundling it, but neither statement substitutes for actual legal review.

## Frozen boundaries and failure conditions
- Never touch reference UI-001 through UI-042, silently redesign Qt widgets, or make AAVC editable.
- Do not change the frozen MediaEnginePort export signature, ProjectState schema, CommandBus ownership, credential backend, or final engine without a new approved ADR.
- UI does not import infrastructure; bootstrap wires ports. No expensive render, probe, networking, or native executable startup on Qt UI thread.
- User output requires current request session/revision/hash and T03 preflight, worker T08 staging and T09 independent full decode, with atomic no-clobber publication.
- Without verified native binaries or request profile, render must stay disabled, without fabricated percentage progress.
- No installation of FFmpeg, no admin requirement, no automatic binary downloads and no release bundling without separate owner approval.
- Existing stacked draft PR #1 through #11 remain unmerged. Do not change main or publish releases during this planning task.

## Decisions requiring explicit owner approval
**D1:** Approve or reject pilot A, requiring external FFmpeg/FFprobe. This is permission to plan/test only, not a blanket release approval.
**D2:** Does the FINAL product require a standalone portable ZIP with all codecs included, or may its encoder be a separately installed dependency?
**D3:** Who will approve project source license, Qt/PySide6 notices, GPL-enabled FFmpeg/native redistribution, SBOM, component source and codec/patent risk?
**D4:** Retain libopenshot as primary final-engine qualification candidate under locked D-005, or commission a separately reviewed engine decision?

All four are currently **PENDING**. A generic later message saying "lanjutkan" does not by itself approve redistribution/engine changes. SOL must stop until these decisions and acceptance gate are recorded.

## Serial handoff
After explicit decisions: INT-00 owner-approved ADR → INT-01 external binary identity and capability → INT-02 typed UI request bridge → INT-03 frozen UI guarded states → INT-04 Qt worker and close/cancel → INT-05 controlled pilot render click to verified MP4 → INT-06 combined onedir beta ZIP → INT-07 Windows 11 real E2E and failures → INT-08 dependency/license notices/legal gate → INT-09 full same-head 27 workflow suites and owner release sign-off. One task per turn.
