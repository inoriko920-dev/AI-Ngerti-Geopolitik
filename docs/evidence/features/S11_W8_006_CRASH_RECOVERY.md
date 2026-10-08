# S11-W8-006 — Crash Marker + Startup Recovery Decision

**Status:** PASS  
**Accepted implementation/regression HEAD:** `5a975bb312714f84315b9b752deac75a33021fab`  
**Windows workflow:** [37726261665](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37726261665) — SUCCESS  
**Artifact:** `ANG-S11-W8-006-Crash-Recovery`, ID `11528226010`  
**Artifact SHA-256:** `adc9591b108a82f2b4e09d7f7bc3714133a6dd7ec839ed2216e7568351ad1165`

## Qualified implementation

- Local atomic crash marker records clean/unclean state bound to source digest,
  project identity and unique session ID. A corrupt marker fails closed.
- Startup uses the existing ProjectRepositoryPort and validated W8-005 catalog,
  showing only validated newer snapshots with corrupted newest isolated.
- Decisions are explicit: **Open Source**, **Recover Snapshot**, **Ignore**.
  Ignore does not change marker or session.
- A selected snapshot is re-validated on application; stale/tampered or
  unlisted snapshots are rejected without source mutation.
- Recovery adopts the snapshot into ProjectSession/CommandBus as **dirty working
  state**, with original source path preserved and no automatic Save.
- Normal clean close respects unsaved-change guard before marking clean.
- UI-039 frozen projection/dialog emits semantic intents; startup/main-window
  controller wiring remains deferred to W8-010, not W8-006.

## Windows acceptance

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

## Deferred scope

W8-007 persistence fault-injection; W8-008 cross-job stale hardening;
W8-009 diagnostics and W8-010 full UI/Golden-03 integration are separate.
W5 physical microphone and W6/W7 live Gemini tests remain provisional.

## Exact next action

**SOL S11-W8-007 — Atomic Persistence Failure Injection + Remediation — READY.**
Do not begin W8-008 in the same turn.
