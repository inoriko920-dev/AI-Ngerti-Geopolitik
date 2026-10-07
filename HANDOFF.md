# HANDOFF — AI NGERTI GEOPOLITIK

**Current phase:** SF-STEP 11  
**Current wave:** W6 — Gemini Credential + L1 AI Animation Planning  
**Last completed task:** S11-W6-007 — PASS  
**Accepted W6-007 implementation HEAD:** `70fa8cd6f800166176889068202ab53d03044b24`  
**Accepted W6-007 workflow:** `37609729091` — SUCCESS  
**Next exact task:** S11-W6-008 — Approval → CommandBatch → Undo/Redo  
**Previous W5 status:** PASS_WITH_PROVISIONAL_MIC_HARDWARE

## W6-007 implementation now available

Runtime:
- official `google-genai==2.28.0` is locked in `pyproject.toml` and `uv.lock`;
- `infrastructure/gemini_provider.py` implements `AIProviderPort`;
- `application/ai_jobs.py` owns the provider-agnostic background lifecycle.

Gemini adapter:
- uses the official async `client.aio.models.generate_content` path;
- requests JSON structured output with the locked W6 L1 EditPlan schema;
- Gemini credential is supplied only to the SDK client constructor;
- raw credential is never inserted into instruction/context/prompt, response DTO,
  job snapshot, evidence or error text;
- cancellation is best-effort and checked before/during/after provider work;
- bounded timeout maps to `NETWORK_TIMEOUT`;
- 401/403 → `INVALID_AUTH`;
- 429 → `RATE_LIMIT_OR_QUOTA`;
- timeout/transient 5xx class → `NETWORK_TIMEOUT`;
- malformed/unreadable provider response → `MALFORMED_RESPONSE`;
- raw provider exception details are not surfaced as safe UI messages.

Provider-agnostic lifecycle:
- states: QUEUED / RUNNING / SUCCESS / FAILED / CANCELLED;
- one background provider worker keeps network work off the caller/Qt GUI thread and
  serializes access to the mutable credential-health/failover state;
- reuses W6-004 `CredentialPoolService` rather than bypassing it;
- invalid auth may legally fail over to another enabled credential;
- network timeout may retry the same credential according to W6-004 policy;
- quota/rate-limit records provider cooldown and does not rotate around policy;
- project/session/revision token is captured at submit time;
- stale project revision/session is rejected before a verified result is released;
- verified result can be consumed only once;
- no CommandBus apply or canonical mutation exists in W6-007.

## Tests/evidence

Targeted W6-007 tests: **17/17 PASS**.  
Full pytest: **PASS**.  
Evidence verifier: **11/11 PASS**.  
Official google-genai runtime smoke: **PASS**.  
Workflow: `37609729091` — **SUCCESS**.

Artifact:
- `ANG-S11-W6-007-Gemini-Async-Lifecycle`;
- ID `11477281563`;
- size 373 bytes;
- SHA-256 `46205199699c9a01eb099e664196a14e63d077e17e6cee80da45025e129528e9`.

## Regression lock on accepted W6-007 implementation HEAD

All SUCCESS, attempt 1:
- W6-007 `37609729091`
- W6-006 `37609729078`
- W6-005 `37609729100`
- W6-004 `37609729302`
- W6-003 `37609729109`
- W6-002 `37609729276`
- W6-001 `37609729237`
- W5-010 `37609729164`
- W5-009 `37609729309`
- W5-008 `37609729138`
- W5-007 `37609729331`
- W5-006 `37609729173`
- W5-005 `37609729188`
- W5-004 `37609729203`
- W4 `37609729175`
- W3 `37609729338`
- W2 `37609729334`
- W1 `37609729301`
- W0 `37609729217`
- S10 `37609729234`
- S09 `37609729182`
- S08 `37609729148`.

## Live Gemini qualification status

W6-007 proves the official SDK adapter/runtime and deterministic provider lifecycle.
It deliberately performs **no real Gemini network request in evidence** and therefore
does not claim live-provider qualification. Real live-provider qualification remains
the W6-010 gate.

## Critical boundaries for W6-008

- only a W6-006/W6-007 verified, non-stale result may enter approval;
- PLAN/APPROVAL is mandatory before canonical mutation;
- Cancel/reject = zero mutation;
- stale revision must be checked again immediately before apply;
- one approved plan must become exactly one atomic CommandBatch/history entry;
- commands must use the existing legal manual command path;
- Undo must restore the exact before-state; Redo must restore exact applied state;
- duplicate consumption/apply must fail safely;
- no W6 UI implementation yet;
- no live Gemini closure yet.

## Next exact action

After owner says `lanjutkan`, execute **S11-W6-008 only — Approval → CommandBatch → Undo/Redo**.
