"""Explicit scene duration TXT and real script-driven .angproj end-to-end tests."""

from __future__ import annotations

import zipfile
from pathlib import Path

import pytest
from PySide6.QtGui import QImage

from ai_ngerti_geopolitik.application.scene_import_review import (
    SceneImportReviewError,
    parse_scene_duration_manifest,
)
from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository
from scripts.import_scene_project import main


def _docx(path: Path) -> None:
    xml = (
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        "<w:body><w:p><w:r><w:t>Scene 1: 1</w:t></w:r></w:p>"
        "<w:p><w:r><w:t>Asset 1: Historical Map</w:t></w:r></w:p>"
        "<w:p><w:r><w:t>Scene 2: 2</w:t></w:r></w:p>"
        "<w:p><w:r><w:t>Asset 2: Portrait</w:t></w:r></w:p>"
        "<w:p><w:r><w:t>Asset 3: Flag</w:t></w:r></w:p>"
        "</w:body></w:document>"
    )
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("word/document.xml", xml)


def _media(folder: Path) -> None:
    folder.mkdir()
    for i in range(1, 4):
        image = QImage(5, 5, QImage.Format.Format_RGB32)
        image.fill(0x00112233)
        assert image.save(str(folder / f"A{i:03d}.png"), "PNG")


def _create(docx: Path, folder: Path, timing: Path, target: Path, name: str) -> int:
    args = [
        "create",
        "--docx",
        str(docx),
        "--assets",
        str(folder),
        "--timing",
        str(timing),
        "--output",
        str(target),
        "--name",
        name,
    ]
    return main(args)


def test_manifest_requires_exact_explicit_order_and_rejects_guesswork() -> None:
    assert parse_scene_duration_manifest(
        "# FPS=30\nScene 1: 150 frames\n\nScene 2: 90 frames\n", scene_count=2
    ) == (150, 90)
    for data in (
        "",
        "Scene 1: ____ frames\nScene 2: ____ frames",
        "Scene 1: 5 seconds\nScene 2: 6 seconds",
        "Scene 2: 150 frames\nScene 1: 90 frames",
        "Scene 1: 150 frames\nScene 1: 90 frames",
        "Scene 1: 150 frames",
        "Scene 1: 0 frames\nScene 2: 90 frames",
        "Scene 1: -5 frames\nScene 2: 90 frames",
        "Scene 1: 150 frames\nScene 2: 90 frames\nScene 3: 3 frames",
    ):
        with pytest.raises(SceneImportReviewError):
            parse_scene_duration_manifest(data, scene_count=2)


def test_template_to_real_saved_image_project_without_gui(tmp_path: Path) -> None:
    docx = tmp_path / "scenes.docx"
    _docx(docx)
    folder = tmp_path / "images"
    _media(folder)
    template = tmp_path / "timing.txt"
    target = tmp_path / "documentary.angproj"
    assert main(["template", "--docx", str(docx), "--output", str(template)]) == 0
    assert not target.exists()
    assert "Scene 1: ____ frames" in template.read_text(encoding="utf-8")
    assert _create(docx, folder, template, target, "Historical Film") == 1
    assert not target.exists()
    template.write_text(
        "# 30 FPS\nScene 1: 150 frames\nScene 2: 90 frames\n",
        encoding="utf-8",
    )
    assert _create(docx, folder, template, target, "Historical Film") == 0
    state = JsonProjectRepository().load(target)
    assert state.timeline_end_frame == 240
    assert [a.media_type for a in state.assets] == ["image"] * 3
    assert [c.image_hold_frames for c in state.tracks[0].clips] == [150, 90]
    assert state.tracks[1].clips[0].image_hold_frames == 90
    assert _create(docx, folder, template, target, "Historical Film") == 1


def test_missing_image_cannot_create_project(tmp_path: Path) -> None:
    docx = tmp_path / "scenes.docx"
    _docx(docx)
    folder = tmp_path / "images"
    _media(folder)
    (folder / "A003.png").unlink()
    timing = tmp_path / "timing.txt"
    timing.write_text("Scene 1: 120 frames\nScene 2: 90 frames\n", encoding="utf-8")
    target = tmp_path / "output.angproj"
    assert _create(docx, folder, timing, target, "Invalid") == 1
    assert not target.exists()
