# SF-STEP 09 — APP SHELL / UI IMPLEMENTATION EVIDENCE

**Status:** PASS  
**Role:** SOL  
**Accepted ANG commit:** `61225eca38115a636e062d3e795f7884049d19d4`  
**Windows CI run:** `37520166438` — SUCCESS  
**AAVC comparison baseline:** read-only repo, commit `7d77fc9f724d359c7da6c4796dffce5104740952`, CI run `37498549910`

## Objective

Menerjemahkan UI AAVC yang telah dibekukan menjadi **app shell PySide6 nyata**, tanpa redesign dan tanpa memasukkan media engine, Gemini execution, persistence lengkap, atau render nyata sebelum STEP yang sesuai.

## Implemented shell

Representative frozen/AAVC states yang memiliki real Qt surface dan automated capture:
- `UI-002` — Home / Project Hub;
- `UI-003` — New Project / Scene DOCX;
- `UI-010` — Main Editor Overview;
- `UI-013` — SINGLE scene;
- `UI-014` — DOUBLE scene;
- `UI-027` — Subtitle workspace;
- `UI-035` — Export settings dialog;
- `UI-041` — Validation center.

Implementation uses real PySide6 widgets, layout, dialogs and semantic UI intents. PNG references are evidence only and are not runtime screens.

## Windows quality gate

Run `37520166438` passed both jobs:
1. **UI quality, tests and visual evidence — PASS**
2. **Portable UI shell — PASS**

Verified in the passing run:
- Ruff format PASS;
- Ruff lint PASS;
- mypy PASS — 19 source files, no issues;
- Import Linter PASS — 4 contracts kept, 0 broken;
- custom architecture verifier PASS;
- source-of-truth verifier PASS — 70/70;
- frozen UI manifest PASS — 42/42 SHA-256;
- pytest PASS — **17 tests**;
- representative screenshot capture PASS — **8/8** at canonical logical 1920×1080;
- actual-vs-reference evidence generated and uploaded;
- PyInstaller onedir build PASS;
- packaged Windows UI shell smoke PASS.

Regression workflow **S08 Windows Foundation** also passed on the same accepted commit in run `37520166400`.

## Direct AAVC runtime parity review

To honor the owner's instruction “copas UI AAVC”, STEP 09 also compared ANG runtime screenshots against screenshots produced by the actual read-only AAVC implementation.

AAVC runtime evidence:
- repo: `inoriko920-dev/AI-Automatic-Video-Composer`;
- commit: `7d77fc9f724d359c7da6c4796dffce5104740952`;
- CI run: `37498549910`;
- artifact: `step09-ui-actual`, ID `11429380147`.

After export/validation dialog parity remediation, comparison metrics for representative states were:

| State | MAE | Exact pixels | Pixels within max-channel diff <=5 |
|---|---:|---:|---:|
| UI-002 | 3.465 | 91.313% | 91.367% |
| UI-003 | 0.778 | 98.470% | 98.591% |
| UI-010 | 4.948 | 92.429% | 92.661% |
| UI-013 | 3.322 | 84.514% | 92.778% |
| UI-014 | 3.637 | 84.148% | 92.256% |
| UI-027 | 4.893 | 82.479% | 90.739% |
| UI-035 | 3.241 | 89.470% | 92.750% |
| UI-041 | 5.656 | 87.750% | 87.983% |

Representative average:
- MAE: **3.74246**
- exact pixel match: **88.8216%**
- within diff <=5: **92.3906%**

These figures are evidence of close runtime parity, **not a claim of pixel-identical output**. Remaining differences are primarily branding, font/rasterization/capture behavior, and small fixture details.

Notable remediation:
- UI-035 export dialog improved from MAE **13.087** to **3.241** after replacing the custom ANG interpretation with the simpler AAVC reference-era hierarchy.

## Windows portable artifact

Final STEP 09 artifact from run `37520166438`:
- artifact name: `AI-Ngerti-Geopolitik-S09-UI-Shell-Windows-x64`;
- artifact ID: `11440840340`;
- wrapper size: **50,502,014 bytes**;
- wrapper SHA-256: `25399ac1b9e1b3c10db1834c269c416e52a444e7e4e657dca7b69ad516ab8cd8`.

Inner portable ZIP:
- file: `AI-Ngerti-Geopolitik-UI-Shell-Windows-x64.zip`;
- size: **50,660,130 bytes**;
- SHA-256: `47fe8296d1eaa7dbf0b859b2e65335c25b51183d19b7f4eed596a64c2ea162c0`.

Visual evidence artifact:
- name: `ANG-S09-UI-Evidence`;
- artifact ID: `11439161765`;
- wrapper SHA-256: `28d6cff3260fed49b9df115c8c7b5891313f751f570c212898329b375a6479b5`.

## Scope truth

STEP 09 **does not claim** these are complete:
- real media decode/playback/timeline engine;
- libopenshot/MLT production adapter;
- ProjectState persistence/reopen;
- real split/trim/edit mutation;
- real Undo/Redo history;
- real video export/render;
- Gemini execution.

Those capabilities remain later Software Factory work. STEP 09 proves the real AAVC-style UI shell, navigation/state surfaces, presentation boundary, deterministic evidence, Windows packaging and smoke behavior.

## Gate

**SF-STEP 09 = PASS.**

No silent redesign was accepted. Old AAVC repo remained read-only.

## Exact next STEP

**SF-STEP 10 — Minimum End-to-End Vertical Slice**

STEP 10 must prove one narrow real workflow end-to-end before feature expansion. Do not start STEP 10 without the owner's next `lanjutkan`.
