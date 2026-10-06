from pathlib import Path

import pytest

from ai_ngerti_geopolitik.application.commands import (
    CommandBatch,
    UpdateProjectSettingsCommand,
)
from ai_ngerti_geopolitik.application.project_session import (
    ProjectSession,
    ProjectSessionError,
    UnsavedChangesError,
)
from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository


def _settings_batch(session: ProjectSession, width: int) -> CommandBatch:
    return CommandBatch(
        batch_id=f"B{session.state.revision + 1}",
        label="settings",
        actor="manual",
        expected_revision=session.state.revision,
        commands=(UpdateProjectSettingsCommand(width, 720, 30, "16:9"),),
    )


def test_project_lifecycle_dirty_save_backup_and_open(tmp_path: Path) -> None:
    repository = JsonProjectRepository()
    session = ProjectSession(repository)
    session.new_project("P-W1", "W1")
    assert session.dirty
    project_path = tmp_path / "w1.angproj"
    session.save(project_path)
    assert not session.dirty

    session.execute(_settings_batch(session, 1280))
    assert session.dirty
    with pytest.raises(UnsavedChangesError):
        session.close()

    session.save()
    assert not session.dirty
    backup = tmp_path / "w1.angproj.bak"
    assert backup.is_file()
    assert repository.load(backup).settings.width == 1920
    assert repository.load(project_path).settings.width == 1280

    session.close()
    assert not session.is_open
    opened = session.open_project(project_path)
    assert opened.settings.width == 1280
    assert not session.dirty


def test_unsaved_project_requires_save_path_and_force_for_close(tmp_path: Path) -> None:
    session = ProjectSession(JsonProjectRepository())
    session.new_project("P-NEW", "Unsaved")
    with pytest.raises(ProjectSessionError):
        session.save()
    with pytest.raises(UnsavedChangesError):
        session.close()
    session.close(discard_unsaved=True)
    assert not session.is_open


def test_autosave_never_changes_canonical_path_or_dirty_state(tmp_path: Path) -> None:
    repository = JsonProjectRepository()
    session = ProjectSession(repository)
    session.new_project("P-AUTO", "Autosave")
    canonical = tmp_path / "canonical.angproj"
    session.save(canonical)
    canonical_before = canonical.read_bytes()

    session.execute(_settings_batch(session, 1440))
    assert session.dirty
    autosave = session.autosave()
    assert autosave.is_file()
    assert autosave.parent.name == ".ang-autosave"
    assert session.current_path == canonical
    assert session.dirty
    assert canonical.read_bytes() == canonical_before
    assert repository.load(autosave).settings.width == 1440
