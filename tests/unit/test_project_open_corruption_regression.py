"""Post-W8 project-open hardening: malformed .angproj must never crash or leak paths."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ai_ngerti_geopolitik.application.project_session import ProjectSession
from ai_ngerti_geopolitik.domain import ProjectState
from ai_ngerti_geopolitik.infrastructure.persistence import (
    JsonProjectRepository,
    ProjectFormatError,
)


@pytest.mark.parametrize("invalid_track", [None, 42, "corrupt-track"])
def test_corrupt_nested_track_has_typed_private_safe_error(
    tmp_path: Path, invalid_track: object
) -> None:
    repo = JsonProjectRepository()
    document = ProjectState.create("P-OPEN", "Valid", 30).semantic_dict(
        include_revision=True
    )
    document["tracks"] = [invalid_track]
    bad = tmp_path / "SECRET_TOKEN_PRIVATE_PROJECT.angproj"
    bad.write_text(json.dumps(document), encoding="utf-8")

    with pytest.raises(ProjectFormatError, match="^invalid project file$") as error:
        repo.load(bad)

    assert "SECRET_TOKEN" not in str(error.value)
    assert str(bad) not in str(error.value)
    assert error.value.__cause__ is None
    assert error.value.__suppress_context__


def test_invalid_json_and_unavailable_path_are_redacted(tmp_path: Path) -> None:
    repo = JsonProjectRepository()
    broken = tmp_path / "PRIVATE_BAD_JSON.angproj"
    broken.write_text("{malformed", encoding="utf-8")
    absent = tmp_path / "PRIVATE_MISSING.angproj"
    for path in (broken, absent):
        with pytest.raises(ProjectFormatError, match="^invalid project file$") as error:
            repo.load(path)
        assert "PRIVATE_" not in str(error.value)
        assert str(path) not in str(error.value)
        assert error.value.__suppress_context__


def test_corrupt_open_does_not_replace_valid_active_session(tmp_path: Path) -> None:
    repository = JsonProjectRepository()
    session = ProjectSession(repository)
    session.new_project("P-SAFE", "Keep working", 30)
    active = session.save(tmp_path / "active.angproj")
    before_hash = session.state.semantic_hash()
    before_session = session.session_id
    before_bytes = active.read_bytes()

    document = ProjectState.create("P-INVALID", "Corrupt", 30).semantic_dict(
        include_revision=True
    )
    document["tracks"] = [17]
    corrupt = tmp_path / "SECRET_TOKEN_CORRUPTED.angproj"
    corrupt.write_text(json.dumps(document), encoding="utf-8")

    with pytest.raises(ProjectFormatError, match="^invalid project file$"):
        session.open_project(corrupt, discard_unsaved=True)

    assert session.is_open
    assert session.session_id == before_session
    assert session.current_path == active
    assert session.state.semantic_hash() == before_hash
    assert not session.dirty
    assert active.read_bytes() == before_bytes
