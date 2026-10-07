# PLAN — CURRENT IMPLEMENTATION PHASE

**SF-STEP 11 remains active. W6 is closed. W7 is CONTRACT_LOCKED and W7-001 is PASS.**

## Accepted W7-001

Implementation:
`f301c10a16ba33e051ef97e9d166262b7fbac327`

Workflow:
`37640973646` — SUCCESS.

Implemented:
- canonical AutoEditPlan v2 DTO contract;
- exact five-capability registry;
- manual command/property ownership metadata;
- max 20 selected targets / max 40 commands;
- one command family per target;
- duration/speed mutual exclusion;
- typed W7 policy bounds;
- strict integer-safe proposal DTOs for duration/speed/transform/transition;
- W6 effect contract reuse and compatibility assertion.

Evidence:
- targeted tests 27/27 PASS;
- full pytest PASS;
- evidence verifier 18/18 PASS;
- 26/26 regression workflow families SUCCESS, all attempt 1.

## Serial W7 plan

1. W7-001 canonical L2 command contracts + capability registry — **PASS**
2. W7-002 L2 ContextBuilder + selected-scope contract — **READY**
3. W7-003 strict AutoEditPlan v2 parser/schema — BLOCKED_BY_W7_002
4. W7-004 L2 semantic verifier + sequential dry-run translator — BLOCKED_BY_W7_003
5. W7-005 pacing qualification — duration + speed — BLOCKED
6. W7-006 transform qualification — BLOCKED
7. W7-007 transition + mixed-plan qualification — BLOCKED
8. W7-008 Gemini L2 request profile + lifecycle reuse — BLOCKED
9. W7-009 approval/apply/UI diff integration — BLOCKED
10. W7-010 real-media closure + failure/regression lock — BLOCKED

## W7-002 boundary

W7-002 may build bounded deterministic selected-scope context only:
- stable target/track IDs;
- timing/source-duration availability;
- speed/transform/transition/effect state;
- locks/editability;
- dimensions/aspect;
- bounded neighbor summaries;
- project fps/canvas;
- exact capability registry/policy bounds.

It must exclude credentials, paths, media bytes, arbitrary files, logs,
engine objects, output paths and full subtitle/narration/prompt history.

W7-002 must not parse provider plans, dry-run commands, call Gemini, mutate UI or
apply canonical edits.

Do not begin W7-002 until owner says `lanjutkan`.
