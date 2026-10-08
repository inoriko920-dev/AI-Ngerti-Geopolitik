"""W8-007 fault injection gates around existing JsonProjectRepository."""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from ai_ngerti_geopolitik.application.commands import (
    CommandBatch,
    UpdateProjectSettingsCommand,
)
from ai_ngerti_geopolitik.application.persistence_failure import (
    PersistenceError,
    PersistenceStage,
    persistence_error_projection,
)
from ai_ngerti_geopolitik.application.project_session import ProjectSession
from ai_ngerti_geopolitik.domain import ProjectState
from ai_ngerti_geopolitik.infrastructure import persistence
from ai_ngerti_geopolitik.infrastructure.persistence import (
    JsonProjectRepository,
    ProjectFormatError,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def initial(tmp_path: Path) -> tuple[JsonProjectRepository, Path, ProjectState]:
    repo = JsonProjectRepository()
    src = tmp_path / "project.angproj"
    state = ProjectState.create("P-W8-007", "Existing state", 30)
    repo.save(state, src)
    return repo, src, state


def changed(state: ProjectState) -> ProjectState:
    return ProjectState.create(
        state.project_id, "Intended new state", state.fps, width=1280, height=720
    ).with_revision(state.revision + 1)


def assert_no_owned_temp(folder: Path) -> None:
    assert list(folder.glob(".*.tmp")) == []


def faulting_tempfile(original: Any, failure: str):
    def create(*args: Any, **kwargs: Any):
        mode = args[0] if args else kwargs.get("mode", "w")
        if failure == "temp_create" and mode == "w":
            raise OSError("injected private path: C:\\private\\story.txt")
        if failure == "backup_create" and mode == "wb":
            raise OSError("injected backup create fault")
        real = original(*args, **kwargs)
        if failure != "temp_write" or mode != "w":
            return real

        class PartialWrite:
            name: str = real.name

            def __enter__(self):
                real.__enter__()
                return self

            def write(self, payload: str) -> None:
                real.write(payload[:16])
                raise OSError("injected partial write")

            def __exit__(self, typ: Any, value: Any, traceback: Any):
                return real.__exit__(typ, value, traceback)

            def flush(self) -> None:
                real.flush()

            def fileno(self) -> int:
                return real.fileno()

        return PartialWrite()

    return create


def install_fault(monkeypatch: pytest.MonkeyPatch, fault: str, source: Path) -> None:
    if fault in {"temp_create", "backup_create", "temp_write"}:
        original = persistence.tempfile.NamedTemporaryFile
        monkeypatch.setattr(
            persistence.tempfile, "NamedTemporaryFile", faulting_tempfile(original, fault)
        )
    elif fault == "temp_sync":
        monkeypatch.setattr(
            persistence.os,
            "fsync",
            lambda _fd: (_ for _ in ()).throw(OSError("injected fsync")),
        )
    elif fault == "backup_copy":
        monkeypatch.setattr(
            persistence.shutil,
            "copy2",
            lambda *_args: (_ for _ in ()).throw(OSError("injected copy")),
        )
    elif fault in {"backup_replace", "source_replace"}:
        original_replace = persistence.os.replace
        destination = (
            source.with_name(source.name + ".bak")
            if fault == "backup_replace"
            else source
        )

        def fail_replace(src: Path, dst: Path) -> None:
            if Path(dst) == destination:
                raise OSError("injected replace failure")
            original_replace(src, dst)

        monkeypatch.setattr(persistence.os, "replace", fail_replace)
    else:
        raise AssertionError("unexpected fault label")


@pytest.mark.parametrize(
    ("fault", "stage"),
    [
        ("temp_create", PersistenceStage.TEMP_CREATE),
        ("temp_write", PersistenceStage.TEMP_WRITE),
        ("temp_sync", PersistenceStage.TEMP_SYNC),
        ("backup_create", PersistenceStage.BACKUP_CREATE),
        ("backup_copy", PersistenceStage.BACKUP_COPY),
        ("backup_replace", PersistenceStage.BACKUP_REPLACE),
        ("source_replace", PersistenceStage.SOURCE_REPLACE),
    ],
)
def test_existing_source_exact_and_no_orphans_across_failures(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    fault: str,
    stage: PersistenceStage,
) -> None:
    repo, source, baseline = initial(tmp_path)
    # Existing .bak must remain present or a valid copy of the current source.
    backup = source.with_name(source.name + ".bak")
    repo.save(baseline.with_revision(1), source)
    before = source.read_bytes()
    backup_before = backup.read_bytes()
    intended = changed(baseline.with_revision(1))
    with monkeypatch.context() as patcher:
        install_fault(patcher, fault, source)
        with pytest.raises(PersistenceError) as exc:
            repo.save(intended, source)
        assert exc.value.stage is stage
        assert "private" not in str(exc.value)
        assert "C:\\" not in str(exc.value)
    assert source.read_bytes() == before
    assert backup.is_file()
    assert backup.read_bytes() in (backup_before, before)
    assert_no_owned_temp(tmp_path)
    assert repo.load(source).revision == 1
    repo.save(intended, source)
    assert repo.load(source).semantic_hash() == intended.semantic_hash()
    assert repo.load(source).revision == intended.revision
    assert backup.read_bytes() == before
    assert_no_owned_temp(tmp_path)


def test_new_source_temp_failure_does_not_create_fake_project(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = JsonProjectRepository()
    source = tmp_path / "new.angproj"
    with monkeypatch.context() as patcher:
        install_fault(patcher, "temp_write", source)
        with pytest.raises(PersistenceError) as exc:
            repo.save(ProjectState.create("P-NEW", "New project", 30), source)
    assert exc.value.stage is PersistenceStage.TEMP_WRITE
    assert not source.exists()
    assert not source.with_name(source.name + ".bak").exists()
    assert_no_owned_temp(tmp_path)


def test_snapshot_failure_cleans_temp_and_leaves_source_unchanged(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, source, state = initial(tmp_path)
    original = sha256(source)
    dest = tmp_path / "snapshot.autosave.angproj"
    with monkeypatch.context() as patcher:
        install_fault(patcher, "temp_write", dest)
        with pytest.raises(PersistenceError) as exc:
            repo.save_snapshot(changed(state), dest)
    assert exc.value.stage is PersistenceStage.TEMP_WRITE
    assert not dest.exists()
    assert sha256(source) == original
    assert_no_owned_temp(tmp_path)


def test_failed_save_retains_session_dirty_current_path_and_history(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = JsonProjectRepository()
    session = ProjectSession(repo)
    session.new_project("P-SESSION", "Session")
    source = session.save(tmp_path / "active.angproj")
    before = source.read_bytes()
    batch = CommandBatch(
        batch_id="B-W8-007", label="edit dimensions", actor="manual",
        expected_revision=session.state.revision,
        commands=(UpdateProjectSettingsCommand(1280, 720, 30, "16:9"),),
    )
    session.execute(batch)
    assert session.dirty
    intended_hash = session.state.semantic_hash()
    with monkeypatch.context() as patcher:
        install_fault(patcher, "source_replace", source)
        with pytest.raises(PersistenceError) as exc:
            session.save()
    assert exc.value.stage is PersistenceStage.SOURCE_REPLACE
    assert session.dirty and session.current_path == source
    assert session.state.semantic_hash() == intended_hash
    assert source.read_bytes() == before
    assert_no_owned_temp(tmp_path)
    assert session.save() == source
    assert not session.dirty
    assert repo.load(source).semantic_hash() == intended_hash
    assert repo.load(source.with_name(source.name + ".bak")).settings.width == 1920


def test_failed_save_as_does_not_rebind_current_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = JsonProjectRepository()
    session = ProjectSession(repo)
    session.new_project("P-SAVEAS", "Save As")
    first = session.save(tmp_path / "first.angproj")
    previous = first.read_bytes()
    candidate = tmp_path / "second.angproj"
    with monkeypatch.context() as patcher:
        install_fault(patcher, "source_replace", candidate)
        with pytest.raises(PersistenceError):
            session.save_as(candidate)
    assert not candidate.exists()
    assert session.current_path == first
    assert first.read_bytes() == previous
    assert_no_owned_temp(tmp_path)
    assert session.save_as(candidate) == candidate
    assert session.current_path == candidate


def test_existing_backup_replace_fault_preserves_old_backup_and_source(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, source, baseline = initial(tmp_path)
    repo.save(baseline.with_revision(1), source)
    bak = source.with_name(source.name + ".bak")
    source_digest = sha256(source)
    backup_digest = sha256(bak)
    with monkeypatch.context() as patcher:
        install_fault(patcher, "backup_replace", source)
        with pytest.raises(PersistenceError) as exc:
            repo.save(changed(baseline.with_revision(1)), source)
    assert exc.value.stage is PersistenceStage.BACKUP_REPLACE
    assert sha256(source) == source_digest
    assert sha256(bak) == backup_digest
    assert_no_owned_temp(tmp_path)


def test_cleanup_denial_is_typed_not_fake_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, source, baseline = initial(tmp_path)
    old = sha256(source)
    unlink_original = Path.unlink

    def deny_unlink(path: Path, *args: Any, **kwargs: Any) -> None:
        if path.suffix == ".tmp":
            raise PermissionError("injected cleanup denied")
        unlink_original(path, *args, **kwargs)

    with monkeypatch.context() as patcher:
        install_fault(patcher, "source_replace", source)
        patcher.setattr(Path, "unlink", deny_unlink)
        with pytest.raises(PersistenceError) as exc:
            repo.save(changed(baseline), source)
    # The primary failure remains visible; cleanup should never imply success.
    assert exc.value.stage is PersistenceStage.SOURCE_REPLACE
    assert sha256(source) == old
    for leaked in tmp_path.glob(".*.tmp"):
        leaked.unlink()
    assert_no_owned_temp(tmp_path)


def test_invalid_extension_does_not_create_parent(tmp_path: Path) -> None:
    repo = JsonProjectRepository()
    target = tmp_path / "do-not-create" / "invalid.txt"
    with pytest.raises(ProjectFormatError):
        repo.save(ProjectState.create("P", "Invalid", 30), target)
    assert not target.parent.exists()


def test_actionable_failure_projection_has_no_paths_or_secrets() -> None:
    for stage in PersistenceStage:
        err = PersistenceError(stage)
        projection = persistence_error_projection(err)
        assert projection.stage is stage
        assert projection.title and projection.next_action
        assert projection.retryable
        assert "C:\\" not in projection.title + projection.detail + projection.next_action
        assert "password" not in projection.title + projection.detail + projection.next_action
        assert "Path(" not in projection.detail
