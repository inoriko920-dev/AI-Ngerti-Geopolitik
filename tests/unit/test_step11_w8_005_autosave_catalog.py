"""W8-005 autosave catalog retention and fail-closed recovery discovery."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from ai_ngerti_geopolitik.application.autosave_catalog import (
    AutosaveCatalogError,
    AutosaveCatalogService,
)
from ai_ngerti_geopolitik.application.commands import CommandBatch, UpdateProjectSettingsCommand
from ai_ngerti_geopolitik.application.project_session import ProjectSession
from ai_ngerti_geopolitik.domain import ProjectState
from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository


def _project(project_id: str = "P-AUTO", revision: int = 0) -> ProjectState:
    return ProjectState.create(project_id, "Autosave fixture", 30).with_revision(revision)


def _legacy(
    repository: JsonProjectRepository, folder: Path, state: ProjectState
) -> Path:
    target = folder / (
        f"{state.project_id}.r{state.revision:06d}."
        f"{state.semantic_hash()[:12]}.autosave.angproj"
    )
    repository.save_snapshot(state, target)
    return target


def _changed(session: ProjectSession, width: int) -> None:
    session.execute(
        CommandBatch(
            batch_id=f"W8-005-{session.state.revision + 1}",
            label="update dimensions",
            actor="manual",
            expected_revision=session.state.revision,
            commands=(UpdateProjectSettingsCommand(width, 1080, 30, "16:9"),),
        )
    )


def test_legacy_snapshot_backward_read_and_hash_metadata(tmp_path: Path) -> None:
    repository = JsonProjectRepository()
    state = _project(revision=4)
    folder = tmp_path / ".ang-autosave"
    folder.mkdir()
    old = _legacy(repository, folder, state)
    item = AutosaveCatalogService(repository).inspect(folder, state.project_id)
    assert item.rejected == ()
    assert len(item.recoverable) == 1
    record = item.recoverable[0]
    assert record.legacy_filename
    assert record.project_id == state.project_id
    assert record.revision == 4
    assert record.semantic_hash == state.semantic_hash()
    assert len(record.file_sha256) == 64
    assert record.timestamp_ns > 0
    assert record.path == old
    assert old.read_bytes()


def test_catalog_filters_corrupt_newest_and_wrong_project(tmp_path: Path) -> None:
    repository = JsonProjectRepository()
    service = AutosaveCatalogService(repository)
    folder = tmp_path / ".ang-autosave"
    folder.mkdir()
    valid = _legacy(repository, folder, _project(revision=2))
    corrupt = folder / f"P-AUTO.r000004.{'f' * 12}.autosave.angproj"
    corrupt.write_text("{ not json", encoding="utf-8")
    mislabeled_state = _project(project_id="P-FOREIGN", revision=3)
    mislabeled = folder / (
        f"P-AUTO.r000003.{mislabeled_state.semantic_hash()[:12]}.autosave.angproj"
    )
    repository.save_snapshot(mislabeled_state, mislabeled)
    foreign = _legacy(repository, folder, _project(project_id="P-FOREIGN", revision=7))
    catalog = service.inspect(folder, "P-AUTO")
    assert [entry.path for entry in catalog.recoverable] == [valid]
    assert set(catalog.rejected) == {corrupt, mislabeled}
    assert corrupt.exists() and mislabeled.exists() and foreign.exists()


def test_ordering_is_timestamp_then_revision_deterministic(tmp_path: Path) -> None:
    repo = JsonProjectRepository()
    folder = tmp_path / ".ang-autosave"
    folder.mkdir()
    first = _legacy(repo, folder, _project(revision=1))
    second = _legacy(repo, folder, _project(revision=2))
    third = _legacy(repo, folder, _project(revision=3))
    os.utime(first, ns=(100_000_000_000, 100_000_000_000))
    os.utime(second, ns=(300_000_000_000, 300_000_000_000))
    os.utime(third, ns=(200_000_000_000, 200_000_000_000))
    listed = AutosaveCatalogService(repo).inspect(folder, "P-AUTO")
    assert [item.path for item in listed.recoverable] == [second, third, first]
    assert AutosaveCatalogService(repo).inspect(folder, "P-AUTO") == listed


def test_retention_keeps_20_valid_managed_without_touching_source(tmp_path: Path) -> None:
    repo = JsonProjectRepository()
    catalog = AutosaveCatalogService(repo)
    session = ProjectSession(repo, autosave_catalog=catalog)
    session.new_project("P-AUTO", "Autosaves")
    source = tmp_path / "source.angproj"
    session.save(source)
    _changed(session, 1600)
    session.save()
    original_bytes = source.read_bytes()
    backup = tmp_path / "source.angproj.bak"
    backup_bytes = backup.read_bytes()
    folder = tmp_path / ".ang-autosave"
    folder.mkdir()
    foreign = _legacy(repo, folder, _project(project_id="P-FOREIGN", revision=9))
    corrupt = folder / f"P-AUTO.r000099.{'f' * 12}.autosave.angproj"
    corrupt.write_text("BROKEN", encoding="utf-8")
    latest = None
    for revision in range(1, 24):
        _changed(session, 1600 + revision)
        latest = session.autosave()
        assert session.dirty
    result = catalog.inspect(folder, "P-AUTO")
    assert len(result.recoverable) == 20
    assert latest is not None and latest.is_file()
    assert latest == result.recoverable[0].path
    assert corrupt in result.rejected
    assert foreign.is_file() and corrupt.is_file()
    assert source.read_bytes() == original_bytes
    assert backup.read_bytes() == backup_bytes
    assert session.current_path == source


def test_prune_refuses_foreign_legacy_bak_and_corrupt(tmp_path: Path) -> None:
    repo = JsonProjectRepository()
    catalog = AutosaveCatalogService(repo, retention_limit=1)
    folder = tmp_path / ".ang-autosave"
    folder.mkdir()
    first = _legacy(repo, folder, _project(revision=1))
    foreign = _legacy(repo, folder, _project(project_id="P-FOREIGN", revision=1))
    unsafe = folder / f"P-AUTO.r000000.{'f' * 12}.autosave.angproj"
    unsafe.write_text("not-a-project", encoding="utf-8")
    source = tmp_path / "actual.angproj"
    repo.save(_project(revision=1), source)
    bak = source.with_name(source.name + ".bak")
    bak.write_bytes(b"NEVER DELETE BACKUP")
    second = _legacy(repo, folder, _project(revision=2))
    os.utime(first, ns=(100_000_000_000, 100_000_000_000))
    os.utime(second, ns=(300_000_000_000, 300_000_000_000))
    source_bytes = source.read_bytes()
    pruned = catalog.enforce_retention(folder, "P-AUTO", source_path=source)
    assert pruned.deleted == (first,)
    assert [x.path for x in pruned.kept] == [second]
    assert second.is_file()
    assert foreign.is_file()
    assert unsafe.is_file()
    assert source.read_bytes() == source_bytes
    assert bak.read_bytes() == b"NEVER DELETE BACKUP"


def test_snapshot_write_failure_preserves_source_and_old_snapshot(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = JsonProjectRepository()
    catalog = AutosaveCatalogService(repo, retention_limit=1)
    state = _project(revision=8)
    folder = tmp_path / ".ang-autosave"
    folder.mkdir()
    older = _legacy(repo, folder, _project(revision=5))
    original = older.read_bytes()
    source = tmp_path / "source.angproj"
    repo.save(state, source)
    source_before = source.read_bytes()

    def fail_snapshot(_state: ProjectState, _target: Path) -> None:
        raise OSError("injected write fault")

    with monkeypatch.context() as patch:
        patch.setattr(repo, "save_snapshot", fail_snapshot)
        with pytest.raises(OSError, match="injected"):
            catalog.create_snapshot(state, folder, source_path=source)
    assert source.read_bytes() == source_before
    assert older.read_bytes() == original
    assert len(list(folder.glob("*.autosave.angproj"))) == 1


def test_prune_failure_is_typed_and_does_not_touch_source(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = JsonProjectRepository()
    service = AutosaveCatalogService(repo, retention_limit=1)
    folder = tmp_path / ".ang-autosave"
    folder.mkdir()
    old = _legacy(repo, folder, _project(revision=1))
    new = _legacy(repo, folder, _project(revision=2))
    os.utime(old, ns=(100_000_000_000, 100_000_000_000))
    os.utime(new, ns=(200_000_000_000, 200_000_000_000))
    source = tmp_path / "project.angproj"
    repo.save(_project(revision=3), source)
    before = source.read_bytes()
    unlink_original = Path.unlink

    def denied(path: Path, *args: object, **kwargs: object) -> None:
        if path == old:
            raise OSError("injected deletion error")
        unlink_original(path, *args, **kwargs)

    with monkeypatch.context() as patch:
        patch.setattr(Path, "unlink", denied)
        with pytest.raises(AutosaveCatalogError, match="unable to prune"):
            service.enforce_retention(folder, "P-AUTO", source_path=source)
    assert source.read_bytes() == before
    assert new.exists() and old.exists()


def test_symlink_and_project_id_safety(tmp_path: Path) -> None:
    repo = JsonProjectRepository()
    service = AutosaveCatalogService(repo)
    for project_id in ("../outside", "a/b", "a\\b", "..", ""):
        with pytest.raises(AutosaveCatalogError):
            service.inspect(tmp_path, project_id)
    folder = tmp_path / "managed"
    folder.mkdir()
    link = tmp_path / "link"
    try:
        link.symlink_to(folder, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("symlink unavailable on this runner")
    with pytest.raises(AutosaveCatalogError):
        service.inspect(link, "P-AUTO")
    with pytest.raises(AutosaveCatalogError):
        service.create_snapshot(_project(), link)


def test_autosave_new_naming_roundtrip_and_no_source_overwrite(tmp_path: Path) -> None:
    repo = JsonProjectRepository()
    session = ProjectSession(repo)
    session.new_project("P-AUTO", "Autosaves")
    source = tmp_path / "source.angproj"
    session.save(source)
    before = source.read_bytes()
    autosave_path = session.autosave()
    catalog = session.autosave_catalog.inspect(autosave_path.parent, "P-AUTO")
    assert len(catalog.recoverable) == 1
    assert not catalog.recoverable[0].legacy_filename
    assert repo.load(autosave_path).semantic_hash() == session.state.semantic_hash()
    assert autosave_path.name.endswith(".autosave.angproj")
    assert source.read_bytes() == before
    assert session.current_path == source
    assert not session.dirty
