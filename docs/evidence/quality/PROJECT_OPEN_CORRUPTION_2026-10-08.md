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
