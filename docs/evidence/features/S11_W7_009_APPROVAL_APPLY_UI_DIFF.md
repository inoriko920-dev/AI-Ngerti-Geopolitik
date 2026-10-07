# S11-W7-009 — APPROVAL / APPLY / UI DIFF INTEGRATION

**Status:** PASS  
**Accepted implementation HEAD:** `2eef5762454f367c2fad5550f75209f8ffeb0a16`  
**Accepted workflow:** `37673518251` — SUCCESS  
**Artifact:** `ANG-S11-W7-009-Approval-UI-Diff`  
**Artifact ID:** `11505484572`  
**Artifact size:** 820 bytes  
**Artifact SHA-256:** `4b1fd4b585bb2739c42fc314345a8961c743defa7eadea37245045fb1b42de59`

## Scope

W7-009 connects the already-verified W7 L2 plan path to explicit user review,
approval, one atomic canonical apply, one Undo/Redo transaction and bounded
before→after UI text. It reuses the W6 approval and UI owners rather than
creating a second approval service or a new screen/layout.

W7-010 final real-media/failure/regression closure is not started by this task.

## Approval owner reuse

The existing `AIPlanApprovalService` remains the only approval owner.

W6 L1 remains available through:
- `stage_from_job()`;
- `PlanVerifier`;
- the existing L1 command translation;
- the existing `AIApprovalSnapshot`.

W7 L2 adds only:
- `stage_from_job_l2()`;
- `AutoEditPlanVerifier + W7SelectedScope` final revalidation;
- reuse of the verified canonical translated manual commands;
- bounded `AIPlanDiffEntry` review text;
- the same approve/reject/cancel/apply state machine.

No provider result mutates `ProjectState` directly.

## Atomic apply proof

A reviewed six-command mixed L1/L2 plan is staged without canonical mutation.

After explicit approval:
- final project/session/revision/semantic-base checks run;
- the plan is reverified through `AutoEditPlanVerifier`;
- the translated candidate hash must still equal the verified proof;
- all six canonical commands execute inside one
  `CommandBatch(actor="ai")`;
- project revision increments exactly once;
- mixed timeline result is 210 frames;
- one Undo restores the pre-AI semantic hash;
- one Redo restores the applied semantic hash.

Reject/cancel create no history entry.  
Apply without explicit approval is rejected.  
Duplicate apply is rejected.  
A same-revision semantic replacement is rejected as `STALE_PLAN`.

## Bounded diff proof

W7-009 builds one diff entry per verified L2 command from the exact sequential
candidate dry-run.

Qualified diff families:
- effects;
- duration;
- transform;
- transition;
- speed including effective duration;
- transition after pacing.

Each UI display line:
- identifies the target clip and command type;
- contains explicit before → after text;
- is bounded to 280 characters;
- never changes the candidate while being built.

The evidence mixed plan produces **6 bounded diff lines**.

## UI reuse

The completed W6 AI Agent surface is reused.

Changes are limited to existing controls/projections:
- existing model combo gains `Mode: Auto Edit L2`;
- L1 remains the default mode and its existing submit payload remains unchanged;
- L2 submit adds only `profile=l2_auto_edit`;
- existing plan list renders W7 bounded diff lines when supplied;
- existing PLAN / APPROVAL button gating remains unchanged;
- existing safety label switches to the L2 capability wording only for an L2 diff projection;
- no new screen or layout is created;
- no new image-generation/UI-prompt gate is required by the locked W7 contract.

Frozen UI reference integrity remains **42/42 PASS**.

## Backward compatibility

The regression lock proves W6 remains green after the approval generalization:
- W6 L1 provider/request contract unchanged;
- W6 L1 approval path unchanged;
- W6 frozen AI UI tests remain green;
- existing semantic UI intents remain the ownership boundary;
- presentation still does not call Gemini, secure storage, ProjectState mutation
  or CommandBus directly.

## Gates

Workflow `37673518251` — SUCCESS:
- uv lock/frozen sync PASS;
- Ruff format/check PASS;
- mypy PASS — 68 source files;
- import contracts PASS — 4 kept / 0 broken;
- architecture PASS;
- source-of-truth PASS — 70/70 on implementation HEAD;
- no-secret PASS;
- frozen UI references 42/42 PASS;
- targeted W7-009 application + Qt tests **8/8 PASS**;
- full pytest **386/386 PASS**;
- deterministic atomic approval/apply/Undo/Redo evidence PASS;
- evidence verifier **2/2 files PASS**;
- artifact upload PASS.

## Regression lock

On accepted implementation HEAD
`2eef5762454f367c2fad5550f75209f8ffeb0a16`:

- **26/26 triggered workflow families SUCCESS**;
- all 26 succeeded on attempt 1;
- S08 Windows portable foundation PASS;
- S09 Windows UI shell PASS;
- S10 Windows E2E vertical slice + packaged smoke PASS;
- W0 engine qualification PASS;
- prior W1..W7 gates remain green;
- no application regression failure was observed.

## Safety boundary

- no credential handling change;
- no second provider/job/approval service;
- no new screen/layout;
- no direct provider-to-canonical mutation;
- no W7-010 implementation started.

## Next

**S11-W7-010 — Real-media closure + failure/regression lock — READY.**
