# STEP12-01 — Complete saved .angproj → H.264 MP4 Pilot A

Date: 2026-10-09 WIB
Owner-approved external FFmpeg and FFprobe execution, development only.
PR #20 Draft. No main merge or Windows portable.

## Real capability added
- New worker-only `export_still_project_mp4` composes existing source-integrity
  checks, complete batched PNG timeline, SHA verified frame order and
  the actual Pilot A FFmpeg libx264 postflight.
- Verified `.angproj` is loaded through the existing JSON repository
  before any frame export. Missing/unreadable project fails closed.
- No user-supplied pre-rendered frames needed: temporary frame directory
  is created, verified and discarded in the same transaction.
- `scene_cli mp4-pilot-a` is a narrowly scoped executable entry path
  gated by `ANG_PILOT_A_FFMPEG=1`; caller must provide absolute ffmpeg
  and ffprobe binary paths and full SHA-256 identities.
- Only silent image HOLD clips without soundtrack, subtitle, motion or
  arbitrary media tracks are qualified. The existing preview validator
  rejects unsupported content.
- On cancelled/invalid/failed output, no final MP4 is committed.
- Native binary distribution, general GUI Export wiring, H265,
  resolution conversion, advanced frame parity, SRT, audio, transitions,
  long-project QA, and portable build are not asserted complete.

## Acceptance criteria
Windows CI must execute saved-project-to-real-MP4 regression and CLI
missing-file, gate-disabled, pre-cancel cleanup regressions. All prior
Windows testing, frozen 42 UI references and security must PASS.
