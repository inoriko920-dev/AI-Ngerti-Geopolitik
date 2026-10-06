# HANDOFF — AI NGERTI GEOPOLITIK

**Fase:** SF-STEP 08  
**Completed task:** S08-T01 — Source-of-Truth & Exact UI Reference Gate  
**Task result:** **PASS**  
**Next exact task:** S08-T02 — Repository Skeleton, Toolchain & Architecture Fitness  
**Application source:** NONE at S08-T01 close

## Read first

1. `AGENTS.md`
2. Software Factory master + guide
3. `docs/planning/00..08` in order
4. `docs/ui_reference/UI_REFERENCE_MANIFEST.md`
5. `docs/ui_reference/raw/UI-001.png..UI-042.png`
6. `docs/evidence/ui/S08_T01_UI_REFERENCE_GATE.md`
7. `docs/DECISIONS_LOCKED.md`
8. `docs/PROJECT_STATUS.md`
9. `docs/REPOSITORY_RULES.md`
10. this `HANDOFF.md`

## S08-T01 final evidence

Source-of-truth:
- Master Blueprint + STEP 00–07 DOCX/TXT are present.
- exact frozen UI references are present in GitHub.

Remote raw UI:
- path: `docs/ui_reference/raw/`;
- count: **42/42**;
- complete payload commit: `06ac2cb5899dd8c55e96f3e97b5bf171ae9388f8`;
- remote byte-size parity with canonical local PNG: **42/42 PASS**;
- remote Git blob SHA-1 parity with exact local PNG Git object identity: **42/42 PASS**;
- local SHA-256 against authoritative manifest: **42/42 PASS**.

The previous connector binary-upload blocker is **RESOLVED**. The workaround was lossless Base64 transport into Git blobs, not image conversion.

## Exact next action

If owner says **"lanjutkan"**, execute **S08-T02 only**.

S08-T02 goal:
- materialize minimal Python `src/` layout;
- create only foundation packages needed by the architecture;
- establish `pyproject.toml`, .gitignore/.editorconfig and foundation test/tool configs;
- add architecture/import/source-of-truth/secret checks;
- prove package import + cheap gates;
- create concise operational docs from STEP 06/07 only as needed.

Do NOT in S08-T02:
- implement the 42-screen product UI;
- implement libopenshot/MLT feature stack;
- implement Gemini editing;
- implement render/export product features;
- claim portable release;
- start S08-T03 automatically.
