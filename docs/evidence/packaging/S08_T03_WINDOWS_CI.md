# S08-T03 — WINDOWS CI & PORTABLE PACKAGING SCAFFOLD

Status: ACTIVE — CI evidence pending.

Baseline: `main @ 61a91b3fbc3cf01ec7d517ef3d0e94823ddbad7e`.

Scope added:
- Windows x64 workflow on CPython 3.12.10;
- uv 0.12.21 lock resolution artifact;
- Ruff/mypy/Import Linter/pytest/pytest-qt/security/UI-reference gates;
- PyInstaller 6.22.3 onedir foundation scaffold;
- portable foundation ZIP artifact.

The executable is intentionally only a foundation smoke and must not be called the product editor or final release.

Gate remains NOT TESTED until the GitHub Actions run is inspected.
