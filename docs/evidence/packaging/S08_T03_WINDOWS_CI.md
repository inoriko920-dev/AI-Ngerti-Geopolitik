# S08-T03 — WINDOWS CI & PORTABLE PACKAGING SCAFFOLD

Status: **CANDIDATE PASS — final checkpoint run pending after workflow trigger hardening**

## Successful implementation run

Workflow: **S08 Windows Foundation**  
Run ID: `37499102659`  
Run number: 4  
Commit: `c708bdf219ca93d31cb2cc5ec7d44692498e2d89`  
Result: **SUCCESS**

Windows environment:
- `windows-latest`, x64;
- CPython **3.12.10**;
- uv **0.12.21**;
- PySide6 **6.11.1**;
- PyInstaller **6.22.3**.

PASS jobs:
- Resolve lock;
- Quality and architecture;
- Tests;
- Qt smoke;
- UI reference integrity;
- Security and dependency audit;
- Portable foundation.

Quality evidence:
- Ruff format PASS;
- Ruff lint PASS;
- mypy PASS — 8 source files, 0 issues;
- Import Linter PASS — 4 contracts kept, 0 broken;
- custom architecture verifier PASS;
- source-of-truth PASS — 70/70.

Test/UI evidence:
- pytest PASS — 7 tests;
- dedicated Qt lifecycle smoke PASS;
- frozen UI references PASS — 42/42 SHA-256.

Security evidence:
- detect-secrets scoped source/config scan PASS;
- custom secret verifier PASS;
- pip-audit PASS — no known vulnerabilities found.

Resolved lock:
- committed `uv.lock`;
- run-4 lock artifact ID: `11428502590`;
- artifact wrapper digest: `sha256:641b9efb973707714f9c5a6e2eb6615d06bd95df3b3af75020658a23f3f83d54`;
- extracted `uv.lock` size: 103,889 bytes;
- extracted `uv.lock` SHA-256: `6a6776743f3965171b3466bccad5d7c8c2ef968ef5af9b70303d24f21a35b5bd`.

Portable foundation:
- PyInstaller onedir build PASS;
- Windows executable smoke PASS;
- output: `AI Ngerti Geopolitik foundation ready; product UI is not implemented in SF-STEP 08.`;
- inner portable ZIP SHA-256: `03a2aa9dcbe8eb9197ba889630d8b13472f9bec3031cf4559ccf17013323dc0f`;
- inner portable ZIP size: 8,448,103 bytes;
- GitHub artifact ID: `11429540449`;
- artifact name: `AI-Ngerti-Geopolitik-S08-Foundation-Windows-x64`;
- artifact wrapper size: 8,417,926 bytes;
- artifact wrapper digest: `sha256:5949a943ff20e9bbc2af58b8c661d80f439575185a8e211fd524c74c8db3a518`.

## Failure history retained

Run 1 (`37497820132`) and run 2 (`37498380436`) failed on real foundation defects; no check was disabled to obtain green. Run 3 (`37498681106`) isolated the last Ruff lint issue. Each root cause was fixed before run 4 achieved full green.

## Scope truth

This artifact is **foundation-only**, not the ANG editor:
- no 42-screen production UI;
- no libopenshot/MLT production integration;
- no Gemini editing;
- no real video render/export feature;
- no release claim.

The workflow trigger is now hardened so later status/evidence-only commits do not create meaningless CI loops, while source, tests, configuration, UI references/manifests, planning, dependencies and workflow changes still trigger CI.

A final workflow run on the workflow-hardening checkpoint is required before closing S08-T03.
