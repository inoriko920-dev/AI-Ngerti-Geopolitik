# PROJECT STATUS — AI NGERTI GEOPOLITIK

**Current STEP:** SF-STEP 11 — Feature Implementation Waves  
**Current wave:** **W7 — AI Auto Edit L2**  
**W7 status:** **CONTRACT_LOCKED / W7-001 PASS / W7-002 READY**  
**Accepted W7-001 implementation HEAD:** `f301c10a16ba33e051ef97e9d166262b7fbac327`  
**Accepted W7-001 workflow:** `37640973646` — SUCCESS  
**Next exact task:** **S11-W7-002 — L2 ContextBuilder + selected-scope contract**  
**W6 final status:** **CLOSED / PASS_WITH_PROVISIONAL_LIVE_GEMINI**

## W7-001 proven

Canonical L2 contract module:
`src/ai_ngerti_geopolitik/application/ai_l2_contracts.py`.

Exact command union:
- set_clip_effects;
- set_clip_duration;
- set_clip_speed;
- set_clip_transform;
- set_clip_transition.

Structural bounds:
- schema version 2;
- selected targets max 20;
- commands max 40;
- one family per target;
- duration and speed mutually exclusive per target.

Manual ownership:
- effects → SetClipPropertiesCommand + EffectProperties;
- duration → SetClipDurationCommand;
- speed → SetClipSpeedCommand + SpeedProperties;
- transform → SetClipPropertiesCommand + VideoProperties;
- transition → SetClipPropertiesCommand + TransitionProperties.

AI policy:
- duration 50%..200%, min ceil(fps/2);
- speed 50%..200%;
- position ± half canvas;
- uniform scale 50%..200%;
- rotation ±15°;
- opacity 60%..100%;
- transition none/fade_black only;
- fade_black dynamic max helper;
- W6 effects allowlist unchanged.

## Gates

Workflow `37640973646`:
- Ruff format/check PASS;
- mypy PASS — 64 source files;
- import contracts PASS;
- architecture PASS;
- source-of-truth 70/70 PASS;
- no-secret PASS;
- UI references 42/42 PASS;
- targeted tests 27/27 PASS;
- full pytest PASS;
- deterministic evidence PASS;
- evidence verifier 18/18 PASS.

Artifact:
- `ANG-S11-W7-001-L2-Contracts`;
- ID `11491927299`;
- SHA-256 `2adab3d3e6a010134b820344d9609962634c0fd2f6846b65575d3d4394c9cc5f`.

Regression:
**26/26 workflow families SUCCESS on the same HEAD, all attempt 1.**

## Not started by W7-001

- L2 ContextBuilder;
- strict JSON parser;
- semantic verifier/dry-run translator;
- provider profile changes;
- runtime UI;
- L2 apply.

## Exact next action

After owner says **lanjutkan**, execute **S11-W7-002 only**.
