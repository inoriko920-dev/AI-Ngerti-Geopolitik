# S11 W7-001 — Canonical L2 Command Contracts + Capability Registry

**Status:** PASS  
**Accepted implementation HEAD:** `f301c10a16ba33e051ef97e9d166262b7fbac327`  
**Accepted workflow:** `37640973646` — SUCCESS  
**Artifact:** `ANG-S11-W7-001-L2-Contracts`  
**Artifact ID:** `11491927299`  
**Artifact size:** 788 bytes  
**Artifact SHA-256:** `2adab3d3e6a010134b820344d9609962634c0fd2f6846b65575d3d4394c9cc5f`

## Scope

W7-001 establishes the application-layer contract for bounded AI Auto Edit L2.
It does not implement context generation, provider parsing, semantic dry-run,
Gemini request changes, UI or canonical apply.

## Canonical implementation

Added:
`src/ai_ngerti_geopolitik/application/ai_l2_contracts.py`.

The module contains no provider, secure-store, Qt, filesystem, engine or
ProjectState mutation implementation.

## Schema/caps

- AutoEditPlan schema version: 2.
- Maximum selected/target clips represented by a plan: 20.
- Maximum commands: 40.
- Request ID + summary required.
- Base revision must be non-negative.
- Empty plans are rejected.

## Capability registry

Immutable registry contains exactly five commands:

1. `set_clip_effects`
   - family: effects;
   - manual owner: SetClipPropertiesCommand;
   - property owner: EffectProperties.
2. `set_clip_duration`
   - family: duration;
   - manual owner: SetClipDurationCommand;
   - ripple: application-owned.
3. `set_clip_speed`
   - family: speed;
   - manual owner: SetClipSpeedCommand;
   - property owner: SpeedProperties;
   - ripple: application-owned.
4. `set_clip_transform`
   - family: transform;
   - manual owner: SetClipPropertiesCommand;
   - property owner: VideoProperties.
5. `set_clip_transition`
   - family: transition;
   - manual owner: SetClipPropertiesCommand;
   - property owner: TransitionProperties.

Unknown/deferred capability lookup hard-rejects.

## Typed policy bounds

Duration:
- 50%..200% ratio helper;
- minimum ceil(fps/2).

Speed:
- 50%..200%.

Transform:
- position bounds derived from ± half canvas;
- uniform scale 50%..200%;
- rotation -150..+150 tenths;
- opacity 60%..100%;
- crop is not represented by the DTO.

Transition:
- presets exactly none/fade_black;
- none requires duration 0;
- fade_black requires positive duration;
- dynamic maximum helper = min(2×fps, floor(candidate duration/2)).

Effects:
- exact W6 render-qualified effect allowlist is reused;
- W6 EditPlan schema remains version 1.

## Structural plan guards

AutoEditPlan:
- rejects duplicate command family on the same target;
- rejects simultaneous duration + speed on one target;
- rejects more than 20 unique targets;
- rejects more than 40 commands;
- accepts different non-conflicting families on the same target.

Dynamic project-aware validation remains intentionally deferred to W7-004.

## Backward compatibility

W7-001 contains a fail-fast compatibility assertion proving:
- W6 EditPlan schema version remains 1;
- W6 L1 effect allowlist remains unchanged.

Existing W6 tests and workflows remain green on the accepted W7-001 HEAD.

## Targeted tests

Target:
`tests/unit/test_step11_w7_001_contracts.py`.

Result:
**27/27 PASS** including parameterized forbidden-capability and range cases.

Coverage includes:
- exact registry and manual owners;
- deferred/forbidden capability rejection;
- typed dynamic policy helpers;
- application-owned duration/speed ripple contract;
- narrow W7 speed bounds;
- transform field/range contract and no crop;
- transition allowlist;
- W6 effect carry-forward;
- duplicate-family and pacing conflict rejection;
- command/target caps;
- strict integer-safe root contract;
- W6 schema/behavior compatibility.

## Deterministic evidence

Evidence verifier:
**18/18 PASS**.

Evidence proves:
- W7 schema 2;
- W6 schema 1 unchanged;
- five exact command types;
- five-command mixed contract instance;
- 3 unique targets;
- 20/40 caps;
- duration bounds 30fps/120frames = 60..240;
- position bounds 1920×1080 = ±960/±540;
- transition max 30fps/300frames = 60;
- no provider network;
- no ContextBuilder;
- no v2 parser;
- no semantic verifier;
- no runtime UI change;
- no canonical apply.

## Quality gates

Workflow `37640973646`:
- uv lock PASS;
- frozen sync PASS;
- Ruff format PASS;
- Ruff check PASS;
- mypy PASS — 64 source files;
- import contracts PASS;
- architecture PASS;
- source-of-truth 70/70 PASS;
- no-secret PASS;
- UI references 42/42 SHA-256 PASS;
- targeted tests 27/27 PASS;
- full pytest PASS;
- deterministic evidence PASS;
- evidence verifier 18/18 PASS;
- artifact upload PASS.

## Regression lock

All **26/26 workflow families** SUCCESS on accepted W7-001 HEAD, all attempt 1:

- S08 `37640973805` — SUCCESS, attempt 1
- S09 `37640973698` — SUCCESS, attempt 1
- S10 `37640973647` — SUCCESS, attempt 1
- W0 `37640973806` — SUCCESS, attempt 1
- W1 `37640973835` — SUCCESS, attempt 1
- W2 `37640973588` — SUCCESS, attempt 1
- W3 `37640973773` — SUCCESS, attempt 1
- W4 `37640973619` — SUCCESS, attempt 1
- W5-004 `37640973670` — SUCCESS, attempt 1
- W5-005 `37640973919` — SUCCESS, attempt 1
- W5-006 `37640973802` — SUCCESS, attempt 1
- W5-007 `37640973568` — SUCCESS, attempt 1
- W5-008 `37640973613` — SUCCESS, attempt 1
- W5-009 `37640973679` — SUCCESS, attempt 1
- W5-010 `37640973632` — SUCCESS, attempt 1
- W6-001 `37640973651` — SUCCESS, attempt 1
- W6-002 `37640973863` — SUCCESS, attempt 1
- W6-003 `37640973743` — SUCCESS, attempt 1
- W6-004 `37640973815` — SUCCESS, attempt 1
- W6-005 `37640973798` — SUCCESS, attempt 1
- W6-006 `37640973589` — SUCCESS, attempt 1
- W6-007 `37640973736` — SUCCESS, attempt 1
- W6-008 `37640973799` — SUCCESS, attempt 1
- W6-009 `37640973775` — SUCCESS, attempt 1
- W6-010 `37640973721` — SUCCESS, attempt 1
- W7-001 `37640973646` — SUCCESS, attempt 1

S08 portable foundation build/smoke PASS.
S10 packaged real-media smoke PASS.
W0 MLT playback/seek/decode/render qualification PASS.

## Next

**S11-W7-002 — L2 ContextBuilder + selected-scope contract only.**
