# REPOSITORY RULES & STRUCTURE

## Current state

SF-STEP 08 foundation is materialized. S08-T01 is PASS. S08-T02 is PASS_WITH_PROVISIONAL. Product feature implementation has not started.

## Canonical source package

`src/ai_ngerti_geopolitik/`

Boundaries:
- domain — pure product state/rules;
- application — future commands/queries/ports/use-cases/jobs;
- presentation — PySide6 UI boundary; actual product shell later;
- infrastructure — concrete adapters;
- bootstrap — construction/startup only.

## Dependency direction

`presentation -> application -> domain`

`infrastructure -> application ports + domain contract types`

`bootstrap -> all` for construction only.

Forbidden:
- domain importing Qt/libopenshot/MLT/FFmpeg/Gemini/keyring/subprocess implementation;
- application importing concrete infrastructure/presentation;
- presentation importing concrete infrastructure;
- business logic in widgets;
- direct ProjectState mutation outside future semantic CommandBus;
- mutable global product state.

Checker: `scripts/verify/verify_architecture.py`. Import-Linter config is also committed for target-toolchain verification.

## Search -> Understand -> Modify

Search concept, locate owner, read contract, search call sites/config, read tests, explain gap, modify owner first, re-search duplicate responsibility.

## Ownership

- `src/ai_ngerti_geopolitik/` product source
- `tests/` automated evidence
- `docs/` source-of-truth/evidence
- `resources/` future read-only shipped assets
- `scripts/` repeatable tooling, no product business logic
- `.github/workflows/` S08-T03 Windows CI
- `vendor/` audited payload only
- `build/`, `dist/` generated/ignored

Do not create architecture-theater empty folders.

## Frozen UI

`docs/ui_reference/raw/UI-001.png..UI-042.png` must keep matching `UI_REFERENCE_MANIFEST.md`.

## Change rules

One logical task per change; one concern one owner; no god manager/helper; no secrets/private data; no hardcoded developer paths; no generated build/log/recovery/user settings as source; architecture exception requires ADR/Astra review.

## Toolchain reality

Target Python = CPython 3.12.10 x64. Candidate direct pins are in `pyproject.toml`.

The current local runner could not install target Python/dependencies or generate a truthful `uv.lock`. Do not fabricate it. S08-T03 must resolve and verify lock/Windows tools.

## "lanjutkan"

Execute only the next exact action in HANDOFF.
