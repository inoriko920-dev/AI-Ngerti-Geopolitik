# S11 W6-007 — Gemini Adapter + Async Lifecycle

**Status:** PASS  
**Accepted implementation HEAD:** `70fa8cd6f800166176889068202ab53d03044b24`  
**Accepted workflow:** `37609729091` — SUCCESS  
**Artifact:** `ANG-S11-W6-007-Gemini-Async-Lifecycle`  
**Artifact ID:** `11477281563`  
**Artifact size:** 373 bytes  
**Artifact SHA-256:** `46205199699c9a01eb099e664196a14e63d077e17e6cee80da45025e129528e9`

## Scope

W6-007 implements the official Gemini adapter and provider-agnostic asynchronous
job lifecycle.

It intentionally does not implement:
- approval/apply;
- CommandBatch/Undo/Redo integration;
- W6 UI;
- live Gemini qualification/closure.

## Official SDK/runtime

Project runtime now locks:
`google-genai==2.28.0`.

The Windows workflow verifies:
- installed package version;
- `google.genai.Client`;
- official `errors.APIError`;
- structured JSON response configuration.

No live API credential is used by deterministic W6-007 evidence.

## GeminiAIProvider

File:
`src/ai_ngerti_geopolitik/infrastructure/gemini_provider.py`.

Properties:
- implements `AIProviderPort`;
- uses official async client path;
- response MIME type is application/json;
- response schema is the W6 L1 EditPlan surface;
- schema permits only set_clip_effects and render-qualified W4 effects;
- credential is passed only into SDK client construction;
- prompt/context never includes the credential;
- project/user context is explicitly treated as untrusted;
- cancellation polling is supported;
- timeout is bounded;
- provider exceptions are mapped to safe typed application errors.

Error mapping:
- 401/403 → INVALID_AUTH;
- 429 → RATE_LIMIT_OR_QUOTA;
- timeout/408/transient 5xx → NETWORK_TIMEOUT;
- other rejected/malformed/unreadable response → MALFORMED_RESPONSE.

## AIPlanJobService

File:
`src/ai_ngerti_geopolitik/application/ai_jobs.py`.

Lifecycle:
- QUEUED;
- RUNNING;
- SUCCESS;
- FAILED;
- CANCELLED.

Safety:
- provider call executes in a dedicated background worker;
- worker is provider-agnostic and does not import Gemini or Qt;
- one serialized provider worker avoids concurrent credential-health mutation;
- W6-004 CredentialPoolService supplies transient credentials;
- invalid auth/network timeout reuse bounded failover behavior;
- quota/rate-limit records cooldown and never rotates around provider policy;
- project/session/base-revision token is captured;
- cancellation produces no verified result;
- stale project revision/session cannot release a result;
- result may be consumed only once;
- provider response still passes W6-006 PlanVerifier;
- no CommandBus execution occurs.

## Deterministic targeted tests

Target:
`tests/unit/test_step11_w6_007_gemini_jobs.py`.

Result:
**17/17 PASS**.

Coverage:
- official SDK structured-output types;
- async adapter request shape;
- credential absent from prompt/config;
- preflight cancellation;
- timeout mapping;
- 401/403/429/503/400 mapping;
- empty response rejection;
- provider work off caller thread;
- invalid-auth failover;
- same-slot network retry;
- quota no-rotation;
- active cancellation;
- stale revision/session rejection;
- one-time verified-result consumption;
- malformed plan failure;
- zero canonical mutation.

## Deterministic evidence

Evidence deliberately uses an in-memory fake provider, not the live Gemini network.

Proof:
- provider runs off caller thread;
- terminal state SUCCESS;
- one provider call;
- one verified L1 command;
- candidate revision preserved;
- canonical ProjectState unchanged;
- credential absent from job snapshot;
- no approval/apply;
- no W6 UI.

Evidence verifier:
**11/11 PASS**.

## Quality gates

Workflow `37609729091`:
- uv lock check PASS;
- frozen dependency sync PASS;
- Ruff format PASS;
- Ruff check PASS;
- mypy PASS;
- import contracts PASS;
- architecture PASS;
- source-of-truth PASS;
- no-secret scan PASS;
- UI-reference integrity PASS;
- official google-genai runtime smoke PASS;
- targeted W6-007 tests 17/17 PASS;
- full pytest PASS;
- deterministic evidence PASS;
- evidence verifier 11/11 PASS;
- artifact upload PASS.

## Regression lock

All SUCCESS on accepted W6-007 implementation HEAD, all attempt 1:
- W6-006 `37609729078`;
- W6-005 `37609729100`;
- W6-004 `37609729302`;
- W6-003 `37609729109`;
- W6-002 `37609729276`;
- W6-001 `37609729237`;
- W5-010 `37609729164`;
- W5-009 `37609729309`;
- W5-008 `37609729138`;
- W5-007 `37609729331`;
- W5-006 `37609729173`;
- W5-005 `37609729188`;
- W5-004 `37609729203`;
- W4 `37609729175`;
- W3 `37609729338`;
- W2 `37609729334`;
- W1 `37609729301`;
- W0 `37609729217`;
- S10 `37609729234`;
- S09 `37609729182`;
- S08 `37609729148`.

S08 portable foundation build and smoke also PASS with the new google-genai
dependency graph.

## Live Gemini boundary

This task proves the official adapter/runtime and deterministic lifecycle only.
No live provider request is claimed here. W6-010 remains the live Gemini
qualification gate.

## Next

**S11-W6-008 — Approval → CommandBatch → Undo/Redo only.**
