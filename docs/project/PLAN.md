# PLAN — CURRENT IMPLEMENTATION PHASE

**SF-STEP 11 remains active. W5 is closed. W6 is CONTRACT_LOCKED. W6-001..006 PASS.**

## Accepted W6-006

Implementation:
`571cf941e64124628d1f8dadafb022eb20c0a541`

Workflow:
`37606369024` — SUCCESS.

Implemented:
- strict EditPlan JSON parsing with exact root/command schema;
- maximum 20 L1 commands;
- fixed `set_clip_effects` command allowlist;
- strict scalar types;
- target existence and selected-scope checks;
- effect/range validation;
- effect-lock + track-lock rejection;
- stale-revision rejection;
- ProviderPlanResponse/inner request ID correlation;
- W4 manual-command-parity dry-run on local candidate state;
- zero canonical mutation / zero CommandBus history.

Gates:
- targeted 12/12 PASS;
- full pytest PASS;
- evidence verifier 24/24 PASS;
- quality/architecture/security/source-of-truth/UI-reference PASS;
- full regression matrix SUCCESS on attempt 1.

## Active next task

**S11-W6-007 — Gemini adapter + async lifecycle**

Scope:
- official google-genai family behind AIProviderPort;
- asynchronous/background provider execution;
- structured lifecycle/progress;
- cancellation and timeout handling;
- typed provider error mapping;
- reuse W6-004 credential-pool health/failover/cooldown;
- stale-result protection token;
- deterministic fake-provider integration tests.

W6-007 must not:
- apply verified plans to CommandBus;
- create approval/Undo/Redo transactions;
- build W6 UI;
- implement AI L2;
- add another provider.

Do not begin W6-007 until owner says `lanjutkan`.
