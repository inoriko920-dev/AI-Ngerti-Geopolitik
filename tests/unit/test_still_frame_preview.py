"""Actual Qt image frame compositing from saved canonical .angproj; no native engine."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest
from PySide6.QtGui import QImage

from ai_ngerti_geopolitik.application.scene_docx_contract import parse_scene_docx_lines
from ai_ngerti_geopolitik.application.scene_import_review import (
    build_scene_timeline_review,
    create_canonical_scene_image_project,
)
from ai_ngerti_geopolitik.bootstrap.scene_cli import main as import_cli_main
from ai_ngerti_geopolitik.domain import FrameTime
from ai_ngerti_geopolitik.domain.properties import (
    ClipProperties,
    VideoProperties,
)
from ai_ngerti_geopolitik.infrastructure.mlt_projection import (
    MltProjectionError,
    build_mlt_timeline_plan,
)
from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository
from ai_ngerti_geopolitik.infrastructure.scene_asset_discovery import (
    scan_scene_asset_folder,
    verify_scene_image_media,
)
from ai_ngerti_geopolitik.infrastructure.still_frame_preview import (
    StillFramePreviewError,
    render_still_frame,
)


def _save_real_project(tmp_path: Path):
    docx = parse_scene_docx_lines(
        (
            "Scene 1: 1",
            "Asset 1: Red image",
            "Scene 2: 2",
            "Asset 2: Green image",
            "Asset 3: Blue image",
        )
    )
    for number, rgb in ((1, 0xFFFF0000), (2, 0xFF00FF00), (3, 0xFF0000FF)):
        image = QImage(8, 8, QImage.Format.Format_ARGB32)
        image.fill(rgb)
        assert image.save(str(tmp_path / f"A{number:03d}.png"), "PNG")
    inventory = scan_scene_asset_folder(docx, tmp_path)
    review = build_scene_timeline_review(docx, inventory, (150, 90), fps=30)
    state = create_canonical_scene_image_project(
        review,
        verify_scene_image_media(inventory),
        project_id="P-PREVIEW",
        project_name="Preview",
    )
    state = replace(state, settings=replace(state.settings, width=13, height=8))
    path = tmp_path / "preview.angproj"
    repo = JsonProjectRepository()
    repo.save(state, path)
    return repo.load(path)


@pytest.mark.parametrize("frame", [0, 1, 149])
def test_single_is_real_red_full_canvas_at_every_hold_frame(tmp_path: Path, frame: int) -> None:
    state = _save_real_project(tmp_path)
    image = render_still_frame(state, frame)
    assert (image.width(), image.height()) == (13, 8)
    for x in range(13):
        for y in (0, 4, 7):
            assert image.pixelColor(x, y).name() == "#ff0000"


@pytest.mark.parametrize("frame", [150, 151, 239])
def test_double_is_real_green_left_blue_right_parallel(tmp_path: Path, frame: int) -> None:
    image = render_still_frame(_save_real_project(tmp_path), frame)
    assert image.pixelColor(0, 2).name() == "#00ff00"
    assert image.pixelColor(5, 2).name() == "#00ff00"
    assert image.pixelColor(6, 2).name() == "#0000ff"
    assert image.pixelColor(12, 7).name() == "#0000ff"


def test_deleted_or_changed_file_blocks_preview_with_no_user_path(
    tmp_path: Path,
) -> None:
    state = _save_real_project(tmp_path)
    (tmp_path / "A002.png").write_bytes(b"private broken input")
    with pytest.raises(StillFramePreviewError) as error:
        render_still_frame(state, 150)
    assert str(tmp_path) not in str(error.value)


def test_unapproved_transform_never_silently_ignored(tmp_path: Path) -> None:
    state = _save_real_project(tmp_path)
    current = state.tracks[0].clips[0]
    changed = replace(
        current,
        properties=ClipProperties(video=VideoProperties(position_x=12)),
    )
    modified = replace(
        state,
        tracks=(
            replace(state.tracks[0], clips=(changed, *state.tracks[0].clips[1:])),
            state.tracks[1],
        ),
    )
    with pytest.raises(StillFramePreviewError, match="effects"):
        render_still_frame(modified, 0)


def test_missing_lane_and_out_of_range_do_not_render_wrong_pixels(tmp_path: Path) -> None:
    state = _save_real_project(tmp_path)
    for frame in (-1, 240, True):
        with pytest.raises(StillFramePreviewError, match="outside"):
            render_still_frame(state, frame)
    empty = replace(state, tracks=(state.tracks[1],))
    with pytest.raises(StillFramePreviewError, match="gap"):
        render_still_frame(empty, 0)


def test_mlt_native_preview_remains_blocked_separately(tmp_path: Path) -> None:
    state = _save_real_project(tmp_path)
    with pytest.raises(MltProjectionError, match="requires video assets"):
        build_mlt_timeline_plan(state)


def test_image_intrinsic_frame_stays_one_across_hold(tmp_path: Path) -> None:
    state = _save_real_project(tmp_path)
    assert state.clip("SCENE-0001-A001").source_frame_at_timeline_offset(149) == 0
    assert state.asset("A001").duration == FrameTime(1, 30)


def test_cli_outputs_real_preview_png_and_refuses_overwrite(tmp_path: Path) -> None:
    state = _save_real_project(tmp_path)
    project = tmp_path / "preview.angproj"
    output = tmp_path / "frame_150.png"
    assert state.timeline_end_frame == 240
    args = ["preview", "--project", str(project), "--frame", "150", "--output", str(output)]
    assert import_cli_main(args) == 0
    saved = QImage(str(output))
    assert not saved.isNull()
    assert (saved.width(), saved.height()) == (13, 8)
    assert saved.pixelColor(0, 1).name() == "#00ff00"
    assert saved.pixelColor(12, 1).name() == "#0000ff"
    assert import_cli_main(args) == 1
    invalid_args = [
        "preview",
        "--project",
        str(project),
        "--frame",
        "240",
        "--output",
        str(tmp_path / "outside.png"),
    ]
    assert import_cli_main(invalid_args) == 1
    assert not (tmp_path / "outside.png").exists()
