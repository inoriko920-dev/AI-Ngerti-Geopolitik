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

Run full GitHub Windows CI on the exact proposed branch SHA: Ruff formatting,
lint, mypy, architecture, source-of-truth, frozen UI manifest and both
targeted/full pytest. Mark PASS only after CI verifies the updated SHA.
`main` stays unchanged; no release/portable packaging.

## Boundaries

The external native-engine D1 Pilot A decision remains pending. This
source-contained regression fix does not approve engine selection, FFmpeg
distribution, UI render activation, merge or release.
