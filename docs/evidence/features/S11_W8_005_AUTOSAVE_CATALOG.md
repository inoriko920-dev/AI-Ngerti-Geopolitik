# S11-W8-005 — AUTOSAVE CATALOG + RETENTION HARDENING

**Status:** PASS  
**Accepted implementation/regression HEAD:** `43cb1d04b5d519c26f843714c4b7cd9793054fe9`  
**Windows qualification:** [37724812333](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37724812333) — SUCCESS  
**Artifact:** `ANG-S11-W8-005-Autosave-Catalog`  
**Artifact ID:** `11526779061`  
**Artifact ZIP SHA-256:** `c9a305ccc6cee9744e271e7520df4722192fa27a2a44544cf8ab68c717cf556c`

## Accepted implementation and scope

- Existing `JsonProjectRepository` remains sole persistence serializer and
  atomic writer/loader; no duplicate canonical state or history owner.
- `ProjectSession.autosave()` delegates to
  `AutosaveCatalogService.create_snapshot()`.
- Timestamp-qualified new snapshots are managed; original W1 revision+hash
  `.autosave.angproj` files remain readable without rewriting.
- Catalog returns project ID, revision, timestamp, semantic hash and
  file SHA-256, with deterministic ordering.
- Catalog validates every candidate's JSON, canonical project ID, revision,
  filename hash and schema before marking recoverable.
- Corrupt/invalid/mislabeled/symlink/foreign entries are excluded from
  automatic pruning; foreign project snapshots remain untouched.
- Retention cap is 20 validated managed snapshots per project.
- Canonical source `.angproj` and `.bak` never prune; source/backup
  bytes remain exact in the owned evidence report.
- Injected snapshot-write and prune-unlink failures are tested; failures
  are not treated as successful cleanup.

## Windows qualification

- Accepted W8-005 implementation/regression HEAD: `43cb1d04b5d519c26f843714c4b7cd9793054fe9`.
- Windows autosave qualification: [37724812333](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37724812333) **SUCCESS**.
- Artifact `ANG-S11-W8-005-Autosave-Catalog`, ID `11526779061`; ZIP SHA-256 `c9a305ccc6cee9744e271e7520df4722192fa27a2a44544cf8ab68c717cf556c`.
- Dedicated catalog tests **9/9 PASS**; full pytest **429/429 PASS**; owned evidence **12/12 PASS**.
- Ruff, mypy (76 files), lint-imports, architecture, no-secrets, source-of-truth **70/70**, frozen UI **42/42 SHA-256 PASS**.
- Full same-HEAD regression **27/27 workflow families SUCCESS, all attempt 1**; Windows portable foundation PASS.
- New and legacy autosave filename compatibility, deterministic timestamp ordering, validated per-project catalog, maximum **20** managed valid snapshots, corrupt/foreign isolation and write/unlink failure guards qualified.
- Source `.angproj` and `.bak` are never retention/prune targets; source bytes unchanged in evidence. UI-039 recovery is deferred to W8-006.

W8-005 remains scoped to catalogue and retention. It does NOT introduce
UI-039 crash startup decision, automatic recovery, diagnostics, or STEP 12.
W8-006 and W8-007 remain separate serialized work items.

## Next

S11-W8-006 — Crash Marker + Startup Recovery Decision — READY.
Do not start W8-007 until W8-006 independently passes its gate.
