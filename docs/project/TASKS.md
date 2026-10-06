# TASKS

## S08-T01 — DONE / PASS
Source-of-truth + exact UI reference gate.

## S08-T02 — DONE
Repository skeleton, toolchain contracts, architecture fitness and foundation tests.

## S08-T03 — DONE / PASS
Final Windows run `37500196775` is fully green on verified commit `dcb1326ac2fececdf229190b4d62a5c35cbf33fc`.

Evidence includes:
- real lock;
- quality/type/import architecture;
- tests + Qt;
- UI 42/42;
- security/audit;
- portable foundation build and EXE smoke.

## SF-STEP 08 — PASS

## NEXT — SF-STEP 09
App Shell / UI Implementation.

First wave:
- implement actual PySide6 shell against frozen AAVC UI contract;
- use fixture/dummy project data only where product behavior is not scheduled;
- implement real widgets/layout/states, not PNG runtime UI;
- capture actual 1920×1080 screenshots;
- compare representative frozen states before expanding coverage;
- do not implement full engine/Gemini/render stack in the shell wave.
