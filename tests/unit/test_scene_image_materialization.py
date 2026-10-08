"""Scene DOCX -> real canonical image .angproj serialization regression."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest
from PySide6.QtGui import QImage

from ai_ngerti_geopolitik.application.scene_docx_contract import parse_scene_docx_lines
from ai_ngerti_geopolitik.application.scene_import_review import (
    SceneImportReviewError,
    build_scene_timeline_review,
    create_canonical_scene_image_project,
)
from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository
from ai_ngerti_geopolitik.infrastructure.scene_asset_discovery import (
    scan_scene_asset_folder,
    verify_scene_image_media,
)


def _ready(tmp_path: Path):
    docx = parse_scene_docx_lines(
        (
            "Scene 1: 1",
            "Asset 1: Historical map",
            "Source Quote: Preserve original source context",
            "Scene 2: 2",
            "Asset 2: Portrait",
            "Asset 3: Flag",
        )
    )
    for i in (1, 2, 3):
        image = QImage(4, 4, QImage.Format.Format_RGB32)
        image.fill(0x00228844)
        assert image.save(str(tmp_path / f"A{i:03d}.png"), "PNG")
    inventory = scan_scene_asset_folder(docx, tmp_path)
    review = build_scene_timeline_review(docx, inventory, (150, 90), fps=30)
    verified = verify_scene_image_media(inventory)
    return review, verified


def test_canonical_scene_images_are_saved_and_opened_without_video_spoofing(
    tmp_path: Path,
) -> None:
    review, verified = _ready(tmp_path)
    state = create_canonical_scene_image_project(
        review, verified, project_id="P-SCENE", project_name="Documentary"
    )
    assert state.revision == 1
    assert state.timeline_end_frame == 240
    assert [x.media_type for x in state.assets] == ["image"] * 3
    assert [x.track_id for x in state.tracks] == ["V1", "V2"]
    assert [x.image_hold_frames for x in state.tracks[0].clips] == [150, 90]
    assert [x.image_hold_frames for x in state.tracks[1].clips] == [90]
    assert state.tracks[1].clips[0].timeline_start.frames == 150
    assert [m.marker_id for m in state.markers] == ["SCENE-0001", "SCENE-0002"]
    assert state.markers[0].label.endswith("Source Quote: Preserve original source context")
    for asset in state.assets:
        assert asset.fingerprint_sha256 in {x.fingerprint_sha256 for x in verified.images}
    path = tmp_path / "created.angproj"
    repo = JsonProjectRepository()
    repo.save(state, path)
    loaded = repo.load(path)
    assert loaded.semantic_hash() == state.semantic_hash()
    assert loaded.timeline_end_frame == 240
    assert loaded.markers == state.markers


def test_materializer_rejects_forged_or_missing_verified_image(tmp_path: Path) -> None:
    review, verified = _ready(tmp_path)
    forged = replace(verified.images[0], path=tmp_path / "forged.png")
    modified = replace(verified, images=(forged, *verified.images[1:]))
    with pytest.raises(SceneImportReviewError, match="inconsistent"):
        create_canonical_scene_image_project(
            review, modified, project_id="P1", project_name="Wrong"
        )
    incomplete = replace(verified, images=verified.images[:-1])
    with pytest.raises(SceneImportReviewError, match="count"):
        create_canonical_scene_image_project(
            review, incomplete, project_id="P1", project_name="Missing"
        )


def test_materializer_rejects_gapped_scene_timing(tmp_path: Path) -> None:
    review, verified = _ready(tmp_path)
    gapped = replace(review.scenes[1], start_frame=151)
    broken = replace(review, scenes=(review.scenes[0], gapped))
    with pytest.raises(SceneImportReviewError, match="timing"):
        create_canonical_scene_image_project(broken, verified, project_id="P1", project_name="Gap")
