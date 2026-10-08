"""Post-W8 project-open hardening: malformed .angproj must never crash or leak paths."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

from ai_ngerti_geopolitik.application.project_session import ProjectSession
from ai_ngerti_geopolitik.domain import (
    Asset,
    Clip,
    FrameTime,
    NarrationTrack,
    ProjectState,
    SubtitleCue,
    SubtitleTrack,
    Track,
)
from ai_ngerti_geopolitik.infrastructure.persistence import (
    JsonProjectRepository,
    ProjectFormatError,
)


@pytest.mark.parametrize("invalid_track", [None, 42, "corrupt-track"])
def test_corrupt_nested_track_has_typed_private_safe_error(
    tmp_path: Path, invalid_track: object
) -> None:
    repo = JsonProjectRepository()
    document = ProjectState.create("P-OPEN", "Valid", 30).semantic_dict(include_revision=True)
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

    document = ProjectState.create("P-INVALID", "Corrupt", 30).semantic_dict(include_revision=True)
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


@pytest.mark.parametrize(
    "field_path",
    [
        ("assets", 0, "has_audio"),
        ("tracks", 0, "locked"),
        ("tracks", 0, "muted"),
        ("tracks", 0, "visible"),
        ("tracks", 0, "clips", 0, "enabled"),
        ("tracks", 0, "clips", 0, "properties", "title", "enabled"),
        ("tracks", 0, "clips", 0, "properties", "effects", "locked"),
        ("subtitle", "enabled"),
        ("subtitle", "style", "background_box"),
        ("narration", "muted"),
    ],
)
@pytest.mark.parametrize("invalid", ["false", "true", 0, 1, None])
def test_malformed_boolean_never_silently_flips_project_state(
    tmp_path: Path, field_path: tuple[str | int, ...], invalid: object
) -> None:
    document = _full_project().semantic_dict(include_revision=True)
    location: object = document
    for item in field_path[:-1]:
        location = location[item]  # type: ignore[index]
    location[field_path[-1]] = invalid  # type: ignore[index]
    path = tmp_path / "SECRET_BOOLEAN.angproj"
    path.write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(ProjectFormatError, match="^invalid project file$") as error:
        JsonProjectRepository().load(path)
    assert "SECRET_BOOLEAN" not in str(error.value)
    assert error.value.__suppress_context__


def test_valid_boolean_flags_roundtrip_without_semantic_change(tmp_path: Path) -> None:
    repository = JsonProjectRepository()
    source = _full_project()
    path = tmp_path / "valid.angproj"
    repository.save(source, path)
    reopened = repository.load(path)
    assert reopened.semantic_hash() == source.semantic_hash()
    assert reopened.tracks[0].visible
    assert not reopened.tracks[0].muted
    assert reopened.subtitle is not None and reopened.subtitle.enabled
    assert reopened.narration is not None and not reopened.narration.muted


def _full_project() -> ProjectState:
    video = Asset(
        "A-VIDEO",
        "source.mp4",
        "video",
        FrameTime(90, 30),
        1920,
        1080,
        True,
        "a" * 64,
    )
    narration_asset = Asset(
        "A-VOICE",
        "narration.wav",
        "audio",
        FrameTime(90, 30),
        0,
        0,
        True,
        "b" * 64,
    )
    clip = Clip(
        "C-VIDEO",
        "A-VIDEO",
        FrameTime(0, 30),
        FrameTime(0, 30),
        FrameTime(90, 30),
    )
    cues = (SubtitleCue("SUB-1", 1, FrameTime(0, 30), FrameTime(30, 30), "Caption"),)
    project = replace(
        ProjectState.create("P-BOOL", "Boolean guard", 30),
        assets=(video, narration_asset),
        tracks=(Track("V1", "video", 0, (clip,)),),
        subtitle=SubtitleTrack("subtitles.srt", cues),
        narration=NarrationTrack("N-1", "A-VOICE", FrameTime(0, 30)),
    )
    project.validate()
    return project
