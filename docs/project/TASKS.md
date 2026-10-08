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

### W7 — AI Auto Edit L2 — CLOSED / PASS_WITH_PROVISIONAL_LIVE_GEMINI

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
- [x] **S11-W7-008 — Gemini L2 request profile + lifecycle reuse — PASS**
- [x] **S11-W7-009 — Approval/apply/UI diff integration — PASS**
- [x] **S11-W7-010 — Real-media closure + failure/regression lock — PASS**

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

Accepted W7-008 implementation HEAD:
`fa142e4d7eee21f79f79837339e76dfb974b8ba8`

W7-008 workflow:
`37671042698` — SUCCESS

W7-008 evidence:
`docs/evidence/features/S11_W7_008_GEMINI_L2_LIFECYCLE.md`

W7-008 artifact:
`ANG-S11-W7-008-Gemini-L2-Lifecycle` / ID `11505072385`

W7-008 proof:
- one shared Gemini provider supports L1 schema v1 and L2 schema v2 profiles;
- frozen W6 AIProviderRequest remains exactly four dataclass fields;
- L2AIProviderRequest selects the L2 profile without adding fields;
- same AIPlanJobService, CredentialPoolService, cancellation and error taxonomy reused;
- L2 provider response verified by AutoEditPlanVerifier + W7SelectedScope;
- profile-specific result access prevents L1/L2 result confusion;
- invalid-auth failover, cancellation and stale session gates reused;
- canonical ProjectState unchanged;
- no W7-009 approval/apply/UI work started;
- targeted tests 9/9 PASS;
- full pytest 370/370 PASS;
- evidence verifier 1/1 PASS;
- 26/26 triggered workflow families SUCCESS, all attempt 1;
- S08/S09/S10 and prior W0..W7 regression families PASS.

Accepted W7-009 implementation HEAD:
`2eef5762454f367c2fad5550f75209f8ffeb0a16`

W7-009 workflow:
`37673518251` — SUCCESS

W7-009 evidence:
`docs/evidence/features/S11_W7_009_APPROVAL_APPLY_UI_DIFF.md`

W7-009 artifact:
`ANG-S11-W7-009-Approval-UI-Diff` / ID `11505484572`

W7-009 proof:
- existing W6 AIPlanApprovalService remains the only approval owner;
- successful verified L2 result stages without canonical mutation/history;
- six bounded before→after diff lines are generated from the exact candidate path;
- explicit approval is required before apply;
- final stale/hash/semantic revalidation runs before canonical mutation;
- approved mixed six-command plan executes as one CommandBatch(actor="ai");
- apply increments revision exactly once;
- one Undo restores pre-AI semantic state;
- one Redo restores applied semantic state;
- reject/cancel create no history;
- duplicate apply is rejected;
- same-revision semantic replacement is stale;
- existing W6 AI Agent surface gains L2 mode + diff review without a new screen/layout;
- L1 UI submit behavior remains backward-compatible;
- targeted tests 8/8 PASS;
- full pytest 386/386 PASS;
- evidence verifier 2/2 files PASS;
- 26/26 triggered workflow families SUCCESS, all attempt 1;
- S08/S09/S10/W0 and prior W1..W7 gates PASS.

Accepted W7-010 final implementation HEAD:
`ca6dd582a4916caa4b0ac4affe4c3119e9ad2049`

W7-010 workflow:
`37675538957` — SUCCESS

W7-010 evidence:
`docs/evidence/features/S11_W7_010_REAL_MEDIA_FAILURE_REGRESSION_CLOSURE.md`

W7-010 artifact:
`ANG-S11-W7-010-Closure` / ID `11507307240`

W7-010 proof:
- integrated L2 context/provider/verifier/approval/apply chain PASS;
- mixed real-media export = 210 frames with audio retained;
- real transform/effect/fade_black/pacing PASS;
- save/reopen semantic hash and rendered preview exact;
- one atomic apply, one exact Undo, one exact Redo;
- invalid/out-of-range/out-of-scope/locked/stale/provider failures are safe;
- targeted tests 8/8 PASS;
- full pytest 386/386 PASS;
- evidence verifier 9/9 files PASS;
- final regression lock 27/27 workflow families SUCCESS, all attempt 1;
- S08/S09/S10/W0 and earlier waves PASS;
- no live Gemini network success claimed.

**W7 final status:** CLOSED / PASS_WITH_PROVISIONAL_LIVE_GEMINI.

**Next:** ASTRA planning only for the next wave mapped to Master Blueprint
TECH-WAVE STEP 11 — Validation/recovery/diagnostics hardening. Detailed planning
DOCX is required before SOL implementation; next wave has not started.


### W8 — Validation / Recovery / Diagnostics Hardening — CONTRACT_LOCKED

Planning:
- `docs/planning/11_S11_W8_VALIDATION_RECOVERY_DIAGNOSTICS_HARDENING_CONTRACT_PLAN_2026-10-08.docx`
- `docs/planning/11_S11_W8_VALIDATION_RECOVERY_DIAGNOSTICS_HARDENING_CONTRACT_PLAN_2026-10-08.txt`
- `docs/project/W8_VALIDATION_RECOVERY_DIAGNOSTICS_CONTRACT.md`

Master Blueprint mapping: **TECH-WAVE STEP 11**.

Serial contract:
- [x] **S11-W8-001 — Canonical Validation Contracts + Baseline Rules — PASS**
- [x] **S11-W8-002 — Real Media Integrity + Validation Center Projection — PASS**
- [x] **S11-W8-003 — Single Asset Relink Command + Exact Identity Preservation — PASS**
- [x] **S11-W8-004 — Batch Directory Relink Scan + Candidate Ranking — PASS**
- [x] **S11-W8-005 — Autosave Catalog + Retention Hardening — PASS**
- [x] **S11-W8-006 — Crash Marker + Startup Recovery Decision — PASS**
- [x] **S11-W8-007 — Atomic Persistence Failure Injection + Remediation — PASS**
- [x] **S11-W8-008 — Stale Result Hardening for W8 Background Jobs — PASS**
- [x] **S11-W8-009 — Structured Diagnostics + Redacted Diagnostic Bundle — PASS**
- [x] **S11-W8-010 — Frozen UI Wiring + GOLDEN-03 Recovery/Relink Closure + Regression Lock — PASS**

Locked boundaries:
- build on existing ProjectState/CommandBus/ProjectSession/JsonProjectRepository;
- validation results are transient, not canonical project state;
- relink preserves Axxx identity and requires verified candidate + explicit confirmation;
- filename similarity alone never auto-relinks;
- recovery never silently overwrites source;
- max 20 managed autosave snapshots/project by default;
- W8 background jobs use project/session/revision stale safety;
- diagnostic bundle is redacted/no raw secret/full content/media bytes by default;
- UI-039/UI-040/UI-041 are reused without redesign;
- STEP 12 export matrix is outside W8.

Accepted W8-001 implementation HEAD:
`fd319947ea8ce2579de4918b5c4b49c046851609`

W8-001 workflow:
`37681708473` — SUCCESS

W8-001 evidence:
`docs/evidence/features/S11_W8_001_CANONICAL_VALIDATION_CONTRACTS.md`

W8-001 artifact:
`ANG-S11-W8-001-Validation-Contracts` / ID `11509960710`

W8-001 proof:
- frozen typed ValidationIssue/ValidationResult contracts;
- deterministic non-mutating ValidationService;
- ProjectState.validate() remains structural authority;
- referenced missing BLOCKER;
- referenced offline ERROR;
- unreferenced missing WARNING;
- unreferenced offline INFO;
- exact Asset/Clip/Narration target IDs;
- revision/project/same-revision semantic stale detection;
- targeted tests 9/9 PASS;
- full pytest 395/395 PASS;
- evidence verifier 22/22 PASS;
- regression 27/27 workflow families SUCCESS, all attempt 1;
- S08/S09/S10/W0 and W1–W7 remain green.

Accepted W8-002 implementation HEAD:
`c73a38d8fd6d3796f988769ca43354185eb66a6d`

W8-002 workflow:
`37684517658` — SUCCESS

W8-002 evidence:
`docs/evidence/features/S11_W8_002_REAL_MEDIA_VALIDATION_CENTER.md`

W8-002 artifact:
`ANG-S11-W8-002-Real-Media-Validation` / ID `11510448492`

W8-002 proof:
- real ffprobe-backed integrity inspection;
- physical missing / zero-byte / probe-failure typed issues;
- type/fingerprint mismatch typed;
- duplicate fingerprint INFO projection;
- zero ProjectState mutation;
- frozen UI-041 real projection without redesign;
- stale projection disables issue action and keeps Validasi Ulang enabled;
- targeted 7/7 PASS;
- full pytest 402/402 PASS;
- mypy 71 source files PASS;
- evidence 18/18 PASS;
- regression 27/27 SUCCESS, all attempt 1.

**Accepted W8-003 implementation/regression HEAD:** `25e5f6cefbbef5f554bd17e64d50a61db948bf13`

**W8-003 workflow:** `37689420848` — SUCCESS

**W8-003 artifact:** `ANG-S11-W8-003-Single-Asset-Relink` / ID `11513225118`

**W8-003 evidence:** `docs/evidence/features/S11_W8_003_SINGLE_ASSET_RELINK.md`

**W8-003 proof:**
- validated manual single-asset relink through canonical CommandBatch / CommandBus;
- exact Asset ID and clip references preserved;
- wrong media type, fingerprint, duration, dimensions and audio metadata fail safely with zero mutation;
- path already owned by another asset is rejected;
- missing source -> renamed relocated media -> verified rebind -> validation clears;
- one revision on apply, exact Undo and Redo, exact .angproj save/reopen;
- no batch scan, ranking, recovery flow or frozen UI redesign in W8-003;
- targeted tests **9/9 PASS**, full pytest **411/411 PASS**;
- real-media evidence verifier **23/23 PASS**;
- Windows CI lint, mypy, architecture, source-of-truth, secret and UI 42/42 gates PASS;
- full main-HEAD regression **27/27 workflow families SUCCESS**, all attempt 1.

**W8-004 implementation HEAD:** `4988e84ca6bca1e64fc5a755ff0d3287802e70f8`

**W8-004 accepted — PASS**

**Accepted W8-004 implementation/regression HEAD:** `4988e84ca6bca1e64fc5a755ff0d3287802e70f8`  
**Dedicated Windows workflow:** [37721840504](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37721840504) — SUCCESS  
**Artifact:** `ANG-S11-W8-004-Batch-Directory-Relink`, ID `11525753140`  
**Artifact SHA-256:** `75f33b72c4cf147d37b151e17bb7ae6bddc84982941f9f0aa8847c97d4fe4fb4`  
**Tests:** targeted 9/9 PASS; full pytest 420/420 PASS; real-media evidence 14/14 PASS  
**Gates:** Ruff, mypy (75 modules), import contracts, architecture, no-secret, source-of-truth 70/70, UI SHA 42/42 PASS  
**Full same-HEAD regression:** 27/27 workflow families SUCCESS, all attempt 1.

Verified: bounded worker scan, cancellation, stale project/session/revision/hash safety,
rank 1–4, SHA-256 verified explicit selection only, ambiguous candidate review,
one atomic CommandBatch, stable asset/clip IDs, exact Undo/Redo, save/reopen and
real-media validation. UI-040 projects intents; controller wiring remains W8-010.

**W8-005 accepted qualification:**
- W8-005 accepted implementation/regression HEAD: `43cb1d04b5d519c26f843714c4b7cd9793054fe9`.
- Windows qualification workflow: `37724812333` — SUCCESS.
- Artifact: `ANG-S11-W8-005-Autosave-Catalog` ID `11526779061`;
  SHA-256 `c9a305ccc6cee9744e271e7520df4722192fa27a2a44544cf8ab68c717cf556c`.
- Targeted autosave tests **9/9 PASS**, full pytest **429/429 PASS**,
  owned evidence verifier **12/12 PASS**, frozen UI **42/42 PASS**.
- Ruff/mypy/imports/architecture/security/source-of-truth PASS.
- Same-HEAD regression **27/27 workflow families SUCCESS, all attempt 1**.
- Maximum 20 validated managed autosaves/project, legacy compatibility,
  corrupt isolation and writer/unlink failure injection PASS.
- Never prune source `.angproj`, `.bak`, or foreign project snapshots.

**W8-006 accepted — PASS**

- Accepted W8-006 implementation and same-HEAD regression commit: `5a975bb312714f84315b9b752deac75a33021fab`.
- [Dedicated Windows recovery workflow](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37726261665): **SUCCESS**.
- Artifact: `ANG-S11-W8-006-Crash-Recovery`, ID `11528226010`,
  ZIP SHA-256 `adc9591b108a82f2b4e09d7f7bc3714133a6dd7ec839ed2216e7568351ad1165`.
- Dedicated recovery tests **15/15 PASS** (12 unit + 3 Qt).
- Full Python suite **444/444 PASS**; owned crash evidence verifier **12/12 PASS**.
- Ruff, mypy (79 source files), import contracts, architecture, no-secrets,
  source-of-truth **70/70** and frozen UI references **42/42 SHA-256 PASS**.
- Same-HEAD regression **27/27 workflow families SUCCESS, attempt 1**,
  including Windows portable foundation, UI shell, timeline, E2E, subtitle,
  media and previous W8 qualification.
- Proven: clean/unclean marker, valid newer-only snapshots, corrupt-newest
  isolation, explicit Open Source / Recover Snapshot / Ignore choices,
  stale snapshot/source rejection, exact project source bytes unchanged
  during recovery, dirty working state until explicit Save, clean-close guard.
- UI-039 intent/projection qualification only; complete main-window wiring
  remains W8-010. W8-007 persistence-failure injection is a separate next STEP.

**W8-007 accepted qualification:**

- Accepted W8-007 implementation + same-HEAD regression: `130407dc728b6417c30dbbc935ecd9b04d37ba43`.
- [Windows atomic-persistence workflow](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37727525574) — **SUCCESS**.
- Artifact: `ANG-S11-W8-007-Atomic-Persistence`, ID `11528930146`; SHA-256 `5cf537b7ec5fcf7043c2a0fe640d3f7d9008d2e60209b712c0d81ca06a95be91`.
- **15/15** targeted fault tests PASS; **459/459** full Python tests PASS;
  **19/19** owned evidence checks PASS.
- Ruff, mypy (80 source files), import-linter, architecture, no-secrets,
  source-of-truth **70/70** and frozen UI references **42/42 SHA-256 PASS**.
- **28/28 same-HEAD workflow families SUCCESS, all attempt 1**,
  including portable Windows foundation, UI shell, timeline and E2E.
- Verified temporary create/write/sync, backup create/copy/replace and
  source replacement fault injection; preexisting source bytes exact on
  failed Save, backup always readable, orphan .tmp cleanup for recoverable
  failures, Session dirty/Save As guards and successful retry with intended
  canonical state. Snapshot save failure does not publish invalid recovery.
- **Confirmed and fixed:** pre-W8-007 code registered temp filename only
  after write/sync, leaving orphan temp on early failure. Existing repository
  serializer and ownership remain unchanged; no schema/UI changes.
- Typed `PersistenceError` stages and an actionable, redacted Indonesian
  failure projection qualified. W8-008 not implemented.

## Accepted W8-008

- Accepted W8-008 implementation/regression HEAD: `6c35b70bd9122664473a69eff6635ed9b71da5cb`.
- [Windows W8-008 workflow](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37728798520) — **SUCCESS**.
- Artifact: `ANG-S11-W8-008-Stale-Result-Jobs`, ID `11529365791`,
  SHA-256 `3b622ad005a16951e040c1d590f63974304c583a13374aa87fa1bc2f6a0c1a5c`.
- Dedicated concurrency tests **12/12 PASS**, full pytest **471/471 PASS**,
  owned concurrency evidence **18/18 PASS**.
- Ruff, mypy (81 source files), import contracts, architecture, no-secrets,
  source-of-truth **70/70** and frozen UI references **42/42 SHA-256 PASS**.
- **27/27 same-HEAD regression workflows SUCCESS**, all attempt 1;
  Windows portable foundation, media/speech/UI and E2E passed.
- Verified manual edit while scan runs, closed session, new session with
  identical revision/hash, different project, same-revision semantic swap,
  cancellation with late worker completion, stale result discard and
  zero automatic project mutation.
- Existing CommandBus/ProjectRepository and frozen UI remain unchanged.
  Actual main-window UI-039/040/041 wiring remains W8-010.

**Exact next task:** SOL S11-W8-009 Structured Diagnostics +
Redacted Diagnostic Bundle ONLY. W8-010 remains serial-blocked.

**W8-009 PASS**

W8-009 accepted code HEAD `6a4ec93d445e71dc037bcc4dc6edff2008894268`.
Windows `37730435314` SUCCESS, artifact `11529353867`,
ZIP SHA-256 `17bc6c66063c240258f8f27fd68e8755ea8d26b63ba73a498c96e1f6e08d3b6e`.
Targeted **11/11**, full pytest **482/482**, evidence **18/18**,
frozen UI **42/42**, same-HEAD regression **27/27 SUCCESS**, all attempt 1.
Deterministic 128KiB max redacted ZIP contains fixed manifest/events only.
No raw paths, private content, credentials or media bytes.

**Exact next task:** SOL S11-W8-010 only. UI-001..042 must remain frozen.

## W8-010 accepted closure — 2026-10-08 WIB

**W8-010 accepted implementation and same-HEAD regression:** `45c3294f5a8c93cee17369fa4b95122e3fca035b`.

- [Windows W8-010 UI/GOLDEN-03 run](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37732709194): **SUCCESS**.
- Artifact `ANG-S11-W8-010-UI-GOLDEN03`, ID `11530068997`, size 11,387,537 bytes.
- Artifact ZIP SHA-256: `4a24f45f3c6ef6d73924ec83d0ea2149b1490119abb766dd079d6db2a5840241`.
- **5/5** targeted Qt controller tests, **487/487** full Python suite, **23/23** owned GOLDEN-03 evidence checks PASS.
- Ruff, mypy **85 source files**, lint-imports, architecture and no-secret checks PASS; source-of-truth **70/70** PASS.
- Frozen UI-001..042 manifest **42/42 SHA-256 PASS** — no raster redesign or AAVC source changes.
- **27/27** same-code-HEAD workflow families **SUCCESS on attempt 1**, including S08 portable foundation, S09 UI shell, S10 real Windows E2E, W0-W7 and W8.
- Demonstrated live UI-041 missing referenced media BLOCKER, UI-040 bounded worker discovery and fingerprint-verified manual relink, canonical CommandBus/Undo-Redo, revalidation, save/reopen, UI-039 explicit crash snapshot restoration without silent source overwrite, and redacted diagnostic ZIP.
- Fixed a real compatibility regression: FFprobe is initialized lazily only during a media probe, so the Qt shell and fake-probe tests do not require an installed FFprobe.
- W5 physical microphone and W6/W7 live Gemini qualification remain provisional, not claimed as PASS.

**Next exact action:** SF-STEP 12 planning/contract readiness review only, after the owner's next `lanjutkan`. Do not implement STEP 12 in this W8-010 turn.


## SF-STEP 12 — T02 acceptance, non-breaking contract (2026-10-08 WIB)

- [x] **SF12-T01 — Export capability truth-in-UI — PASS_WITH_PROVISIONAL_NATIVE_ENCODER_INVENTORY**
- [x] **SF12-T02 — Typed ExportRequest and additive port contract — PASS_CONTRACT_ONLY**
- [ ] **SF12-T03 — Export preflight + capability negotiation — READY, NOT STARTED**
- [ ] T04–T10 — WAITING FOR SERIAL GATE

T02 GitHub Actions workflow 37735699709 SUCCESS for code SHA 9e12498; targeted 27/27 cases, full pytest, Ruff/mypy/imports/architecture/secrets/70 source-of-truth/42 UI reference checks PASS. No actual FFmpeg render, native matrix qualification or merge to main. See `docs/evidence/features/SF12_T02_EXPORT_REQUEST_CONTRACT.md`. Breaking `MediaEnginePort` adoption requires ASTRA/ADR first.


## SF12-T03 acceptance checkpoint — 2026-10-08 WIB

- [x] SF12-T01 — Export Capability Truth in UI — PASS_WITH_PROVISIONAL_NATIVE_ENCODER_INVENTORY.
- [x] SF12-T02 — Typed ExportRequest non-breaking contract — PASS_CONTRACT_ONLY.
- [x] **SF12-T03 — Export preflight and capability negotiation — PASS_CONTRACT_ONLY**.
- [ ] **SF12-T04 — Real H.264 baseline export pipeline — READY, not started.**
- [ ] SF12-T05..T10 — serial blocked pending prior gates.

T03 code `7bee32aae7248ae9023afe4b9b62bf2caf357095`, Windows CI `37736630766` SUCCESS, new targeted+full pytest pass; Ruff, mypy(90), architecture/import contracts/secrets, 70 source-of-truth, UI 42/42 SHA PASS. No real codec render, no GUI render enablement or frozen MediaEnginePort change. See `docs/evidence/features/SF12_T03_EXPORT_PREFLIGHT.md`. Draft stacked PR #4 not merged.


## SF12-T04 H264 real-media acceptance — 2026-10-08 WIB

- [x] SF12-T01 Capability truth in UI — PASS/provisional native.
- [x] SF12-T02 Typed request & additive boundary — PASS contracts.
- [x] SF12-T03 Preflight and conservative capability negotiation — PASS contracts.
- [x] **SF12-T04 H.264 1080p30 AAC baseline, safe publish — PASS real Windows output**, with production GUI/packaging still provisional.
- [ ] **SF12-T05 Frame-accurate FULL/SELECTION mapping — NEXT; not started.**
- [ ] SF12-T06..T10 — serial blocked.

Evidence T04 Windows `37737863469` SUCCESS on SHA `96cf5a46ecfeea6cdb9ff767414a6dde828a2a42`, 1-second owned H264/AAC MP4; no-clobber, cancel, source and race negatives PASS; full pytest/static/source-of-truth/UI gates PASS. Draft PR #5 (stacked) remains unmerged. GUI render stays disabled until T08/T09 and further release gates.


## SF12-T05 accepted — 2026-10-08 WIB

- [x] SF12-T01 — Export capability truth-in-UI — PASS with native provisional.
- [x] SF12-T02 — Typed ExportRequest additive contract — PASS.
- [x] SF12-T03 — Safe preflight and capability negotiation — PASS contract.
- [x] SF12-T04 — Safe full-project H264/AAC baseline — PASS real Windows.
- [x] **SF12-T05 — FULL/SELECTION frame-accurate mapping including subtitle/narration — PASS real Windows** (engine-side two-pass qualification, not a UI capability).
- [ ] **SF12-T06 — Codec/resolution/FPS matrix — NEXT, not started.**
- [ ] SF12-T07..T10 — blocked serially.

SF12-T05 code `9dca99397f3dcbac4d491d5d930cf8309d744271`, Windows workflow `37738941089` SUCCESS, synthetic 120f project with subtitle and narration, 3 selected intervals exactly 30f, video PSNR >=33dB, H264/AAC 1080p30. Full pytest/typing/arch/70 source docs/42 UI hashes PASS. Draft PR #6 stacked; not merged to main. Keep renderer UI disabled until T08/T09/T10 gates.


## SF12-T06 Windows codec/fps/resolution matrix — 2026-10-08 WIB

- [x] SF12-T01 — Capability truth in UI — PASS / native provisional.
- [x] SF12-T02 — Typed immutable request — PASS contract.
- [x] SF12-T03 — Safe preflight — PASS contract.
- [x] SF12-T04 — H264/AAC 1080p30 full export — PASS real Windows.
- [x] SF12-T05 — Full/selection frame mapping — PASS real Windows.
- [x] **SF12-T06 — Four selected codec/resolution/FPS cells — PASS real Windows MP4**: H264 1440p30, H264 4K30, H264 1080p60, H265 1080p30; output is scaled/converted from 1080p30, 0.5s fixture, not native detail or final product qualification.
- [ ] **SF12-T07 — Subtitle, narration, sharpen and quality binding — NEXT not started.**
- [ ] SF12-T08 job/cancellation, T09 full output postflight, T10 packaged Windows E2E — blocked serially.

Run `37740103975` SUCCESS at code `00761740666c66c8787aec4865d3e2184a13fe7d`; full pytest, Ruff, mypy 92, architecture/source-of-truth70/UI42/secrets PASS. Test artifacts `ANG-SF12-T06-CodecMatrix-RealMedia` ID 11533866135. T06 PR #7 stacked and not merged; UI render remains disabled; H265 4K60 unqualified.


## SF12-T07 style/narration actual Windows acceptance — 2026-10-08 WIB

- [x] SF12-T01 – Capability truth-in-UI — PASS native provisional.
- [x] SF12-T02 – Immutable request contract — PASS.
- [x] SF12-T03 – Safe preflight — PASS.
- [x] SF12-T04 – H264 full baseline — PASS real Windows.
- [x] SF12-T05 – H264 selected frames including subtitle/audio — PASS real Windows.
- [x] SF12-T06 – Four actual Windows codec/resolution/FPS cells — PASS.
- [x] **SF12-T07 – Six individually qualified subtitle/quality/sharpen variants, with narration AAC — PASS actual Windows**.
- [ ] **SF12-T08 – Nonblocking render worker/progress/cancel/timeout/close and stale guards — NEXT, NOT STARTED**.
- [ ] SF12-T09 postflight and T10 packaged Windows E2E — blocked serially.

T07 Windows run `37741355411` SUCCESS on implementation `79b24e93d4574cff0fc8a1650a6bd569e7640965`; six H264/AAC MP4s (2s each), subtitle gray on/off mean 1.1399, sharpen light/crisp means 0.6486/1.0716, narration PCM late pre 4.2776 / during 2399.3156. Full regression/architecture/docs/UI PASS, artifact ID 11533749234. Draft PR #8 stacked, not merged to main. GUI export remains disabled pending T08-T10; qualified cells are not a release claim.


## SF12-T08 background export job acceptance — 2026-10-08 WIB

- [x] SF12-T01 — Capability truth-in-UI — PASS, native provisional.
- [x] SF12-T02 — Immutable typed request — PASS.
- [x] SF12-T03 — Safe preflight — PASS.
- [x] SF12-T04 — Baseline H264+AAC real export — PASS Windows.
- [x] SF12-T05 — Full/selection frame mapping — PASS real media.
- [x] SF12-T06 — Four codec/resolution/FPS matrix cells — PASS Windows.
- [x] SF12-T07 — Six quality/sharpen/subtitle style variants + narration — PASS Windows.
- [x] **SF12-T08 — Nonblocking render worker, cancel, timeout, stale/close guard and owner-only commit — PASS Windows lifecycle + real H264 output; phase progress only; UI not wired**.
- [ ] **SF12-T09 — Independent postflight / typed errors / exact request comparison — NEXT, NOT STARTED.**
- [ ] SF12-T10 — packaged Windows E2E + UI regression — pending T09.

Accepted SHA `596a48db355878537227f193c6dee33d0ae3f24a`; CI `37742882153` SUCCESS; all unit/Qt/full regression/static docs gates PASS, artifact 11534776048. Draft PR #9 stacked, unmerged; UI export still disabled, no packaged release.


## SF12-T09 acceptance — 2026-10-08 WIB

- [x] SF12-T01 capability truth-in-UI — PASS / native provisional.
- [x] SF12-T02 immutable typed ExportRequest — PASS.
- [x] SF12-T03 fail-closed preflight — PASS.
- [x] SF12-T04 real FFmpeg H264/AAC full baseline — PASS.
- [x] SF12-T05 selection frame mapping and subtitle/narration timing — PASS.
- [x] SF12-T06 four native codec/resolution/FPS cells — PASS.
- [x] SF12-T07 six individually qualified subtitle/sharpen/quality cells with narration — PASS.
- [x] SF12-T08 single nonblocking background worker/phase/cancel/timeout/stale/close/atomic output — PASS.
- [x] **SF12-T09 independent FFprobe + full FFmpeg decode, typed redacted errors, exact requested frames/codec/audio, SHA256 receipt and owner publish gate — PASS REAL WINDOWS**.
- [ ] **SF12-T10 Windows packaged E2E, frozen UI regression, native codec/license decision and release gating — NEXT, NOT STARTED**.

T09 Windows CI `37744843294` SUCCESS on code SHA `270fe789834354a7e2adb38fc5859023db93f547`. Five real MP4s, AAC, full decode; corrupted/truncated real MP4 rejected. T08 HEVC dispatch corrected. Target/full pytest, mypy 98, architecture/source-of-truth70/UI42/secrets PASS. Artifact 11535670942, draft stacked PR #10 still unmerged. **UI render stays disabled pending T10.**


## SF12-T10 Windows package qualification and release blocker handoff — 2026-10-08 WIB

- [x] SF12-T01 capability truth-in-UI — PASS / native provisional.
- [x] SF12-T02 immutable request DTO — PASS.
- [x] SF12-T03 safe media/output preflight — PASS.
- [x] SF12-T04 baseline H264 AAC — PASS.
- [x] SF12-T05 selection full/out mapping — PASS.
- [x] SF12-T06 exact codec/resolution/FPS allowlist — PASS.
- [x] SF12-T07 exact subtitle/sharpen/quality + narration cells — PASS.
- [x] SF12-T08 nonblocking background render job & cancel/timeout/stale — PASS.
- [x] SF12-T09 independent FFprobe+whole FFmpeg decode and typed failures — PASS.
- [x] **SF12-T10 scoped existing onedir packaged media (9 actual MP4 profiles) + original UI shell Qt smoke — PASS Windows 3-job CI 37746307421**.
- [ ] **SF12-T10 combined product GUI + native licence/redistribution + end-user portable + all 27 workflow families same HEAD — NOT QUALIFIED / RELEASE BLOCKED**.
- [ ] **ASTRA ADR required NEXT:** engine, external/bundled FFmpeg libx264/libx265 redistribution, licensing/notices, packaging and frozen UI render integration plan; owner decision before SOL changes core.

T10 SHA `c945d9a4d0079c4b6c1ba40cd19a2326c03fa268`, full source/test/Qt/architecture/UI42/docs70 PASS. GitHub artifacts media ID11535444050, UI ID11535718409. Draft stacked PR #11, main unchanged. Product GUI render DISABLED; original media/Qt packages remain different ZIPs and are NOT the final Windows portable editor.
