# ASTRA ADR — Canonical image-backed Scene timeline

Date: 2026-10-08 WIB
Status: PROPOSED / NOT APPROVED / NO SOL SCHEMA OR RENDER CODING AUTHORITY
Project: AI-Ngerti-Geopolitik, Draft PR #20

## Verified gap and guard

- Master Blueprint requires SINGLE/DOUBLE layouts and one canonical timeline, with scene identity and source references preserved.
- Current ProjectState accepts image Assets but its validator requires every timeline Clip to reference media_type=video.
- Imported still images have an intrinsic source duration of one frame; their on-screen HOLD time needs its own explicit duration, not a fake video stream.
- Current MLT timeline projection rejects image Clips and export/preview are not image-lane qualified. No truthful end-to-end image workflow exists yet.
- Scene DOCX parser, exact Axxx folder inventory and the noncanonical, frame-exact SceneTimelineReview are validated in PR #20.
- Read-only image metadata verification now captures dimensions, file size and SHA-256 and rejects stale/changed files. A final-save use case must re-scan the folder to catch new duplicates, then re-probe before commit.

## Proposed ASTRA decision

Recommendation: model a still-image HOLD as explicit canonical Clip timing (new optional backward-compatible image_hold_frames field, or approved equivalent), independent of the image Asset's intrinsic one-frame source interval. Keep a single ProjectState/CommandBus as owner; preserve video Clip behavior by default. Define canonical scene number, order, SINGLE/DOUBLE grouping and source/context ownership in a reviewed persistence contract so they survive Save/Open; no second scene-state store.

Rejected alternatives:
1. Treat PNG/JPEG/WebP as video asset: misrepresents source media and can break playback.
2. Change intrinsic image duration whenever its display duration changes: conflates source media with an edit and breaks relink identity.
3. Create a separate live scene model outside ProjectState: breaks canonical single source of truth.
4. Auto-transcode every image before project creation: creates unsupported native side effects and unnecessary media dependencies.

## Required implementation sequence AFTER approval

A. Lock schema-v1 compatible optional image timing and scene metadata or explicitly migrate schema with backwards-reader guarantees; include type and positivity invariants.
B. Implement canonical image Clip validation; exact-frame SINGLE FULL and DOUBLE concurrent LEFT/RIGHT scene composition; stable Axxx IDs, scene/context persistence, and a single undoable CommandBatch for creation.
C. Review image Clip editing: set duration/trim/split/reorder, media relink, undo-redo. Reject unsupported operations rather than silently mutating image source time.
D. Re-scan exact Axxx folder at Save, reject missing/duplicate/stale entries, fingerprint and dimensions check, and atomic .angproj persistence.
E. Qualify the SAME canonical properties for MLT playback/seek/preview and export. Until source and renderer parity tests pass, keep affected UI controls disabled or fail closed.
F. Use the approved frozen UI design; new timing/review controls need UI approval, no silent structural changes. Test two golden scenes (one FULL, one LEFT/RIGHT), metadata, preview/export geometry and retained scene IDs on Windows.
G. Complete targeted and full pytest, Ruff, mypy, source-of-truth/security and 42 frozen UI checks at same HEAD. Portable Windows remains last; native DLL/license review separately gated.

## Review and permissions

G-IMAGE-01: schema semantic change TRIGGERED under AGENTS.md and Code Constitution. This ADR is PROPOSED, not approval. No implementation of canonical image Clip/schema now.
G-IMAGE-02: new UI visual changes require separate approved reference.
G-IMAGE-03: external native FFmpeg runner Pilot A D1 remains separately UNAPPROVED; accepting this ADR must not be treated as granting that permission.
G-IMAGE-04: merge remains blocked absent owner's explicit instruction; main unchanged.
G-IMAGE-05: final portable remains last, after real functionality and licensing tests.

If owner approves, precise statement:
"Saya setuju ADR image-backed canonical timeline: gunakan durasi HOLD eksplisit untuk gambar pada Clip, proyek lama tetap kompatibel. ASTRA boleh mengunci kontraknya, SOL boleh implementasi domain/persistence dan pengujian di Draft PR. Jangan ubah UI, merge, jalankan FFmpeg eksternal, atau buat portable."
