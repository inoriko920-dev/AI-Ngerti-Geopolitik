# S11 W6-003 — Windows Secure-Store Qualification

**Status:** PASS  
**Accepted implementation HEAD:** `84e8ef7ce30be24875c37faaa8dd94ab9a6d3c7f`  
**Accepted workflow:** `37594820105` — SUCCESS  
**Artifact:** `ANG-S11-W6-003-Windows-Secure-Store`  
**Artifact ID:** `11470101865`

## Scope

W6-003 implements and qualifies the production Windows secret-storage boundary
only.

It does not implement:
- credential health/failover;
- bulk TXT import;
- Gemini SDK/network;
- ContextBuilder;
- PlanVerifier;
- W6 UI;
- AI plan apply.

## Production adapter

Added:
`src/ai_ngerti_geopolitik/infrastructure/windows_credentials.py`.

`WindowsCredentialStore` implements the application CredentialPort using the
native Windows Credential Manager Generic Credential APIs:
- `CredWriteW`;
- `CredReadW`;
- `CredDeleteW`;
- `CredFree`.

No additional plaintext credential dependency is introduced.

## Secret handling

- logical slots remain 1..100 through CredentialSlotRef;
- target names contain only namespace + slot ID;
- raw secret is encoded only for the native write boundary;
- native write buffer is zeroed after the call;
- adapter repr contains namespace only;
- raw saved credential is returned only as transient CredentialSecret;
- native errors never include the raw secret.

Missing credential maps to:
- CredentialContractError;
- code NO_CREDENTIAL;
- safe message only.

Other native failures map to:
- WindowsCredentialStoreError;
- operation + numeric Windows error code only.

## Real Windows secure-store smoke

The accepted GitHub Windows runner performed a real Windows Credential Manager
smoke with runtime-generated secrets.

Proven:
- slot 1 store/load round-trip;
- slot 100 store/load round-trip;
- fresh WindowsCredentialStore instance reopens slot 1;
- fresh WindowsCredentialStore instance reopens slot 100;
- fixed mask remains `••••••••`;
- delete removes slot 1 secure secret + metadata;
- delete removes slot 100 secure secret + metadata;
- load after delete is safely rejected;
- all smoke targets are removed during cleanup.

The generated secret values are never written into evidence.

## Deterministic tests

Target:
`tests/unit/test_step11_w6_003_windows_secure_store.py`

Coverage:
- slot 1/100 shared-backend round trip/reopen;
- idempotent delete;
- typed missing credential;
- safe write/read/delete native failures;
- invalid slot rejection before backend access;
- native constructor platform boundary.

Result:
**7/7 PASS**.

## Quality gates

Workflow `37594820105`:
- Ruff format PASS;
- Ruff check PASS;
- mypy PASS — 56 source files;
- import contracts PASS;
- architecture PASS;
- source-of-truth 70/70 PASS;
- no-secret scan PASS;
- UI reference integrity 42/42 PASS;
- targeted W6-003 tests 7/7 PASS;
- full pytest PASS;
- real Windows secure-store smoke PASS;
- evidence verifier 4/4 PASS.

## Artifact

- name: `ANG-S11-W6-003-Windows-Secure-Store`;
- ID: `11470101865`;
- size: 1,377 bytes.

The artifact intentionally contains safe boolean/slot/backend diagnostics only.
No credential value is present.

## Regression lock

All SUCCESS on accepted W6-003 HEAD:
- W6-002: `37594819993`;
- W6-001: `37594820046`;
- W5-010: `37594820121`;
- W5-009: `37594819998`;
- W5-008: `37594820079`;
- W5-007: `37594820065`;
- W5-006: `37594820058`;
- W5-005: `37594820034`;
- W5-004: `37594820142`;
- W4: `37594820038`;
- W3: `37594820204`;
- W2: `37594820090`;
- W1: `37594820078`;
- W0: `37594820018`;
- S10: `37594819996`;
- S09: `37594820042`;
- S08: `37594819997`.

## Next

**S11-W6-004 — Credential health + safe failover only.**
