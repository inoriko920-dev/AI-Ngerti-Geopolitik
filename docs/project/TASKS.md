# TASKS

## SF-STEP 08 — DONE / PASS
Repository foundation, exact UI references, Windows CI and portable foundation.

## SF-STEP 09 — DONE / PASS
Real AAVC-derived PySide6 shell and visual evidence.

## SF-STEP 10 — DONE / PASS_WITH_PROVISIONAL
Minimum real E2E backbone.

## SF-STEP 11

### W0 — DONE / PASS
Engine qualification and regression lock.

### W1 — DONE / PASS
Project, Media & Persistence Foundation.

### W2 — DONE / PASS
Timeline, playback and core editing.

### W3 — DONE / PASS

Accepted implementation HEAD:
`79217e687a9930087260e7dd3203b6ab8492b477`

Accepted workflow:
`37545032247` — SUCCESS

- [x] S11-W3-001 inspector context binding by project/track/asset/clip;
- [x] S11-W3-002 video position/scale/rotation/opacity;
- [x] S11-W3-003 crop/basic composition;
- [x] S11-W3-004 audio volume/pan/fade in/out;
- [x] S11-W3-005 brightness/exposure/contrast/saturation/WB/tint;
- [x] S11-W3-006 uniform speed 25%–400% + duration recompute/ripple;
- [x] S11-W3-007 Reverse explicitly disabled because backend qualification is
  not yet safe;
- [x] S11-W3-008 cross-property Undo/Redo + project reload + real preview/output
  evidence.

Additional proof:
- [x] real PySide6 property controls emit semantic intents;
- [x] old schema-v1 clip properties load with safe defaults;
- [x] real W3 preview differs from baseline;
- [x] real 1920×1080 / 30 fps / 180-frame export with audio;
- [x] W3 evidence verifier PASS 8/8;
- [x] S08/S09/S10/W0/W1/W2 regressions all green on accepted HEAD.

Evidence:
`docs/evidence/features/S11_W3_PROPERTIES_VIDEO_AUDIO_COLOR_SPEED.md`.

### W4 — DONE / PASS

**Titles / Transitions / Effects**

Accepted implementation HEAD:
`3e3cd376189e9f183e70ca537ad25f037e25bcd7`

Accepted workflow:
`37570612799` — SUCCESS

- [x] **S11-W4-001 — Canonical title overlay**
  - per-clip enabled/text/font size/position/color/background;
  - title remains distinct from the later full subtitle workspace;
  - state belongs to ProjectState through ClipProperties.
- [x] **S11-W4-002 — Transition semantics**
  - qualified presets: `none` and `fade_black`;
  - duration is frame-based and bounded to the clip;
  - dissolve/crossfade is intentionally not claimed while the canonical
    timeline forbids overlapping clips.
- [x] **S11-W4-003 — Render-backed AAVC effect subset**
  - qualified legacy effects: Fade, Pop, Breathe, Stomp, Tumble, Tectonic,
    Rise, Pan and Drift;
  - unsupported legacy effects remain unavailable rather than fake:
    Wipe, Blur, Succession, Baseline, Neon, Scrapbook, Brush, Ink, Digital,
    Spray Paint, Sketch and Gradient;
  - effect state includes enter/exit, bounded intensity and lock.
- [x] **S11-W4-004 — Semantic UI controls**
  - AAVC-compatible Animation inspector surface;
  - PySide6 emits semantic intents only;
  - no presentation-to-engine/project direct mutation.
- [x] **S11-W4-005 — History and persistence**
  - title/transition/effect mutation through CommandBus/CommandBatch;
  - Undo/Redo across W4 mutations;
  - .angproj save/reopen round-trip;
  - schema-v1 projects without W4 fields load with safe defaults.
- [x] **S11-W4-006 — Real media qualification**
  - preview visibly reflects W4 creative state;
  - export reflects title/transition/effect state;
  - output remains valid and retains audio.
- [x] **S11-W4-007 — Evidence + regression lock**
  - deterministic W4 evidence bundle and verifier PASS 8/8;
  - Ruff format/check, mypy, import contracts, architecture, source-of-truth,
    UI-reference and secret gates PASS;
  - full pytest PASS;
  - W3/W2/W1/W0/S10/S09/S08 all SUCCESS on the same implementation HEAD.

Evidence:
`docs/evidence/features/S11_W4_TITLES_TRANSITIONS_EFFECTS.md`.

Locked boundaries carried forward:
- ProjectState + CommandBus + MediaEnginePort remain canonical;
- MLT remains the primary production-engine implementation candidate;
- FFmpeg remains a real qualification adapter, not a production-engine switch;
- AAVC UI-001..UI-042 remains frozen 1:1;
- Reverse remains disabled;
- dissolve/crossfade remains unsupported until overlap semantics are qualified;
- unsupported legacy W4 effect names must stay unavailable;
- Gemini/AI implementation, SF-STEP 12 and release packaging remain blocked
  until their proper wave/STEP.

### W5 — DONE / PASS_WITH_PROVISIONAL_MIC_HARDWARE

**Subtitle + Narration**

Contract:
`docs/project/W5_SUBTITLE_NARRATION_CONTRACT.md`

Accepted implementation HEAD:
`cb54b544dd8c6977d117bb71e137117830feb061`

W5-010 closure workflow:
`37583174352` — SUCCESS

W5-010 evidence:
`docs/evidence/features/S11_W5_010_CLOSURE_REGRESSION.md`

W5-010 artifact:
`ANG-S11-W5-010-Closure` / ID `11466065855`

Serial contract:
- [x] **S11-W5-001 — Canonical subtitle/narration model — PASS**
- [x] **S11-W5-002 — SRT import + validation — PASS**
- [x] **S11-W5-003 — Cue editing + safe working-copy flow — PASS**
- [x] **S11-W5-004 — Subtitle style — PASS**
- [x] **S11-W5-005 — Render-backed subtitle animation + per-word boundary — PASS**
- [x] **S11-W5-006 — Narration import + binding — PASS**
- [x] **S11-W5-007 — Microphone recording — PASS_WITH_PROVISIONAL_MIC_HARDWARE**
- [x] **S11-W5-008 — Frozen UI parity — PASS**
- [x] **S11-W5-009 — Real subtitle/narration preview/export qualification — PASS**
- [x] **S11-W5-010 — Failure paths + evidence + regression lock — PASS**

W5-010 closure proof:
- subtitle + narration cross-feature Undo/Redo PASS;
- pre-W5 W4 project loads with `subtitle=None` and `narration=None` while
  preserving W4 creative state;
- malformed SRT is rejected without canonical mutation;
- dirty subtitle working-copy reload guard is enforced;
- missing/corrupt narration is rejected without fake success;
- bound narration source missing at runtime cannot create a fake preview;
- failed microphone capture cannot clobber existing narration;
- source SRT and narration media stay byte-identical;
- targeted W5-010 tests 6/6 PASS;
- full pytest PASS;
- W5-010 evidence verifier 9/9 PASS.

Final regression lock on accepted W5 HEAD:
- W5-010 `37583174352` — SUCCESS;
- W5-009 `37583174359` — SUCCESS;
- W5-008 `37583174310` — SUCCESS;
- W5-007 `37583174255` — SUCCESS, attempt 2;
- W5-006 `37583174384` — SUCCESS, attempt 2;
- W5-005 `37583174296` — SUCCESS;
- W5-004 `37583174275` — SUCCESS;
- W4 `37583174301` — SUCCESS;
- W3 `37583174280` — SUCCESS;
- W2 `37583174363` — SUCCESS, attempt 2;
- W1 `37583174318` — SUCCESS;
- W0 `37583174261` — SUCCESS;
- S10 `37583174258` — SUCCESS, attempt 2;
- S09 `37583174265` — SUCCESS;
- S08 `37583174297` — SUCCESS.

The second attempts above were required only because the Chocolatey community
feed returned HTTP 504 while installing FFmpeg. No product-code change was made
for that external outage.

Final W5 status is **PASS_WITH_PROVISIONAL_MIC_HARDWARE**, not full PASS,
because the GitHub Windows runner exposes 0 DirectShow audio input devices.
The software recording path and its safety/failure behavior are PASS; physical
microphone capture remains unproven and is not faked.

Hard boundaries remain:
- no ASR/transcription/speech-alignment claim;
- only render-proven subtitle animations are enabled;
- W4 unsupported effects/crossfade stay unavailable;
- Reverse stays disabled;
- FFmpeg remains qualification adapter; MLT remains production-engine candidate;
- Gemini/provider/AI work and SF-STEP 12 remain blocked until their proper
  contracted wave/STEP.

**Next:** W6 is now contract-locked below. Continue only by its serial task order.


### W6 — CLOSED / PASS_WITH_PROVISIONAL_LIVE_GEMINI

**Gemini Credential + L1 AI Animation Planning**

Derived from frozen Master Blueprint TECH-WAVE STEP 09 immediately after the
completed Subtitle + Narration wave.

Contract:
`docs/project/W6_GEMINI_CREDENTIAL_L1_AI_CONTRACT.md`

Planning source:
- `docs/planning/09_S11_W6_GEMINI_CREDENTIAL_L1_AI_CONTRACT_PLAN_2026-10-07.txt`
- `docs/planning/09_S11_W6_GEMINI_CREDENTIAL_L1_AI_CONTRACT_PLAN_2026-10-07.docx`

Accepted W6-001 implementation HEAD:
`160a320768e4d4b788bc9e2bc9e4174569a32f31`

W6-001 workflow:
`37591531616` — SUCCESS

W6-001 evidence:
`docs/evidence/features/S11_W6_001_AI_CREDENTIAL_CONTRACTS.md`

Serial contract:
- [x] **S11-W6-001 — Canonical AI + credential contracts — PASS**
- [x] **S11-W6-002 — Secure credential slots 1–100 — PASS**
- [x] **S11-W6-003 — Windows secure-store qualification — PASS**
- [x] **S11-W6-004 — Credential health + safe failover — PASS**
- [x] **S11-W6-005 — L1 ContextBuilder + allowlist — PASS**
- [x] **S11-W6-006 — EditPlan schema + PlanVerifier — PASS**
- [x] **S11-W6-007 — Gemini adapter + async lifecycle — PASS**
- [x] **S11-W6-008 — Approval → CommandBatch → Undo/Redo — PASS**
- [x] **S11-W6-009 — Frozen UI parity — PASS**
- [x] **S11-W6-010 — Live Gemini + failure + regression closure — PASS_WITH_PROVISIONAL_LIVE_GEMINI**

Locked boundaries:
- Gemini is the only W6 provider;
- AI L1 may plan only render-qualified W4 effects;
- no direct AI mutation of ProjectState/JSON/engine;
- credential slots 1..100 live outside ProjectState in secure OS storage;
- no raw credential may reach repo/project/log/error/evidence/UI after save;
- no quota/rate-limit circumvention;
- no AI L2, Validation hardening, Export matrix or SF-STEP 12 in W6;
- full live-provider PASS requires a real Gemini smoke; otherwise the final
  W6 status must retain a provisional live-Gemini qualifier.

W6-001 proof:
- AIProviderPort + CredentialPort are application-layer, provider-agnostic ports;
- raw credential is represented by a transient masked CredentialSecret wrapper;
- logical slot references reject outside 1..100;
- EditPlan is revision-bound and can express only typed L1 effect proposals;
- L1 proposal shape has no lock/title/timeline/shell mutation fields;
- W6 L1 allowlist is locked to the render-qualified W4 effects;
- provider request DTO deliberately has no credential/api_key/secret field;
- typed credential/provider/plan errors and provider-agnostic job states are locked;
- targeted W6-001 tests 10/10 PASS;
- full pytest PASS;
- Ruff/mypy/import-contract/architecture/source-of-truth/security/UI-reference gates PASS;
- W5/W4/W3/W2/W1/W0/S10/S09/S08 regressions are green on the accepted HEAD;
- S10 packaged-smoke required attempt 2 only because Chocolatey returned HTTP 504
  while fetching FFmpeg; no product-code change was required.

Accepted W6-002 implementation HEAD:
`7a3f3551b9080347c64ab53cca0be4ee646c41ed`

W6-002 workflow:
`37593139064` — SUCCESS

W6-002 evidence:
`docs/evidence/features/S11_W6_002_CREDENTIAL_SLOTS.md`

W6-002 artifact:
`ANG-S11-W6-002-Credential-Slots` / ID `11469631614`

W6-002 proof:
- slot 1 and 100 supported; 0/101 rejected;
- non-secret metadata uses slot/label/enabled + fixed masked marker;
- add/update/delete/enable/disable/mask service PASS;
- deterministic in-memory secret+metadata backend PASS;
- raw secret absent from ProjectState, .angproj and safe diagnostics;
- metadata label may not contain the credential value;
- delete removes secret + metadata consistently;
- targeted tests 9/9 PASS;
- full pytest PASS;
- evidence verifier 5/5 PASS;
- W6-001/W5/W4/W3/W2/W1/W0/S10/S09/S08 all SUCCESS on the accepted HEAD.

Accepted W6-003 implementation HEAD:
`84e8ef7ce30be24875c37faaa8dd94ab9a6d3c7f`

W6-003 workflow:
`37594820105` — SUCCESS

W6-003 evidence:
`docs/evidence/features/S11_W6_003_WINDOWS_SECURE_STORE.md`

W6-003 artifact:
`ANG-S11-W6-003-Windows-Secure-Store` / ID `11470101865`

W6-003 proof:
- production Windows Generic Credential adapter behind CredentialPort;
- native CredWriteW/CredReadW/CredDeleteW via ctypes;
- slot 1 and slot 100 real Windows round-trip PASS;
- fresh adapter reopen reads both slots;
- delete removes secure secret + non-secret metadata;
- load-after-delete returns safe typed NO_CREDENTIAL;
- raw secrets absent from evidence/diagnostics;
- secure-store targets cleaned after smoke;
- targeted tests 7/7 PASS;
- full pytest PASS;
- evidence verifier 4/4 PASS;
- W6-002/W6-001/W5/W4/W3/W2/W1/W0/S10/S09/S08 all SUCCESS on the same HEAD.

Accepted W6-004 implementation HEAD:
`2ebe3fbd89e0cbbf62135a44bb2e4193c4906e32`

W6-004 workflow:
`37602706734` — SUCCESS

W6-004 evidence:
`docs/evidence/features/S11_W6_004_CREDENTIAL_HEALTH_SAFE_FAILOVER.md`

W6-004 artifact:
`ANG-S11-W6-004-Credential-Health-Safe-Failover` / ID `11472879781`

W6-004 proof:
- non-secret credential health/test state machine;
- invalid auth disables only the affected slot;
- bounded same-slot network retry then bounded failover;
- rate/quota provider-wide cooldown blocks immediate credential rotation;
- typed all-slots-unavailable behavior;
- malformed/non-credential provider failures do not rotate;
- bulk TXT trim/dedupe/max100/count-only preview/no-retention boundary;
- raw runtime secrets absent from evidence;
- targeted tests 10/10 PASS;
- full pytest PASS;
- evidence verifier 18/18 PASS;
- W6-003/W6-002/W6-001/W5/W4/W3/W2/W1/W0/S10/S09/S08 all SUCCESS on the same HEAD.

Accepted W6-005 implementation HEAD:
`043f8f250b7d61356bdf71757e8c6a7904615a06`

W6-005 workflow:
`37604630826` — SUCCESS

W6-005 evidence:
`docs/evidence/features/S11_W6_005_L1_CONTEXT_BUILDER.md`

W6-005 artifact:
`ANG-S11-W6-005-L1-Context-Builder` / ID `11474213026`

W6-005 proof:
- bounded deterministic context, max 20 selected clips;
- stable clip/track IDs + current revision;
- media type/dimensions/aspect ratio only;
- current effect/intensity + effect/track/effective lock;
- exact W4 render-qualified effect allowlist + 0..200 intensity range;
- bounded previous/next neighbor summary;
- project text normalized and marked untrusted;
- credential/path/source-name/fingerprint/title/subtitle/narration/log/engine data excluded;
- project state remains byte/semantic unchanged;
- targeted tests 10/10 PASS;
- full pytest PASS;
- evidence verifier 23/23 PASS;
- W6-004/W6-003/W6-002/W6-001/W5/W4/W3/W2/W1/W0/S10/S09/S08 all SUCCESS on the same HEAD.

Accepted W6-006 implementation HEAD:
`571cf941e64124628d1f8dadafb022eb20c0a541`

W6-006 workflow:
`37606369024` — SUCCESS

W6-006 evidence:
`docs/evidence/features/S11_W6_006_EDITPLAN_PLAN_VERIFIER.md`

W6-006 artifact:
`ANG-S11-W6-006-EditPlan-PlanVerifier` / ID `11475207107`

W6-006 proof:
- strict exact-field EditPlan JSON parser;
- maximum 20 L1 commands;
- fixed set_clip_effects command family;
- unknown root/command/type rejected;
- target existence + selected-scope gate;
- W4 effect/range validation;
- track/effect lock enforcement;
- stale revision + request-ID correlation;
- dry-run through manual W4 SetClipPropertiesCommand;
- live ProjectState and CommandBus history remain unchanged;
- targeted tests 12/12 PASS;
- full pytest PASS;
- evidence verifier 24/24 PASS;
- W6-005/W6-004/W6-003/W6-002/W6-001/W5/W4/W3/W2/W1/W0/S10/S09/S08 all SUCCESS on the same HEAD.

Accepted W6-007 implementation HEAD:
`70fa8cd6f800166176889068202ab53d03044b24`

W6-007 workflow:
`37609729091` — SUCCESS

W6-007 evidence:
`docs/evidence/features/S11_W6_007_GEMINI_ASYNC_LIFECYCLE.md`

W6-007 artifact:
`ANG-S11-W6-007-Gemini-Async-Lifecycle` / ID `11477281563`

W6-007 proof:
- official google-genai 2.28.0 runtime locked by uv;
- Gemini adapter behind AIProviderPort;
- async structured JSON provider request;
- provider work off caller/Qt GUI thread;
- cancellation/timeout/typed safe provider errors;
- W6-004 retry/failover/cooldown reuse;
- stale project/session/revision guard;
- one-time verified result consumption;
- no credential in prompt/context/snapshot;
- no CommandBus/canonical mutation;
- targeted tests 17/17 PASS;
- full pytest PASS;
- evidence verifier 11/11 PASS;
- W6-006/W6-005/W6-004/W6-003/W6-002/W6-001/W5/W4/W3/W2/W1/W0/S10/S09/S08 all SUCCESS on the same HEAD;
- live Gemini network qualification remains W6-010.

Accepted W6-008 implementation HEAD:
`544bbde03a55c673e26b5e933b04c23b5336ba42`

W6-008 workflow:
`37613133911` — SUCCESS

W6-008 evidence:
`docs/evidence/features/S11_W6_008_APPROVAL_COMMANDBATCH_UNDO_REDO.md`

W6-008 artifact:
`ANG-S11-W6-008-Approval-CommandBatch` / ID `11479655608`

W6-008 proof:
- verified W6-007 result consumed once into explicit approval lifecycle;
- staging/approval/reject/cancel zero canonical mutation;
- stale project/revision/semantic re-check immediately before apply;
- W6-006 PlanVerifier re-runs before mutation;
- sequential translation to existing W4 SetClipPropertiesCommand;
- one approved plan = one atomic AI CommandBatch/history entry;
- exact semantic Undo/Redo;
- duplicate stage/apply protection;
- targeted tests 9/9 PASS;
- full pytest PASS;
- evidence verifier 15/15 PASS;
- W6-007/W6-006/W6-005/W6-004/W6-003/W6-002/W6-001/W5/W4/W3/W2/W1/W0/S10/S09/S08 all SUCCESS on the same HEAD, all attempt 1.

**Exact next task:** S11-W6-009 only — Frozen UI parity.


#### W6-009 closure

Accepted W6-009 implementation HEAD:
`7a2d79115e376205571bf529624993ed5fcc5f9f`

Accepted workflow:
`37620520208` — SUCCESS

Evidence:
`docs/evidence/features/S11_W6_009_FROZEN_UI_PARITY.md`

Artifact:
`ANG-S11-W6-009-Frozen-UI` / ID `11481533239`

Proof:
- real AI Director / AI Agent / Provider & API Key PySide6 widgets;
- semantic UI intents only;
- READY/PLAN/APPROVAL/APPLYING/SUCCESS/PROVIDER_ERROR/LOCK_CONFLICT/STALE;
- L1-only capability claims;
- saved credential masking;
- physical frozen mapping UI-020/021/022/023/024/033 audited and recorded;
- targeted Qt tests 8/8 PASS;
- full pytest PASS;
- evidence verifier 15/15 PASS;
- 24/24 regression workflows SUCCESS on accepted HEAD;
- S10 packaged smoke succeeded on retry after external Chocolatey HTTP 504;
- S08 security/dependency + portable foundation PASS.

#### W6-010 closure

Accepted implementation HEAD:
`0915a7045014e5ea1209f933dd703d6601ff26e9`

Accepted workflow:
`37628909459` — SUCCESS

Evidence:
`docs/evidence/features/S11_W6_010_LIVE_FAILURE_REGRESSION_CLOSURE.md`

Artifact:
`ANG-S11-W6-010-Closure` / ID `11485567340`

Proof:
- targeted closure tests 6/6 PASS;
- full pytest PASS;
- AI-selected Rise/intensity 120 produces a different rendered preview;
- invalid auth / quota / malformed / lock / stale paths remain safe;
- exact one-transaction Undo/Redo;
- regression matrix 25/25 SUCCESS, all attempt 1;
- live credential unavailable, so live network request was not attempted;
- final W6 status is PASS_WITH_PROVISIONAL_LIVE_GEMINI.

### W7 — AI Auto Edit L2 — CONTRACT_LOCKED

Planning:
- `docs/planning/10_S11_W7_AI_AUTO_EDIT_L2_CONTRACT_PLAN_2026-10-07.docx`
- `docs/planning/10_S11_W7_AI_AUTO_EDIT_L2_CONTRACT_PLAN_2026-10-07.txt`
- `docs/project/W7_AI_AUTO_EDIT_L2_CONTRACT.md`

Initial allowlist:
- set_clip_effects;
- set_clip_duration;
- set_clip_speed;
- set_clip_transform;
- set_clip_transition.

Serial contract:
- [x] **S11-W7-001 — Canonical L2 command contracts + capability registry — PASS**
- [x] **S11-W7-002 — L2 ContextBuilder + selected-scope contract — PASS**
- [x] **S11-W7-003 — Strict AutoEditPlan v2 parser/schema — PASS**
- [x] **S11-W7-004 — L2 semantic verifier + sequential dry-run translator — PASS**
- [x] **S11-W7-005 — Pacing qualification: duration + speed — PASS**
- [x] **S11-W7-006 — Transform qualification — PASS**
- [x] **S11-W7-007 — Transition + mixed-plan qualification — PASS**
- [ ] **S11-W7-008 — Gemini L2 request profile + lifecycle reuse — READY**
- [ ] **S11-W7-009 — Approval/apply/UI diff integration — BLOCKED_BY_W7_008**
- [ ] **S11-W7-010 — Real-media closure + failure/regression lock — BLOCKED_BY_W7_009**

Locked safety boundaries:
- selected scope max 20 clips;
- plan max 40 commands;
- no structural/destructive Auto Edit in initial W7;
- no crop/reverse/crossfade;
- no subtitle/narration/export/credential/path mutation;
- reuse W6 provider/credential/approval owners;
- strict schema + hard reject unknowns;
- one approved plan = one atomic CommandBatch + one Undo/Redo transaction.

Accepted W7-001 implementation HEAD:
`f301c10a16ba33e051ef97e9d166262b7fbac327`

W7-001 workflow:
`37640973646` — SUCCESS

W7-001 evidence:
`docs/evidence/features/S11_W7_001_L2_CONTRACTS.md`

W7-001 artifact:
`ANG-S11-W7-001-L2-Contracts` / ID `11491927299`

W7-001 proof:
- exact five-capability registry tied to existing manual commands;
- AutoEditPlan schema v2 DTO contract;
- max 20 targets / 40 commands;
- typed duration/speed/transform/transition policy bounds;
- duplicate family and duration/speed conflict rejection;
- W6 schema v1 + effect allowlist backward compatibility;
- targeted tests 27/27 PASS;
- full pytest PASS;
- evidence verifier 18/18 PASS;
- 26/26 regression workflows SUCCESS on the same HEAD, all attempt 1.

Accepted W7-002 implementation HEAD:
`23aad912cb789f98dd3ec61d11e799390d602381`

W7-002 workflow:
`37644007477` — SUCCESS

W7-002 evidence:
`docs/evidence/features/S11_W7_002_L2_CONTEXT.md`

W7-002 artifact:
`ANG-S11-W7-002-L2-Context` / ID `11494315331`

W7-002 proof:
- selected scope 1..20 stable unique clip IDs;
- deterministic schema-v2 context;
- source-duration availability and bounded neighbor context;
- exact W7 policy/allowlist;
- credentials/paths/private content excluded;
- zero mutation;
- targeted 18/18 PASS;
- full pytest PASS;
- evidence verifier 24/24 PASS;
- 26/26 triggered regression workflows SUCCESS, all attempt 1.

Accepted W7-003 implementation HEAD:
`a57c8acd96cdcff8b20f659171229ad0bff913d0`

W7-003 workflow:
`37647150710` — SUCCESS

W7-003 evidence:
`docs/evidence/features/S11_W7_003_L2_PARSER.md`

W7-003 artifact:
`ANG-S11-W7-003-L2-Parser` / ID `11494393982`

W7-003 proof:
- closed canonical JSON Schema v2;
- strict exact root fields;
- five exact command shapes;
- 1..40 commands;
- bool-as-int rejection;
- unknown root/command/field rejection;
- ripple/crop/unlock/crossfade extra fields rejected;
- W7-001 typed DTO construction;
- no ProjectState/CommandBus/provider/UI/apply work;
- targeted tests 41/41 PASS;
- full pytest PASS;
- evidence verifier 24/24 PASS;
- 26/26 triggered regression workflows SUCCESS, all attempt 1.

Accepted W7-004 implementation HEAD:
`05bbf416e3f4440b23b23a8912aa86e2d1a39d44`

W7-004 workflow:
`37650364257` — SUCCESS

W7-004 evidence:
`docs/evidence/features/S11_W7_004_L2_SEMANTIC_VERIFIER.md`

W7-004 artifact:
`ANG-S11-W7-004-L2-Verifier` / ID `11496527057`

W7-004 proof:
- stale/scope/target/lock semantic gates;
- dynamic duration/source/canvas/transition policy;
- exact existing manual command translation;
- application-owned pacing ripple;
- sequential dry-run with candidate transition revalidation;
- candidate semantic hash proof;
- zero canonical mutation/history;
- targeted tests 24/24 PASS;
- full pytest PASS;
- evidence verifier 23/23 PASS;
- 26/26 triggered workflows SUCCESS, all attempt 1.

Accepted W7-005 implementation HEAD:
`e00ad734833ceac4f32f42e5363f5b8b5c203212`

W7-005 workflow:
`37653613643` — SUCCESS

W7-005 evidence:
`docs/evidence/features/S11_W7_005_PACING_QUALIFICATION.md`

W7-005 artifact:
`ANG-S11-W7-005-L2-Pacing` / ID `11498316525`

W7-005 proof:
- existing W7 verifier/manual duration+speed command path reused;
- application-owned ripple=true;
- real duration qualification 60→90 frames, timeline 210 frames;
- real speed 200% timeline 150 frames;
- real speed 50% timeline 240 frames;
- speed-aware preview source mapping 15→30 / 7;
- baseline/fast/slow real previews distinct;
- all real exports retain audio;
- source media unchanged;
- canonical state/revision/CommandBus history unchanged;
- targeted tests 6/6 PASS;
- full pytest PASS;
- evidence verifier 11/11 files PASS;
- 26/26 regression workflows SUCCESS on the same HEAD, all attempt 1.

Accepted W7-006 implementation HEAD:
`7ba2640068e5e5c0d153bd3c1bd304bc1be64f06`

W7-006 workflow:
`37656965367` — SUCCESS

W7-006 evidence:
`docs/evidence/features/S11_W7_006_TRANSFORM_QUALIFICATION.md`

W7-006 artifact:
`ANG-S11-W7-006-L2-Transform` / ID `11498533256`

W7-006 proof:
- existing W7-004 transform translation reused through canonical SetClipPropertiesCommand;
- real position, scale, rotation and opacity previews are distinct from baseline;
- composite transform real export PASS with audio retained;
- uniform scale maps to equal X/Y scale;
- crop and unspecified transform fields are preserved;
- verifier candidate hash matches translated candidate hash;
- source media and canonical state/revision/CommandBus history unchanged;
- targeted tests 5/5 PASS;
- full pytest PASS;
- evidence verifier 9/9 files PASS;
- 28/28 triggered workflows SUCCESS on the accepted HEAD, all attempt 1;
- S08 portable build/smoke, S09 UI shell, S10 packaged real-media and W0 engine gates PASS.

Accepted W7-007 implementation HEAD:
`642ce15c89b3a0e65011387d67f9898d0cd1f542`

W7-007 workflow:
`37667149646` — SUCCESS

W7-007 evidence:
`docs/evidence/features/S11_W7_007_TRANSITION_MIXED_QUALIFICATION.md`

W7-007 artifact:
`ANG-S11-W7-007-L2-Transition-Mixed` / ID `11503996235`

W7-007 proof:
- canonical SetClipPropertiesCommand + TransitionProperties reused for transitions;
- real fade_black preview/export PASS with audio retained;
- none transition clears fade_black;
- sequential candidate transition maximum proven after speed change;
- six-command mixed L1/L2 plan qualified across effects/duration/transform/transition/speed;
- mixed real export 210 frames with audio retained;
- verifier candidate hashes match translated candidates;
- canonical state/revision/CommandBus history and source media unchanged;
- targeted tests 5/5 PASS;
- full pytest 361/361 PASS;
- evidence verifier 8/8 files PASS;
- 26/26 triggered workflow families SUCCESS;
- 23 attempt 1, 3 attempt 2 only after transient Chocolatey HTTP 504 during FFmpeg install;
- S08/S10 and prior W0..W7 regression families PASS.

**Exact next task:** S11-W7-008 only — Gemini L2 request profile + lifecycle reuse.
