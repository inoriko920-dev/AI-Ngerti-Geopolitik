# S11-W6 — GEMINI CREDENTIAL + L1 AI ANIMATION PLANNING CONTRACT

**Status:** CONTRACT_LOCKED / W6-001 PASS / W6-002 READY / W6-003..010 BLOCKED_BY_PREVIOUS_TASKS  
**Phase:** SF-STEP 11 — Feature Implementation Waves  
**Derived from:** Master Blueprint TECH-WAVE STEP 09 — Gemini credential + L1 AI  
**Previous wave:** W5 Subtitle + Narration — CLOSED / PASS_WITH_PROVISIONAL_MIC_HARDWARE

## 1. Why W6 is this wave

The frozen Master Blueprint implementation order places:
- TECH-WAVE STEP 08 — Subtitle + narration;
- TECH-WAVE STEP 09 — Gemini credential + L1 AI;
- TECH-WAVE STEP 10 — AI Auto Edit L2;
- TECH-WAVE STEP 11 — Validation/recovery/diagnostics hardening;
- TECH-WAVE STEP 12 — Export matrix.

W5 closed TECH-WAVE STEP 08. Therefore W6 is locked as **Gemini Credential + L1 AI Animation Planning**. Background workspace, Validation Center hardening, Export matrix and AI L2 are not W6.

## 2. Binding requirements

W6 is governed by:
- F-009 / FR-009 — Gemini produces a validated EditPlan; unknown command/target/value or stale revision must fail without partial mutation;
- FR-010 — AI uses only commands that are also legal in the manual/application command layer;
- F-015 / FR-015 — up to 100 Gemini credentials with secure storage and masking;
- AI-001 — manual editor remains fully usable without Gemini;
- AI-002 — structured plan, never direct ProjectState/JSON/engine mutation;
- AI-003 — command parity;
- AI-009 — Gemini is the only V1 provider;
- AI-010 — slots 1..100 are for legitimate resilience/operations, never quota circumvention;
- IO-006 — manual/TXT credential input followed by secure storage;
- ADR-008 — provider requests are background jobs with cancellation/progress/stale protection;
- ADR-009 — official google-genai family behind AIProviderPort and the chain ContextBuilder → provider → PlanVerifier → risk/approval → CommandBatch;
- frozen UI-010, UI-011, UI-012, UI-013, UI-014 and UI-023.

## 3. Canonical ownership and mutation

- ProjectState remains canonical project truth.
- Raw credential values are **never** ProjectState.
- AI output is an application-layer EditPlan DTO, not canonical project state.
- Provider response may not mutate project state.
- Only a PlanVerifier-approved and user-approved plan may become one CommandBatch.
- One approved AI plan = one atomic Undo/Redo history transaction.
- Cancel, invalid plan, stale plan, provider error or lock conflict = zero canonical mutation.
- Presentation emits semantic intents only.
- No AI-only mutation path is allowed.

## 4. L1 capability boundary

W6 L1 may propose only render-backed W4 animation/effect operations that already have a legal manual command equivalent.

Allowed effect names:
- Fade;
- Pop;
- Breathe;
- Stomp;
- Tumble;
- Tectonic;
- Rise;
- Pan;
- Drift;
- none, only where the existing command semantics support clearing the effect.

Rules:
- intensity must stay inside canonical bounds;
- stable canonical target IDs are mandatory;
- target locks must be honored;
- AI may never silently unlock a target.

Still unsupported:
- Wipe;
- Blur;
- Succession;
- Baseline;
- Neon;
- Scrapbook;
- Brush;
- Ink;
- Digital;
- Spray Paint;
- Sketch;
- Gradient.

W6 L1 must not change:
- title;
- subtitle;
- narration;
- output/project paths;
- credentials;
- render settings;
- project duration/pacing;
- transforms/pan/zoom;
- transitions as AI reasoning;
- arbitrary files.

No shell/code execution may be generated or executed from prompt/project content.

## 5. Credential contract

Credential slots are logical IDs **1..100**.

Production target:
- Windows Generic Credential / keyring WinVault-compatible secure storage.

Non-secret metadata may contain:
- slot_id;
- label;
- enabled;
- health category;
- last test/result category;
- bounded cooldown timestamp when needed.

Raw secret rules:
- raw key is stored only in the secure-store backend;
- presentation never receives a raw saved key;
- provider adapter/credential service may retrieve the raw key only immediately for a request/test;
- raw key is never written to .angproj, repo, settings JSON, evidence, screenshots, logs, exceptions, CLI arguments or URL query;
- raw key is never sent inside the Gemini prompt/context;
- UI never reveals the full key after submission.

Operations:
- add/update → secure store;
- delete → secure secret + metadata consistently removed;
- enable/disable → metadata only;
- test → returns typed health/result category without echoing secret;
- slot 0 or >100 → reject.

Bulk TXT may be enabled only after single-slot storage is stable:
- one key per line;
- trim;
- dedupe;
- hard max 100;
- source TXT not retained;
- preview/count only;
- no plaintext logging/history/project persistence.

Failover is bounded operational resilience only. It must not be designed or documented as quota/rate-limit circumvention.

## 6. Provider/error taxonomy

Typed categories:
- NO_CREDENTIAL;
- INVALID_AUTH;
- RATE_LIMIT_OR_QUOTA;
- NETWORK_TIMEOUT;
- MALFORMED_RESPONSE;
- SCHEMA_INVALID;
- SEMANTIC_INVALID;
- STALE_PLAN;
- LOCK_CONFLICT;
- ALL_SLOTS_UNAVAILABLE.

Behavior:
- provider failure never disables manual editing;
- invalid auth marks only the affected slot unhealthy/disabled until fixed;
- network retry is bounded;
- quota/cooldown handling follows provider policy;
- malformed/schema/semantic/stale/lock failures never partially mutate the project.

## 7. EditPlan contract

EditPlan must carry at minimum:
- schema_version;
- base_project_revision;
- request_id/job_id;
- human-readable summary;
- ordered command proposals.

PlanVerifier gates:
1. strict schema parse;
2. allowed root fields;
3. allowed command types;
4. target existence;
5. lock state;
6. supported capability/effect;
7. canonical range validation;
8. stale revision check;
9. dry-run against a candidate state;
10. approval before CommandBatch creation.

Unknown root/command/target/effect or out-of-range value = reject.

Stale revision is checked again immediately before apply.

## 8. ContextBuilder contract

Allowed bounded context:
- project title/global style summary;
- selected scope and stable target IDs;
- media aspect/type metadata;
- current effect/intensity/lock;
- bounded neighboring summary where necessary;
- supported-effect enum and ranges;
- current project revision;
- bounded subtitle/narration timing summary only if directly relevant.

Forbidden:
- API keys;
- credential secrets;
- arbitrary filesystem listing;
- unrestricted file contents;
- engine objects;
- private logs;
- source media bytes.

Project/prompt text is untrusted data and may not override application policy.

## 9. Async/job lifecycle

Gemini network work must not run on the Qt GUI thread.

Lifecycle:
- QUEUED;
- RUNNING;
- SUCCESS;
- FAILED;
- CANCELLED.

Required:
- structured progress/status;
- best-effort cancellation;
- project/session/revision token;
- stale-result rejection;
- duplicate-apply guard;
- provider failures isolated from manual editor availability.

If W6 introduces a reusable job abstraction, it must be canonical and provider-agnostic, not a Gemini-specific second owner.

## 10. Frozen UI contract

W6 implements real PySide6 widgets matching frozen AAVC surfaces:
- UI-010 — AI Director / AI Otomatis;
- UI-011 — AI Agent Ready / Chat;
- UI-012 — AI Agent Plan;
- UI-013 — AI Agent Applied;
- UI-014 — Provider unavailable;
- UI-023 — Provider & API Key Manager.

Required states:
- READY;
- PLAN;
- APPROVAL;
- APPLYING;
- SUCCESS;
- PROVIDER_ERROR;
- LOCK_CONFLICT;
- STALE.

UI rules:
- only L1 capabilities may be claimed;
- provider unavailable states distinguish no key, invalid key, quota/rate limit and network/provider failure where known;
- manual fallback remains visible;
- API keys are masked and never revealed after save;
- screenshot-as-runtime UI is forbidden.

## 11. Live Gemini qualification gate

Fake provider tests are mandatory for deterministic CI, but are **not** proof of live Gemini operation.

Full W6 PASS requires:
- at least one real request through the official Gemini adapter;
- credential supplied through secure store on Windows;
- a valid L1 plan returned and validated/applied;
- raw secret absent from logs/evidence.

If a live credential is unavailable, W6 may close only as:
**PASS_WITH_PROVISIONAL_LIVE_GEMINI**.

Never fake full live-provider PASS.

## 12. Serial task contract

1. **S11-W6-001 — Canonical AI + credential contracts**
   - AIProviderPort;
   - CredentialPort;
   - EditPlan DTO/schema;
   - typed provider/credential errors;
   - no concrete Gemini/keyring imports outside infrastructure;
   - unit + architecture tests.

2. **S11-W6-002 — Secure credential slots 1–100**
   - logical slot model;
   - metadata;
   - add/update/delete/enable/disable/mask;
   - deterministic in-memory fake secure store tests;
   - no secret in ProjectState/persistence/log.

3. **S11-W6-003 — Windows secure-store qualification**
   - WinVault/keyring adapter;
   - slot 1 and 100;
   - delete/reopen;
   - failure behavior;
   - real Windows secure-store smoke required for full credential PASS.

4. **S11-W6-004 — Credential pool health + safe failover**
   - health/test states;
   - invalid auth;
   - network retry;
   - quota/cooldown;
   - all-unavailable;
   - bounded legal failover;
   - bulk TXT only after single-slot path is stable.

5. **S11-W6-005 — L1 ContextBuilder + allowlist**
   - bounded context;
   - no secrets;
   - supported W4 effect enum only;
   - lock/stable target representation;
   - untrusted-text isolation.

6. **S11-W6-006 — EditPlan schema + PlanVerifier**
   - strict structured parser;
   - unknown fields/commands/targets/effects rejected;
   - range/lock/capability/stale/dry-run gates;
   - zero mutation on invalid plan.

7. **S11-W6-007 — Gemini adapter + async lifecycle**
   - official google-genai family behind AIProviderPort;
   - network work off GUI thread;
   - timeout/cancel/error mapping;
   - deterministic fake-provider integration tests.

8. **S11-W6-008 — Approval → CommandBatch → Undo/Redo**
   - PLAN/APPROVAL required;
   - one approved plan = one atomic transaction;
   - Cancel = no mutation;
   - stale check immediately before apply;
   - exact Undo/Redo.

9. **S11-W6-009 — Frozen UI parity**
   - UI-010/011/012/013/014/023;
   - semantic intents;
   - only L1 claims;
   - credential masking;
   - provider fallback states;
   - screenshot parity evidence.

10. **S11-W6-010 — Live Gemini + failure + regression closure**
    - real Gemini smoke if a credential is available;
    - valid L1 + invalid/stale/provider failure evidence;
    - no-secret scan;
    - full regressions;
    - without live credential final status may only be PASS_WITH_PROVISIONAL_LIVE_GEMINI.

Every task must close PASS (or its explicit provisional hardware/provider gate) before the next task starts.

## 13. W6 non-scope

- AI L2 pacing/duration/transform/pan/zoom/transition reasoning;
- Validation Center/relink/recovery hardening;
- export matrix H.264/H.265/1440p/4K/60fps;
- legacy importer;
- providers other than Gemini;
- generative image/video;
- AI subtitle rewriting;
- ASR/speech alignment;
- arbitrary background/video tracks;
- auto-unlock;
- raw credential reveal/export.

## 14. Test/evidence matrix

Must include:
- slot 1 and 100 valid, 0/101 invalid;
- secure add/test/delete/reopen;
- no raw secret in repo/.angproj/settings/log/errors/screenshots/evidence;
- masked UI;
- bulk TXT trim/dedupe/max100/no retention if enabled;
- invalid auth, quota/rate-limit, timeout, malformed response, all-unavailable;
- unknown plan command/field/target/effect rejection;
- lock conflict and range rejection;
- stale result after revision change;
- cancel request/plan = zero mutation;
- one approved plan = one Undo entry, exact Undo/Redo;
- render proof that an L1-selected qualified effect actually appears;
- UI-010..014/UI-023 actual-vs-frozen evidence;
- GUI responsiveness/background network job;
- full quality/architecture/security/source-of-truth/UI regressions;
- W5/W4/W3/W2/W1/W0/S10/S09/S08 remain green.

## 15. Security red lines

Never:
- commit an API key;
- write raw keys to project/settings/evidence/screenshots/logs/errors/CLI args/URLs/test fixtures;
- echo a key after save;
- place a key in prompt/context;
- retain credential source TXT after import;
- use rotation to evade quotas/provider policy;
- execute arbitrary AI command types;
- allow direct AI JSON/engine mutation.

## 16. Gate before W6 coding

Before W6-001:
- this contract MD must be committed;
- detailed planning DOCX and TXT mirror must be committed/readable;
- TASKS / PLAN / PROJECT_STATUS / HANDOFF / SOURCE_OF_TRUTH_INDEX updated;
- W5 closure remains unchanged;
- frozen UI reference integrity remains intact;
- no provider beyond Gemini added;
- owner says **lanjutkan**.

## 17. Implementation progress

### S11-W6-001 — PASS

Accepted implementation HEAD:
`160a320768e4d4b788bc9e2bc9e4174569a32f31`

Accepted workflow:
`37591531616` — SUCCESS.

Evidence:
`docs/evidence/features/S11_W6_001_AI_CREDENTIAL_CONTRACTS.md`.

Implemented contract surface:
- AIProviderPort;
- CredentialPort;
- CredentialSecret;
- CredentialSlotRef 1..100;
- AIProviderRequest / ProviderPlanResponse;
- EditPlan / EffectEditProposal;
- typed credential/provider/plan errors;
- provider-agnostic job lifecycle.

W6-001 intentionally does not include:
- WinVault/keyring backend;
- credential metadata CRUD service;
- credential health/failover;
- Gemini SDK/network;
- ContextBuilder;
- PlanVerifier;
- approval/apply;
- W6 UI.

Quality:
- targeted tests 10/10 PASS;
- full pytest PASS;
- architecture/security/source-of-truth/UI gates PASS;
- W5 through S08 regression matrix green on the same implementation HEAD.

## Exact next action

On the next owner **lanjutkan**, execute **S11-W6-002 only — Secure credential slots 1–100**.

Do not create the production Windows secure-store adapter, make a Gemini network
call, implement failover, W6 UI or apply an AI EditPlan in W6-002.
