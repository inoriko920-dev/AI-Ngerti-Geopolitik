# PLAN — CURRENT IMPLEMENTATION PHASE

**SF-STEP 11 remains active. W6 is closed. W7 is CONTRACT_LOCKED and W7-001..002 are PASS.**

## Accepted W7-002

Implementation:
`23aad912cb789f98dd3ec61d11e799390d602381`

Workflow:
`37644007477` — SUCCESS.

Implemented:
- explicit selected scope 1..20 stable unique clip IDs;
- deterministic L2 context schema v2;
- bounded current pacing state + source-duration availability;
- bounded transform/transition/effect state;
- lock/editability state;
- one previous + one next neighbor;
- exact W7 capability/policy surface;
- bounded untrusted project text;
- explicit exclusion of credential/path/media-byte/log/engine/private-content surfaces;
- zero mutation.

Evidence:
- targeted tests 18/18 PASS;
- full pytest PASS;
- evidence verifier 24/24 PASS;
- 26/26 triggered regression workflows SUCCESS, all attempt 1.

## Serial W7 plan

1. W7-001 canonical L2 command contracts + capability registry — **PASS**
2. W7-002 L2 ContextBuilder + selected-scope contract — **PASS**
3. W7-003 strict AutoEditPlan v2 parser/schema — **READY**
4. W7-004 L2 semantic verifier + sequential dry-run translator — BLOCKED_BY_W7_003
5. W7-005 pacing qualification — duration + speed — BLOCKED
6. W7-006 transform qualification — BLOCKED
7. W7-007 transition + mixed-plan qualification — BLOCKED
8. W7-008 Gemini L2 request profile + lifecycle reuse — BLOCKED
9. W7-009 approval/apply/UI diff integration — BLOCKED
10. W7-010 real-media closure + failure/regression lock — BLOCKED

## W7-003 boundary

W7-003 may implement strict provider JSON parsing for AutoEditPlan schema v2 only:
- exact root fields;
- exact command discriminators and command-specific fields;
- strict integer typing with booleans rejected;
- max command/target structural bounds;
- unknown-field/unknown-command hard rejection;
- conversion into W7-001 typed DTOs;
- provider request-ID correlation if owned by parser boundary.

W7-003 must not:
- run semantic range/lock/selected-target checks owned by W7-004;
- dry-run manual commands;
- mutate ProjectState/CommandBus;
- change Gemini request profile;
- change UI.

Do not begin W7-003 until owner says `lanjutkan`.
