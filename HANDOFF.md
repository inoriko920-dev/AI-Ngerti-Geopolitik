# HANDOFF — AI NGERTI GEOPOLITIK

**Current phase:** SF-STEP 11 — Feature Implementation Waves  
**Current wave:** W8 — Validation / Recovery / Diagnostics Hardening  
**Role completed:** ASTRA planning  
**W8 status:** CONTRACT_LOCKED / IMPLEMENTATION_NOT_STARTED  
**Only READY task:** S11-W8-001  
**W7 final status:** CLOSED / PASS_WITH_PROVISIONAL_LIVE_GEMINI  
**Accepted W7 HEAD:** `ca6dd582a4916caa4b0ac4affe4c3119e9ad2049`

## Read before implementation

1. `AGENTS.md`
2. Software Factory source-of-truth
3. all planning docs in numeric order
4. W8 planning DOCX/TXT
5. `docs/project/W8_VALIDATION_RECOVERY_DIAGNOSTICS_CONTRACT.md`
6. current PLAN/TASKS/PROJECT_STATUS/DECISIONS
7. existing W1 persistence/media foundation and W6/W7 stale-job patterns.

## ASTRA decisions locked

- Build on existing ProjectState/CommandBus/ProjectSession/JsonProjectRepository.
- ValidationIssue is transient application DTO, not ProjectState.
- Relink preserves Asset ID and clip references.
- No filename-similarity-only auto relink.
- Multi-relink confirmation commits one intentional CommandBatch.
- Recovery source project remains untouched until explicit Save.
- Managed recovery retention default max 20 snapshots/project.
- W8 heavy background results use project/session/revision stale safety.
- Diagnostic bundle is redacted and contains no raw credentials/full content/media by default.
- UI-039/UI-040/UI-041 are reused; no new UI generation.
- STEP 12 export work is outside W8.

## Serial W8

W8-001 validation contracts — READY.  
W8-002 real media validation — blocked by W8-001.  
W8-003 single relink — blocked by W8-002.  
W8-004 batch relink scan — blocked by W8-003.  
W8-005 recovery catalog/retention — blocked by W8-004.  
W8-006 crash marker/startup recovery — blocked by W8-005.  
W8-007 persistence fault injection — blocked by W8-006.  
W8-008 stale-result hardening — blocked by W8-007.  
W8-009 diagnostics bundle — blocked by W8-008.  
W8-010 frozen UI/GOLDEN-03/regression closure — blocked by W8-009.

## Exact next action

On next owner `lanjutkan`, switch to SOL and execute **S11-W8-001 only**.
Do not implement W8-002 in the same turn.
