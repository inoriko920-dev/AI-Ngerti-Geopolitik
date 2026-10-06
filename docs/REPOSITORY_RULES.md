# REPOSITORY RULES & STRUCTURE

## Current state

Repository remains **docs-first / pre-implementation**. SF-STEP 07 defines the future source structure, but it is not implemented until STEP 08 evidence exists.

## Canonical future source package

`src/ai_ngerti_geopolitik/`

Main boundaries:
- `domain/` — pure product state/rules;
- `application/` — commands, queries, ports, use cases, jobs;
- `presentation/` — PySide6 UI, AAVC frozen shell/screens/components;
- `infrastructure/` — engine/provider/persistence/credentials/config/process/platform adapters;
- `bootstrap/` — composition root only.

## Dependency direction

`presentation -> application -> domain`

`infrastructure -> application ports + domain contract types`

`bootstrap -> all` for construction only.

Forbidden:
- domain importing Qt, libopenshot/MLT, FFmpeg, Gemini, keyring, subprocess or filesystem implementation;
- presentation importing concrete infrastructure adapters;
- business logic in MainWindow/widgets;
- direct ProjectState mutation outside semantic CommandBus;
- hidden mutable global project state.

## Search -> Understand -> Modify

Before adding a new file/class/service/helper:
1. search the concept and synonyms;
2. locate canonical owner;
3. read contracts/ports/schema;
4. search call sites/registration/config;
5. read relevant tests;
6. explain why existing owner is insufficient;
7. modify canonical owner first;
8. re-search for duplicate responsibility.

## Planned repository tree

Top-level intended ownership:
- `src/ai_ngerti_geopolitik/` — product source;
- `tests/` — automated evidence;
- `docs/` — source-of-truth/evidence;
- `resources/` — read-only shipped QSS/icons/defaults;
- `scripts/` — repeatable dev/build/verify/package entrypoints, no business logic;
- `.github/workflows/` — Windows CI;
- `vendor/` — intentionally audited third-party payload only;
- `build/`, `dist/` — generated/ignored.

Do not create every empty folder simply to imitate the diagram. Materialize only what the current READY task requires.

## Planning/reference naming

- Planning STEP: stable numeric prefix and STEP number.
- Status/handoff: one canonical file, updated in place.
- UI reference: stable `UI-xxx`.
- Visible ANG-only UI delta: `UI-ANG-Dxx`.
- Do not rename source-of-truth without updating index/read order.

## Change rules

- One logical task per change.
- No mixed redesign + broad refactor + dependency upgrade + bug fix without justification.
- One concern has one canonical owner.
- No generic god manager/service/helper.
- No secret/token/API key/cookie/private user data in Git.
- No hardcoded developer Windows path.
- No generated cache/build/log/recovery/user settings as manual source.
- Architecture exception requires ADR/Astra review.

## STEP 08 first task

**S08-T01 — Source-of-Truth & Exact UI Reference Gate**

Before production source coding:
- STEP00–07 DOCX+TXT must be present/readable in repo;
- exact full-resolution UI-001..UI-042 raw references must be committed;
- 42/42 SHA-256 must match `docs/ui_reference/UI_REFERENCE_MANIFEST.md`;
- status must explicitly flip pre-coding docs/UI gate to PASS.

No product source code is allowed in S08-T01.

## State updates

After meaningful work update:
- `docs/PROJECT_STATUS.md`;
- `HANDOFF.md`;
- `docs/DECISIONS_LOCKED.md` if a locked decision changes;
- task/evidence files for the active STEP.

## Definition of "lanjutkan"

"lanjutkan" means execute the **next exact action** in current handoff only. It is never blanket permission to skip Software Factory gates.
