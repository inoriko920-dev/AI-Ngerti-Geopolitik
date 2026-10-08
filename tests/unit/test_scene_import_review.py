"""Scene 1/2 deterministic timing and non-canonical review contracts."""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_ngerti_geopolitik.application.scene_asset_bindings import (
    SceneAssetCandidate,
    SceneAssetStatus,
    bind_scene_asset_candidates,
)
from ai_ngerti_geopolitik.application.scene_docx_contract import parse_scene_docx_lines
from ai_ngerti_geopolitik.application.scene_import_review import (
    SceneImportReviewError,
    SceneLayout,
    SceneRegion,
    build_scene_timeline_review,
)


def _docx():
    return parse_scene_docx_lines(
        (
            "Tampilan Scene 1: 1",
            "Asset 1: Map of Asia",
            "Source Quote: Retain all original context",
            "Scene 2: 2",
            "Asset 2: Portrait",
            "Asset 3: Flag",
        )
    )


def _ready(tmp_path: Path):
    return bind_scene_asset_candidates(
        _docx(),
        tuple(
            SceneAssetCandidate(f"A{i:03d}", tmp_path / f"A{i:03d}.png", True, True)
            for i in range(1, 4)
        ),
    )


def test_one_and_two_image_scenes_preserve_frames_parallel_lanes_and_quote(
    tmp_path: Path,
) -> None:
    source = _docx()
    inventory = _ready(tmp_path)
    review = build_scene_timeline_review(source, inventory, (150, 90), fps=30)
    assert review.fps == 30 and review.asset_count == 3
    assert review.total_frames == 240
    assert [x.layout for x in review.scenes] == [SceneLayout.SINGLE, SceneLayout.DOUBLE]
    first, second = review.scenes
    assert (first.start_frame, first.end_frame) == (0, 150)
    assert (second.start_frame, second.end_frame) == (150, 240)
    assert first.source_context == ("Source Quote: Retain all original context",)
    assert len(first.visuals) == 1 and first.visuals[0].region is SceneRegion.FULL
    assert first.visuals[0].asset_id == "A001"
    assert first.visuals[0].track_id == "V1"
    assert [x.region for x in second.visuals] == [SceneRegion.LEFT, SceneRegion.RIGHT]
    assert [x.track_id for x in second.visuals] == ["V1", "V2"]
    assert {x.start_frame for x in second.visuals} == {150}
    assert {x.end_frame for x in second.visuals} == {240}
    assert [x.asset_id for x in second.visuals] == ["A002", "A003"]
    assert build_scene_timeline_review(source, inventory, (150, 90), fps=30) == review


@pytest.mark.parametrize("durations", [(), (150,), (0, 120), (-1, 120), (True, 100), (30.0, 120)])
def test_invalid_or_missing_explicit_durations_fail_closed(
    tmp_path: Path, durations: tuple[int, ...]
) -> None:
    with pytest.raises(SceneImportReviewError):
        build_scene_timeline_review(_docx(), _ready(tmp_path), durations, fps=30)


@pytest.mark.parametrize("fps", [0, 29, 25, 120, True])
def test_invalid_fps_rejected(tmp_path: Path, fps: int) -> None:
    with pytest.raises(SceneImportReviewError, match="FPS"):
        build_scene_timeline_review(_docx(), _ready(tmp_path), (150, 150), fps=fps)


def test_60fps_review_uses_exact_source_frame_counts(tmp_path: Path) -> None:
    review = build_scene_timeline_review(_docx(), _ready(tmp_path), (300, 120), fps=60)
    assert review.total_frames == 420
    assert review.scenes[1].start_frame == 300


def test_missing_and_duplicate_cannot_be_reviewed_or_auto_selected(tmp_path: Path) -> None:
    source = _docx()
    inventory = bind_scene_asset_candidates(
        source,
        (
            SceneAssetCandidate("A001", tmp_path / "A001.png", True, True),
            SceneAssetCandidate("A001", tmp_path / "a001.jpg", True, True),
            SceneAssetCandidate("A002", tmp_path / "A002.png", True, True),
        ),
    )
    assert inventory.bindings[0].status is SceneAssetStatus.DUPLICATE
    assert inventory.bindings[2].status is SceneAssetStatus.MISSING
    with pytest.raises(SceneImportReviewError, match="preflight"):
        build_scene_timeline_review(source, inventory, (150, 150), fps=30)


def test_inventory_for_wrong_scene_fails_closed(tmp_path: Path) -> None:
    different = parse_scene_docx_lines(("Scene 1: 1", "Asset 1: Only first"))
    inventory = bind_scene_asset_candidates(
        different,
        (SceneAssetCandidate("A001", tmp_path / "A001.png", True, True),),
    )
    with pytest.raises(SceneImportReviewError, match="inconsistent"):
        build_scene_timeline_review(_docx(), inventory, (150, 90), fps=30)


def test_cumulative_duration_limit_fails_without_partial_review(tmp_path: Path) -> None:
    with pytest.raises(SceneImportReviewError, match="exceeds"):
        build_scene_timeline_review(_docx(), _ready(tmp_path), (30 * 86400, 1), fps=30)
