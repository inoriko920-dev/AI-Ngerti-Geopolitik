# TASKS

## S08-T01 — DONE / PASS
Source-of-truth and exact frozen UI references are committed and verified 42/42.

## S08-T02 — DONE / PASS_WITH_PROVISIONAL
Repository/source/test/tool foundation exists and local non-target checks passed. Its former Windows/toolchain provisional items are now resolved by S08-T03 CI evidence.

## S08-T03 — ACTIVE / CANDIDATE PASS
Run 4 (`37499102659`) is fully green on Windows x64 / Python 3.12.10:
- lock PASS;
- quality/architecture PASS;
- tests PASS;
- Qt smoke PASS;
- UI 42/42 PASS;
- security/audit PASS;
- portable foundation build + executable smoke PASS.

A final checkpoint CI run is required because this task also hardens the workflow trigger. After that run succeeds, mark S08-T03 and SF-STEP 08 PASS.

## NEXT AFTER SF-STEP 08 PASS
SF-STEP 09 — App Shell / UI Implementation. First wave must implement the real AAVC-frozen shell with fixture/dummy data, not engine/Gemini/render features.
