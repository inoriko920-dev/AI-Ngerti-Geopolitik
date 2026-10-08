# AI Ngerti Geopolitik

> **STATUS ON THIS UNMERGED FEATURE STACK: SF12-T01..T09 engineering gates PASS; SF12-T10 separate Windows packaged qualification PASS, combined desktop product/render UI and native licensing/release BLOCKED. Main is still the W8 closure baseline. Product GUI export is DISABLED, portable editor NOT FINAL; native FFmpeg/codec distribution and libopenshot engine decision remain pending. W5 physical microphone and W6/W7 live Gemini PROVISIONAL.**

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

**Current:** SOL S11-W8-010 IN_VERIFICATION. UI frozen; AAVC unchanged.

## W8-010 accepted closure — 2026-10-08 WIB

**W8-010 accepted implementation and same-HEAD regression:** `45c3294f5a8c93cee17369fa4b95122e3fca035b`.

- [Windows W8-010 UI/GOLDEN-03 run](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37732709194): **SUCCESS**.
- Artifact `ANG-S11-W8-010-UI-GOLDEN03`, ID `11530068997`, size 11,387,537 bytes.
- Artifact ZIP SHA-256: `4a24f45f3c6ef6d73924ec83d0ea2149b1490119abb766dd079d6db2a5840241`.
- **5/5** targeted Qt controller tests, **487/487** full Python suite, **23/23** owned GOLDEN-03 evidence checks PASS.
- Ruff, mypy **85 source files**, lint-imports, architecture and no-secret checks PASS; source-of-truth **70/70** PASS.
- Frozen UI-001..042 manifest **42/42 SHA-256 PASS** — no raster redesign or AAVC source changes.
- **27/27** same-code-HEAD workflow families **SUCCESS on attempt 1**, including S08 portable foundation, S09 UI shell, S10 real Windows E2E, W0-W7 and W8.
- Demonstrated live UI-041 missing referenced media BLOCKER, UI-040 bounded worker discovery and fingerprint-verified manual relink, canonical CommandBus/Undo-Redo, revalidation, save/reopen, UI-039 explicit crash snapshot restoration without silent source overwrite, and redacted diagnostic ZIP.
- Fixed a real compatibility regression: FFprobe is initialized lazily only during a media probe, so the Qt shell and fake-probe tests do not require an installed FFprobe.
- W5 physical microphone and W6/W7 live Gemini qualification remain provisional, not claimed as PASS.

**Next exact action:** SF-STEP 12 planning/contract readiness review only, after the owner's next `lanjutkan`. Do not implement STEP 12 in this W8-010 turn.
