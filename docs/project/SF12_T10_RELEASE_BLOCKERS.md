# SF12-T10 — Release blockers and ASTRA handoff (2026-10-08 WIB)

**Decision:** Scoped CI package verification **PASS**; combined final Windows portable **NOT READY / RELEASE BLOCKED**. No production UI render permission granted.

## Required decision before SOL may build a final product

1. **Which native media engine is final?** Locked D-005 and STEP06 nominate libopenshot primary, MLT fallback, FFmpeg qualification. Current bundled CLI uses external FFmpeg and is not the agreed production-engine packaging solution. A new final engine selection/integration requires ASTRA architecture ADR and source/license compatibility.
2. **How will H264/H265 external native encoders be provided legally and reliably on users' Windows 11 PCs?** No built-in FFmpeg binary in T10 ZIPs. GPL implications of libx264/libx265, distribution/provenance/build configurations, project license, PySide6/Qt and notices must be resolved by owner/ASTRA. Relevant official sources: https://www.ffmpeg.org/legal.html ; https://ffmpeg.org/doxygen/trunk/md_LICENSE.html ; https://www.openshot.org/libopenshot/ . This is a license risk inventory, not a legal opinion.
3. **How to make one genuine portable editor?** Existing Windows `UI Shell` and `S10 Media Smoke` ZIPs remain separate. `btn_export_render` must stay disabled until binding the typed ExportRequest, qualified options, responsive jobs, exact postflight, close/cancel, error messages and an actual usable render path. Never simply toggle `can_start_render` without verifying the target binary and user workflow; preserving all UI reference raster files is mandatory.
4. **How to close release E2E?** Run complete Windows 11 packaged GUI scenario: project+media import, timeline and subtitles/narration, select exact supported profile, cancel/resume/output integrity/reopen, compare exact clips/frames/probe, inspect memory/disk/codec availability, verify frozen pixel baseline, repeat all 27 relevant workflow families at same HEAD, audit native notices and build reproducibility, explicit owner release signoff.

### Evidence already qualified (do not repeat without a change)

Windows [37746307421](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37746307421) at code `c945d9a4d0079c4b6c1ba40cd19a2326c03fa268` SUCCESS 3/3 jobs: 98 source mypy, full pytest, UI42, docs70, separate packaged UI launch, legacy packaged media smoke and **nine real packaged MP4 cells** with worker+FFprobe+whole decode. Media artifact ID 11535444050; UI artifact ID 11535718409. Source app codec/renderer logic is not activated in the GUI; no merged PR, no final release.

### Owner-facing acceptance

- Technical package subsystem: **PASS**.
- Frozen UI raster regressions: **PASS 42/42**.
- Actual full usable desktop editor / combined executable: **NOT IMPLEMENTED**.
- Native redistribution/legal gate: **OPEN**.
- Final same-HEAD CI/release: **BLOCKED**.
- Escalation: **ASTRA ADR** before changing core engine, license-bearing native deps, packaging model, or frozen UI structure. SOL remains stopped at this boundary.
