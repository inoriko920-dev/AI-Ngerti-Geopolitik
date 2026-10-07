# S11 W6-002 — Secure Credential Slots 1–100

**Status:** PASS  
**Accepted implementation HEAD:** `7a3f3551b9080347c64ab53cca0be4ee646c41ed`  
**Accepted workflow:** `37593139064` — SUCCESS  
**Artifact:** `ANG-S11-W6-002-Credential-Slots`  
**Artifact ID:** `11469631614`

## Scope

W6-002 implements logical credential-slot behavior and deterministic
credential separation only.

It intentionally does not implement:
- production Windows WinVault/keyring;
- credential health/failover;
- bulk TXT;
- Gemini SDK/network;
- W6 UI;
- ContextBuilder/PlanVerifier;
- AI plan apply.

## Non-secret metadata

Added `CredentialSlotMetadata`:
- slot reference;
- label;
- enabled state.

It exposes a fixed masked value:
`••••••••`.

Raw secret is not a metadata field.

Metadata validation rejects:
- empty label;
- label over 80 characters;
- control whitespace;
- a label containing the raw credential value when saved through
  CredentialSlotService.

## Ports

Added:
`CredentialMetadataPort`.

The secret and metadata boundaries remain separate:
- CredentialPort owns raw secret operations;
- CredentialMetadataPort owns non-secret metadata.

## CredentialSlotService

Added:
`application/credential_slots.py`.

Operations:
- add/update;
- get;
- sorted list;
- fixed mask;
- enable/disable;
- delete.

Consistency:
- candidate metadata is validated before secret storage;
- update preserves existing enabled state;
- enable/disable mutates metadata only;
- coordinated write failure restores previous secret/metadata;
- delete removes secret + metadata consistently;
- delete rollback restores prior state on storage failure.

The service never returns a stored raw secret.

## Deterministic qualification backend

Added:
`infrastructure/in_memory_credentials.py`.

`InMemoryCredentialStore` implements:
- CredentialPort;
- CredentialMetadataPort.

It is explicitly a qualification/test fake, not the production Windows secure
store.

Its repr lists slot IDs only.

## Secret-separation proof

Runtime evidence proves:
- slot 1 accepted;
- slot 100 accepted;
- slot 0 rejected;
- slot 101 rejected;
- update works;
- slot 100 can be disabled without changing its secret;
- fixed mask is used;
- service can be reconstructed over the same deterministic backend;
- delete removes secret and metadata;
- raw secret cannot be copied into metadata label;
- raw credential is absent from ProjectState semantic JSON;
- raw credential is absent from saved .angproj;
- raw credential is absent from safe diagnostic output.

W6-002 does not mutate ProjectState.

## Tests/gates

Target:
`tests/unit/test_step11_w6_002_credential_slots.py`

Targeted result:
**9/9 PASS**.

Workflow:
`37593139064` — SUCCESS.

Quality:
- Ruff format PASS;
- Ruff check PASS;
- mypy PASS — 55 source files;
- import contracts PASS;
- architecture PASS;
- source-of-truth 70/70 PASS;
- no-secret scan PASS;
- frozen UI references 42/42 PASS;
- full pytest PASS;
- evidence verifier **5/5 PASS**.

## Artifact

- name: `ANG-S11-W6-002-Credential-Slots`;
- ID: `11469631614`;
- size: 1,677 bytes.

Artifact content is intentionally tiny and contains only safe metadata,
diagnostics and a credential-free project file.

## Regression lock

All SUCCESS on the accepted W6-002 implementation HEAD:
- W6-001: `37593138955`;
- W5-010: `37593138805`;
- W5-009: `37593138857`;
- W5-008: `37593139330`;
- W5-007: `37593139227`;
- W5-006: `37593139195`;
- W5-005: `37593138944`;
- W5-004: `37593139165`;
- W4: `37593138895`;
- W3: `37593138967`;
- W2: `37593139072`;
- W1: `37593139158`;
- W0: `37593139078`;
- S10: `37593138946`;
- S09: `37593139140`;
- S08: `37593139151`.

## Next

**S11-W6-003 — Windows secure-store qualification only.**
