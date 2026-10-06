# AGENTS.md — WAJIB DIBACA SEBELUM BEKERJA

Entry gate wajib untuk AI/agent/sesi yang melanjutkan **AI Ngerti Geopolitik**.

## Read order

1. `AGENTS.md`
2. Software Factory master + guide
3. seluruh `docs/planning/`
4. `docs/project/PRODUCT.md`
5. `docs/project/UI_SPEC.md`
6. `docs/project/ARCHITECTURE.md`
7. `docs/project/CODE_CONSTITUTION.md`
8. `docs/project/TASKS.md`
9. `HANDOFF.md`
10. `docs/PROJECT_STATUS.md`
11. `docs/DECISIONS_LOCKED.md`
12. `docs/REPOSITORY_RULES.md`
13. source/tests/evidence aktual.

Jika DOCX tidak dapat dibaca, gunakan TXT mirror di folder yang sama.

## Implementation rules

- Kerjakan satu task Software Factory aktif pada satu waktu.
- AAVC repo read-only.
- UI-001..UI-042 frozen 1:1; no silent redesign.
- Search -> Understand -> Modify before creating owner/service/helper.
- One concern = one canonical owner.
- Dependency: presentation -> application -> domain; infrastructure implements inward ports; bootstrap constructs only.
- Domain tidak boleh import Qt/media-engine/Gemini/keyring/process implementation.
- Presentation tidak boleh import concrete infrastructure.
- Future project mutation wajib melalui semantic CommandBus/CommandBatch.
- No blocking network/probe/render/native-engine work on UI thread.
- No plaintext secret, hardcoded developer path, fake feature, fake green, atau static-image runtime UI.
- Material architecture exception requires ADR/Astra review.

## Foundation commands verified S08-T02

```text
PYTHONPATH=src python -m ai_ngerti_geopolitik
PYTHONPATH=src python -m pytest -q
python scripts/verify/run_foundation_checks.py --root .
python scripts/verify/verify_architecture.py --root .
python scripts/verify/verify_ui_reference_manifest.py --root .
python scripts/verify/verify_no_secrets.py --root .
python -m compileall -q src
```

uv/Ruff/mypy/Import Linter/detect-secrets/pip-audit commands become fully authoritative after S08-T03 produces the real lock and Windows CI evidence.

## Astra review triggers

Stop for new top-level architecture layer/service, dependency exception, project schema semantic change, breaking MediaEnginePort change or engine switch, new native/license-impacting dependency, frozen UI structural delta, new destructive AI permission family, credential backend change, or packaging-model change.

## Before ending meaningful work

Update `docs/PROJECT_STATUS.md`, `HANDOFF.md`, task/evidence, and decision records if a locked decision changes.
