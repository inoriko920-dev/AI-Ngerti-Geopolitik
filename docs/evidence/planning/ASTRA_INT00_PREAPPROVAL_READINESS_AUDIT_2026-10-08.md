# ASTRA INT-00 — Read-only Readiness Reaudit (2026-10-08 WIB)

**Gate:** `AUDIT_PASS / OWNER_AUTHORIZATION_BLOCKED / SOL_CODING_NOT_STARTED`  
**Baseline:** branch `planning/astra-sf12-post-t10-integration-adr-20261008` at `18eecc5a673dd748a49b4ba5b4f17690741316bc`.  
**Scope:** Verify the existing GitHub plan / PR topology / proofs and explicitly record unresolved decisions. This is a **readiness audit only**, NOT acceptance of ADR, native redistribution, or new code authorization.

## Read-only GitHub reconciliation

- `main` remains at `c9154eef85f8b475630816a7c63f5e2b52bf1523` (unchanged from pre-SF12).
- All twelve drafts are open and stacked in order. PR #1 targets main; #2 targets PR #1's branch, continuing one stage at a time; PR #11 targets T09 and PR #12 targets PR #11's T10 branch. **No PR was merged or rebased in this audit.**
- T10 implementation `866464471e5926d7f9a782e56f2030ed2425e7a2` [Windows run 37746818497](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37746818497): completed SUCCESS, real packaged media CLI and separately packaged UI shell. This is **not** an integrated editor.
- Prior ASTRA proposal `18eecc5a673dd748a49b4ba5b4f17690741316bc` [Windows run 37748230963](https://github.com/inoriko920-dev/AI-Ngerti-Geopolitik/actions/runs/37748230963): completed SUCCESS. Source-of-truth 70/70, frozen UI SHA manifest 42/42, pytest, architecture and editable planning DOCX 82 paragraphs PASS.
- The existing DOCX is real and committed at `docs/planning/13_ASTRA_POST_T10_INTEGRATION_AND_NATIVE_LICENSE_PLAN_2026-10-08.docx` (27,582 bytes), with TXT and Markdown mirrors. No need to invent or replace a second DOCX for this same gate.
- The repository tree contains the 42 frozen reference PNG files and **no top-level LICENSE**. `THIRD_PARTY_NOTICES.md` explicitly describes itself as an incomplete foundation scaffold.
- Current `presentation/dialogs.py` still sets `btn_export_render` from a fail-closed capability gate. `bootstrap/main.py` wires W8 runtime; it does **not** instantiate/route the SF12 T08 job service for the live Qt render button. `ExportCapabilities.can_start_render` remains false unless **both** a qualified exporter and a wired handler are declared and the native toolchain is detected.
- Existing `infrastructure/export_capability_probe.py` uses bounded `ffmpeg -encoders` and `ffprobe -version` calls. This is a preliminary detection contract, **not** sufficient proof that a user-configured native binary is trusted for execution. The approved pilot must account for path spoofing/FFmpeg disappearance.

## Decision matrix (all pending)

| Decision | Current finding | Blocked capability |
|---|---|---|
| D1 — external FFmpeg Pilot A | ASTRA recommended, user has not explicitly said “Setuju Pilot A” | **All implementation INT-01..INT-09** |
| D2 — final portable format | Separate encoder install vs truly self-contained ZIP not chosen | Native packaging architecture; cannot ship bundled GPL codecs |
| D3 — software/native licensing | No top-level LICENSE; scaffold notices only; FFmpeg x264/x265 / Qt / libopenshot obligations require owner/legal review | Native redistribution and final public release |
| D4 — engine selection | D-005 still lists libopenshot primary *candidate*, MLT fallback; no engine replacement approved | Production libopenshot switch or MediaEnginePort contract change |

**Guard:** A generic “lanjutkan” or successful CI is not evidence of acceptance for D1-D4. The next user instruction can approve the scoped pilot explicitly without granting final binary distribution permission.

## Minimal safe next step / owner decision

Recommended exact opt-in: **“Saya setuju Pilot A: integrasikan UI dan worker menggunakan FFmpeg eksternal untuk pengujian. Jangan bundel FFmpeg, jangan ubah UI, dan jangan rilis aplikasi final.”**

Even after D1 approval, D2-D4 must be tracked as pending release/native decisions. ASTRA should first record accepted D1 and a constrained pilot ADR gate, then SOL can start INT-01 only within its scope; any native bundling, LICENSE choice or production engine switch still requires explicit owner authority. For a fully final product, all four decisions and legal notices must be accepted before release.

## Change boundary and evidence

- Changed this turn: **documentation readiness only** — the audit, status and handoff; no app source, core ports, native dependencies, reference PNG, GitHub PR base, `main`, or binary release changes.
- Status: `INT00_PREAPPROVAL_REVIEW_PASS / GO_NO_GO_BLOCKED`.
- Next **after explicit owner approval**: finalize owner-approved pilot ADR and start INT-01 native executable validation.
