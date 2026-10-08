# SOL — Project Open: Malformed Nested JSON / Privacy-Safe Failure

**Date:** 2026-10-08 WIB  
**Scope:** Post-W8 reliability bugfix to the existing `JsonProjectRepository.load` path.
**Native Pilot A:** Not required; NO FFmpeg/FFprobe execution or production render changes.

## Confirmed code defect

The former `load()` handler caught basic JSON/dict errors, but could leak
`AttributeError` (e.g. `tracks: [42]` iterated as a track object), leaving
a malformed user project as an untyped application exception. It also embedded
the input path in `ProjectFormatError` text, contrary to the existing
privacy-safe error conventions.

## Resolution

- Normalize ordinary malformed nested content (`AttributeError`, `IndexError`,
  `OverflowError`, `RecursionError` plus existing parser/IO failures)
  into fixed `ProjectFormatError("invalid project file")`.
- Suppress raw exception context when presenting a normal load error, without
  masking unrelated programmer errors with a blanket `except Exception`.
- Explicit regression tests for malformed nested tracks, malformed JSON,
  missing files, private path redaction and preserving an existing project
  session/source bytes after a failed open.
- Existing valid .angproj projects continue to use the same serialization
  schema and save behavior; no migration, feature expansion, UI change or
  new dependency.

## Acceptance

Verified code SHA `24af2d6707a05fb3558911a62e91b8f43253b00c` at [Windows CI #37772403305](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37772403305) — **SUCCESS**. Verified: Ruff formatting,
lint, mypy, architecture, source-of-truth, frozen UI manifest and both
targeted/full pytest. Targeted and full pytest passed. This documentation follow-up has no source changes; verify CI at the final branch SHA.
`main` stays unchanged; no release/portable packaging.

## Boundaries

The external native-engine D1 Pilot A decision remains pending. This
source-contained regression fix does not approve engine selection, FFmpeg
distribution, UI render activation, merge or release.


## JSON boolean data-integrity fix (8 October 2026 WIB)

`JsonProjectRepository.load` formerly performed `bool(value)` coercion in ten
canonical flag locations. For example, malformed `"muted": "false"` or
`"enabled": "false"` would become `True`, silently changing an edited project's
timeline, effect locks, audio mute state or captions when reopened.

- Require exact JSON boolean values (`true` / `false`) for all ten canonical
  asset, clip, track, title, effects, subtitle and narration flags. Invalid
  strings, numeric values and JSON null now fail closed as a
  `ProjectFormatError("invalid project file")`.
- Keep the same v1 schema, defaults, save serialization and legitimate True/False
  semantics: no migration, no new dependency, no UI change.
- Add a fully populated canonical project fixture (video timeline, narration and
  subtitles), 50 malformed-boolean regression cases and a legitimate
  save/reopen roundtrip test. Neither the original active project nor any
  file is modified by failing `load`.
- Windows CI on the updated exact branch SHA must pass before acceptance.
  Native FFmpeg Pilot A remains pending; portable is reserved for final release.

## Invalid-Unicode project-load atomicity (8 October 2026 WIB)

- A JSON document may contain escaped lone UTF-16 surrogates (`\\ud800` or `\\udfff`). The prior decoder accepted such strings because the domain validation did not check Unicode encodability. `ProjectSession.open_project` then attempted `state.semantic_hash()` only **after** replacing the active project, raising `UnicodeEncodeError` and leaving a partial session switch.
- `JsonProjectRepository.load` now computes the canonical semantic hash before returning, so strings that cannot be encoded as UTF-8 are rejected through existing privacy-safe `ProjectFormatError` handling. No JSON schema changes.
- `ProjectSession.open_project` computes the hash and builds a new bus before altering `_bus`, `_session_id`, path, or saved hash; even an alternate repository that returns an unhashable state cannot partially swap an active project.
- New tests exercise escaped lone surrogates in project name, track name and subtitle cue text, confirm the previous project and bytes remain intact, and simulate a non-JSON repository returning an invalid state.
- Current source and tests require **new same-HEAD Windows CI PASS**; no FFmpeg external execution, UI rework, codec bundling, main merge, or portable release.

## Save As and autosave recovery atomicity (2026-10-08 WIB)

- The session previously invoked `repository.save()` and changed `current_path` **before** computing `state.semantic_hash()`. For an alternate adapter that wrote unhashable state, a failed hash could leave a newly written file and a rebound project path. Now canonical hashing happens **before** any repository write and the resulting hash is reused after a successful save.
- `recover_snapshot()` previously validated two domain models and immediately replaced the current session without checking semantic-hash encodability. Both source and restored state are now hashed **before** the recovered session is accepted; its new command bus is also built before mutation.
- Two synthetic, deterministic regression tests use a repository adapter returning malformed Unicode or capable of prematurely writing. They verify no accidental save target, no active-session replacement, no altered source bytes, and no false clean state.
- Changes keep the existing project v1 schema, file format, UI, and source-of-truth permissions. Real external FFmpeg and portable release are outside this change.
- The new exact-head Windows CI must pass targeted and full pytest, Ruff, mypy, architecture, secrets and frozen UI reference checks before this follow-up is accepted.
