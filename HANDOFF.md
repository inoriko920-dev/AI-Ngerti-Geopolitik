# HANDOFF — AI NGERTI GEOPOLITIK

**Current phase:** SF-STEP 11  
**Current wave:** W6 — Gemini Credential + L1 AI Animation Planning  
**W6 status:** CONTRACT_LOCKED / W6-001 READY  
**Previous W5 status:** PASS_WITH_PROVISIONAL_MIC_HARDWARE

## Read first

Follow `AGENTS.md` and `docs/SOURCE_OF_TRUTH_INDEX.md`.

Read in particular:
- frozen Master Blueprint and Product Definition;
- ADR-008 / ADR-009 architecture planning;
- W5 closure evidence;
- `docs/project/W6_GEMINI_CREDENTIAL_L1_AI_CONTRACT.md`;
- W6 planning TXT + DOCX;
- PLAN/TASKS/PROJECT_STATUS.

## W6 is planning-locked, not implemented

Do not infer that Gemini, WinVault or AI apply is already coded.

W6 establishes:
- CredentialPort + AIProviderPort boundary;
- secure slots 1..100;
- L1 render-backed W4 effect allowlist;
- structured EditPlan + strict PlanVerifier;
- stale/lock/range/dry-run gates;
- explicit approval;
- one approved plan = one CommandBatch;
- async provider lifecycle;
- frozen UI-010..014 + UI-023;
- live-provider gate.

## Critical security boundaries

- raw keys never ProjectState;
- raw keys never repo/.angproj/settings/log/error/evidence/screenshot/CLI/URL;
- presentation never receives saved raw keys;
- prompt/context never contains credentials;
- bulk credential TXT must not be retained;
- failover may not be used to evade quota/provider policy;
- AI may not execute arbitrary commands or direct JSON/engine mutations.

## Next exact action

On owner `lanjutkan`, execute **S11-W6-001 only**:
- define canonical AI/credential application contracts;
- AIProviderPort;
- CredentialPort;
- EditPlan DTO/schema;
- typed provider/credential errors;
- architecture/unit tests.

Do not implement WinVault, make a live Gemini call, build W6 UI or apply an AI
plan in W6-001.
