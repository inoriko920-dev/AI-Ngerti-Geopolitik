# S11 W6-001 — Canonical AI + Credential Contracts

**Status:** PASS  
**Accepted implementation HEAD:** `160a320768e4d4b788bc9e2bc9e4174569a32f31`  
**Accepted workflow:** `37591531616` — SUCCESS

## Scope

W6-001 establishes application-layer contracts only.

It intentionally does not implement:
- Windows secure-store/keyring;
- credential metadata service;
- Gemini SDK/network;
- health/failover;
- ContextBuilder;
- PlanVerifier;
- approval/apply;
- W6 UI.

## Canonical contract objects

Added:
`src/ai_ngerti_geopolitik/application/ai_contracts.py`.

Contracts:
- `CredentialSecret`;
- `CredentialSlotRef`;
- `CredentialErrorCode`;
- `ProviderErrorCode`;
- `PlanErrorCode`;
- `AIJobState`;
- `AIProviderRequest`;
- `ProviderPlanResponse`;
- `EffectEditProposal`;
- `EditPlan`.

Ports added to:
`src/ai_ngerti_geopolitik/application/ports.py`:
- `CredentialPort`;
- `AIProviderPort`.

## Credential boundary

`CredentialSlotRef`:
- slot 1 accepted;
- slot 100 accepted;
- 0/101/negative rejected.

`CredentialSecret`:
- trims input;
- empty secret rejected;
- `str(secret)` => masked;
- `repr(secret)` => masked;
- raw secret requires explicit `reveal()`.

The secret wrapper is transient application data, not ProjectState.

`CredentialPort` defines only the secure-storage boundary:
- store_secret;
- load_secret;
- delete_secret;
- has_secret.

W6-002 owns logical metadata/service behavior.
W6-003 owns the production Windows secure-store adapter.

## Provider boundary

`AIProviderPort.request_plan(...)` accepts:
- sanitized `AIProviderRequest`;
- transient `CredentialSecret`;
- optional cancellation token.

The request DTO itself contains only:
- request_id;
- base_project_revision;
- instruction;
- context_json.

It deliberately has no:
- credential;
- api_key;
- secret.

No provider implementation exists yet.

## EditPlan boundary

EditPlan schema version:
**1**.

Required:
- base project revision;
- request ID;
- human summary;
- ordered L1 effect proposals.

`EffectEditProposal` can express only:
- stable target clip ID;
- enter effect;
- exit effect;
- intensity;
- fixed command type `set_clip_effects`.

It cannot express:
- lock mutation;
- title;
- subtitle;
- narration;
- timeline start/duration;
- transforms;
- render settings;
- files;
- credentials;
- arbitrary command/shell execution.

## L1 allowlist

Locked exactly to the current render-qualified W4 effect set:
- None;
- Fade;
- Pop;
- Breathe;
- Stomp;
- Tumble;
- Tectonic;
- Rise;
- Pan;
- Drift.

Unsupported legacy effect values are rejected at contract construction.

Intensity:
0..200 inclusive.

## Typed errors

Credential:
- NO_CREDENTIAL;
- INVALID_SLOT;
- ALL_SLOTS_UNAVAILABLE.

Provider:
- INVALID_AUTH;
- RATE_LIMIT_OR_QUOTA;
- NETWORK_TIMEOUT;
- MALFORMED_RESPONSE.

Plan:
- SCHEMA_INVALID;
- SEMANTIC_INVALID;
- STALE_PLAN;
- LOCK_CONFLICT.

Provider-agnostic job lifecycle:
- QUEUED;
- RUNNING;
- SUCCESS;
- FAILED;
- CANCELLED.

## Tests

Target:
`tests/unit/test_step11_w6_001_contracts.py`.

Result:
**10/10 PASS**.

Coverage proves:
1. slot 1/100 allowed, invalid slots rejected;
2. secret string representations are masked;
3. CredentialPort/AIProviderPort are runtime-checkable and provider-agnostic;
4. L1 allowlist matches render-qualified W4 effects;
5. proposal shape cannot encode lock/title/timeline/arbitrary command;
6. target/change/intensity validation;
7. revision-bound EditPlan schema;
8. provider request has no credential field;
9. typed error taxonomy/job lifecycle;
10. malformed empty provider response rejected.

## Quality gates

Workflow `37591531616`:
- Ruff format PASS;
- Ruff check PASS;
- mypy PASS — 53 source files;
- import contracts PASS;
- architecture PASS;
- source-of-truth 70/70 PASS;
- no-secret scan PASS;
- UI reference integrity 42/42 PASS;
- targeted W6-001 tests PASS;
- full pytest PASS.

## Regression lock

On accepted W6-001 implementation HEAD:
- W5-010: `37591531601` — SUCCESS;
- W5-009: `37591531521` — SUCCESS;
- W5-008: `37591531560` — SUCCESS;
- W5-007: `37591531572` — SUCCESS;
- W5-006: `37591531512` — SUCCESS;
- W5-005: `37591531539` — SUCCESS;
- W5-004: `37591531600` — SUCCESS;
- W4: `37591531556` — SUCCESS;
- W3: `37591531593` — SUCCESS;
- W2: `37591531584` — SUCCESS;
- W1: `37591531540` — SUCCESS;
- W0: `37591531542` — SUCCESS;
- S10: `37591531550` — SUCCESS on attempt 2;
- S09: `37591531497` — SUCCESS;
- S08: `37591531604` — SUCCESS.

S10 attempt 1 failed because Chocolatey returned HTTP 504 resolving FFmpeg.
The same failed job was retried unchanged and passed. No product-code change
was made for that external package-feed failure.

## Next

**S11-W6-002 — Secure credential slots 1–100 only.**
