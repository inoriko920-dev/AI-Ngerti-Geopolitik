# SOL INT-01B/B2-prep — Pure argv syntax safety

Date: 2026-10-08 WIB
Gate: IMPLEMENTED_PENDING_WINDOWS_CI / D1_PILOT_A_OWNER_PENDING
Stacked on Draft PR #18. This is a separate preparatory change, NOT execution of native FFmpeg.

- Pure inspect_native_command_shape checks absolute executable path syntax, immutable tuple args, NUL/type/relative/traversal rejection, and policy maximum counts and characters (including executable).
- Return immutable privacy-safe counts only. Never echo executable path, untrusted argv, environment or media contents.
- Valid arguments with Unicode, whitespace or shell metacharacters remain data. Future runner must use shell=False and never assemble a command string.
- Lexical path checks do NOT validate existence, executable hash, identity, symlinks or TOCTOU. No filesystem reads or subprocess calls occur.
- Workflow includes Windows Ruff/mypy/architecture/source-of-truth/no-secrets/UI42/targeted+full pytest and no-native-execution audit.
- D1 Pilot A external FFmpeg permission is still required for real B2 runner. B3 Windows child-tree, B4 FFprobe, B5 adapter, B6 real native QA all remain serial later gates. No UI, release, codec bundling or main merge.
