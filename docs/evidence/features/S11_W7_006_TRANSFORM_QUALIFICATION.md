# S11-W7-006 — L2 TRANSFORM QUALIFICATION

**Status:** PASS  
**Accepted implementation HEAD:** `7ba2640068e5e5c0d153bd3c1bd304bc1be64f06`  
**Accepted workflow:** `37656965367` — SUCCESS  
**Artifact:** `ANG-S11-W7-006-L2-Transform`  
**Artifact ID:** `11498533256`  
**Artifact size:** 4,907,796 bytes  
**Artifact SHA-256:** `2fc4cf664eb677939c1620930b6b71c2f33b1fff9cd7c8cef164e084cde9e006`

## Scope

W7-006 qualifies the transform family already implemented by the W7-004
semantic verifier. It does not add a new mutation owner, provider profile,
runtime UI, approval/apply flow, transition work, or mixed-plan work.

## Canonical path reused

- `TransformEditProposal`;
- `AutoEditPlanVerifier`;
- canonical `SetClipPropertiesCommand`;
- existing `VideoProperties`;
- existing W3 `build_w3_filter_plan()`;
- existing FFmpeg qualification adapter.

No AI-only transform path exists.

## Qualified transform fields

Real-media proof covers:
- position X/Y;
- uniform scale;
- rotation;
- opacity;
- composite transform using all fields together.

Uniform scale translates to equal X/Y scale. Existing crop values and
unspecified transform fields remain preserved.

## Real-media evidence

At frame 30:
- baseline preview created;
- position preview differs from baseline;
- scale preview differs from baseline;
- rotation preview differs from baseline;
- opacity preview differs from baseline;
- composite preview differs from all other previews.

Composite transform export:
- 90 canonical frames;
- real FFmpeg export created and independently probed;
- audio retained;
- transform render path uses existing W3 filter plan.

## Safety

- candidate semantic hash matches W7-004 verifier proof;
- candidate revision remains unchanged;
- canonical ProjectState remains unchanged;
- CommandBus history remains unchanged;
- source media SHA-256 remains unchanged;
- provider profile unchanged;
- runtime UI unchanged;
- canonical AI apply not started;
- W7-007 transition + mixed-plan qualification not started.

## Gates

Workflow `37656965367` — SUCCESS:
- FFmpeg qualification toolchain PASS;
- uv lock/frozen sync PASS;
- Ruff format/check PASS;
- mypy PASS — 68 source files;
- import contracts PASS;
- architecture PASS;
- source-of-truth PASS;
- no-secret PASS;
- frozen UI references 42/42 PASS;
- targeted transform tests **5/5 PASS**;
- full pytest PASS;
- owned real-media fixture PASS;
- real transform evidence PASS;
- evidence verifier **9/9 files PASS**;
- artifact upload PASS.

## Regression lock

On accepted HEAD `7ba2640068e5e5c0d153bd3c1bd304bc1be64f06`:
- **28/28 triggered workflows SUCCESS**;
- every workflow succeeded on attempt 1;
- W7-006/W7-005/W7-004 PASS;
- W6 regression PASS;
- W5 regression PASS;
- W4/W3/W2/W1/W0 PASS;
- S10 packaged real-media PASS;
- S09 UI shell PASS;
- S08 portable build/smoke PASS.

## Next

**S11-W7-007 — Transition + mixed-plan qualification — READY.**

W7-008 and later tasks remain blocked by the serial contract.
