from __future__ import annotations

import argparse
from pathlib import Path

PLANNING_BASES = [
    "00_MASTER_BLUEPRINT_AI_NGERTI_GEOPOLITIK",
    "01_STEP_00_PROJECT_INTAKE_AI_NGERTI_GEOPOLITIK",
    "02_STEP_01_PRODUCT_DEFINITION_AI_NGERTI_GEOPOLITIK",
    "03_STEP_02_EXISTING_SOLUTION_GITHUB_DISCOVERY_AI_NGERTI_GEOPOLITIK",
    "04_STEP_03_UI_UX_INVENTORY_AI_NGERTI_GEOPOLITIK",
    "05_STEP_04_UI_DESIGN_REFERENCE_ADOPTION_AI_NGERTI_GEOPOLITIK",
    "06_STEP_05_UI_FREEZE_PRODUCT_BLUEPRINT_AI_NGERTI_GEOPOLITIK",
    "07_STEP_06_ARCHITECTURE_TECHNOLOGY_DECISION_AI_NGERTI_GEOPOLITIK",
    "08_STEP_07_CODE_CONSTITUTION_REPOSITORY_ARCHITECTURE_AI_NGERTI_GEOPOLITIK",
]


def required_paths() -> list[Path]:
    paths = [
        Path("AGENTS.md"),
        Path("HANDOFF.md"),
        Path("docs/PROJECT_STATUS.md"),
        Path("docs/DECISIONS_LOCKED.md"),
        Path("docs/REPOSITORY_RULES.md"),
        Path("docs/SOURCE_OF_TRUTH_INDEX.md"),
        Path("docs/software_factory/00_MASTER_SOFTWARE_FACTORY_PROMPT.txt"),
        Path("docs/software_factory/PANDUAN_PENGGUNAAN_SOFTWARE_FACTORY_ASTRA_SOL.docx"),
        Path("docs/software_factory/PANDUAN_PENGGUNAAN_SOFTWARE_FACTORY_ASTRA_SOL.txt"),
        Path("docs/ui_reference/UI_REFERENCE_MANIFEST.md"),
    ]
    for base in PLANNING_BASES:
        paths.extend(
            [
                Path(f"docs/planning/{base}.docx"),
                Path(f"docs/planning/{base}.txt"),
            ]
        )
    paths.extend(Path(f"docs/ui_reference/raw/UI-{index:03d}.png") for index in range(1, 43))
    return paths


def missing(root: Path) -> list[Path]:
    return [path for path in required_paths() if not (root / path).is_file()]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    absent = missing(args.root)
    if absent:
        for path in absent:
            print(f"FAIL missing source-of-truth: {path.as_posix()}")
        return 1
    count = len(required_paths())
    print(f"PASS source-of-truth files: {count}/{count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
