# S11-W7-003 — STRICT AUTOEDITPLAN V2 PARSER / SCHEMA

**Status:** PASS  
**Accepted implementation HEAD:** `a57c8acd96cdcff8b20f659171229ad0bff913d0`  
**Accepted workflow:** `37647150710` — SUCCESS  
**Artifact:** `ANG-S11-W7-003-L2-Parser`  
**Artifact ID:** `11494393982`  
**Artifact size:** 1436 bytes  
**Artifact SHA-256:** `fe7542cad4dbac0af22df2cde72b78d7e3ee6c464f28fed617e76264e7863d9f`

## Scope

W7-003 implements structural parsing only:
- strict JSON → AutoEditPlan v2 decoding;
- canonical JSON Schema v2;
- exact field/discriminator enforcement;
- typed DTO construction.

It deliberately does not implement W7-004 semantic ProjectState verification or
sequential dry-run translation.

## Canonical parser

Added:
`src/ai_ngerti_geopolitik/application/ai_l2_parser.py`.

Owner:
`AutoEditPlanParser`.

Canonical schema:
`AUTO_EDIT_PLAN_V2_JSON_SCHEMA`.

## Strict root

Required exact fields:
- schema_version;
- base_project_revision;
- request_id;
- summary;
- commands.

Rules:
- schema_version strict integer 2;
- base revision strict integer >= 0;
- request ID + summary non-blank string;
- commands array 1..40;
- unknown/missing fields rejected.

## Command decoding

Supported only:
- set_clip_effects;
- set_clip_duration;
- set_clip_speed;
- set_clip_transform;
- set_clip_transition.

Each command has closed exact fields.

Hard-rejected structural examples:
- unknown command family;
- unknown field;
- provider-selected ripple;
- crop;
- unlock;
- crossfade extra field;
- bool masquerading as int;
- missing required field;
- effect/transform command with no change;
- target ID with outer whitespace.

Decoded commands use W7-001 typed DTOs, so their already-locked static invariants
remain intact.

## Deferred to W7-004

Not performed by W7-003:
- ProjectState read;
- target existence;
- selected-scope validation;
- track/effect lock policy;
- stale project/session/revision correlation;
- dynamic duration ratio/source availability;
- canvas-relative position bounds;
- candidate-duration transition maximum;
- manual-command translation/dry-run;
- candidate semantic hash proof.

No Gemini request-profile, UI or canonical apply change was made.

## Tests and evidence

Targeted parser tests:
**41/41 PASS**.

Full pytest:
**PASS**.

Evidence verifies:
- all five command families decode;
- root + every command schema are closed;
- command cap = 40;
- unknown fields/commands reject;
- bool-as-int rejects;
- provider ripple rejects;
- crop rejects;
- all W7-004+ operations remain unstarted.

Evidence verifier:
**24/24 PASS**.

## Quality gates

- Ruff format/check PASS;
- mypy PASS — 67 source files;
- import contracts PASS;
- architecture PASS;
- source-of-truth 70/70 PASS;
- no-secret PASS;
- frozen UI references 42/42 PASS;
- artifact upload PASS.

## Regression lock

All **26/26 workflows** triggered on accepted W7-003 implementation HEAD
succeeded, all attempt 1:

- W7-003 `37647150710`
- W6-010 `37647150578`
- W6-009 `37647150670`
- W6-008 `37647150440`
- W6-007 `37647150617`
- W6-006 `37647150803`
- W6-005 `37647150527`
- W6-004 `37647150505`
- W6-003 `37647150697`
- W6-002 `37647150548`
- W6-001 `37647150566`
- W5-010 `37647150753`
- W5-009 `37647150423`
- W5-008 `37647150295`
- W5-007 `37647150526`
- W5-006 `37647150532`
- W5-005 `37647150480`
- W5-004 `37647150554`
- W4 `37647150567`
- W3 `37647150717`
- W2 `37647150740`
- W1 `37647150729`
- W0 `37647150520`
- S10 `37647150564`
- S09 `37647150315`
- S08 `37647150326`

S08 portable foundation PASS.
S10 real-media/package PASS.
W0 engine qualification PASS.

## Next

**S11-W7-004 — L2 semantic verifier + sequential dry-run translator only.**
