# HANDOFF — AI NGERTI GEOPOLITIK

**Current phase:** SF-STEP 11  
**Current wave:** W6 — Gemini Credential + L1 AI Animation Planning  
**Last completed task:** S11-W6-005 — PASS  
**Accepted W6-005 implementation HEAD:** `043f8f250b7d61356bdf71757e8c6a7904615a06`  
**Accepted W6-005 workflow:** `37604630826` — SUCCESS  
**Next exact task:** S11-W6-006 — EditPlan schema + PlanVerifier  
**Previous W5 status:** PASS_WITH_PROVISIONAL_MIC_HARDWARE

## W6-005 implementation now available

Application:
- `application/ai_context.py`;
- deterministic bounded `L1ContextBuilder`;
- strict W4/L1 effect allowlist parity;
- max 20 selected clips per context;
- one previous + one next neighbor summary per selected target.

Provider context contains only:
- project id/name-as-untrusted-data/revision/fps/canvas;
- stable clip + track IDs;
- clip enabled state;
- media type/width/height/aspect ratio;
- current enter/exit effect + intensity;
- effect lock, track lock and effective lock;
- bounded neighboring clip effect summary;
- fixed allowed command type and effect/range policy.

Explicitly excluded:
- credentials/API keys;
- credential metadata labels;
- arbitrary filesystem paths/listings;
- asset source path/name/fingerprint;
- source media bytes;
- title/subtitle/narration text;
- logs;
- engine objects;
- Gemini/provider calls.

Untrusted project text is normalized/bounded and carried only as data with fixed
policy flags stating that project text cannot override application policy.

## Tests/evidence

Targeted W6-005 tests: **10/10 PASS**.  
Full pytest: **PASS**.  
Evidence verifier: **23/23 PASS**.  
Workflow: `37604630826` — **SUCCESS**.

Artifact:
- `ANG-S11-W6-005-L1-Context-Builder`;
- ID `11474213026`;
- size 1,158 bytes.

## Regression lock on accepted W6-005 implementation HEAD

All SUCCESS:
- W6-005 `37604630826`
- W6-004 `37604630749`
- W6-003 `37604630776`
- W6-002 `37604631067`
- W6-001 `37604630883`
- W5-010 `37604630852`
- W5-009 `37604630844`
- W5-008 `37604630864`
- W5-007 `37604630810`
- W5-006 `37604630863` — attempt 2
- W5-005 `37604630869`
- W5-004 `37604630760` — attempt 2
- W4 `37604630905`
- W3 `37604630824`
- W2 `37604630943` — attempt 2
- W1 `37604630878` — attempt 2
- W0 `37604630972` — attempt 2
- S10 `37604630887`
- S09 `37604630896`
- S08 `37604630811`.

The second attempts were required only because FFmpeg was temporarily unavailable
on the Windows runner during the first fixture-generation attempt. No product-code
change was made for those retry-only failures.

## Critical boundaries for W6-006

- strict EditPlan JSON/schema parsing;
- reject unknown root fields, commands, targets and effects;
- enforce target existence, lock state, L1 capability and intensity range;
- enforce base project revision / stale-plan rejection;
- dry-run against candidate state only, with zero canonical mutation;
- no Gemini network call yet;
- no W6 UI yet;
- no approval/apply transaction yet.

## Next exact action

After owner says `lanjutkan`, execute **S11-W6-006 only — EditPlan schema + PlanVerifier**.
