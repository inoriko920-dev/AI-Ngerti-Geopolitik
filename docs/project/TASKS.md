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


### W6 — CONTRACT_LOCKED / S11-W6-001 PASS / S11-W6-002 PASS / S11-W6-003 READY

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
- [ ] **S11-W6-003 — Windows secure-store qualification — READY**
- [ ] **S11-W6-004 — Credential health + safe failover — BLOCKED_BY_W6_003**
- [ ] **S11-W6-005 — L1 ContextBuilder + allowlist — BLOCKED_BY_W6_004**
- [ ] **S11-W6-006 — EditPlan schema + PlanVerifier — BLOCKED_BY_W6_005**
- [ ] **S11-W6-007 — Gemini adapter + async lifecycle — BLOCKED_BY_W6_006**
- [ ] **S11-W6-008 — Approval → CommandBatch → Undo/Redo — BLOCKED_BY_W6_007**
- [ ] **S11-W6-009 — Frozen UI parity — BLOCKED_BY_W6_008**
- [ ] **S11-W6-010 — Live Gemini + failure + regression closure — BLOCKED_BY_W6_009**

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

**Exact next task:** S11-W6-003 only — Windows secure-store qualification.
