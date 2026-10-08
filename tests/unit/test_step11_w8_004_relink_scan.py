from __future__ import annotations

import threading
import time
from collections.abc import Iterator
from contextlib import suppress
from dataclasses import replace
from pathlib import Path

import pytest

from ai_ngerti_geopolitik.application.commands import CommandBus
from ai_ngerti_geopolitik.application.ports import ProbeResult
from ai_ngerti_geopolitik.application.relink_scan import (
    RelinkScanError,
    RelinkScanJobService,
    ScanCancel,
    ScanState,
)
from ai_ngerti_geopolitik.domain import Asset, Clip, FrameTime, ProjectState, Track
from ai_ngerti_geopolitik.infrastructure.relink_scan import LocalRelinkDirectoryScanner


class TestSession:
    __test__ = False

    def __init__(self, state: ProjectState) -> None:
        self.bus = CommandBus(state)

    @property
    def state(self) -> ProjectState:
        return self.bus.state

    def execute(self, batch):
        return self.bus.execute(batch)


class FakeProbe:
    def __init__(self, fingerprints: dict[str, str]) -> None:
        self.fingerprints = fingerprints

    def probe(self, path: Path) -> ProbeResult:
        return ProbeResult(
            path.resolve(),
            120,
            30,
            1920,
            1080,
            True,
            self.fingerprints[path.name],
            "video",
            4.0,
            1000,
            48000,
        )


class PauseScanner:
    def __init__(self) -> None:
        self.started = threading.Event()
        self.release = threading.Event()

    def paths(
        self, root: Path, *, cancellation: ScanCancel, max_files: int, max_depth: int
    ) -> Iterator[Path]:
        del cancellation, max_files, max_depth
        self.started.set()
        self.release.wait(timeout=5)
        yield root / "candidate.mp4"


def state(*, two: bool = False) -> ProjectState:
    first = Asset(
        "A001",
        "lost/original.mp4",
        "video",
        FrameTime(120, 30),
        1920,
        1080,
        True,
        "a" * 64,
        "source.mp4",
        1000,
        48000,
        "missing",
    )
    second = Asset(
        "A002",
        "lost/second.mp4",
        "video",
        FrameTime(120, 30),
        1920,
        1080,
        True,
        "b" * 64,
        "second-source.mp4",
        1000,
        48000,
        "missing",
    )
    clips = (Clip("C001", "A001", FrameTime(0, 30), FrameTime(0, 30), FrameTime(120, 30)),)
    if two:
        clips += (Clip("C002", "A002", FrameTime(120, 30), FrameTime(0, 30), FrameTime(120, 30)),)
    return ProjectState(
        "P-SCAN",
        "W8-004",
        1,
        30,
        7,
        assets=(first, second) if two else (first,),
        tracks=(Track("V1", "video", 0, clips),),
    )


def await_finished(service: RelinkScanJobService, job_id: str, current: ProjectState):
    end = time.monotonic() + 10
    while time.monotonic() < end:
        result = service.snapshot(job_id, state=current, session_id="S001")
        if result.state not in {ScanState.QUEUED, ScanState.RUNNING}:
            return result
        time.sleep(0.01)
    raise AssertionError("background scan timeout")


def test_ranked_ambiguity_and_manual_exact_approval(tmp_path: Path) -> None:
    for name in ("original.mp4", "source.mp4", "renamed.mp4", "fake.mp4"):
        (tmp_path / name).write_bytes(b"fixture")
    probe = FakeProbe(
        {
            name: "a" * 64
            for name in (
                "original.mp4",
                "source.mp4",
                "renamed.mp4",
            )
        }
        | {"fake.mp4": "f" * 64}
    )
    session = TestSession(state())
    before = session.state.semantic_hash()
    with RelinkScanJobService(LocalRelinkDirectoryScanner(), probe) as service:
        job = service.submit(session.state, tmp_path, session_id="S001")
        done = await_finished(service, job.job_id, session.state)
        assert done.state is ScanState.SUCCESS
        assert done.scanned_files == 4
        assert done.ambiguous_assets == ("A001",)
        assert [
            (item.path.name, item.rank, item.fingerprint_verified) for item in done.candidates
        ] == [
            ("original.mp4", 1, True),
            ("source.mp4", 2, True),
            ("renamed.mp4", 3, True),
            ("fake.mp4", 4, False),
        ]
        assert session.state.semantic_hash() == before
        with pytest.raises(RelinkScanError):
            service.apply_selected(job.job_id, session, session_id="S001", selections=())
        with pytest.raises(RelinkScanError):
            service.apply_selected(
                job.job_id,
                session,
                session_id="S001",
                selections=(("A001", tmp_path / "fake.mp4"),),
            )
        result = service.apply_selected(
            job.job_id,
            session,
            session_id="S001",
            selections=(("A001", tmp_path / "renamed.mp4"),),
        )
        assert result.revision == 8
        assert result.asset("A001").asset_id == "A001"
        assert result.clip("C001").asset_id == "A001"
        assert session.bus.undo().semantic_hash() == before
        assert session.bus.redo().asset("A001").path_ref == str(
            (tmp_path / "renamed.mp4").resolve()
        )
        with pytest.raises(RelinkScanError):
            service.apply_selected(
                job.job_id,
                session,
                session_id="S001",
                selections=(("A001", tmp_path / "original.mp4"),),
            )


def test_two_selections_commit_once_and_undo_once(tmp_path: Path) -> None:
    for filename in ("renamed-a.mp4", "renamed-b.mp4"):
        (tmp_path / filename).write_bytes(b"fixture")
    session = TestSession(state(two=True))
    before = session.state.semantic_hash()
    probe = FakeProbe({"renamed-a.mp4": "a" * 64, "renamed-b.mp4": "b" * 64})
    with RelinkScanJobService(LocalRelinkDirectoryScanner(), probe) as service:
        job = service.submit(session.state, tmp_path, session_id="S001")
        result = await_finished(service, job.job_id, session.state)
        assert len(result.candidates) == 2
        approved = service.apply_selected(
            job.job_id,
            session,
            session_id="S001",
            selections=(("A001", tmp_path / "renamed-a.mp4"), ("A002", tmp_path / "renamed-b.mp4")),
        )
        assert approved.revision == 8
        assert approved.clip("C001").asset_id == "A001"
        assert approved.clip("C002").asset_id == "A002"
        applied_hash = approved.semantic_hash()
        assert session.bus.undo().semantic_hash() == before
        assert session.bus.redo().semantic_hash() == applied_hash


def test_revision_semantic_and_session_stale_reject_before_mutation(tmp_path: Path) -> None:
    (tmp_path / "candidate.mp4").write_bytes(b"fixture")
    probe = FakeProbe({"candidate.mp4": "a" * 64})
    session = TestSession(state())
    with RelinkScanJobService(LocalRelinkDirectoryScanner(), probe) as service:
        job = service.submit(session.state, tmp_path, session_id="S001")
        await_finished(service, job.job_id, session.state)
        assert (
            service.snapshot(job.job_id, state=session.state, session_id="different").state
            is ScanState.STALE
        )
        with pytest.raises(RelinkScanError):
            service.apply_selected(
                job.job_id,
                session,
                session_id="different",
                selections=(("A001", tmp_path / "candidate.mp4"),),
            )
        session.bus.replace_loaded_state(replace(session.state, name="changed"))
        assert (
            service.snapshot(job.job_id, state=session.state, session_id="S001").state
            is ScanState.STALE
        )
        with pytest.raises(RelinkScanError):
            service.apply_selected(
                job.job_id,
                session,
                session_id="S001",
                selections=(("A001", tmp_path / "candidate.mp4"),),
            )
        assert session.state.asset("A001").availability == "missing"


def test_cancel_running_scan_cannot_publish_or_apply(tmp_path: Path) -> None:
    (tmp_path / "candidate.mp4").write_bytes(b"fixture")
    scanner = PauseScanner()
    session = TestSession(state())
    with RelinkScanJobService(scanner, FakeProbe({"candidate.mp4": "a" * 64})) as service:
        job = service.submit(session.state, tmp_path, session_id="S001")
        assert scanner.started.wait(timeout=5)
        service.cancel(job.job_id)
        scanner.release.set()
        done = await_finished(service, job.job_id, session.state)
        assert done.state is ScanState.CANCELLED and done.candidates == ()
        with pytest.raises(RelinkScanError):
            service.apply_selected(
                job.job_id,
                session,
                session_id="S001",
                selections=(("A001", tmp_path / "candidate.mp4"),),
            )
        assert session.state.asset("A001").availability == "missing"


def test_bounded_scanner_does_not_follow_symlinks_or_search_outside(tmp_path: Path) -> None:
    root = tmp_path / "media"
    nested = root / "nested"
    nested.mkdir(parents=True)
    for name in ("c.mp4", "a.mp4", "b.mp4"):
        (root / name).write_bytes(b"x")
    (nested / "nested.mp4").write_bytes(b"x")
    (root / "ignore.txt").write_text("no media")
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "secret.mp4").write_bytes(b"x")
    with suppress(OSError, NotImplementedError):
        (root / "escape").symlink_to(outside, target_is_directory=True)
    scanner = LocalRelinkDirectoryScanner()
    cancel = ScanCancel()
    limited = list(scanner.paths(root, cancellation=cancel, max_files=2, max_depth=4))
    assert [item.name for item in limited] == ["a.mp4", "b.mp4"]
    shallow = list(scanner.paths(root, cancellation=cancel, max_files=20, max_depth=0))
    assert [item.name for item in shallow] == ["a.mp4", "b.mp4", "c.mp4"]
    full = list(scanner.paths(root, cancellation=cancel, max_files=20, max_depth=4))
    assert [item.name for item in full] == ["a.mp4", "b.mp4", "c.mp4", "nested.mp4"]
    assert not any("secret.mp4" in str(item) for item in full)
    cancel.cancel()
    assert list(scanner.paths(root, cancellation=cancel, max_files=20, max_depth=4)) == []


def test_reject_duplicate_path_and_unsupported_bounds(tmp_path: Path) -> None:
    (tmp_path / "candidate.mp4").write_bytes(b"fixture")
    session = TestSession(state(two=True))
    probe = FakeProbe({"candidate.mp4": "a" * 64})
    with RelinkScanJobService(LocalRelinkDirectoryScanner(), probe) as service:
        with pytest.raises(RelinkScanError):
            service.submit(session.state, tmp_path, session_id="S001", max_files=0)
        job = service.submit(session.state, tmp_path, session_id="S001")
        await_finished(service, job.job_id, session.state)
        with pytest.raises(RelinkScanError):
            service.apply_selected(
                job.job_id,
                session,
                session_id="S001",
                selections=(
                    ("A001", tmp_path / "candidate.mp4"),
                    ("A002", tmp_path / "candidate.mp4"),
                ),
            )
        assert session.state.revision == 7
