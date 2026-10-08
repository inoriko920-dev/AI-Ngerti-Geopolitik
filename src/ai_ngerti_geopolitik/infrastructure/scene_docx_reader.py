"""Bounded read-only extraction of Word DOCX paragraphs for Scene v1.

Uses only Python standard-library ZIP + XML. No DOCX macros, embedded files,
relationships, or external references are executed/followed.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

from ai_ngerti_geopolitik.application.scene_docx_contract import (
    SceneDocxFormatError,
    SceneDocxPlan,
    parse_scene_docx_lines,
)

_WORD_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
_MAX_DOCX_BYTES = 16 * 1024 * 1024
_MAX_DOCUMENT_XML = 2 * 1024 * 1024
_MAX_PARAGRAPHS = 12000


def read_scene_docx(path: Path) -> SceneDocxPlan:
    """Open a selected .docx and return validated, non-mutating Scene DTOs."""
    try:
        target = path.resolve()
        if target.suffix.lower() != ".docx" or not target.is_file():
            raise SceneDocxFormatError("Scene DOCX file is missing or invalid")
        if target.stat().st_size > _MAX_DOCX_BYTES:
            raise SceneDocxFormatError("Scene DOCX exceeds size limit")
        with zipfile.ZipFile(target) as archive:
            info = archive.getinfo("word/document.xml")
            if info.file_size > _MAX_DOCUMENT_XML:
                raise SceneDocxFormatError("Scene DOCX content exceeds size limit")
            with archive.open(info) as document:
                payload = document.read(_MAX_DOCUMENT_XML + 1)
        if len(payload) > _MAX_DOCUMENT_XML:
            raise SceneDocxFormatError("Scene DOCX content exceeds size limit")
        # Reject DTD/entity declarations even where an XML backend supports them.
        if b"<!DOCTYPE" in payload.upper() or b"<!ENTITY" in payload.upper():
            raise SceneDocxFormatError("unsupported DOCX XML declaration")
        root = ET.fromstring(payload)
        body = root.find(f"{_WORD_NS}body")
        if body is None:
            raise SceneDocxFormatError("Scene DOCX body is missing")
        lines: list[str] = []
        # Paragraphs inside tables appear in document order too.
        for paragraph in body.iter(f"{_WORD_NS}p"):
            if len(lines) >= _MAX_PARAGRAPHS:
                raise SceneDocxFormatError("Scene DOCX has too many paragraphs")
            words = [node.text or "" for node in paragraph.iter(f"{_WORD_NS}t")]
            lines.append("".join(words))
        return parse_scene_docx_lines(tuple(lines))
    except SceneDocxFormatError:
        raise
    except (
        OSError,
        ValueError,
        ET.ParseError,
        zipfile.BadZipFile,
        zipfile.LargeZipFile,
        KeyError,
        RuntimeError,
        EOFError,
    ):
        raise SceneDocxFormatError("Scene DOCX cannot be read") from None
