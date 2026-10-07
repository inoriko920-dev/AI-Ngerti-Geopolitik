# S11 W6-004 — Credential Health + Safe Failover

**Status:** PASS  
**Accepted implementation HEAD:** `2ebe3fbd89e0cbbf62135a44bb2e4193c4906e32`  
**Accepted workflow:** `37602706734` — SUCCESS  
**Artifact:** `ANG-S11-W6-004-Credential-Health-Safe-Failover`  
**Artifact ID:** `11472879781`  
**Artifact size:** 775 bytes

## Scope

W6-004 implements credential health, bounded safe failover and the contracted
bulk TXT import boundary only.

It does not implement:
- ContextBuilder;
- PlanVerifier;
- Gemini SDK/network calls;
- W6 UI;
- AI plan approval/apply.

## Credential health

Added `application/credential_pool.py`.

Health categories:
- UNKNOWN;
- HEALTHY;
- INVALID_AUTH;
- NETWORK_DEGRADED;
- COOLDOWN.

Result categories:
- NEVER_TESTED;
- PASS;
- INVALID_AUTH;
- RATE_LIMIT_OR_QUOTA;
- NETWORK_TIMEOUT.

Invalid authentication disables only the affected logical slot. Other
configured slots are not silently disabled.

## Safe failover

`CredentialFailoverSession` is bounded per request.

Qualified behavior:
- network timeout retries the same slot only up to the configured bound;
- after that bound a different eligible slot may be selected;
- distinct slots per request are bounded;
- malformed/non-credential provider failures do not rotate credentials;
- no eligible slot returns typed `ALL_SLOTS_UNAVAILABLE`.

Rate/quota behavior is deliberately different from network failure:
- a bounded provider-wide cooldown is recorded;
- immediate selection of another credential is blocked while that cooldown is active;
- this prevents the credential pool from acting as quota/rate-limit circumvention.

No provider network request is made in W6-004. Provider outcomes are injected
into the provider-agnostic state machine by deterministic tests/evidence.

## Bulk TXT boundary

Single-slot secure storage was already proven by W6-002/W6-003, so W6-004
enables the contracted bulk path:
- trim blank/whitespace lines;
- deduplicate equal credentials;
- reject more than 100 unique credentials;
- count-only preview;
- check free-slot capacity before mutation;
- coordinated rollback if storage fails;
- do not retain source TXT;
- do not write raw values to logs/evidence/project state.

## Secret safety

- secrets remain behind `CredentialPort`;
- `CredentialLease.__repr__` is masked;
- health snapshots are non-secret;
- evidence uses runtime-generated credentials only;
- evidence is scanned after generation and rejects any raw secret occurrence;
- no Gemini prompt/context exists yet.

## Deterministic tests

Target:
`tests/unit/test_step11_w6_004_credential_pool.py`

Coverage:
- health transitions;
- success reset;
- invalid-auth slot isolation;
- bounded network retry then failover;
- provider cooldown for rate/quota;
- no immediate quota rotation;
- typed all-unavailable;
- bounded distinct-slot attempts;
- non-credential failure does not rotate;
- bulk TXT trim/dedupe/import;
- >100 unique rejection;
- capacity preflight.

Result:
**10/10 PASS**.

## Quality gates

Workflow `37602706734`:
- Ruff format PASS;
- Ruff check PASS;
- mypy PASS;
- import contracts PASS;
- architecture PASS;
- source-of-truth PASS;
- no-secret scan PASS;
- frozen UI reference integrity PASS;
- targeted W6-004 tests 10/10 PASS;
- full pytest PASS;
- deterministic evidence PASS;
- evidence verifier 18/18 PASS;
- artifact upload PASS.

## Regression lock

All SUCCESS on accepted W6-004 implementation HEAD:
- W6-003 `37602706876`;
- W6-002 `37602706766`;
- W6-001 `37602706721`;
- W5-010 `37602706804`;
- W5-009 `37602706750`;
- W5-008 `37602706894`;
- W5-007 `37602706907`;
- W5-006 `37602706764`;
- W5-005 `37602706936`;
- W5-004 `37602706756`;
- W4 `37602706703`;
- W3 `37602706733`;
- W2 `37602706702`;
- W1 `37602706775`;
- W0 `37602706791`;
- S10 `37602706802`;
- S09 `37602706884`;
- S08 `37602706767`.

## Next

**S11-W6-005 — L1 ContextBuilder + allowlist only.**
