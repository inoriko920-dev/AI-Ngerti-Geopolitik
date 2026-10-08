"""Fail-closed integrity handoff between verified PNG batches and future encoder."""

from __future__ import annotations

import json
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
from ai_ngerti_geopolitik.infrastructure.still_frame_sequence import (
    export_complete_still_sequence,
)
from ai_ngerti_geopolitik.infrastructure.still_sequence_verification import (
    StillSequenceVerificationError,
    verify_complete_still_sequence,
)


def _fixture(tmp_path: Path) -> tuple[ProjectState, Path, Path]:
    plan = parse_scene_docx_lines(
        ("Scene 1: 1", "Asset 1: Red", "Scene 2: 2", "Asset 2: Green", "Asset 3: Blue")
    )
    for number, color in ((1, 0xFFFF0000), (2, 0xFF00FF00), (3, 0xFF0000FF)):
        img = QImage(8, 8, QImage.Format.Format_ARGB32)
        img.fill(color)
        assert img.save(str(tmp_path / f"A{number:03d}.png"), "PNG")
    inventory = scan_scene_asset_folder(plan, tmp_path)
    review = build_scene_timeline_review(plan, inventory, (2, 3), fps=30)
    state = create_canonical_scene_image_project(
        review,
        verify_scene_image_media(inventory),
        project_id="P-MP4-GATE",
        project_name="Integrity handoff",
    )
    state = replace(state, settings=replace(state.settings, width=13, height=8))
    project = tmp_path / "film.angproj"
    JsonProjectRepository().save(state, project)
    state = JsonProjectRepository().load(project)
    folder = tmp_path / "rendered"
    export_complete_still_sequence(state, folder, batch_size=2)
    return state, project, folder


def _reject(state: ProjectState, folder: Path) -> None:
    with pytest.raises(StillSequenceVerificationError, match="integrity verification"):
        verify_complete_still_sequence(state, folder)


def test_verified_frames_order_and_user_cli(tmp_path: Path, capsys) -> None:
    state, project, folder = _fixture(tmp_path)
    result = verify_complete_still_sequence(state, folder)
    assert result.frame_count == 5
    assert result.fps == 30
    assert (result.width, result.height) == (13, 8)
    assert [p.name for p in result.frame_files] == [f"frame_{i:06d}.png" for i in range(5)]
    assert result.png_bytes > 0
    assert verify_cli(["--project", str(project), "--frames", str(folder)]) == 0
    assert "BELUM MP4" in capsys.readouterr().out


def test_reject_frame_pixel_mutation_even_with_valid_png(tmp_path: Path) -> None:
    state, _, folder = _fixture(tmp_path)
    target = folder / "batch_000000_000002" / "frame_000000.png"
    edited = QImage(13, 8, QImage.Format.Format_ARGB32)
    edited.fill(0xFFFFFFFF)
    assert edited.save(str(target), "PNG")
    _reject(state, folder)


def test_reject_master_batch_gap_without_touching_source(tmp_path: Path) -> None:
    state, project, folder = _fixture(tmp_path)
    previous = project.read_bytes()
    master_path = folder / "manifest.json"
    master = json.loads(master_path.read_text(encoding="utf-8"))
    master["batches"][1]["start_frame"] = 500
    master_path.write_text(json.dumps(master), encoding="utf-8")
    _reject(state, folder)
    assert project.read_bytes() == previous


def test_reject_unknown_files_and_linked_batch(tmp_path: Path) -> None:
    state, _, folder = _fixture(tmp_path)
    extraneous = folder / "batch_000000_000002" / "unexpected.txt"
    extraneous.write_text("unexpected", encoding="utf-8")
    _reject(state, folder)


def test_reject_changed_original_image_after_frame_export(tmp_path: Path) -> None:
    state, _, folder = _fixture(tmp_path)
    image = QImage(8, 8, QImage.Format.Format_ARGB32)
    image.fill(0xFFFFFF00)
    assert image.save(str(tmp_path / "A001.png"), "PNG")
    _reject(state, folder)


def test_reject_corrupted_manifest_and_strict_boolean(tmp_path: Path) -> None:
    state, _, folder = _fixture(tmp_path)
    master_path = folder / "manifest.json"
    master = json.loads(master_path.read_text(encoding="utf-8"))
    master["frame_count"] = True
    master_path.write_text(json.dumps(master), encoding="utf-8")
    _reject(state, folder)


def test_reject_missing_batch_frame_and_cli_fail_closed(tmp_path: Path, capsys) -> None:
    state, project, folder = _fixture(tmp_path)
    (folder / "batch_000002_000004" / "frame_000003.png").unlink()
    _reject(state, folder)
    assert verify_cli(["--project", str(project), "--frames", str(folder)]) == 1
    assert "GAGAL" in capsys.readouterr().err
