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

## W8 GUI project-open inspection gate — 2026-10-08 WIB

**Defect:** `W8RuntimeController.request_open` previously closed a valid, clean project and its active crash marker **before** asynchronous `RecoveryManager.inspect` checked the newly selected file. A malformed or missing target therefore discarded the existing on-screen project even when inspection failed.

**Change:** Keep the existing project and its marker during asynchronous inspection; decline a dirty-project switch immediately; decline opening the exact same already-active project path. Retire the prior clean session and cancel its jobs only after a verified offer and an actual source/snapshot-open choice; `IGNORE` leaves the old session intact. `RecoveryManager.decide` still independently validates the source and selected snapshot.

**Regression:** Added Qt tests for a corrupt selected `.angproj` preserving active session ID, canonical hash, project bytes and crash marker, and a same-path open leaving session untouched. Windows targeted Qt tests, targeted unit tests and full suite run in the PR #20 same-head workflow. This is not a full transaction guarantee against a file changing after inspection; stale decisions remain fail-closed under `RecoveryManager.decide`.

**Gate:** PENDING latest-head Windows CI. No UI-001..UI-042 visual changes, production native FFmpeg runner, external binary bundling, merge or portable.
## W8 GUI staged open/restore transaction — 2026-10-08 WIB

- **Defect:** A candidate could change after asynchronous inspection (or its recovery marker write could fail) while the old editor session was already closed before the final `RecoveryManager.decide`. A rejected/stale final decision then destroyed a valid active project.
- **Fix:** Keep the prior clean project open while `RecoveryManager.decide` performs final source/snapshot freshness validation, candidate ProjectSession setup and crash-marker write on a **temporary candidate session**. Only after it succeeds does the controller retire the old session and promote the candidate as its sole active state owner. IGNORE has no state/marker mutation, and dirty state still blocks switching.
- On failure to close the previous session, the staged candidate is never promoted and its marker receives a best-effort clean close. This does not guarantee rollback if the *old* `close_clean` itself closed the session before its marker failed; that separate pre-existing failure mode is not claimed resolved.
- Three Qt regression tests cover (1) staleness between inspect and decision, (2) candidate marker-write failure, and (3) successful switch with the previous marker cleaned and source files unchanged.
- **Gate:** Windows same-HEAD Ruff/mypy/security/architecture/42 UI-manifest checks, targeted unit+Qt, and full pytest. PASS must not be claimed until verified. Scope remains project lifecycle, no production FFmpeg, UI redesign, main merge, or portable.

## Crash-marker close failure: preserve active session (2026-10-08 WIB)

**Confirmed defect:** `RecoveryManager.close_clean` previously cleared the live `ProjectSession` before attempting to atomically write the `clean` crash marker. If that marker write failed (for example, access denied), the controller refused to switch but the previous valid editor state had already been erased.

**Scoped correction:** Check the unsaved-changes guard before marker mutation; write the clean marker while the saved or explicitly discarded session remains intact; release the in-memory session only after successful marker persistence. This is safe in the synchronous Qt decision path, where no edit can intervene between the guard and close. For unexpected in-memory close exceptions, attempt to restore the prior `unclean` marker and propagate the failure. This does not promise a crash-consistent multi-file transaction or rollback when *both* closing and marker restoration fail.

**Regression:** Add two fault-injection unit tests (clean-marker write rejection and unexpected close failure) and one Qt staged-switch test (old marker write rejected, candidate marker cleaned, original session/bytes preserved). The Windows workflow now runs both W8-006 unit recovery and W8-010 Qt targeted tests plus full pytest/Ruff/mypy/security/architecture/UI checks.

**Acceptance:** PENDING same-HEAD Windows CI for this commit; `main` remains unchanged, PR #20 remains Draft; no native FFmpeg integration, UI design change, or portable package.

## Home → Editor route: real project-open success (2026-10-08 WIB)

**Confirmed user-facing defect:** Opening a valid saved `.angproj` from the Home screen successfully established the W8 session, but `W8RuntimeController._decide` never navigated to `UiRoute.EDITOR`. The Home page remained visible despite the project being active. The recovery UI handoff likewise lacked a successful route change.

**Fix:** On successful staged project open/recovery and only after acquiring the active session, route to existing frozen Editor Overview `UI-010`. Do not navigate on corrupt file, stale offer, declined recovery or failed marker transition. The patch changes runtime navigation behavior only, **not** the frozen 42 UI designs, widget layout or product render controls.

**Qt regression:** Real saved project opened from `UI-002` navigates to `UI-010` and keeps canonical project session; malformed `.angproj` fails safely and remains at `UI-002`. The existing W8-010 GUI suite and entire Windows CI must pass on the latest exact commit before accepting.

**Gate:** PENDING exact-head Windows CI. No merge, no native FFmpeg Pilot A execution, no portable package.

## New Project wizard: reject phantom editor session (8 Oct 2026 WIB)

- **Confirmed live workflow defect:** The frozen UI-003 wizard's Continue callback directly called `show_route(UiRoute.EDITOR)` after emitting `NEW_PROJECT`. But W8's intent controller ignored `NEW_PROJECT`, so a selected DOCX appeared to create a project while `ProjectSession.is_open` remained false and scene/asset mapping was never imported.
- **Scoped integrity fix:** Pass the selected DOCX path in the semantic intent and remove automatic editor navigation. W8 reports a clear, path-free status for missing/invalid input and, for an existing selected DOCX, explicitly states that Scene DOCX ingestion is not wired. No fake project, empty editor or unintended replacement of an active project.
- **No speculative parser:** The required Prompt-1 DOCX Scene/Asset-ID mapping contract does not yet have a production importer connected to this wizard. Merely checking the extension is not a parser and does not assert the DOCX content is valid. Actual import+asset validation+session construction remains a separate feature milestone and gate.
- **Regression:** Qt tests check the real Browse→Continue wizard path remains at UI-003 without creating a phantom project, and a missing DOCX never discards an already open project. No frozen UI artwork/layout changes, no main merge, no native FFmpeg or portable release.
- **Gate:** Pending exact-head Windows CI with targeted Qt/unit plus full suite.
