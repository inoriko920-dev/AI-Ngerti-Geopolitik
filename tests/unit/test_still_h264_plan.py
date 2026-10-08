"""No-FFmpeg silent H.264 planning from verified canonical image-only projects."""

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
from ai_ngerti_geopolitik.bootstrap.still_verify_cli import main as verify_cli
from ai_ngerti_geopolitik.domain import ProjectState
from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository
from ai_ngerti_geopolitik.infrastructure.scene_asset_discovery import (
    scan_scene_asset_folder,
    verify_scene_image_media,
)
from ai_ngerti_geopolitik.infrastructure.still_frame_sequence import export_complete_still_sequence
from ai_ngerti_geopolitik.infrastructure.still_h264_plan import (
    SilentH264PlanError,
    plan_silent_h264_mp4,
)


def _fixture(tmp_path: Path, *, width: int = 14) -> tuple[ProjectState, Path, Path]:
    docx = parse_scene_docx_lines(
        ("Scene 1: 1", "Asset 1: Red", "Scene 2: 2", "Asset 2: Green", "Asset 3: Blue")
    )
    for number, color in ((1, 0xFFFF0000), (2, 0xFF00FF00), (3, 0xFF0000FF)):
        png = QImage(8, 8, QImage.Format.Format_ARGB32)
        png.fill(color)
        assert png.save(str(tmp_path / f"A{number:03d}.png"), "PNG")
    inventory = scan_scene_asset_folder(docx, tmp_path)
    review = build_scene_timeline_review(docx, inventory, (2, 3), fps=30)
    state = create_canonical_scene_image_project(
        review,
        verify_scene_image_media(inventory),
        project_id="P-PLAN-H264",
        project_name="Silent pre-encode plan",
    )
    state = replace(state, settings=replace(state.settings, width=width, height=8))
    project = tmp_path / "silent.angproj"
    JsonProjectRepository().save(state, project)
    state = JsonProjectRepository().load(project)
    root = tmp_path / "sequence"
    export_complete_still_sequence(state, root, batch_size=2)
    return state, project, root


def test_exact_h264_plan_without_file_write_or_process(tmp_path: Path, capsys) -> None:
    state, project, root = _fixture(tmp_path)
    output = tmp_path / "final.mp4"
    before = project.read_bytes()
    plan = plan_silent_h264_mp4(state, root, output)
    assert plan.destination == output
    assert plan.duration_numerator == 5
    assert plan.duration_denominator == 30
    assert plan.rgb24_bytes_per_frame == 14 * 8 * 3
    assert len(plan.verified_frames.frame_files) == 5
    assert tuple(p.name for p in plan.verified_frames.frame_files) == tuple(
        f"frame_{index:06d}.png" for index in range(5)
    )
    args = plan.ffmpeg_argument_suffix
    assert args[-1] == str(output)
    assert args[args.index("-pixel_format") + 1] == "rgb24"
    assert args[args.index("-video_size") + 1] == "14x8"
    assert args[args.index("-framerate") + 1] == "30"
    assert args[args.index("-frames:v") + 1] == "5"
    assert args[args.index("-c:v") + 1] == "libx264"
    assert "-an" in args
    assert "-n" in args
    assert not output.exists()
    assert project.read_bytes() == before
    assert verify_cli(
        ["--project", str(project), "--frames", str(root), "--plan-mp4", str(output)]
    ) == 0
    stdout = capsys.readouterr().out
    assert "DRY RUN" in stdout
    assert "belum dijalankan" in stdout
    assert not output.exists()


@pytest.mark.parametrize("output", ("sequence/hack.mp4", "final.mov", "final.mp4"))
def test_existing_or_invalid_output_is_rejected(tmp_path: Path, output: str) -> None:
    state, _, root = _fixture(tmp_path)
    target = tmp_path / output
    if output == "final.mp4":
        target.write_text("keep existing", encoding="utf-8")
    with pytest.raises(SilentH264PlanError):
        plan_silent_h264_mp4(state, root, target)
    if output == "final.mp4":
        assert target.read_text(encoding="utf-8") == "keep existing"


def test_odd_size_blocks_yuv420p_without_truncation(tmp_path: Path) -> None:
    state, _, root = _fixture(tmp_path, width=13)
    with pytest.raises(SilentH264PlanError):
        plan_silent_h264_mp4(state, root, tmp_path / "output.mp4")


def test_changed_source_after_export_cannot_be_planned(tmp_path: Path) -> None:
    state, _, root = _fixture(tmp_path)
    tampered = QImage(8, 8, QImage.Format.Format_ARGB32)
    tampered.fill(0xFFFFFFFF)
    assert tampered.save(str(tmp_path / "A002.png"), "PNG")
    with pytest.raises(SilentH264PlanError):
        plan_silent_h264_mp4(state, root, tmp_path / "output.mp4")


def test_deleted_frame_blocks_plan_and_cli(tmp_path: Path, capsys) -> None:
    state, project, root = _fixture(tmp_path)
    (root / "batch_000002_000004" / "frame_000003.png").unlink()
    with pytest.raises(SilentH264PlanError):
        plan_silent_h264_mp4(state, root, tmp_path / "output.mp4")
    assert verify_cli(
        ["--project", str(project), "--frames", str(root), "--plan-mp4",
         str(tmp_path / "output.mp4")]
    ) == 1
    assert "GAGAL" in capsys.readouterr().err


def test_relative_destination_and_linked_input_is_not_qualified(tmp_path: Path) -> None:
    state, _, root = _fixture(tmp_path)
    with pytest.raises(SilentH264PlanError):
        plan_silent_h264_mp4(state, root, Path("relative.mp4"))
    with pytest.raises(SilentH264PlanError):
        plan_silent_h264_mp4(state, root, tmp_path / "CON.mp4")
