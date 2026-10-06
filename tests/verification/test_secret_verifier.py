from __future__ import annotations

import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).parents[2] / "scripts/verify/verify_no_secrets.py"
spec = importlib.util.spec_from_file_location("verify_no_secrets", SCRIPT)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_source_scope_has_no_obvious_secrets() -> None:
    root = Path(__file__).parents[2]
    assert module.scan(root) == []
