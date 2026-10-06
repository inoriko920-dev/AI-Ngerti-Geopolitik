from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

SCRIPT = Path(__file__).parents[2] / "scripts/verify/verify_architecture.py"
spec = importlib.util.spec_from_file_location("verify_architecture", SCRIPT)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def test_current_source_has_no_architecture_violations() -> None:
    root = Path(__file__).parents[2]
    assert module.find_violations(root / "src") == []


def test_presentation_to_infrastructure_violation_is_detected(tmp_path: Path) -> None:
    source = tmp_path / "src/ai_ngerti_geopolitik/presentation"
    source.mkdir(parents=True)
    (source / "bad.py").write_text(
        "from ai_ngerti_geopolitik.infrastructure import adapters\n", encoding="utf-8"
    )
    violations = module.find_violations(tmp_path / "src")
    assert len(violations) == 1
    assert "presentation must not import internal layer infrastructure" in violations[0].message
