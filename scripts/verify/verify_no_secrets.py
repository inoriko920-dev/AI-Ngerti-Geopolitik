from __future__ import annotations

import argparse
import re
from pathlib import Path

TEXT_EXTENSIONS = {".py", ".toml", ".ini", ".cfg", ".yml", ".yaml", ".json", ".ps1", ".sh"}
SKIP_PARTS = {".git", ".venv", "build", "dist", "docs", "__pycache__"}
PATTERNS = [
    re.compile(r"AIza[0-9A-Za-z_-]{30,}"),
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
]
ASSIGNMENT = re.compile(
    r"(?i)(?:api[_-]?key|access[_-]?token|secret|password)\s*=\s*[\"']([^\"']{12,})[\"']"
)
PLACEHOLDER_WORDS = {"example", "placeholder", "dummy", "changeme", "test-only", "not-a-secret"}


def scan(root: Path) -> list[str]:
    findings: list[str] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        if any(part in SKIP_PARTS for part in path.parts):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for lineno, line in enumerate(text.splitlines(), start=1):
            if any(pattern.search(line) for pattern in PATTERNS):
                findings.append(f"{path}:{lineno}: likely secret/token")
            for match in ASSIGNMENT.finditer(line):
                value = match.group(1).lower()
                if not any(word in value for word in PLACEHOLDER_WORDS):
                    findings.append(f"{path}:{lineno}: secret-like assignment")
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    findings = scan(args.root)
    if findings:
        for finding in findings:
            print(f"FAIL {finding}")
        return 1
    print("PASS no obvious committed secrets in source/config/test/script scope")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
