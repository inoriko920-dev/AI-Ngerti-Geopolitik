from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
from pathlib import Path

PACKAGE = "ai_ngerti_geopolitik"
INTERNAL_FORBIDDEN = {
    "domain": {"application", "presentation", "infrastructure", "bootstrap"},
    "application": {"presentation", "infrastructure", "bootstrap"},
    "presentation": {"infrastructure", "bootstrap"},
    "infrastructure": {"presentation", "bootstrap"},
    "bootstrap": set(),
}
EXTERNAL_FORBIDDEN = {
    "domain": {"PySide6", "openshot", "mlt", "google", "keyring", "subprocess"},
    "application": {"PySide6", "openshot", "mlt", "google", "keyring"},
    "presentation": {"openshot", "mlt", "google", "keyring", "subprocess"},
    "infrastructure": set(),
    "bootstrap": set(),
}


@dataclass(frozen=True, slots=True)
class Violation:
    path: Path
    line: int
    message: str


def _layer(path: Path, package_root: Path) -> str | None:
    try:
        rel = path.relative_to(package_root)
    except ValueError:
        return None
    return rel.parts[0] if rel.parts else None


def _absolute_imports(tree: ast.AST, module_parts: tuple[str, ...]) -> list[tuple[int, str]]:
    found: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.extend((node.lineno, alias.name) for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                base = list(module_parts[: -node.level]) if node.level <= len(module_parts) else []
                if node.module:
                    base.extend(node.module.split("."))
                name = ".".join(base)
            else:
                name = node.module or ""
            if name:
                found.append((node.lineno, name))
    return found


def find_violations(src_root: Path) -> list[Violation]:
    package_root = src_root / PACKAGE
    violations: list[Violation] = []
    for path in sorted(package_root.rglob("*.py")):
        layer = _layer(path, package_root)
        if layer not in INTERNAL_FORBIDDEN:
            continue
        rel = path.relative_to(src_root).with_suffix("")
        module_parts = rel.parts
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for line, imported in _absolute_imports(tree, module_parts):
            if imported.startswith(f"{PACKAGE}."):
                target = imported.split(".")[1]
                if target in INTERNAL_FORBIDDEN[layer]:
                    violations.append(
                        Violation(
                            path,
                            line,
                            f"{layer} must not import internal layer {target}: {imported}",
                        )
                    )
            top = imported.split(".")[0]
            if top in EXTERNAL_FORBIDDEN[layer]:
                violations.append(
                    Violation(
                        path,
                        line,
                        f"{layer} must not import external package {top}: {imported}",
                    )
                )
    return violations


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    violations = find_violations(args.root / "src")
    if violations:
        for item in violations:
            print(f"FAIL {item.path}:{item.line}: {item.message}")
        return 1
    print("PASS architecture boundaries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
