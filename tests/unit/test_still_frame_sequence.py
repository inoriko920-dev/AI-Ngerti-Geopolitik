"""Real Qt still-frame sequence golden-pixel and atomic failure regressions."""

from __future__ import annotations

import hashlib
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
from ai_ngerti_geopolitik.bootstrap.scene_cli import main as scene_cli
from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository
from ai_ngerti_geopolitik.infrastructure.scene_asset_discovery import (
    scan_scene_asset_folder,
    verify_scene_image_media,
)
from ai_ngerti_geopolitik.infrastructure.still_frame_sequence import (
    StillSequenceExportError,
    export_still_frame_sequence,
)


def _project(tmp_path: Path):
    docx = parse_scene_docx_lines(
        (
            "Scene 1: 1",
            "Asset 1: Red",
            "Scene 2: 2",
            "Asset 2: Green",
            "Asset 3: Blue",
        )
    )
    for number, color in ((1, 0xFFFF0000), (2, 0xFF00FF00), (3, 0xFF0000FF)):
        image = QImage(8, 8, QImage.Format.Format_ARGB32)
        image.fill(color)
        assert image.save(str(tmp_path / f"A{number:03d}.png"), "PNG")
    inventory = scan_scene_asset_folder(docx, tmp_path)
    review = build_scene_timeline_review(docx, inventory, (150, 90), fps=30)
    state = create_canonical_scene_image_project(
        review,
        verify_scene_image_media(inventory),
        project_id="P-SEQ",
        project_name="Sequence",
    )
    state = replace(state, settings=replace(state.settings, width=13, height=8))
    path = tmp_path / "source.angproj"
    repo = JsonProjectRepository()
    repo.save(state, path)
    return repo.load(path), path


def test_sequence_has_exact_scene_boundary_pixels_and_verified_manifest(tmp_path: Path) -> None:
    state, path = _project(tmp_path)
    target = tmp_path / "frames"
    args = [
        "frames", "--project", str(path), "--start", "148",
        "--count", "5", "--output", str(target),
    ]
    assert scene_cli(args) == 0
    assert target.is_dir()
    manifest = json.loads((target / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["format"] == "ang-still-sequence-v1"
    assert manifest["project_id"] == state.project_id
    assert manifest["project_semantic_sha256"] == state.semantic_hash()
    assert manifest["fps"] == 30
    assert (manifest["start_frame"], manifest["end_frame_exclusive"]) == (148, 153)
    assert manifest["frame_count"] == 5
    assert len(manifest["frames"]) == 5
    for frame in range(148, 153):
        entry = manifest["frames"][frame - 148]
        png = target / f"frame_{frame:06d}.png"
        assert entry["frame"] == frame
        assert entry["png"] == png.name
        assert png.is_file()
        assert entry["sha256"] == hashlib.sha256(png.read_bytes()).hexdigest()
        assert entry["bytes"] == png.stat().st_size
        actual = QImage(str(png))
        assert not actual.isNull()
        assert (actual.width(), actual.height()) == (13, 8)
        if frame < 150:
            assert actual.pixelColor(0, 1).name() == "#ff0000"
            assert actual.pixelColor(12, 1).name() == "#ff0000"
        else:
            assert actual.pixelColor(0, 1).name() == "#00ff00"
            assert actual.pixelColor(12, 1).name() == "#0000ff"
    assert scene_cli(args) == 1
    assert len(list(target.iterdir())) == 6


def test_out_of_range_and_too_many_frames_fail_without_side_effects(tmp_path: Path) -> None:
    state, _ = _project(tmp_path)
    for start, count in ((-1, 1), (0, 0), (0, 301), (239, 2), (True, 2)):
        output = tmp_path / "invalid-frames"
        with pytest.raises(StillSequenceExportError, match="range"):
            export_still_frame_sequence(state, output, start_frame=start, count=count)
        assert not output.exists()


def test_failed_decode_discards_staging_and_does_not_publish(tmp_path: Path) -> None:
    state, _ = _project(tmp_path)
    (tmp_path / "A002.png").write_bytes(b"changed since import")
    output = tmp_path / "incomplete"
    with pytest.raises(StillSequenceExportError, match="safely exported"):
        export_still_frame_sequence(state, output, start_frame=149, count=2)
    assert not output.exists()
    assert not list(tmp_path.glob(".angseq-*"))


def test_existing_output_is_preserved_including_existing_manifest(tmp_path: Path) -> None:
    state, _ = _project(tmp_path)
    target = tmp_path / "frames"
    target.mkdir()
    (target / "manifest.json").write_text("KEEP ME", encoding="utf-8")
    with pytest.raises(StillSequenceExportError, match="already exists"):
        export_still_frame_sequence(state, target, start_frame=150, count=1)
    assert (target / "manifest.json").read_text(encoding="utf-8") == "KEEP ME"


def test_manifest_and_golden_frame_deterministic_across_repeated_export(tmp_path: Path) -> None:
    state, _ = _project(tmp_path)
    first = export_still_frame_sequence(state, tmp_path / "first", start_frame=150, count=2)
    second = export_still_frame_sequence(state, tmp_path / "second", start_frame=150, count=2)
    assert (first / "manifest.json").read_bytes() == (second / "manifest.json").read_bytes()
    assert (first / "frame_000150.png").read_bytes() == (
        second / "frame_000150.png"
    ).read_bytes()
