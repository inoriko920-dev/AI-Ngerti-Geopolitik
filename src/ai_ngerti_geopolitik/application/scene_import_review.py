"""Deterministic Scene DOCX -> timeline review; no unsupported image Clip state.

A duration must be explicitly provided for each scene. The resulting lanes
and half-open frame ranges are *preview/review metadata*, not a renderer
qualification or a second owner of canonical ProjectState.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from ai_ngerti_geopolitik.application.commands import (
    AddClipCommand,
    AddMarkerCommand,
    Command,
    CommandBatch,
    CommandBus,
    ImportAssetCommand,
)
from ai_ngerti_geopolitik.application.scene_asset_bindings import (
    SceneAssetInventory,
    VerifiedSceneImageSet,
)
from ai_ngerti_geopolitik.application.scene_docx_contract import SceneDocxPlan
from ai_ngerti_geopolitik.domain import Asset, Clip, FrameTime, Marker, ProjectState

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



def create_canonical_scene_image_project(
    review: SceneTimelineReview,
    verified: VerifiedSceneImageSet,
    *,
    project_id: str,
    project_name: str,
) -> ProjectState:
    """Make one genuine ProjectState using one semantic CommandBatch.

    The caller must re-scan and re-verify original files immediately before
    persistence. This produces canonical project data, NOT qualified rendering.
    """
    if review.fps not in (30, 60) or not review.scenes or review.total_frames <= 0:
        raise SceneImportReviewError("scene review is invalid")
    if len(verified.images) != review.asset_count:
        raise SceneImportReviewError("verified asset count does not match review")
    by_id = {item.asset_id: item for item in verified.images}
    if len(by_id) != len(verified.images):
        raise SceneImportReviewError("verified image IDs are duplicated")

    commands: list[Command] = []
    for item in verified.images:
        if (
            item.width <= 0
            or item.height <= 0
            or item.file_size <= 0
            or len(item.fingerprint_sha256) != 64
        ):
            raise SceneImportReviewError("verified image metadata is invalid")
        commands.append(
            ImportAssetCommand(
                Asset(
                    asset_id=item.asset_id,
                    path_ref=str(item.path),
                    media_type="image",
                    duration=FrameTime(1, review.fps),
                    width=item.width,
                    height=item.height,
                    has_audio=False,
                    fingerprint_sha256=item.fingerprint_sha256,
                    source_name=item.path.name,
                    file_size=item.file_size,
                )
            )
        )
    cursor = 0
    seen: set[str] = set()
    for index, scene in enumerate(review.scenes, 1):
        if (
            scene.scene_number != index
            or scene.start_frame != cursor
            or scene.end_frame <= scene.start_frame
            or scene.end_frame > review.total_frames
        ):
            raise SceneImportReviewError("scene order or timing is invalid")
        regions = (
            ((SceneRegion.FULL, "V1"),)
            if scene.layout is SceneLayout.SINGLE
            else ((SceneRegion.LEFT, "V1"), (SceneRegion.RIGHT, "V2"))
        )
        if len(scene.visuals) != len(regions):
            raise SceneImportReviewError("scene visual count is inconsistent")
        for visual, (region, track_id) in zip(scene.visuals, regions, strict=True):
            media = by_id.get(visual.asset_id)
            if (
                media is None
                or visual.asset_id in seen
                or visual.path != media.path
                or visual.region is not region
                or visual.track_id != track_id
                or visual.start_frame != scene.start_frame
                or visual.end_frame != scene.end_frame
            ):
                raise SceneImportReviewError("scene image placement is inconsistent")
            seen.add(visual.asset_id)
            commands.append(
                AddClipCommand(
                    Clip(
                        clip_id=f"SCENE-{index:04d}-{visual.asset_id}",
                        asset_id=visual.asset_id,
                        timeline_start=FrameTime(scene.start_frame, review.fps),
                        source_in=FrameTime(0, review.fps),
                        source_out=FrameTime(1, review.fps),
                        image_hold_frames=scene.end_frame - scene.start_frame,
                    ),
                    track_id=track_id,
                )
            )
        commands.append(
            AddMarkerCommand(
                Marker(
                    marker_id=f"SCENE-{index:04d}",
                    frame=FrameTime(scene.start_frame, review.fps),
                    label="\n".join(
                        (f"Scene {index} [{scene.layout.value}]", *scene.source_context)
                    ),
                    marker_type="note",
                )
            )
        )
        cursor = scene.end_frame

    if cursor != review.total_frames or seen != set(by_id):
        raise SceneImportReviewError("review and verified images differ")
    try:
        bus = CommandBus(ProjectState.create(project_id, project_name, review.fps))
        return bus.execute(
            CommandBatch(
                batch_id="SCENE-DOCX-IMPORT-0001",
                label="Create Scene DOCX image timeline",
                actor="manual",
                expected_revision=0,
                commands=tuple(commands),
            )
        )
    except (ValueError, RuntimeError):
        raise SceneImportReviewError("canonical scene project creation failed") from None
