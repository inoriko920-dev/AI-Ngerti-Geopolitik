# PLAN — CURRENT IMPLEMENTATION PHASE

**SF-STEP 11 is active. W0/W1/W2/W3/W4 PASS. W5-001..006 PASS. W5-007 PASS_WITH_PROVISIONAL_MIC_HARDWARE.**

## Accepted W5-007

- implementation HEAD:
  `be4daa667bf5030ba3810460cc6841a2e8be4fee`;
- workflow:
  `37578572691` — SUCCESS;
- dedicated RecorderPort boundary added;
- staging-first recording flow implemented;
- stage validation before finalization/import;
- collision-safe no-overwrite finalization;
- W5-006 canonical narration import/bind reused;
- failed/cancelled/empty/invalid capture preserves current narration;
- successful import/bind remains Undo/Redo-safe;
- Windows FFmpeg DirectShow recorder added;
- cancellation can terminate live capture;
- targeted deterministic tests 6/6 PASS;
- full pytest PASS;
- all W5-006/W5-005/W5-004/W4/W3/W2/W1/W0/S10/S09/S08 regressions
  SUCCESS.

Hardware result:
- GitHub Windows runner DirectShow audio device count = 0;
- no real physical recording could be attempted;
- status therefore remains
  **PASS_WITH_PROVISIONAL_MIC_HARDWARE**.

Evidence:
`docs/evidence/features/S11_W5_007_MICROPHONE_RECORDING.md`.

## Active next task

**S11-W5-008 — Frozen UI parity**

Implement only frozen W5 surfaces:
- SCR-008 Subtitle Workspace;
- UI-017 cue/text editor;
- UI-033 subtitle style;
- UI-034 subtitle animation;
- UI-035/UI-036 timing/highlight states only where supported;
- SCR-009 / UI-018 narration workspace;
- WIN-001 narration recording;
- WIN-003 subtitle edit/timing tools.

UI constraints:
- exact frozen AAVC parity; no redesign;
- semantic intents/controllers only;
- no direct engine/domain JSON mutation from widgets;
- hidden/disabled unsupported animation labels;
- explicit **NOT speech alignment** wording for deterministic per-word fallback;
- device-unavailable and provisional microphone state must be honest.

W5-008 must not start:
- W5-009 combined real-media qualification;
- W5-010 closure;
- Gemini/provider work;
- final release work.

Do not begin W5-008 until owner says `lanjutkan`.
