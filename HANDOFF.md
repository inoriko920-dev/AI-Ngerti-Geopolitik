# HANDOFF — AI NGERTI GEOPOLITIK

**Current phase:** SF-STEP 11 — Feature Implementation Waves  
**Current wave:** W7 — AI Auto Edit L2  
**W7 status:** **CONTRACT_LOCKED / W7-001..003 PASS / W7-004 READY**  
**Last completed task:** S11-W7-003 — PASS  
**Accepted W7-003 implementation HEAD:** `a57c8acd96cdcff8b20f659171229ad0bff913d0`  
**Accepted W7-003 workflow:** `37647150710` — SUCCESS  
**Next exact task:** S11-W7-004 — L2 semantic verifier + sequential dry-run translator  
**W6 final status:** PASS_WITH_PROVISIONAL_LIVE_GEMINI  
**W5 final status:** PASS_WITH_PROVISIONAL_MIC_HARDWARE

## W7-003 implementation now available

Application:
- `application/ai_l2_parser.py`;
- canonical `AUTO_EDIT_PLAN_V2_JSON_SCHEMA`;
- provider-agnostic `AutoEditPlanParser`.

Strict root contract:
- exact fields only: schema_version, base_project_revision, request_id, summary, commands;
- schema_version must be strict integer 2;
- base revision strict integer >= 0;
- request_id and summary non-blank strings;
- commands must be an array with 1..40 items;
- unknown root fields hard-reject.

Strict command decoding:
- set_clip_effects;
- set_clip_duration;
- set_clip_speed;
- set_clip_transform;
- set_clip_transition;
- exact fields per family;
- unknown commands/fields hard-reject;
- booleans masquerading as integers hard-reject;
- provider-owned ripple is not representable;
- crop/crossfade/unlock extras are not representable;
- transform/effect commands require at least one actual change;
- decoded commands become W7-001 typed DTOs.

Static versus semantic boundary:
- W7-001 DTO static invariants remain active during decode;
- dynamic duration/source availability, canvas position limits, candidate transition max,
  target existence, selected scope, locks, stale revision/session and dry-run remain W7-004;
- parser does not import/read ProjectState or CommandBus;
- no provider profile, UI, approval or canonical apply changes.

## W7-003 gates

Workflow `37647150710` — **SUCCESS**:
- Ruff format/check PASS;
- mypy PASS — 67 source files;
- import contracts PASS;
- architecture PASS;
- source-of-truth 70/70 PASS;
- no-secret PASS;
- UI references 42/42 PASS;
- targeted parser tests **41/41 PASS**;
- full pytest PASS;
- deterministic evidence PASS;
- evidence verifier **24/24 PASS**;
- artifact upload PASS.

Artifact:
- `ANG-S11-W7-003-L2-Parser`;
- ID `11494393982`;
- size 1436 bytes;
- SHA-256 `fe7542cad4dbac0af22df2cde72b78d7e3ee6c464f28fed617e76264e7863d9f`.

Evidence:
`docs/evidence/features/S11_W7_003_L2_PARSER.md`.

## Regression lock

All **26/26 workflows triggered on accepted W7-003 HEAD** are SUCCESS,
all attempt 1:

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

S08 portable build/smoke PASS.  
S10 real-media + packaged smoke PASS.  
W0 engine qualification PASS.

## Deliberately not started

- W7-004 ProjectState semantic verifier;
- selected-scope/target/lock/stale validation;
- dynamic duration/source/canvas/transition candidate checks;
- sequential manual-command dry-run;
- provider request-profile changes;
- runtime UI changes;
- canonical L2 apply.

## Next exact action

After owner says `lanjutkan`, execute **S11-W7-004 only — L2 semantic verifier + sequential dry-run translator**.

Do not start W7-005 pacing qualification in the same turn.
