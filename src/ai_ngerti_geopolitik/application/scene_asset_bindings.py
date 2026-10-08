"""Read-only Scene DOCX Axxx asset binding and blocker projection.

The import candidate inventory is NOT canonical ProjectState and never
auto-commits or substitutes one media file for another.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from ai_ngerti_geopolitik.application.scene_docx_contract import SceneDocxPlan


class SceneAssetStatus(StrEnum):
    READY = "READY"
    MISSING = "MISSING"
    DUPLICATE = "DUPLICATE"
    CORRUPT = "CORRUPT"
    UNSUPPORTED = "UNSUPPORTED"


class SceneAssetScanError(RuntimeError):
    """Fixed, user-safe failure; filesystem paths are intentionally omitted."""


@dataclass(frozen=True, slots=True)
class SceneAssetCandidate:
    asset_id: str
    path: Path
    supported: bool
    readable: bool


@dataclass(frozen=True, slots=True)
class SceneAssetBinding:
    asset_id: str
    status: SceneAssetStatus
    path: Path | None
    candidates: tuple[Path, ...]


@dataclass(frozen=True, slots=True)
class SceneAssetInventory:
    bindings: tuple[SceneAssetBinding, ...]

    @property
    def ready_count(self) -> int:
        return sum(item.status is SceneAssetStatus.READY for item in self.bindings)

    @property
    def blockers(self) -> tuple[SceneAssetBinding, ...]:
        return tuple(item for item in self.bindings if item.status is not SceneAssetStatus.READY)

    @property
    def all_ready(self) -> bool:
        return bool(self.bindings) and not self.blockers


def bind_scene_asset_candidates(
    plan: SceneDocxPlan, candidates: tuple[SceneAssetCandidate, ...]
) -> SceneAssetInventory:
    """Bind only exact Axxx filename stems. Duplicates hard-block auto-selection."""
    ordered = [asset.canonical_id for scene in plan.scenes for asset in scene.assets]
    if not ordered or len(set(ordered)) != len(ordered) or len(ordered) != plan.asset_count:
        raise SceneAssetScanError("invalid scene asset plan")
    indexed: dict[str, list[SceneAssetCandidate]] = {key: [] for key in ordered}
    for item in candidates:
        if item.asset_id not in indexed:
            continue
        indexed[item.asset_id].append(item)
    result: list[SceneAssetBinding] = []
    for asset_id in ordered:
        matches = sorted(indexed[asset_id], key=lambda x: (str(x.path).casefold(), str(x.path)))
        paths = tuple(x.path for x in matches)
        if not matches:
            status = SceneAssetStatus.MISSING
        elif len(matches) > 1:
            status = SceneAssetStatus.DUPLICATE
        elif not matches[0].supported:
            status = SceneAssetStatus.UNSUPPORTED
        elif not matches[0].readable:
            status = SceneAssetStatus.CORRUPT
        else:
            status = SceneAssetStatus.READY
        result.append(
            SceneAssetBinding(
                asset_id, status, paths[0] if status is SceneAssetStatus.READY else None, paths
            )
        )
    return SceneAssetInventory(tuple(result))


@dataclass(frozen=True, slots=True)
class VerifiedSceneImage:
    """Read-only image identity, not yet a canonical Asset."""

    asset_id: str
    path: Path
    fingerprint_sha256: str
    file_size: int
    width: int
    height: int


@dataclass(frozen=True, slots=True)
class VerifiedSceneImageSet:
    images: tuple[VerifiedSceneImage, ...]
