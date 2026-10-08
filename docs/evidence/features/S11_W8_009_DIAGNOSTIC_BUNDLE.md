# S11-W8-009 — Structured Diagnostics + Redacted Diagnostic Bundle

**Status:** IN_VERIFICATION — NOT PASS  
**Contract:** locked ASTRA W8 §10.9  
**Dedicated CI:** `.github/workflows/s11-wave8-009-diagnostics.yml`

## Implementation and privacy gates

- `application/diagnostics.py`: bounded typed event ledger (max 256, dropped count),
  allowlisted event code/status/persistence stage + bounded numeric counters.
- `application/diagnostic_bundle.py`: strict serialization of allowed fields,
  deterministic JSON event + manifest bytes, SHA-256 manifest integrity,
  single-worker on-demand job, status/cancel/failure without UI blocking.
- `infrastructure/diagnostic_bundle.py`: fixed ZIP layout of
  `manifest.json` and `events.json`, fixed timestamps/order, 128KiB cap,
  safe atomic hard-link publish (never overwrite existing user ZIP),
  temp cleanup, typed no-path errors.
- Raw exception cause/args, project ID/hash, private paths, file names,
  media bytes, AI user prompt, subtitle/narration text, API keys, token strings,
  raw ValidationIssue messages/targets are NOT serialized.
- Owned real proof runner injects private markers and validates exclusion,
  deterministic ZIP SHA/bytes, fixed whitelist, count, archive bound,
  typed failure stage.
- Tests check exclusion, deterministic ZIP, cancellation, overwrite refusal,
  output failure, symlink safety, strict type validation and event cap.
- No changes to ProjectState/schema/CommandBus, AAVC repository or frozen UI.
- W8-010 UI wiring remains future task.

## Pending QA

Dedicated Windows Ruff/mypy/import-linter/architecture/security/UI manifest,
targeted/full pytest, proof verifier, and same-HEAD historical workflows must
pass. No status PASS until complete.
