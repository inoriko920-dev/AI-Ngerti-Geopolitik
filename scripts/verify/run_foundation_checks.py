from __future__ import annotations

import argparse
import compileall
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from verify_architecture import find_violations  # noqa: E402
from verify_no_secrets import scan  # noqa: E402
from verify_source_of_truth import missing  # noqa: E402
from verify_ui_reference_manifest import verify as verify_ui  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    root = args.root.resolve()
    failures: list[str] = []

    missing_paths = missing(root)
    if missing_paths:
        failures.append(f"source-of-truth missing: {len(missing_paths)}")
    failures.extend(verify_ui(root))
    failures.extend(item.message for item in find_violations(root / "src"))
    failures.extend(scan(root))
    if not compileall.compile_dir(root / "src", quiet=1):
        failures.append("compileall failed")

    if failures:
        for failure in failures:
            print(f"FAIL {failure}")
        return 1
    print("PASS foundation checks: source-of-truth, UI 42/42, architecture, secrets, compile")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
