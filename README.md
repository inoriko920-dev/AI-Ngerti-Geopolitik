# AI Ngerti Geopolitik

> **STATUS: SF-STEP 11 ACTIVE — W7 CLOSED PROVISIONAL LIVE GEMINI — W8-001..003 PASS — W8-004..005 PASS — W8-006 PASS — W8-007 PASS — W8-008 PASS — NEXT W8-010**

Repository resmi aplikasi **AI Ngerti Geopolitik**.

Baca `AGENTS.md`, `docs/SOURCE_OF_TRUTH_INDEX.md` dan `HANDOFF.md`.

## W8 — Validation / Recovery / Diagnostics

Completed:
- W8-001 Canonical Validation Contracts + Baseline Rules = **PASS**;
- W8-002 Real Media Integrity + Validation Center Projection = **PASS**;
- W8-003 Single Asset Relink Command + Exact Identity Preservation = **PASS**;
- W8-004 Batch Directory Relink Scan + Candidate Ranking = **PASS**;
- W8-005 Autosave Catalog + Retention Hardening = **PASS**.

Verified W8-003 implementation/regression:
`25e5f6cefbbef5f554bd17e64d50a61db948bf13`

Workflow:
[37689420848](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37689420848) — SUCCESS.

Proof:
- stable asset identity, exact clip references;
- verified candidate, rejected incompatible media/path conflict;
- exact Undo/Redo, save/reopen and real-media relink validation;
- targeted 9/9 tests, full 411/411 tests and evidence 23/23 PASS;
- 27/27 workflow regression families SUCCESS on the same HEAD.

Evidence: `docs/evidence/features/S11_W8_003_SINGLE_ASSET_RELINK.md`.  
Artifact: `ANG-S11-W8-003-Single-Asset-Relink` / ID `11513225118`.

## W8-004 accepted

W8-004 validated scanner, verified explicit relink and UI-040 projection remain
accepted. Full evidence: `docs/evidence/features/S11_W8_004_BATCH_RELINK_SCAN.md`.

## W8-005 accepted

- Accepted W8-005 implementation/regression HEAD: `43cb1d04b5d519c26f843714c4b7cd9793054fe9`.
- Windows autosave qualification: [37724812333](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37724812333) **SUCCESS**.
- Artifact `ANG-S11-W8-005-Autosave-Catalog`, ID `11526779061`; ZIP SHA-256 `c9a305ccc6cee9744e271e7520df4722192fa27a2a44544cf8ab68c717cf556c`.
- Dedicated catalog tests **9/9 PASS**; full pytest **429/429 PASS**; owned evidence **12/12 PASS**.
- Ruff, mypy (76 files), lint-imports, architecture, no-secrets, source-of-truth **70/70**, frozen UI **42/42 SHA-256 PASS**.
- Full same-HEAD regression **27/27 workflow families SUCCESS, all attempt 1**; Windows portable foundation PASS.
- New and legacy autosave filename compatibility, deterministic timestamp ordering, validated per-project catalog, maximum **20** managed valid snapshots, corrupt/foreign isolation and write/unlink failure guards qualified.
- Source `.angproj` and `.bak` are never retention/prune targets; source bytes unchanged in evidence. UI-039 recovery is deferred to W8-006.

Evidence: `docs/evidence/features/S11_W8_005_AUTOSAVE_CATALOG.md`.

## W8-008 accepted

Project lifecycle session IDs, project/revision/hash stale tokens, bounded
read-only validation/recovery jobs and relink close/cancel guards were
qualified on Windows. **12/12** targeted, **471/471** full pytest,
**18/18** owned evidence and **27/27** same-HEAD regression PASS.
Accepted code HEAD `6c35b70bd9122664473a69eff6635ed9b71da5cb`; workflow
[37728798520](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37728798520);
artifact ID `11529365791`. See
`docs/evidence/features/S11_W8_008_STALE_JOBS.md`.

**Next:** S11-W8-009 — Structured Diagnostics + Redacted Diagnostic
Bundle — READY. W8-010 remains blocked. UI-001..042 frozen; AAVC read-only.

## W8-009 Redacted Diagnostics — PASS

- W8-009 accepted code/regression HEAD: `6a4ec93d445e71dc037bcc4dc6edff2008894268`.
- Windows W8-009 run: https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37730435314 — SUCCESS.
- Artifact `ANG-S11-W8-009-Redacted-Diagnostics` ID `11529353867`;
  ZIP SHA-256 `17bc6c66063c240258f8f27fd68e8755ea8d26b63ba73a498c96e1f6e08d3b6e`.
- **11/11** targeted tests, **482/482** full Python suite, **18/18**
  owned redaction evidence checks PASS.
- Ruff, mypy **84 files**, import architecture/security,
  source-of-truth **70/70**, frozen UI SHA **42/42** PASS.
- **27/27** same-code-HEAD regression workflows SUCCESS, all attempt 1;
  Windows portable, UI shell, media, E2E regressions PASS.
- Deterministic 128KiB bounded ZIP with only manifest.json/events.json;
  excludes project paths, contents, media, exception text and credentials.
- No canonical state/schema changes or frozen UI redesign.

Evidence: `docs/evidence/features/S11_W8_009_DIAGNOSTIC_BUNDLE.md`.

**Next:** SOL S11-W8-010 only. UI frozen; AAVC unchanged.
