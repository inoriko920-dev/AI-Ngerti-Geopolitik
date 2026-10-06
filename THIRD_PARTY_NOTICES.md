# THIRD-PARTY NOTICES — FOUNDATION SCAFFOLD

This file belongs to the SF-STEP 08 **foundation packaging scaffold**, not a final product release.

The portable foundation artifact is built with:
- CPython 3.12.10 runtime;
- PyInstaller 6.22.3 bootloader/runtime components;
- transitive components selected by the resolved `uv.lock`.

PySide6 is a project runtime dependency and is exercised by CI Qt smoke. The current foundation executable does not import or claim the final UI implementation.

Before any release candidate, regenerate a complete dependency/native manifest and preserve required notices for binaries actually bundled. Media engine, FFmpeg, Gemini, and final Qt UI distribution compliance are later gates.
