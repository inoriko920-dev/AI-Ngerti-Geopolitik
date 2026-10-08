"""Final Scene DOCX re-scan, stale-media and atomic .angproj save regression."""

from __future__ import annotations

import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

import pytest
from PySide6.QtGui import QImage

from ai_ngerti_geopolitik.application.project_session import ProjectSession
from ai_ngerti_geopolitik.application.scene_docx_contract import parse_scene_docx_lines
from ai_ngerti_geopolitik.application.scene_import_review import (
    SceneImportReviewError,
    build_scene_timeline_review,
    save_reviewed_scene_image_project,
)
from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository
from ai_ngerti_geopolitik.infrastructure.scene_asset_discovery import (
    scan_scene_asset_folder,
    verify_scene_image_media,
)
from ai_ngerti_geopolitik.infrastructure.scene_docx_reader import read_scene_docx


def _image(path: Path) -> None:
    image = QImage(4, 4, QImage.Format.Format_RGB32)
    image.fill(0x00228844)
    assert image.save(str(path), "PNG")


def _docx(path: Path, lines: tuple[str, ...]) -> None:
    body = "".join("<w:p><w:r><w:t>" + escape(line) + "</w:t></w:r></w:p>" for line in lines)
    xml = (
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        "<w:body>" + body + "</w:body></w:document>"
    )
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as output:
        output.writestr("word/document.xml", xml)


def _prepare(tmp_path: Path):
    lines = (
        "Scene 1: 1",
        "Asset 1: Historical map",
        "Source Quote: Source retained",
        "Scene 2: 2",
        "Asset 2: Portrait",
        "Asset 3: Flag",
    )
    docx = parse_scene_docx_lines(lines)
    docx_path = tmp_path / "Scene.docx"
    _docx(docx_path, lines)
    root = tmp_path / "images"
    root.mkdir()
    for i in range(1, 4):
        _image(root / f"A{i:03d}.png")
    inventory = scan_scene_asset_folder(docx, root)
    review = build_scene_timeline_review(docx, inventory, (150, 90), fps=30)
    verified = verify_scene_image_media(inventory)
    target = tmp_path / "documentary.angproj"
    return docx, docx_path, root, review, verified, target


def _save(
    prepared,
    *,
    repository=None,
    read_docx=read_scene_docx,
    scan=scan_scene_asset_folder,
    verify=verify_scene_image_media,
):
    docx, docx_path, root, review, verified, target = prepared
    return save_reviewed_scene_image_project(
        docx,
        docx_path,
        root,
        review,
        verified,
        target,
        project_id="P-DOCX-01",
        project_name="Scene Documentary",
        repository=repository or JsonProjectRepository(),
        read_docx=read_docx,
        scan=scan,
        verify=verify,
    )


def test_final_save_rechecks_then_persists_and_loads_real_scene_project(tmp_path: Path) -> None:
    prepared = _prepare(tmp_path)
    document = _save(prepared)
    target = prepared[-1]
    assert target.exists()
    assert document.revision == 1
    assert document.timeline_end_frame == 240
    assert len(document.assets) == 3
    assert document.markers[0].label.endswith("Source Quote: Source retained")
    assert [a.media_type for a in document.assets] == ["image", "image", "image"]
    assert [clip.image_hold_frames for clip in document.tracks[0].clips] == [150, 90]
    assert document.tracks[1].clips[0].image_hold_frames == 90
    session = ProjectSession(JsonProjectRepository())
    reopened = session.open_project(target)
    assert reopened.semantic_hash() == document.semantic_hash()
    assert session.current_path == target.resolve()
    assert session.dirty is False


def test_modified_image_after_preflight_does_not_create_file(tmp_path: Path) -> None:
    prepared = _prepare(tmp_path)
    _image(prepared[2] / "A002.png")
    (prepared[2] / "A002.png").write_bytes(b"corrupt replacement")
    with pytest.raises(SceneImportReviewError, match="safely saved"):
        _save(prepared)
    assert not prepared[-1].exists()


def test_added_duplicate_image_after_preflight_blocks_save(tmp_path: Path) -> None:
    prepared = _prepare(tmp_path)
    nested = prepared[2] / "new-subfolder"
    nested.mkdir()
    _image(nested / "a001.png")
    with pytest.raises(SceneImportReviewError, match="unresolved"):
        _save(prepared)
    assert not prepared[-1].exists()


def test_docx_changed_after_preflight_blocks_save(tmp_path: Path) -> None:
    prepared = _prepare(tmp_path)
    _docx(prepared[1], ("Scene 1: 1", "Asset 1: Changed image"))
    with pytest.raises(SceneImportReviewError, match="DOCX changed"):
        _save(prepared)
    assert not prepared[-1].exists()


def test_new_duplicate_injected_during_finalization_blocks_save(tmp_path: Path) -> None:
    prepared = _prepare(tmp_path)
    called = 0

    def scan_with_concurrent_change(docx, folder):
        nonlocal called
        called += 1
        if called == 2:
            nested = folder / "late"
            nested.mkdir()
            _image(nested / "A003.png")
        return scan_scene_asset_folder(docx, folder)

    with pytest.raises(SceneImportReviewError, match="before project Save"):
        _save(prepared, scan=scan_with_concurrent_change)
    assert called == 2
    assert not prepared[-1].exists()


def test_existing_destination_is_never_overwritten(tmp_path: Path) -> None:
    prepared = _prepare(tmp_path)
    target = prepared[-1]
    original = b"EXISTING PROJECT MUST SURVIVE"
    target.write_bytes(original)
    with pytest.raises(SceneImportReviewError, match="already exists"):
        _save(prepared)
    assert target.read_bytes() == original


def test_reverification_detects_changed_metadata_without_file_write(tmp_path: Path) -> None:
    prepared = _prepare(tmp_path)
    called = 0

    def verify_with_change(inventory):
        nonlocal called
        called += 1
        valid = verify_scene_image_media(inventory)
        if called == 1:
            _image(prepared[2] / "A001.png")
            replacement = QImage(5, 6, QImage.Format.Format_RGB32)
            replacement.fill(0x00FF4433)
            assert replacement.save(str(prepared[2] / "A001.png"), "PNG")
            return verify_scene_image_media(inventory)
        return valid

    with pytest.raises(SceneImportReviewError, match="changed since preflight"):
        _save(prepared, verify=verify_with_change)
    assert not prepared[-1].exists()
