"""W8-006 explicit crash recovery, safe marker and source-byte preservation."""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_ngerti_geopolitik.application.autosave_catalog import AutosaveCatalogService
from ai_ngerti_geopolitik.application.project_session import ProjectSession, UnsavedChangesError
from ai_ngerti_geopolitik.application.recovery import (
    CrashMarker,
    RecoveryChoice,
    RecoveryError,
    RecoveryManager,
)
from ai_ngerti_geopolitik.domain import ProjectState
from ai_ngerti_geopolitik.infrastructure.crash_marker import FileCrashMarkerStore
from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository


def fixture(tmp_path: Path):
    repo = JsonProjectRepository()
    service = AutosaveCatalogService(repo)
    markers = FileCrashMarkerStore()
    manager = RecoveryManager(repo, service, markers)
    source = tmp_path / "canonical.angproj"
    state = ProjectState.create("P-RECOVERY", "Original", 30)
    repo.save(state, source)
    before = source.read_bytes()
    return repo, service, markers, manager, source, state, before


def crash(repo, service, manager, source, state, *, revision: int = 5):
    session = ProjectSession(repo)
    first = manager.inspect(source)
    decision = manager.decide(first, RecoveryChoice.OPEN_SOURCE, session)
    assert decision.active_marker is not None
    snapshot = service.create_snapshot(
        state.with_revision(revision), source.parent / ".ang-autosave", source_path=source
    )
    # Deliberately do not call close_clean: simulates abnormal process termination.
    return decision.active_marker, snapshot


def test_clean_close_and_explicit_open_source(tmp_path: Path) -> None:
    repo, service, markers, manager, source, state, before = fixture(tmp_path)
    session = ProjectSession(repo)
    fresh = manager.inspect(source)
    assert not fresh.interrupted and not fresh.can_recover
    decision = manager.decide(fresh, RecoveryChoice.OPEN_SOURCE, session)
    assert decision.opened_state == state
    assert decision.active_marker is not None
    assert markers.read(source, state.project_id).status == "unclean"
    manager.close_clean(session, source, decision.active_marker)
    assert markers.read(source, state.project_id).status == "clean"
    assert manager.inspect(source).candidates == ()
    assert source.read_bytes() == before


def test_crash_recovery_explicit_and_no_silent_save(tmp_path: Path) -> None:
    repo, service, markers, manager, source, state, before = fixture(tmp_path)
    old_marker, valid = crash(repo, service, manager, source, state)
    assert markers.read(source, state.project_id) == old_marker
    offer = RecoveryManager(repo, service, markers).inspect(source)
    assert offer.interrupted and offer.can_recover
    assert len(offer.candidates) == 1 and offer.candidates[0].path == valid
    assert source.read_bytes() == before
    session = ProjectSession(repo)
    choice = manager.decide(offer, RecoveryChoice.RECOVER_SNAPSHOT, session, selected_path=valid)
    assert choice.opened_state is not None and choice.opened_state.revision == 5
    assert choice.active_marker is not None
    assert session.current_path == source
    assert session.dirty  # explicit Save required even if payload is semantically equal
    assert source.read_bytes() == before
    assert markers.read(source, state.project_id) != old_marker
    manager.close_clean(session, source, choice.active_marker, discard_unsaved=True)
    assert markers.read(source, state.project_id).status == "clean"
    assert source.read_bytes() == before


def test_corrupt_newest_falls_back_to_older_valid(tmp_path: Path) -> None:
    repo, service, _markers, manager, source, state, before = fixture(tmp_path)
    _marker, valid = crash(repo, service, manager, source, state, revision=3)
    folder = source.parent / ".ang-autosave"
    corrupt = folder / f"{state.project_id}.r000099.{'f' * 12}.autosave.angproj"
    corrupt.write_text("{bad-json", encoding="utf-8")
    older = service.create_snapshot(state.with_revision(2), folder, source_path=source)
    offer = manager.inspect(source)
    assert corrupt.exists() and corrupt not in [row.path for row in offer.candidates]
    assert {row.path for row in offer.candidates} == {valid, older}
    sess = ProjectSession(repo)
    decided = manager.decide(offer, RecoveryChoice.RECOVER_SNAPSHOT, sess, selected_path=valid)
    assert decided.opened_state is not None and decided.opened_state.revision == 3
    assert corrupt.exists() and source.read_bytes() == before


def test_older_and_equal_identical_snapshots_not_recoverable(tmp_path: Path) -> None:
    repo, service, _markers, manager, source, state, before = fixture(tmp_path)
    source_state = state.with_revision(4)
    repo.save(source_state, source)
    session = ProjectSession(repo)
    begin = manager.decide(manager.inspect(source), RecoveryChoice.OPEN_SOURCE, session)
    assert begin.active_marker is not None
    folder = source.parent / ".ang-autosave"
    service.create_snapshot(state.with_revision(2), folder, source_path=source)
    service.create_snapshot(state.with_revision(4), folder, source_path=source)
    offer = manager.inspect(source)
    assert offer.interrupted and not offer.can_recover
    assert offer.candidates == ()
    with pytest.raises(RecoveryError, match="validated recovery"):
        manager.decide(
            offer,
            RecoveryChoice.RECOVER_SNAPSHOT,
            ProjectSession(repo),
            selected_path=folder / "not-a-snapshot.angproj",
        )


def test_ignore_preserves_marker_and_does_not_mutate_session(tmp_path: Path) -> None:
    repo, service, markers, manager, source, state, before = fixture(tmp_path)
    prior, _snapshot = crash(repo, service, manager, source, state)
    untouched = ProjectSession(repo)
    result = manager.decide(manager.inspect(source), RecoveryChoice.IGNORE, untouched)
    assert result.opened_state is None and result.active_marker is None
    assert not untouched.is_open
    assert markers.read(source, state.project_id) == prior
    assert manager.inspect(source).interrupted
    assert source.read_bytes() == before


def test_open_source_does_not_take_snapshot(tmp_path: Path) -> None:
    repo, service, markers, manager, source, state, before = fixture(tmp_path)
    prior, valid = crash(repo, service, manager, source, state, revision=6)
    session = ProjectSession(repo)
    decision = manager.decide(manager.inspect(source), RecoveryChoice.OPEN_SOURCE, session)
    assert decision.opened_state is not None and decision.opened_state.revision == 0
    assert session.current_path == source and not session.dirty
    assert decision.active_marker is not None and decision.active_marker != prior
    assert valid.exists() and source.read_bytes() == before
    manager.close_clean(session, source, decision.active_marker)
    assert markers.read(source, state.project_id).status == "clean"


def test_stale_source_change_refuses_recovery(tmp_path: Path) -> None:
    repo, service, _markers, manager, source, state, _before = fixture(tmp_path)
    _m, valid = crash(repo, service, manager, source, state)
    offer = manager.inspect(source)
    repo.save(state.with_revision(10), source)
    session = ProjectSession(repo)
    with pytest.raises(RecoveryError, match="stale"):
        manager.decide(offer, RecoveryChoice.RECOVER_SNAPSHOT, session, selected_path=valid)
    assert not session.is_open


def test_tampered_snapshot_and_unlisted_path_rejected(tmp_path: Path) -> None:
    repo, service, _markers, manager, source, state, before = fixture(tmp_path)
    _m, valid = crash(repo, service, manager, source, state)
    offer = manager.inspect(source)
    with pytest.raises(RecoveryError, match="stale"):
        manager.decide(
            offer,
            RecoveryChoice.RECOVER_SNAPSHOT,
            ProjectSession(repo),
            selected_path=source,
        )
    valid.write_text("tampered", encoding="utf-8")
    with pytest.raises(RecoveryError, match="stale"):
        manager.decide(
            offer,
            RecoveryChoice.RECOVER_SNAPSHOT,
            ProjectSession(repo),
            selected_path=valid,
        )
    assert source.read_bytes() == before


def test_dirty_close_guard_leaves_unclean_marker(tmp_path: Path) -> None:
    repo, service, markers, manager, source, state, before = fixture(tmp_path)
    _m, valid = crash(repo, service, manager, source, state)
    session = ProjectSession(repo)
    offer = manager.inspect(source)
    decided = manager.decide(offer, RecoveryChoice.RECOVER_SNAPSHOT, session, selected_path=valid)
    assert decided.active_marker is not None
    with pytest.raises(UnsavedChangesError):
        manager.close_clean(session, source, decided.active_marker)
    assert session.is_open and session.dirty
    assert markers.read(source, state.project_id).status == "unclean"
    assert source.read_bytes() == before


def test_corrupt_marker_fails_closed_and_preserves_source(tmp_path: Path) -> None:
    repo, _service, markers, manager, source, state, before = fixture(tmp_path)
    bogus = manager.decide(
        manager.inspect(source), RecoveryChoice.OPEN_SOURCE, ProjectSession(repo)
    )
    assert bogus.active_marker is not None
    marker_path = markers._path(source, state.project_id)
    marker_path.write_text("{bad", encoding="utf-8")
    with pytest.raises(RecoveryError, match="inspection failed"):
        manager.inspect(source)
    assert source.read_bytes() == before


def test_recovery_snapshot_project_mismatch_atomic_session(tmp_path: Path) -> None:
    repo, _service, _markers, _manager, source, _state, before = fixture(tmp_path)
    foreign = tmp_path / "foreign.autosave.angproj"
    repo.save_snapshot(ProjectState.create("P-FOREIGN", "Foreign", 30), foreign)
    session = ProjectSession(repo)
    with pytest.raises(RuntimeError, match="project mismatch"):
        session.recover_snapshot(source, foreign)
    assert not session.is_open and source.read_bytes() == before


def test_old_marker_cannot_mark_new_session_clean(tmp_path: Path) -> None:
    repo, service, markers, manager, source, state, before = fixture(tmp_path)
    prior, _ = crash(repo, service, manager, source, state)
    session = ProjectSession(repo)
    new = manager.decide(manager.inspect(source), RecoveryChoice.OPEN_SOURCE, session)
    assert new.active_marker is not None
    with pytest.raises(RecoveryError, match="mismatch"):
        manager.close_clean(session, source, prior)
    assert session.is_open
    assert markers.read(source, state.project_id) == new.active_marker
    assert source.read_bytes() == before


def test_close_marker_write_failure_retains_previous_project_session(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, _catalog, markers, manager, source, state, before = fixture(tmp_path)
    session = ProjectSession(repo)
    chosen = manager.decide(manager.inspect(source), RecoveryChoice.OPEN_SOURCE, session)
    marker = chosen.active_marker
    assert marker is not None
    session_id = session.session_id
    semantic_hash = session.state.semantic_hash()
    original_write = markers.write

    def deny_clean(path: Path, updated_marker: CrashMarker) -> None:
        if updated_marker.status == "clean":
            raise PermissionError("injected marker write rejection")
        original_write(path, updated_marker)

    with monkeypatch.context() as patcher:
        patcher.setattr(markers, "write", deny_clean)
        with pytest.raises(PermissionError, match="marker write rejection"):
            manager.close_clean(session, source, marker)

    assert session.is_open and not session.dirty
    assert session.current_path == source
    assert session.session_id == session_id
    assert session.state.semantic_hash() == semantic_hash
    assert markers.read(source, state.project_id) == marker
    assert source.read_bytes() == before
    manager.close_clean(session, source, marker)
    assert not session.is_open
    assert markers.read(source, state.project_id).status == "clean"


def test_close_failure_attempts_restore_unclean_marker(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, _catalog, markers, manager, source, state, before = fixture(tmp_path)
    session = ProjectSession(repo)
    chosen = manager.decide(manager.inspect(source), RecoveryChoice.OPEN_SOURCE, session)
    marker = chosen.active_marker
    assert marker is not None
    old_id = session.session_id

    def refuse_close(*, discard_unsaved: bool = False) -> None:
        raise RuntimeError("injected in-memory close failure")

    with monkeypatch.context() as patcher:
        patcher.setattr(session, "close", refuse_close)
        with pytest.raises(RuntimeError, match="in-memory close failure"):
            manager.close_clean(session, source, marker)

    assert session.is_open
    assert session.session_id == old_id
    assert markers.read(source, state.project_id) == marker
    assert source.read_bytes() == before
    manager.close_clean(session, source, marker)
    assert not session.is_open
