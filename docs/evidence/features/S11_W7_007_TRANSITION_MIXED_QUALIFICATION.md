# S11-W7-007 — L2 TRANSITION + MIXED-PLAN QUALIFICATION

**Status:** PASS  
**Accepted implementation HEAD:** `642ce15c89b3a0e65011387d67f9898d0cd1f542`  
**Accepted workflow:** `37667149646` — SUCCESS  
**Artifact:** `ANG-S11-W7-007-L2-Transition-Mixed`  
**Artifact ID:** `11503996235`  
**Artifact size:** 14,566,415 bytes  
**Artifact SHA-256:** `767e82d05436c491e984f9d7e3e3f7907d03f6859ceb171c1a0dc6d61a154336`

## Scope

W7-007 qualifies the transition family and mixed L1/L2 sequential plan path
already implemented by the W7-004 semantic verifier. It does not add a new
mutation owner, provider profile, runtime UI, approval/apply path, or direct
AI-to-ProjectState mutation.

## Canonical paths reused

- `TransitionEditProposal`;
- `AutoEditPlanVerifier`;
- canonical `SetClipPropertiesCommand + TransitionProperties`;
- canonical `SetClipDurationCommand`;
- canonical `SetClipSpeedCommand`;
- existing W6 `EffectEditProposal` path;
- existing W7 transform translation;
- existing W4 `build_w4_creative_plan()` fade-through-black render path;
- existing FFmpeg qualification adapter.

No AI-only transition or mixed-plan mutation owner exists.

## Transition proof

Real-media transition qualification proves:
- `fade_black` translates through `SetClipPropertiesCommand`;
- 30-frame `fade_black` on a 120-frame clip is accepted;
- render mapping emits exactly two black fade filters;
- transition preview at frame 1 differs from baseline;
- real transition export is valid and retains audio;
- `none` with duration 0 clears an existing `fade_black`;
- candidate semantic hash equals the verifier proof.

Sequential candidate validation is also proven:
- a 120-frame clip changed to 200% speed becomes 60 frames;
- a later 30-frame fade is valid at the exact half-duration boundary;
- 31 frames is rejected as `SEMANTIC_INVALID`.

## Mixed L1/L2 proof

One dry-run plan across two clips qualifies six ordered commands:
1. L1 effect on C001 — Rise/Fade, intensity 110;
2. C001 duration — 150 frames;
3. C001 transform — position, uniform scale, rotation and opacity;
4. C001 `fade_black` — 45 frames;
5. C002 speed — 200%;
6. C002 `fade_black` — 30 frames.

Canonical translated owner sequence:
- SetClipPropertiesCommand;
- SetClipDurationCommand;
- SetClipPropertiesCommand;
- SetClipPropertiesCommand;
- SetClipSpeedCommand;
- SetClipPropertiesCommand.

Sequential result:
- C001 duration = 150 frames;
- C002 ripples to frame 150;
- C002 effective duration = 60 frames;
- total candidate timeline = 210 frames;
- mixed real-media export = 210 frames within probe tolerance;
- audio retained;
- candidate semantic hash equals the verifier proof;
- candidate revision remains unchanged because this task is qualification-only.

## Safety

- canonical ProjectState remains unchanged;
- CommandBus history remains unchanged;
- source media SHA-256 remains unchanged;
- provider profile unchanged;
- runtime UI unchanged;
- canonical AI approval/apply not started;
- W7-008 Gemini L2 request-profile/lifecycle work not started.

## Gates

Workflow `37667149646` — SUCCESS:
- FFmpeg qualification toolchain PASS;
- uv lock/frozen sync PASS;
- Ruff format/check PASS;
- mypy PASS — 68 source files;
- import contracts PASS — 4 kept / 0 broken;
- architecture PASS;
- source-of-truth PASS — 70/70 on implementation HEAD;
- no-secret PASS;
- frozen UI references 42/42 PASS;
- targeted W7-007 tests **5/5 PASS**;
- full pytest **361/361 PASS**;
- owned real-media fixture PASS;
- transition + mixed-plan real-media evidence PASS;
- evidence verifier **8/8 files PASS**;
- artifact upload PASS.

## Regression lock

On accepted implementation HEAD `642ce15c89b3a0e65011387d67f9898d0cd1f542`:
- **26/26 triggered workflow families SUCCESS**;
- 23 succeeded on attempt 1;
- W5-010, W5-005 and W0 initially hit a transient Chocolatey FFmpeg
  **HTTP 504 Gateway Timeout** before fixture generation;
- those three were rerun unchanged and succeeded on attempt 2;
- no application/unit/regression assertion failed;
- S08 Windows portable foundation PASS;
- S10 Windows E2E real-media regression PASS;
- W0/W1/W2/W3/W4/W5/W6 and prior W7 gates remain green.

## Next

**S11-W7-008 — Gemini L2 request profile + lifecycle reuse — READY.**

W7-009 and W7-010 remain blocked by the serial contract.
