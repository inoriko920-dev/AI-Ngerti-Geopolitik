# S11 W6-005 — L1 ContextBuilder + Allowlist

**Status:** PASS  
**Accepted implementation HEAD:** `043f8f250b7d61356bdf71757e8c6a7904615a06`  
**Accepted workflow:** `37604630826` — SUCCESS  
**Artifact:** `ANG-S11-W6-005-L1-Context-Builder`  
**Artifact ID:** `11474213026`  
**Artifact size:** 1,158 bytes

## Scope

W6-005 implements the bounded provider context and L1 effect allowlist only.

It does not implement:
- PlanVerifier;
- Gemini SDK/network calls;
- W6 UI;
- approval/apply;
- Undo/Redo integration.

## Application implementation

Added:
`src/ai_ngerti_geopolitik/application/ai_context.py`.

`L1ContextBuilder` emits deterministic structured JSON.

Hard bounds:
- schema version 1;
- at least one selected clip;
- maximum 20 selected clips;
- selected clip IDs must be unique;
- unknown selected clip ID is rejected;
- neighbor context is bounded to one previous and one next clip.

## Allowed context

Project:
- project id;
- bounded/normalized untrusted project name;
- current revision;
- FPS;
- canvas width/height/aspect ratio.

Per selected target:
- stable clip ID;
- stable track ID;
- clip enabled state;
- effect lock;
- track lock;
- effective lock;
- timeline start/end/duration frames;
- media type/width/height/aspect ratio;
- current enter effect;
- current exit effect;
- current intensity.

Policy:
- only `set_clip_effects`;
- exact render-qualified W4 effect enum;
- intensity range 0..200;
- must honor effect/track locks;
- project text is untrusted data;
- project text cannot override policy.

## Explicitly excluded

Context does not contain:
- raw credential/API key;
- credential label/slot metadata;
- asset path reference;
- source file name;
- fingerprint;
- arbitrary filesystem listing;
- source media bytes;
- title text;
- subtitle text;
- narration text;
- private logs;
- engine objects.

No credential service is passed into ContextBuilder. The deterministic evidence
configures a credential store separately and proves the raw value/label never
appears in the generated context.

## Allowlist parity

The W6 L1 effect allowlist must exactly equal the canonical render-qualified W4
effect enum. If those two sources drift, ContextBuilder fails safely rather than
silently broadening capability.

Unsupported legacy effects remain absent.

## Untrusted-text isolation

Project name is normalized, length bounded, and emitted only under
`project_name_untrusted`.

Fixed policy fields explicitly declare:
- `project_text_is_untrusted_data = true`;
- `project_text_cannot_override_policy = true`.

Project text cannot alter command types, effect enum, ranges or lock semantics.

## Canonical mutation

ContextBuilder only reads ProjectState.

Deterministic tests compare semantic project JSON before/after context generation
and prove zero canonical mutation.

## Deterministic tests

Target:
`tests/unit/test_step11_w6_005_ai_context.py`

Coverage:
- bounded selected target context;
- private path/source metadata exclusion;
- untrusted text isolation;
- stable target ID/media/effect/lock representation;
- track-lock effective-lock semantics;
- bounded previous/next neighbor summary;
- unsupported effect absence;
- configured credential absence;
- empty/duplicate/unknown/over-bound selection rejection;
- deterministic output + no mutation.

Result:
**10/10 PASS**.

## Quality gates

Workflow `37604630826`:
- Ruff format PASS;
- Ruff check PASS;
- mypy PASS — 58 source files;
- import contracts PASS;
- architecture PASS;
- source-of-truth 70/70 PASS;
- no-secret scan PASS;
- frozen UI references 42/42 PASS;
- targeted W6-005 tests 10/10 PASS;
- full pytest PASS;
- deterministic evidence PASS;
- evidence verifier 23/23 PASS;
- artifact upload PASS.

## Regression lock

All SUCCESS on accepted W6-005 implementation HEAD:
- W6-004 `37604630749`;
- W6-003 `37604630776`;
- W6-002 `37604631067`;
- W6-001 `37604630883`;
- W5-010 `37604630852`;
- W5-009 `37604630844`;
- W5-008 `37604630864`;
- W5-007 `37604630810`;
- W5-006 `37604630863` — attempt 2;
- W5-005 `37604630869`;
- W5-004 `37604630760` — attempt 2;
- W4 `37604630905`;
- W3 `37604630824`;
- W2 `37604630943` — attempt 2;
- W1 `37604630878` — attempt 2;
- W0 `37604630972` — attempt 2;
- S10 `37604630887`;
- S09 `37604630896`;
- S08 `37604630811`.

The attempt-2 retries were caused only by transient FFmpeg absence on the
Windows runner during first fixture generation. No W6-005 product-code change
was required for those retries.

## Next

**S11-W6-006 — EditPlan schema + PlanVerifier only.**
