"""Deterministic Scene DOCX -> timeline review; no unsupported image Clip state.

A duration must be explicitly provided for each scene. The resulting lanes
and half-open frame ranges are *preview/review metadata*, not a renderer
qualification or a second owner of canonical ProjectState.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from ai_ngerti_geopolitik.application.scene_asset_bindings import SceneAssetInventory
from ai_ngerti_geopolitik.application.scene_docx_contract import SceneDocxPlan

_MAX_TIMELINE_SECONDS = 24 * 60 * 60


class SceneImportReviewError(ValueError):
    """User-safe input error without private media paths or source paragraphs."""


class SceneLayout(StrEnum):
    SINGLE = "SINGLE"
    DOUBLE = "DOUBLE"


class SceneRegion(StrEnum):
    FULL = "FULL"
    LEFT = "LEFT"
    RIGHT = "RIGHT"


@dataclass(frozen=True, slots=True)
class SceneVisualPlacement:
    asset_id: str
    path: Path
    region: SceneRegion
    track_id: str
    start_frame: int
    end_frame: int


@dataclass(frozen=True, slots=True)
class SceneTimelineEntry:
    scene_number: int
    layout: SceneLayout
    start_frame: int
    end_frame: int
    visuals: tuple[SceneVisualPlacement, ...]
    source_context: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class SceneTimelineReview:
    fps: int
    scenes: tuple[SceneTimelineEntry, ...]
    total_frames: int
    asset_count: int


def build_scene_timeline_review(
    docx: SceneDocxPlan,
    inventory: SceneAssetInventory,
    duration_frames: tuple[int, ...],
    *,
    fps: int,
) -> SceneTimelineReview:
    """Plan user-supplied scene timing, never inventing asset length or layout.

    DOUBLE means two *simultaneous* lanes in the same frame interval.
    SINGLE is one full-canvas lane. Final renderer geometry remains gated.
    """
    if type(fps) is not int or fps not in (30, 60):
        raise SceneImportReviewError("unsupported project FPS")
    if not docx.scenes or len(duration_frames) != len(docx.scenes):
        raise SceneImportReviewError("one explicit duration is required for every scene")
    if not inventory.all_ready:
        raise SceneImportReviewError("all scene assets must pass media preflight")

    ordered_assets = [asset.canonical_id for scene in docx.scenes for asset in scene.assets]
    indexed: dict[str, Path] = {}
    for item in inventory.bindings:
        if item.asset_id in indexed or item.path is None or len(item.candidates) != 1:
            raise SceneImportReviewError("invalid or ambiguous asset binding")
        indexed[item.asset_id] = item.path
    if (
        len(ordered_assets) != docx.asset_count
        or len(set(ordered_assets)) != len(ordered_assets)
        or set(indexed) != set(ordered_assets)
    ):
        raise SceneImportReviewError("scene and asset inventory are inconsistent")

    scenes: list[SceneTimelineEntry] = []
    current_frame = 0
    for index, (scene, frames) in enumerate(zip(docx.scenes, duration_frames, strict=True)):
        if type(frames) is not int or frames <= 0 or frames > _MAX_TIMELINE_SECONDS * fps:
            raise SceneImportReviewError("scene duration must be a positive frame count")
        if scene.number != index + 1 or scene.expected_visuals not in (1, 2):
            raise SceneImportReviewError("scene order or visual layout is invalid")
        if len(scene.assets) != scene.expected_visuals:
            raise SceneImportReviewError("scene visual count does not match its header")
        end_frame = current_frame + frames
        if end_frame > _MAX_TIMELINE_SECONDS * fps:
            raise SceneImportReviewError("timeline exceeds supported review duration")
        regions = (
            (SceneRegion.FULL,)
            if scene.expected_visuals == 1
            else (SceneRegion.LEFT, SceneRegion.RIGHT)
        )
        placements = tuple(
            SceneVisualPlacement(
                asset_id=asset.canonical_id,
                path=indexed[asset.canonical_id],
                region=region,
                track_id=f"V{lane + 1}",
                start_frame=current_frame,
                end_frame=end_frame,
            )
            for lane, (asset, region) in enumerate(zip(scene.assets, regions, strict=True))
        )
        scenes.append(
            SceneTimelineEntry(
                scene_number=scene.number,
                layout=SceneLayout.SINGLE if len(placements) == 1 else SceneLayout.DOUBLE,
                start_frame=current_frame,
                end_frame=end_frame,
                visuals=placements,
                source_context=scene.source_context,
            )
        )
        current_frame = end_frame
    return SceneTimelineReview(fps, tuple(scenes), current_frame, len(ordered_assets))
