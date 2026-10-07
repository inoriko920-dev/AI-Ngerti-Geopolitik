# S11-W7-002 — L2 ContextBuilder + Selected-Scope Contract

**Status:** PASS  
**Accepted implementation HEAD:** `23aad912cb789f98dd3ec61d11e799390d602381`  
**Accepted workflow:** `37644007477` — SUCCESS  
**Artifact:** `ANG-S11-W7-002-L2-Context`  
**Artifact ID:** `11494315331`  
**Artifact size:** 2373 bytes  
**Artifact SHA-256:** `5ffc24ff6afa0de1942a4e6e4c9eabf1cf55004fd07a77f0263721caf8da4960`

## Scope completed

W7-002 adds only the bounded application-side context boundary required before
provider JSON parsing.

Added:
- `application/ai_l2_scope.py`;
- `application/ai_l2_context.py`.

No W7-003 parser, W7-004 semantic verifier, Gemini request-profile change,
runtime UI change, or canonical L2 apply was started.

## Selected-scope contract

`W7SelectedScope`:
- requires 1..20 stable clip IDs;
- rejects empty/blank IDs;
- rejects outer whitespace;
- rejects duplicate IDs;
- preserves application selection order.

## L2 ContextBuilder

`L2ContextBuilder` is deterministic and reads canonical `ProjectState` only.

It exposes bounded data required for the W7 five-command surface:
- clip/track stable IDs;
- base project revision;
- timeline start/end/current duration;
- source-duration availability;
- current speed;
- current transform fields allowed by W7;
- current transition;
- current L1 effects/intensity;
- track/effect lock and effective editability;
- media type/dimensions/aspect ratio;
- one previous + one next neighbor summary;
- fps/canvas;
- exact W7 command allowlist and policy bounds.

It does not expose:
- credential/API key;
- local filesystem path;
- source file name/fingerprint;
- source bytes;
- crop state;
- subtitle/narration/title/audio/color content;
- logs;
- engine objects;
- output/project paths;
- prompt history.

Project text is bounded normalized untrusted data and cannot change policy.

## W7 policy represented in context

- selected targets max 20;
- commands max 40;
- duration ratio 50%..200%, minimum ceil(fps/2);
- application-owned duration/speed ripple;
- speed 50%..200%;
- position ± half canvas;
- uniform scale 50%..200%;
- rotation -150..+150 tenths;
- opacity 60%..100%;
- transition presets only none/fade_black;
- transition final bound declared candidate-dependent;
- W6 render-qualified effect allowlist reused;
- effect intensity 0..200;
- crop/crossfade/automatic unlock forbidden.

## Gates

Workflow `37644007477`:
- uv lock/check PASS;
- frozen dependency sync PASS;
- Ruff format PASS;
- Ruff check PASS;
- mypy PASS — 66 source files;
- import contracts PASS;
- architecture PASS;
- source-of-truth 70/70 PASS;
- no-secret PASS;
- frozen UI reference integrity 42/42 PASS;
- targeted W7-002 suite **18/18 PASS**;
- full pytest PASS;
- deterministic evidence PASS;
- evidence verifier **24/24 PASS**;
- artifact upload PASS.

## Regression lock

All **26/26 workflows triggered by the accepted W7-002 HEAD** completed SUCCESS,
all attempt 1:

- S08 `37644007666`
- S09 `37644007686`
- S10 `37644007596`
- W0 `37644007481`
- W1 `37644007717`
- W2 `37644007645`
- W3 `37644007507`
- W4 `37644007531`
- W5-004 `37644007636`
- W5-005 `37644007485`
- W5-006 `37644007798`
- W5-007 `37644007385`
- W5-008 `37644007621`
- W5-009 `37644007585`
- W5-010 `37644007372`
- W6-001 `37644007526`
- W6-002 `37644007821`
- W6-003 `37644007427`
- W6-004 `37644007532`
- W6-005 `37644007540`
- W6-006 `37644007327`
- W6-007 `37644007570`
- W6-008 `37644007610`
- W6-009 `37644007261`
- W6-010 `37644007368`
- W7-002 `37644007477`

The W7-001 workflow did not retrigger because its workflow path filter is scoped
to W7-001 files. Its accepted gate remains unchanged, and W7-001 contract tests
remain covered by the full pytest regression on the W7-002 HEAD.

S08 portable build/smoke PASS.  
S10 real-media + packaged smoke PASS.  
W0 MLT Windows playback/decode/render qualification PASS.

## Next

**S11-W7-003 — strict AutoEditPlan v2 parser/schema only.**

W7-003 must not start the semantic verifier/sequential dry-run translator owned
by W7-004.
