"""Source-owned Scene DOCX v1 import contract and hostile-file regressions."""

from __future__ import annotations

import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

import pytest

from ai_ngerti_geopolitik.application.scene_docx_contract import (
    SceneDocxFormatError,
    parse_scene_docx_lines,
)
from ai_ngerti_geopolitik.infrastructure.scene_docx_reader import read_scene_docx


def _write_docx(path: Path, lines: tuple[str, ...]) -> None:
    document = "".join(
        '<w:p><w:r><w:t xml:space="preserve">' + escape(line) + "</w:t></w:r></w:p>"
        for line in lines
    )
    xml = (
        '<w:document xmlns:w="http://schemas.openxmlformats.org/'
        'wordprocessingml/2006/main"><w:body>' + document + "</w:body></w:document>"
    )
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as out:
        out.writestr("word/document.xml", xml)


def test_valid_single_double_scene_asset_mapping_and_source_quote(tmp_path: Path) -> None:
    path = tmp_path / "SCENES. docx".replace(" ", "")
    _write_docx(
        path,
        (
            "Dokumen sejarah",
            "Tampilan Scene 1: 1",
            "Asset 1: Peta Asia Tenggara",
            "Source Quote: Original quotation preserved",
            "scene 2: 2",
            "asset 2: Tokoh pada podium",
            "ASSET 3: Bendera di latar",
            "Context: Presenter speaks about 1945",
        ),
    )
    parsed = read_scene_docx(path)
    assert len(parsed.scenes) == 2
    assert parsed.asset_count == 3
    assert [row.canonical_id for scene in parsed.scenes for row in scene.assets] == [
        "A001",
        "A002",
        "A003",
    ]
    assert parsed.scenes[0].expected_visuals == 1
    assert parsed.scenes[1].expected_visuals == 2
    assert parsed.scenes[0].source_context == ("Source Quote: Original quotation preserved",)
    assert parsed.scenes[1].source_context == ("Context: Presenter speaks about 1945",)


@pytest.mark.parametrize(
    "lines",
    [
        (),
        ("Asset 1: orphan",),
        ("Tampilan Scene 1: 3", "Asset 1: a"),
        ("Scene 2: 1", "Asset 1: a"),
        ("Scene 1: 2", "Asset 1: a"),
        ("Scene 1: 1", "Asset 2: skipped"),
        ("Scene 1: 1", "Asset 1:"),
        ("Scene 1: 1", "Asset 1: x", "Asset 2: y"),
        ("Scene 1: 1", "Asset 1: x", "Scene 3: 1", "Asset 2: y"),
        ("Scene 1: 1", "Asset 1: x", "Scene 1: 1", "Asset 2: y"),
        ("Scene 1: 1", "Asset 1: x", "Asset two: ambiguous"),
        ("Scene 1: 1", "Asset 1: x", "Scene 2: 1", "Asset 1: duplicate"),
    ],
)
def test_reject_ambiguous_invalid_scene_contract(lines: tuple[str, ...]) -> None:
    with pytest.raises(SceneDocxFormatError):
        parse_scene_docx_lines(lines)


def test_corrupt_nonzip_and_missing_are_path_redacted(tmp_path: Path) -> None:
    for path in (tmp_path / "SECRET_CORRUPT.docx", tmp_path / "SECRET_MISSING.docx"):
        if "CORRUPT" in path.name:
            path.write_bytes(b"not a DOCX zip archive")
        with pytest.raises(SceneDocxFormatError) as error:
            read_scene_docx(path)
        assert "SECRET_" not in str(error.value)
        assert str(path) not in str(error.value)


def test_zip_bomb_declared_document_member_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "large.docx"
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as out:
        out.writestr("word/document.xml", b"x" * (2 * 1024 * 1024 + 1))
    with pytest.raises(SceneDocxFormatError, match="size limit"):
        read_scene_docx(path)


def test_reject_dtd_entity_declaration(tmp_path: Path) -> None:
    path = tmp_path / "entity.docx"
    xml = b"""<!DOCTYPE a [<!ENTITY external SYSTEM "file:///secret">]>
    <w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
    <w:body><w:p><w:r><w:t>&external;</w:t></w:r></w:p></w:body></w:document>"""
    with zipfile.ZipFile(path, "w") as out:
        out.writestr("word/document.xml", xml)
    with pytest.raises(SceneDocxFormatError, match="unsupported DOCX XML"):
        read_scene_docx(path)


def test_docx_table_paragraphs_read_in_order(tmp_path: Path) -> None:
    path = tmp_path / "table.docx"
    xml = (
        b'<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        b"<w:body><w:p><w:r><w:t>Scene 1: 1</w:t></w:r></w:p>"
        b"<w:tbl><w:tr><w:tc><w:p><w:r><w:t>Asset 1: table</w:t>"
        b"</w:r></w:p></w:tc></w:tr></w:tbl>"
        b"</w:body></w:document>"
    )
    with zipfile.ZipFile(path, "w") as out:
        out.writestr("word/document.xml", xml)
    parsed = read_scene_docx(path)
    assert parsed.asset_count == 1
    assert parsed.scenes[0].assets[0].description == "table"
