"""Pure Scene DOCX v1 semantic contract (Master Blueprint section 8.1).

No filesystem access or canonical ProjectState mutations are permitted here.
Only explicit scene/asset labels are trusted; ambiguous numbering is rejected.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_SCENE = re.compile(r"^\s*(?:Tampilan\s+)?Scene\s+(\d+)\s*:\s*([12])\s*$", re.I)
_ASSET = re.compile(r"^\s*Asset\s+(\d+)\s*:\s*(.*?)\s*$", re.I)
_SCENE_PREFIX = re.compile(r"^\s*(?:Tampilan\s+)?Scene\b", re.I)
_ASSET_PREFIX = re.compile(r"^\s*Asset\b", re.I)
MAX_SCENES = 1000
MAX_TEXT_LENGTH = 4096


class SceneDocxFormatError(ValueError):
    """Safe structural failure; never include user document text or file paths."""


@dataclass(frozen=True, slots=True)
class SceneAssetRow:
    number: int
    canonical_id: str
    description: str


@dataclass(frozen=True, slots=True)
class SceneDocxRow:
    number: int
    expected_visuals: int
    assets: tuple[SceneAssetRow, ...]
    source_context: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class SceneDocxPlan:
    scenes: tuple[SceneDocxRow, ...]
    asset_count: int


def parse_scene_docx_lines(lines: tuple[str, ...]) -> SceneDocxPlan:
    """Parse the *explicit* Scene N: 1/2 and global Asset N: lines.

    Non-control prose under a scene is retained verbatim as source context.
    No duration, media filenames or layout values are guessed.
    """
    scenes: list[SceneDocxRow] = []
    current_number = 0
    expected_visuals = 0
    assets: list[SceneAssetRow] = []
    context: list[str] = []
    next_asset = 1

    def finish_scene() -> None:
        if current_number == 0:
            return
        if len(assets) != expected_visuals:
            raise SceneDocxFormatError("scene asset count does not match header")
        scenes.append(
            SceneDocxRow(current_number, expected_visuals, tuple(assets), tuple(context))
        )

    for raw in lines:
        if not isinstance(raw, str):
            raise SceneDocxFormatError("DOCX paragraph is not text")
        line = raw.strip()
        if not line:
            continue
        if len(line) > MAX_TEXT_LENGTH:
            raise SceneDocxFormatError("DOCX paragraph exceeds safe length")

        header = _SCENE.fullmatch(line)
        if header is not None:
            finish_scene()
            number = int(header.group(1))
            if number != len(scenes) + 1 or number > MAX_SCENES:
                raise SceneDocxFormatError("scene numbering must be consecutive")
            current_number = number
            expected_visuals = int(header.group(2))
            assets = []
            context = []
            continue

        if _SCENE_PREFIX.match(line):
            raise SceneDocxFormatError("invalid or ambiguous scene header")

        asset = _ASSET.fullmatch(line)
        if asset is not None:
            if current_number == 0:
                raise SceneDocxFormatError("asset declared before first scene")
            number = int(asset.group(1))
            description = asset.group(2).strip()
            if number != next_asset or not description:
                raise SceneDocxFormatError("invalid or non-consecutive asset row")
            if len(assets) >= expected_visuals:
                raise SceneDocxFormatError("too many assets for scene")
            assets.append(SceneAssetRow(number, f"A{number:03d}", description))
            next_asset += 1
            continue

        if _ASSET_PREFIX.match(line):
            raise SceneDocxFormatError("invalid or ambiguous asset row")

        # Ordinary scene prose is not mistaken for an asset or dropped.
        if current_number:
            context.append(line)

    finish_scene()
    if not scenes:
        raise SceneDocxFormatError("no valid scenes in DOCX")
    return SceneDocxPlan(tuple(scenes), next_asset - 1)
