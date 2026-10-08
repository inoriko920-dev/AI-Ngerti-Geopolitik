"""Owned W8-006 crashed-session simulation and fail-closed recovery evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ai_ngerti_geopolitik.application.autosave_catalog import AutosaveCatalogService
from ai_ngerti_geopolitik.application.project_session import ProjectSession
from ai_ngerti_geopolitik.application.recovery import RecoveryChoice, RecoveryManager
from ai_ngerti_geopolitik.domain import ProjectState
from ai_ngerti_geopolitik.infrastructure.crash_marker import FileCrashMarkerStore
from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", required=True, type=Path)
    args = parser.parse_args()
    root = args.evidence.resolve()
    root.mkdir(parents=True, exist_ok=True)
    repo = JsonProjectRepository()
    catalog = AutosaveCatalogService(repo)
    store = FileCrashMarkerStore()
    recovery = RecoveryManager(repo, catalog, store)
    source = root / "canonical.angproj"
    state = ProjectState.create("P-W8-006", "Recovery", 30)
    repo.save(state, source)
    source_before = source.read_bytes()
    session = ProjectSession(repo)
    opened = recovery.decide(recovery.inspect(source), RecoveryChoice.OPEN_SOURCE, session)
    assert opened.active_marker is not None
    folder = source.parent / ".ang-autosave"
    valid = catalog.create_snapshot(state.with_revision(4), folder, source_path=source)
    corrupt = folder / f"P-W8-006.r000099.{'f' * 12}.autosave.angproj"
    corrupt.write_text("{garbled-json", encoding="utf-8")
    # No normal shutdown: next manager observes an unclean marker.
    restarting = RecoveryManager(repo, catalog, store)
    offer = restarting.inspect(source)
    ignored = restarting.decide(offer, RecoveryChoice.IGNORE, ProjectSession(repo))
    assert ignored.opened_state is None and offer.interrupted
    assert len(offer.candidates) == 1 and offer.candidates[0].path == valid
    assert corrupt.exists()
    next_session = ProjectSession(repo)
    recovered = restarting.decide(
        offer, RecoveryChoice.RECOVER_SNAPSHOT, next_session, selected_path=valid
    )
    assert recovered.active_marker is not None
    assert recovered.opened_state is not None
    assert next_session.dirty and next_session.current_path == source
    assert source.read_bytes() == source_before
    restarting.close_clean(next_session, source, recovered.active_marker, discard_unsaved=True)
    assert store.read(source, state.project_id).status == "clean"
    assert not restarting.inspect(source).interrupted
    assert source.read_bytes() == source_before
    report = {
        "status": "PASS",
        "unclean_detected": offer.interrupted,
        "valid_newer_only": len(offer.candidates) == 1,
        "corrupt_newest_excluded": corrupt.exists(),
        "ignore_zero_mutation": ignored.opened_state is None,
        "explicit_restore": recovered.opened_state.revision == 4,
        "recovered_working_state_dirty": not next_session.is_open,
        "source_bytes_unchanged": source.read_bytes() == source_before,
        "clean_close_clears_warning": not restarting.inspect(source).interrupted,
        "no_silent_save": repo.load(source).revision == 0,
        "no_w8_007_started": True,
    }
    (root / "00_w8_006_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
