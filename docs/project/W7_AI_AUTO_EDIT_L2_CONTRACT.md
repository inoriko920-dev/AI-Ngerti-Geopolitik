# W7 — AI AUTO EDIT L2 CONTRACT

**Status:** CONTRACT_LOCKED / W7-001 PASS / W7-002 READY / W7-003..010 BLOCKED_BY_PREVIOUS_TASKS  
**Role that produced this contract:** ASTRA  
**Master Blueprint mapping:** TECH-WAVE STEP 10  
**Runtime implementation:** ACTIVE — W7-001 PASS  
**Planning date:** 2026-10-07

Planning sources:
- `docs/planning/10_S11_W7_AI_AUTO_EDIT_L2_CONTRACT_PLAN_2026-10-07.docx`
- `docs/planning/10_S11_W7_AI_AUTO_EDIT_L2_CONTRACT_PLAN_2026-10-07.txt`

## 1. Purpose

W7 extends the completed W6 effects-only AI planner into a deliberately bounded
Auto Edit L2 planner for pacing, transform and transition.

The Master Blueprint gate remains binding:

> AI L2 may use only operations whose manual command path is already stable,
> render-backed where relevant, validated, persisted and undoable.

W7 must reuse the W6 provider, credential, async-job, approval and CommandBus
ownership boundaries. There is no AI-only mutation path.

## 2. Canonical owners that must be reused

- `ProjectState` = canonical project truth.
- `CommandBus / CommandBatch` = only committed mutation/history owner.
- `SetClipDurationCommand` = pacing duration mutation.
- `SetClipSpeedCommand` = speed mutation.
- `SetClipPropertiesCommand` + `VideoProperties` = transform mutation.
- `SetClipPropertiesCommand` + `TransitionProperties` = transition mutation.
- W6 `set_clip_effects` path = effects carry-forward.
- `GeminiAIProvider` / `AIProviderPort` = only V1 AI provider path.
- existing W6 credential pool / Windows secure store = credential ownership.
- existing W6 background job lifecycle = provider execution ownership.
- existing W6 explicit approval service = approval boundary.

Creating a second provider client, credential owner, history owner, or direct
AI→ProjectState mutation service is prohibited.

## 3. Initial W7 command allowlist

Strict W7 AutoEditPlan schema v2 may contain only:

1. `set_clip_effects`
2. `set_clip_duration`
3. `set_clip_speed`
4. `set_clip_transform`
5. `set_clip_transition`

Every command must target a clip explicitly present in the application-selected
scope.

Plan bounds:
- selected targets: 1..20 clips;
- commands: 1..40;
- maximum one command per family per target;
- `set_clip_duration` and `set_clip_speed` are mutually exclusive for the
  same target in one plan.

## 4. AI-specific policy bounds

Manual editor ranges are not automatically AI ranges.

### Duration
- application-owned `ripple=true`;
- exact frame representability required;
- source media bound must remain valid;
- minimum approximately 0.5 seconds: `ceil(fps / 2)`;
- initial AI policy: 50%..200% of current clip duration.

### Speed
- manual range remains 25%..400%;
- W7 AI range is narrower: **50%..200%**;
- application-owned `ripple=true`;
- reverse is not represented through speed.

### Transform
Allowed fields only:
- position_x;
- position_y;
- uniform `scale_percent`;
- rotation_tenths;
- opacity_percent.

AI bounds:
- position X: ± half project canvas width;
- position Y: ± half project canvas height;
- uniform scale: 50%..200%;
- rotation: -150..+150 tenths (±15°);
- opacity: 60%..100%.

`scale_percent` is translated to equal X/Y scale.

Crop is not part of W7 v2.

### Transition
Allowed presets:
- `none`;
- `fade_black`.

Rules:
- `none` requires duration 0;
- `fade_black` duration: 1..min(2×fps, floor(candidate clip duration / 2));
- true crossfade/dissolve remains unsupported.

### Effects
Exact W6 L1 render-qualified allowlist and 0..200 intensity remain binding.
AI cannot change `effects.locked`.

## 5. Explicitly deferred / forbidden

Not part of initial W7:
- reorder narrative clips;
- split;
- trim;
- delete/remove;
- duplicate;
- move clip across tracks;
- add/delete/reorder tracks;
- crop;
- reverse;
- crossfade/dissolve;
- arbitrary keyframes/path animation/perspective/skew/z-order;
- title/subtitle/narration/audio/color mutation;
- markers / IN-OUT / render preset;
- project FPS/canvas change;
- source asset replacement;
- provider/credential/pool-policy mutation;
- project path/output folder/file-system mutation;
- automatic unlock of user locks.

Unknown or forbidden capability must hard-reject the plan; it must not be ignored
or silently clamped.

## 6. AutoEditPlan schema v2

Required root fields:
- `schema_version = 2`;
- `base_project_revision`;
- `request_id`;
- `summary`;
- `commands`.

Root unknown fields are rejected.

### set_clip_duration
Fields:
- command_type;
- target_clip_id;
- duration_frames.

Provider may not choose the ripple policy.

### set_clip_speed
Fields:
- command_type;
- target_clip_id;
- rate_percent.

Provider may not choose the ripple policy.

### set_clip_transform
Fields:
- command_type;
- target_clip_id;
- at least one of:
  - position_x;
  - position_y;
  - scale_percent;
  - rotation_tenths;
  - opacity_percent.

### set_clip_transition
Fields:
- command_type;
- target_clip_id;
- preset;
- duration_frames.

### set_clip_effects
Carries forward the strict W6 shape:
- target_clip_id;
- optional enter_effect;
- optional exit_effect;
- optional intensity_percent;
- at least one change required.

Booleans masquerading as integers, missing fields, duplicate/conflicting
families, unknown fields or commands and out-of-range values are hard errors.

## 7. W7 ContextBuilder boundary

Max 20 selected targets.

Allowed bounded context per target:
- stable clip_id / track_id;
- base project revision;
- timeline start/end/current duration;
- source-duration availability needed for duration validation;
- current speed;
- current position/scale/rotation/opacity;
- current transition;
- current L1 effects/intensity;
- track lock / effect lock / effective editability;
- media type/dimensions/aspect ratio;
- bounded previous/next neighbor summary.

Project context:
- project_id;
- fps;
- canvas width/height/aspect ratio;
- selected scope;
- exact command allowlist;
- exact W7 policy bounds.

Excluded:
- raw credential/key;
- local file paths;
- source media bytes;
- arbitrary files;
- engine objects;
- raw logs;
- output/project path;
- full subtitle/narration content;
- full prompt history.

User/project text remains bounded untrusted data and cannot override policy.

## 8. Semantic verifier and sequential dry run

Verifier remains application-layer and provider-agnostic.

Required order:
1. strict JSON parse;
2. root/schema validation;
3. provider request-ID correlation;
4. stale revision check;
5. selected-scope check;
6. family uniqueness/conflict check;
7. target existence;
8. lock policy;
9. W7 numeric/capability policy;
10. canonical value-object validation;
11. sequential dry-run through the same manual commands.

Sequential dry run is mandatory because pacing can change the legal duration of
a later transition command.

If any command fails, the complete plan fails. Canonical ProjectState and
CommandBus history remain unchanged.

The verified proof must include at least:
- schema version;
- base revision;
- candidate semantic hash;
- command count;
- target count.

## 9. Provider / async reuse

W7 reuses:
- official `google-genai` adapter;
- credential slots 1..100;
- bounded network retry/failover;
- provider-wide quota/rate-limit cooldown;
- cancellation/timeout mapping;
- stale session/revision protection.

If W6 job/verifier typing is too L1-specific, only a backward-compatible
protocol/strategy generalization is allowed. W6 tests and behavior must remain
green.

No second Gemini service is allowed.

## 10. Approval / apply / history

Provider result never mutates the project directly.

Flow:
provider result → strict W7 verification → explicit user review/approval →
final stale/hash revalidation → one atomic `CommandBatch(actor="ai")`.

One approved mixed L1/L2 plan:
- increments revision once;
- is undone by one Undo;
- is restored by one Redo.

Reject/cancel creates no history entry.
Duplicate apply is rejected.
A same-revision semantic replacement is stale.
A newly locked target is rejected at final revalidation.

## 11. UI policy

Initial W7 reuses the completed W6 AI surfaces and corrected frozen mapping:
- UI-020 AI Director;
- UI-021 Ready/Chat;
- UI-022 Plan;
- UI-023 Applied;
- UI-024 Provider unavailable;
- UI-033 Provider/API Key settings.

The plan view may add bounded before→after text for W7 command differences only
after backend support for the relevant task is proven.

No new image-generation/UI-prompt step is required by this initial contract.

If implementation later requires a genuinely new screen/layout, the Software
Factory UI gate becomes mandatory: create UI prompt → STOP → owner provides
images → inspect/revise → create final UI reference DOCX → only then resume.

## 12. Failure taxonomy

- `SCHEMA_INVALID`: malformed/wrong schema, unknown fields/types, command cap.
- `SEMANTIC_INVALID`: unsupported capability/range, impossible duration,
  conflicting pacing families, transition invalid for candidate state.
- `LOCK_CONFLICT`: track/effect lock forbids requested mutation.
- `STALE_PLAN`: project/session/revision/semantic base no longer matches.
- provider typed errors: invalid auth, timeout/network, quota/rate-limit,
  malformed/empty response.
- apply conflict: translated candidate no longer matches verified proof.
- cancelled: no success state and no history entry.

Every failure path must retain zero unsafe canonical mutation.

## 13. Evidence requirements

Every W7 implementation task:
- Ruff format/check;
- mypy;
- import contracts;
- architecture verifier;
- source-of-truth verifier;
- no-secret verifier;
- frozen UI reference integrity;
- targeted tests;
- full pytest;
- deterministic evidence relevant to the task.

Media/render tasks additionally require real-media proof, not mock-only tests.

Final W7 must prove:
- mixed L1/L2 plan;
- real pacing timing;
- real transform preview/export;
- real fade_black transition;
- persistence/save-reopen;
- one atomic Undo/Redo;
- invalid/out-of-range/out-of-scope/locked/stale/provider failures;
- regression of W6 and earlier workflows on the same accepted HEAD.

Live Gemini success may only be claimed when an actual credential is supplied
and a real network smoke succeeds.

## 14. Serial implementation contract

- **W7-001 — Canonical L2 command contracts + capability registry — PASS**
- **W7-002 — L2 ContextBuilder + selected-scope contract — READY**
- W7-003 — strict AutoEditPlan v2 parser/schema — BLOCKED_BY_W7_002
- W7-004 — L2 semantic verifier + sequential dry-run translator — BLOCKED_BY_W7_003
- W7-005 — pacing qualification: duration + speed — BLOCKED_BY_W7_004
- W7-006 — transform qualification — BLOCKED_BY_W7_005
- W7-007 — transition + mixed-plan qualification — BLOCKED_BY_W7_006
- W7-008 — Gemini L2 request profile + lifecycle reuse — BLOCKED_BY_W7_007
- W7-009 — approval/apply/UI diff integration — BLOCKED_BY_W7_008
- W7-010 — real-media failure/regression closure — BLOCKED_BY_W7_009

## W7-001 implementation closure

Accepted implementation HEAD:
`f301c10a16ba33e051ef97e9d166262b7fbac327`

Accepted workflow:
`37640973646` — SUCCESS.

Implemented:
- application-layer `ai_l2_contracts.py`;
- immutable exact five-command capability registry;
- manual owner/property owner metadata;
- AutoEditPlan schema v2 DTO contract;
- max 20 targets / 40 commands;
- one family per target and duration/speed conflict guard;
- typed duration/speed/transform/transition policy bounds;
- W6 effect contract reuse;
- W6 schema/effect allowlist backward compatibility assertion.

Evidence:
`docs/evidence/features/S11_W7_001_L2_CONTRACTS.md`.

Gates:
- targeted tests 27/27 PASS;
- full pytest PASS;
- evidence verifier 18/18 PASS;
- 26/26 regression workflow families SUCCESS, all attempt 1.

W7-001 did not start ContextBuilder, parser/verifier, provider changes, UI or apply.

## 15. Exact next action

After owner says `lanjutkan`, execute **S11-W7-002 only — L2 ContextBuilder + selected-scope contract**.

W7-002 must not start:
- strict AutoEditPlan v2 provider JSON parser;
- semantic dry-run translator;
- Gemini request-profile changes;
- runtime UI changes;
- canonical L2 apply.

After W7-002, report gate PASS/FAIL and stop.
