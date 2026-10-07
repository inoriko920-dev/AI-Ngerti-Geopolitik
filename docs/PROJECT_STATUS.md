# PROJECT STATUS — AI NGERTI GEOPOLITIK

**Current STEP:** SF-STEP 11 — Feature Implementation Waves  
**Current wave:** **W6 — Gemini Credential + L1 AI Animation Planning**  
**W6 status:** **CONTRACT_LOCKED / W6-001..007 PASS / W6-008 READY**  
**Previous wave:** W5 — CLOSED / PASS_WITH_PROVISIONAL_MIC_HARDWARE  
**Accepted W6-007 implementation HEAD:** `70fa8cd6f800166176889068202ab53d03044b24`  
**Accepted W6-007 workflow:** `37609729091` — SUCCESS  
**Next exact task:** **S11-W6-008 — Approval → CommandBatch → Undo/Redo**

## W6-007 proven

Official provider runtime:
- `google-genai==2.28.0` is frozen in project dependencies;
- official package imports and structured-output config are smoke-tested on Windows;
- Gemini adapter is infrastructure only and implements the inward `AIProviderPort`.

Provider request safety:
- official async SDK path is used inside the provider worker;
- response MIME type is `application/json`;
- W6 L1 EditPlan response JSON schema is supplied;
- credential is only handed to the SDK client constructor;
- credential is absent from provider prompt/context and job snapshots;
- user/project text is labelled untrusted and cannot expand policy.

Typed provider behavior:
- 401/403 → INVALID_AUTH;
- 429 → RATE_LIMIT_OR_QUOTA;
- timeout/transient provider failures → NETWORK_TIMEOUT;
- malformed/unreadable/unsupported provider responses → MALFORMED_RESPONSE;
- raw provider exception detail is not used as safe UI error text.

Async lifecycle:
- provider work runs in a dedicated background worker, never the calling/GUI thread;
- lifecycle states are QUEUED/RUNNING/SUCCESS/FAILED/CANCELLED;
- cancellation token is checked before, during and after provider work;
- W6-004 credential health/failover/cooldown is reused;
- provider work is serialized to avoid concurrent mutation of credential health state;
- job token binds project ID, session ID and base revision;
- stale project/session result is rejected on retrieval;
- successful verified result is one-consume only;
- provider success still passes through W6-006 PlanVerifier;
- no CommandBus apply/history mutation occurs.

## W6-007 gates

Workflow `37609729091`:
- uv frozen lock PASS;
- Ruff format PASS;
- Ruff check PASS;
- mypy PASS;
- import contracts PASS;
- architecture PASS;
- source-of-truth PASS;
- no-secret scan PASS;
- frozen UI reference integrity PASS;
- official google-genai runtime smoke PASS;
- targeted W6-007 tests **17/17 PASS**;
- full pytest PASS;
- deterministic evidence PASS;
- evidence verifier **11/11 PASS**.

Artifact:
- `ANG-S11-W6-007-Gemini-Async-Lifecycle`;
- ID `11477281563`;
- size 373 bytes;
- SHA-256 `46205199699c9a01eb099e664196a14e63d077e17e6cee80da45025e129528e9`.

## Regression lock on accepted W6-007 implementation HEAD

All SUCCESS, attempt 1:
- W6-007: `37609729091`;
- W6-006: `37609729078`;
- W6-005: `37609729100`;
- W6-004: `37609729302`;
- W6-003: `37609729109`;
- W6-002: `37609729276`;
- W6-001: `37609729237`;
- W5-010: `37609729164`;
- W5-009: `37609729309`;
- W5-008: `37609729138`;
- W5-007: `37609729331`;
- W5-006: `37609729173`;
- W5-005: `37609729188`;
- W5-004: `37609729203`;
- W4: `37609729175`;
- W3: `37609729338`;
- W2: `37609729334`;
- W1: `37609729301`;
- W0: `37609729217`;
- S10: `37609729234`;
- S09: `37609729182`;
- S08: `37609729148`.

## Live-provider qualifier

No real Gemini network request is claimed in W6-007 evidence. Official SDK/runtime
and deterministic adapter/lifecycle behavior are PASS. Real Gemini smoke remains a
W6-010 requirement.

## Exact next action

After owner says **lanjutkan**, execute **S11-W6-008 only**:
- approval boundary for verified plan;
- Cancel/reject = zero mutation;
- stale revision re-check immediately before apply;
- convert approved L1 proposals to existing canonical commands;
- one approved plan = one atomic CommandBatch/history entry;
- exact Undo/Redo and duplicate-apply protection.

Do not start W6 UI or live-provider closure in W6-008.
