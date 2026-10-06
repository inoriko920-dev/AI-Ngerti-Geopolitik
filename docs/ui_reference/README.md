# UI Reference — AI Ngerti Geopolitik

- UI Bible: **UIB-ANG-v1.0**
- Source: **AAVC UIF-AAVC-v1.0**
- Coverage: **UI-001..UI-042 = 42/42**
- Decision: **REUSE_1_TO_1 / APPROVED_FOR_FREEZE**
- Runtime UI must be real interactive widgets, never static screenshots.

## Authoritative integrity

Per-image SHA-256 values are stored in:
- `UI_REFERENCE_MANIFEST.md`

During S08-T01, the exact original 42 PNG files were recovered and verified locally:
- SHA/size verification: **42/42 PASS**
- exact local pack: `ANG_UI_REFERENCE_RAW_42_EXACT.zip`
- pack SHA-256: `2fc3e43b5625b0ec709095b53549c6c098f0dbd9c32a0789eb6e2683e59feef2`
- pack bytes: `65,497,507`

## Remote binary gate — NOT PASSED

The exact raw PNG/ZIP bytes are **not yet committed to this repository** because the available GitHub connector currently has no exposed binary-file handoff from the model container/conversation file store.

The manifest/index alone is not sufficient for the pre-coding gate.

Do not:
- substitute preview JPGs;
- regenerate the UI;
- use reconstructed DOCX as the raw-image pack;
- use the VOID ANG 42-prompt ZIP.

S08-T01 remains BLOCKED until the exact binary payload is committed and the remote commit is re-verified 42/42.
