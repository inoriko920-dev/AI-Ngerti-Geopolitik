# S11-W7-004 — L2 SEMANTIC VERIFIER + SEQUENTIAL DRY-RUN TRANSLATOR

**Status:** PASS  
**Accepted implementation HEAD:** `05bbf416e3f4440b23b23a8912aa86e2d1a39d44`  
**Accepted workflow:** `37650364257` — SUCCESS  
**Artifact:** `ANG-S11-W7-004-L2-Verifier`  
**Artifact ID:** `11496527057`  
**Artifact size:** 515 bytes  
**Artifact SHA-256:** `d642dfefd5e68336aa585e959b9c7eb6fd44ba70b5f7387a9204436492d69739`

## Scope

W7-004 implements application-layer semantic verification and non-mutating
translation only.

It deliberately does not:
- change the Gemini request profile;
- change runtime UI;
- create an approval/apply path for W7;
- commit any CommandBus history;
- perform W7-005 real pacing/render qualification.

## Canonical owner

Added:
`src/ai_ngerti_geopolitik/application/ai_l2_verifier.py`.

Owner:
`AutoEditPlanVerifier`.

Proof:
`VerifiedAutoEditPlan`.

Proof fields include:
- AutoEditPlan v2;
- candidate semantic hash;
- candidate revision;
- command count;
- unique target count;
- selected-scope count;
- translated existing manual commands.

## Semantic gates

The verifier:
1. consumes the strict W7-003 parser output;
2. correlates provider request ID when verifying ProviderPlanResponse;
3. rejects stale base revision;
4. validates the selected scope against current ProjectState;
5. rejects targets outside selected scope;
6. defensively rechecks family uniqueness + duration/speed conflict;
7. requires target existence;
8. enforces track locks and effect locks;
9. enforces W7 dynamic policy;
10. constructs canonical value objects;
11. sequentially dry-runs the existing manual command path.

## Manual translation

- effects → `SetClipPropertiesCommand` + `EffectProperties`;
- duration → `SetClipDurationCommand(ripple=True)`;
- speed → `SetClipSpeedCommand(ripple=True)`;
- transform → `SetClipPropertiesCommand` + `VideoProperties`;
- transition → `SetClipPropertiesCommand` + `TransitionProperties`.

There is no AI-only ProjectState mutation command.

## Dynamic W7 policy proven

Duration:
- 50%..200% of current candidate duration;
- minimum half-second policy;
- source-media bound;
- exact frame representability;
- application-owned ripple.

Speed:
- 50%..200%;
- application-owned ripple.

Transform:
- X within ± half canvas width;
- Y within ± half canvas height;
- uniform scale becomes equal X/Y;
- current crop is preserved.

Transition:
- fade_black duration uses the current sequential candidate duration;
- pacing cannot leave an existing/proposed fade_black above the candidate maximum.

Effects:
- W6 render-qualified effect contract reused;
- unspecified effect fields preserved;
- effect lock cannot be overridden.

## Zero-mutation proof

- live ProjectState semantic JSON unchanged;
- revision unchanged;
- CommandBus undo/redo history unchanged;
- candidate semantic hash changes only on the local dry-run candidate.

## Tests/evidence

Targeted tests:
**24/24 PASS**.

Full pytest:
**PASS**.

Evidence verifier:
**23/23 PASS**.

Quality:
- Ruff format/check PASS;
- mypy PASS — 68 source files;
- import contracts PASS;
- architecture PASS;
- source-of-truth 70/70 PASS;
- no-secret PASS;
- UI references 42/42 PASS.

## Regression lock

All **26/26** workflows on the accepted implementation HEAD succeeded,
all attempt 1:

- W7-004 `37650364257`
- W6-010 `37650364420`
- W6-009 `37650363882`
- W6-008 `37650363780`
- W6-007 `37650364468`
- W6-006 `37650364252`
- W6-005 `37650364191`
- W6-004 `37650364167`
- W6-003 `37650363829`
- W6-002 `37650364246`
- W6-001 `37650364106`
- W5-010 `37650363642`
- W5-009 `37650364163`
- W5-008 `37650364495`
- W5-007 `37650364081`
- W5-006 `37650363887`
- W5-005 `37650364066`
- W5-004 `37650364126`
- W4 `37650363776`
- W3 `37650363963`
- W2 `37650363739`
- W1 `37650363821`
- W0 `37650364248`
- S10 `37650363929`
- S09 `37650363713`
- S08 `37650364274`

S08 portable build/smoke PASS.  
S09 portable UI shell PASS.  
S10 real-media/package PASS.  
W0 engine qualification PASS.

## Next

**S11-W7-005 — Pacing qualification: duration + speed only.**
