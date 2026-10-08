"""Full still-image timeline export: real golden pixels, manifests and rollback."""

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
from ai_ngerti_geopolitik.infrastructure import still_frame_sequence as sequence
from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository
from ai_ngerti_geopolitik.infrastructure.scene_asset_discovery import (
    scan_scene_asset_folder,
    verify_scene_image_media,
)
from ai_ngerti_geopolitik.infrastructure.still_frame_sequence import (
    StillSequenceExportError,
    export_complete_still_sequence,
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
    for number, rgba in ((1, 0xFFFF0000), (2, 0xFF00FF00), (3, 0xFF0000FF)):
        image = QImage(8, 8, QImage.Format.Format_ARGB32)
        image.fill(rgba)
        assert image.save(str(tmp_path / f"A{number:03d}.png"), "PNG")
    inventory = scan_scene_asset_folder(docx, tmp_path)
    review = build_scene_timeline_review(docx, inventory, (150, 90), fps=30)
    state = create_canonical_scene_image_project(
        review,
        verify_scene_image_media(inventory),
        project_id="P-FULL-SEQUENCE",
        project_name="Frame parity",
    )
    state = replace(state, settings=replace(state.settings, width=13, height=8))
    project = tmp_path / "scene.angproj"
    JsonProjectRepository().save(state, project)
    return JsonProjectRepository().load(project), project


def test_complete_export_has_two_batches_and_no_missing_frames(tmp_path: Path) -> None:
    state, project = _project(tmp_path)
    root = tmp_path / "frames"
    assert scene_cli(
        [
            "frames-all",
            "--project",
            str(project),
            "--output",
            str(root),
            "--batch-size",
            "120",
        ]
    ) == 0
    master_data = (root / "manifest.json").read_bytes()
    master = json.loads(master_data)
    assert master["format"] == "ang-still-project-v1"
    assert master["frame_count"] == 240
    assert master["batch_count"] == 2
    assert master["project_semantic_sha256"] == state.semantic_hash()
    assert [(b["start_frame"], b["end_frame_exclusive"]) for b in master["batches"]] == [
        (0, 120),
        (120, 240),
    ]
    recovered_frames: list[int] = []
    total_bytes = 0
    for batch in master["batches"]:
        folder = root / batch["directory"]
        manifest_bytes = (folder / "manifest.json").read_bytes()
        assert hashlib.sha256(manifest_bytes).hexdigest() == batch["manifest_sha256"]
        manifest = json.loads(manifest_bytes)
        assert len(manifest["frames"]) == batch["frame_count"]
        for entry in manifest["frames"]:
            png = folder / entry["png"]
            assert entry["sha256"] == hashlib.sha256(png.read_bytes()).hexdigest()
            recovered_frames.append(entry["frame"])
            total_bytes += entry["bytes"]
    assert recovered_frames == list(range(240))
    assert total_bytes == master["png_bytes"]
    for frame, expected_left, expected_right in (
        (0, "#ff0000", "#ff0000"),
        (149, "#ff0000", "#ff0000"),
        (150, "#00ff00", "#0000ff"),
        (239, "#00ff00", "#0000ff"),
    ):
        batch = master["batches"][frame // 120]
        png = root / batch["directory"] / f"frame_{frame:06d}.png"
        image = QImage(str(png))
        assert image.pixelColor(0, 1).name() == expected_left
        assert image.pixelColor(12, 1).name() == expected_right
    assert scene_cli(
        ["frames-all", "--project", str(project), "--output", str(root)]
    ) == 1


def test_second_batch_failure_removes_whole_staged_directory(
    tmp_path: Path, monkeypatch
) -> None:
    state, _ = _project(tmp_path)
    original = sequence.export_still_frame_sequence
    called = 0

    def fail_second(*args, **kwargs):
        nonlocal called
        called += 1
        if called == 2:
            raise StillSequenceExportError("simulated frame decode error")
        return original(*args, **kwargs)

    monkeypatch.setattr(sequence, "export_still_frame_sequence", fail_second)
    target = tmp_path / "unpublished"
    with pytest.raises(StillSequenceExportError):
        export_complete_still_sequence(state, target, batch_size=2)
    assert called == 2
    assert not target.exists()
    assert not list(tmp_path.glob(".angfull-*"))


def test_final_media_recheck_rejects_image_changed_after_last_batch(
    tmp_path: Path, monkeypatch
) -> None:
    state, _ = _project(tmp_path)
    original = sequence.export_still_frame_sequence

    def modify_after_batch(*args, **kwargs):
        result = original(*args, **kwargs)
        if kwargs["start_frame"] == 120:
            altered = QImage(8, 8, QImage.Format.Format_ARGB32)
            altered.fill(0xFFFF00FF)
            assert altered.save(str(tmp_path / "A001.png"), "PNG")
        return result

    monkeypatch.setattr(sequence, "export_still_frame_sequence", modify_after_batch)
    target = tmp_path / "invalidated"
    with pytest.raises(StillSequenceExportError, match="safely exported"):
        export_complete_still_sequence(state, target, batch_size=120)
    assert not target.exists()
    assert not list(tmp_path.glob(".angfull-*"))


def test_existing_output_and_bounded_project_are_not_overwritten(tmp_path: Path) -> None:
    state, _ = _project(tmp_path)
    root = tmp_path / "keep"
    root.mkdir()
    (root / "note.txt").write_text("DO NOT ERASE", encoding="utf-8")
    with pytest.raises(StillSequenceExportError, match="already exists"):
        export_complete_still_sequence(state, root, batch_size=120)
    assert (root / "note.txt").read_text(encoding="utf-8") == "DO NOT ERASE"
    for size in (0, 301, True):
        with pytest.raises(StillSequenceExportError, match="limits"):
            export_complete_still_sequence(state, tmp_path / "invalid", batch_size=size)
        assert not (tmp_path / "invalid").exists()
    clip = state.tracks[0].clips[0]
    extended = replace(clip, image_hold_frames=18001)
    huge = replace(
        state,
        tracks=(
            replace(state.tracks[0], clips=(extended,)),
            replace(state.tracks[1], clips=()),
        ),
    )
    with pytest.raises(StillSequenceExportError, match="limits"):
        export_complete_still_sequence(huge, tmp_path / "huge")
    assert not (tmp_path / "huge").exists()
