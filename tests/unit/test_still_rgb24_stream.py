"""Golden-pixel and tamper tests for bounded offline RGB24 frame streaming."""

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
from ai_ngerti_geopolitik.infrastructure.scene_asset_discovery import (
    scan_scene_asset_folder,
    verify_scene_image_media,
)
from ai_ngerti_geopolitik.infrastructure.still_frame_sequence import export_complete_still_sequence
from ai_ngerti_geopolitik.infrastructure.still_h264_plan import plan_silent_h264_mp4
from ai_ngerti_geopolitik.infrastructure.still_rgb24_stream import (
    RGB24StreamError,
    iter_rgb24_chunks,
)


def _plan(tmp_path: Path):
    scenes = parse_scene_docx_lines(
        ("Scene 1: 1", "Asset 1: Red", "Scene 2: 2", "Asset 2: Green", "Asset 3: Blue")
    )
    for number, fill in ((1, 0xFFFF0000), (2, 0xFF00FF00), (3, 0xFF0000FF)):
        image = QImage(8, 8, QImage.Format.Format_ARGB32)
        image.fill(fill)
        assert image.save(str(tmp_path / f"A{number:03d}.png"), "PNG")
    inventory = scan_scene_asset_folder(scenes, tmp_path)
    review = build_scene_timeline_review(scenes, inventory, (2, 3), fps=30)
    state = create_canonical_scene_image_project(
        review,
        verify_scene_image_media(inventory),
        project_id="P-RGB-STREAM",
        project_name="RGB scanlines",
    )
    state = replace(state, settings=replace(state.settings, width=14, height=8))
    folder = tmp_path / "sequence"
    export_complete_still_sequence(state, folder, batch_size=2)
    return plan_silent_h264_mp4(state, folder, tmp_path / "unused.mp4")


def test_golden_rgb24_frame_sequence_and_scanline_boundaries(tmp_path: Path) -> None:
    plan = _plan(tmp_path)
    assert len(plan.verified_frames.frame_sha256) == 5
    assert len(plan.verified_frames.frame_bytes) == 5
    chunks = list(iter_rgb24_chunks(plan, chunk_rows=2))
    assert len(chunks) == 5 * 4
    assert all(len(part) == 14 * 2 * 3 for part in chunks)
    raw = b"".join(chunks)
    frame_bytes = plan.rgb24_bytes_per_frame
    assert len(raw) == 5 * frame_bytes
    single = b"\xff\x00\x00" * (14 * 8)
    double_row = b"\x00\xff\x00" * 7 + b"\x00\x00\xff" * 7
    double = double_row * 8
    for index in range(5):
        expected = single if index < 2 else double
        assert raw[index * frame_bytes : (index + 1) * frame_bytes] == expected
    assert not (tmp_path / "unused.mp4").exists()
    assert b"".join(iter_rgb24_chunks(plan, chunk_rows=1)) == raw


@pytest.mark.parametrize("row_count", (0, -1, True, 65, "2"))
def test_invalid_row_count_fails_closed(tmp_path: Path, row_count: object) -> None:
    plan = _plan(tmp_path)
    with pytest.raises(RGB24StreamError):
        list(iter_rgb24_chunks(plan, chunk_rows=row_count))


def test_changed_first_png_blocks_before_first_byte(tmp_path: Path) -> None:
    plan = _plan(tmp_path)
    first = plan.verified_frames.frame_files[0]
    changed = QImage(14, 8, QImage.Format.Format_ARGB32)
    changed.fill(0xFFFFFF00)
    assert changed.save(str(first), "PNG")
    blocks: list[bytes] = []
    with pytest.raises(RGB24StreamError):
        for chunk in iter_rgb24_chunks(plan):
            blocks.append(chunk)
    assert not blocks


def test_later_png_mutation_and_missing_file_block(tmp_path: Path) -> None:
    plan = _plan(tmp_path)
    plan.verified_frames.frame_files[-1].write_bytes(b"invalid png")
    with pytest.raises(RGB24StreamError):
        list(iter_rgb24_chunks(plan))
    assert not (tmp_path / "unused.mp4").exists()


def test_reordered_frames_and_missing_file_block(tmp_path: Path) -> None:
    plan = _plan(tmp_path)
    swapped = replace(
        plan.verified_frames,
        frame_files=tuple(reversed(plan.verified_frames.frame_files)),
    )
    with pytest.raises(RGB24StreamError):
        list(iter_rgb24_chunks(replace(plan, verified_frames=swapped)))
    plan.verified_frames.frame_files[1].unlink()
    with pytest.raises(RGB24StreamError):
        list(iter_rgb24_chunks(plan))
