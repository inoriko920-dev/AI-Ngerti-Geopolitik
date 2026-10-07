# S11-W7-008 — GEMINI L2 REQUEST PROFILE + LIFECYCLE REUSE

**Status:** PASS  
**Accepted implementation HEAD:** `fa142e4d7eee21f79f79837339e76dfb974b8ba8`  
**Accepted workflow:** `37671042698` — SUCCESS  
**Artifact:** `ANG-S11-W7-008-Gemini-L2-Lifecycle`  
**Artifact ID:** `11505072385`  
**Artifact size:** 485 bytes  
**Artifact SHA-256:** `75207c3be32f8b967848719e48c3677de34e6608d063fe38121a6deb03f3be39`

## Scope

W7-008 extends the existing W6 provider boundary to Auto Edit L2 without
creating a second Gemini client, credential pool, background job service, or
provider error taxonomy.

The implementation keeps the frozen W6 `AIProviderRequest` dataclass field
contract unchanged. W7 introduces `L2AIProviderRequest` as a no-new-field
subclass that selects the L2 request profile while remaining compatible with
the existing `AIProviderPort`.

## Provider profile

The same `GeminiAIProvider` now resolves one of two bounded profiles:

- W6 L1 / `L1_EFFECTS`:
  - schema version 1;
  - effect-only command allowlist;
  - original W6 system instruction remains the default path.
- W7 L2 / `L2_AUTO_EDIT`:
  - canonical AutoEditPlan schema version 2;
  - exact five-command allowlist;
  - selected-scope-only policy;
  - application-owned ripple;
  - explicit rejection language for crop, reverse, crossfade/dissolve,
    structural edits, automatic unlock, title/subtitle/narration/audio/color/
    marker/export/credential/path mutation.

Both profiles:
- use the official `google-genai` adapter;
- use structured JSON output;
- never place the credential in prompt/context/config;
- share timeout/cancellation/error mapping.

## Shared lifecycle

The existing `AIPlanJobService` remains the only background provider lifecycle.

Backward-compatible generalization:
- L1 continues through the existing `PlanVerifier`;
- L2 dispatches through `AutoEditPlanVerifier + W7SelectedScope`;
- L1 results continue through `take_verified()`;
- L2 results use `take_verified_l2()`;
- the wrong result accessor fails safely without consuming the result;
- the same credential pool handles invalid-auth failover;
- cancellation, stale session/revision, provider errors and result-consumption
  semantics remain shared.

No W7-009 approval/apply logic was introduced.

## Deterministic evidence

A real shared background lifecycle run used:
- request profile: `L2_AUTO_EDIT`;
- two selected clips;
- six schema-v2 commands;
- one existing credential slot;
- one provider call on a background worker.

Evidence proves:
- job terminal state = SUCCESS;
- verified command count = 6;
- verified target count = 2;
- verified selected scope count = 2;
- candidate revision remains 28;
- candidate semantic hash is present;
- canonical ProjectState remains unchanged;
- credential value is absent from the safe snapshot;
- no second provider service or credential pool was created;
- runtime UI unchanged;
- canonical AI apply not started;
- W7-009 not started.

The deterministic evidence intentionally uses a provider double, not a real
Gemini network call. Live Gemini success is therefore not claimed.

## Backward compatibility

The W6 `AIProviderRequest` still exposes exactly its original four dataclass
fields:
- request_id;
- base_project_revision;
- instruction;
- context_json.

The W6 L1 Gemini schema remains version 1 and effect-only.
Existing W6 approval code continues to consume `take_verified()` as before.

## Gates

Workflow `37671042698` — SUCCESS:
- uv lock/frozen sync PASS;
- Ruff format/check PASS;
- mypy PASS — 68 source files;
- import contracts PASS — 4 kept / 0 broken;
- architecture PASS;
- source-of-truth PASS — 70/70 on implementation HEAD;
- no-secret PASS;
- frozen UI references 42/42 PASS;
- official google-genai runtime PASS — 2.28.0, async + structured output importable;
- targeted W7-008 tests **9/9 PASS**;
- full pytest **370/370 PASS**;
- deterministic lifecycle evidence PASS;
- evidence verifier **1/1 PASS**;
- artifact upload PASS.

## Regression lock

On accepted implementation HEAD `fa142e4d7eee21f79f79837339e76dfb974b8ba8`:
- **26/26 triggered workflow families SUCCESS**;
- all succeeded on attempt 1;
- S08 Windows portable foundation PASS;
- S09 UI shell PASS;
- S10 Windows E2E PASS;
- W0/W1/W2/W3/W4/W5/W6 and earlier W7 gates remain green.

## Next

**S11-W7-009 — Approval/apply/UI diff integration — READY.**

W7-010 remains blocked by the serial contract.
