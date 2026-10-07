from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from ai_ngerti_geopolitik.application.commands import CommandBus
from ai_ngerti_geopolitik.application.ports import ProbeResult
from ai_ngerti_geopolitik.application.relink import RelinkError, RelinkErrorCode, RelinkService
from ai_ngerti_geopolitik.domain import Asset, Clip, FrameTime, ProjectState, Track
from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository


class Session:
    def __init__(self, state: ProjectState) -> None:
        self.bus = CommandBus(state)

    @property
    def state(self) -> ProjectState:
        return self.bus.state

    def execute(self, batch):
        return self.bus.execute(batch)


class Probe:
    def __init__(self, result: ProbeResult | Exception) -> None:
        self.result = result

    def probe(self, path: Path) -> ProbeResult:
        if isinstance(self.result, Exception):
            raise self.result
        return replace(self.result, path=path.resolve())


def _asset(path_ref: str = "old/location.mp4", *, availability: str = "missing") -> Asset:
    return Asset(
        "A001",
        path_ref,
        "video",
        FrameTime(240, 30),
        1920,
        1080,
        True,
        "a" * 64,
        source_name=Path(path_ref).name,
        file_size=1000,
        sample_rate=48000,
        availability=availability,
    )


def _state(*, extra_asset: Asset | None = None) -> ProjectState:
    asset = _asset()
    clip = Clip("C001", "A001", FrameTime(0, 30), FrameTime(0, 30), FrameTime(120, 30))
    assets = (asset,) if extra_asset is None else (asset, extra_asset)
    return ProjectState(
        "P-W8-003",
        "Single relink",
        1,
        30,
        14,
        assets=assets,
        tracks=(Track("V1", "video", 0, (clip,)),),
    )


def _probe(
    *,
    media_type: str = "video",
    fingerprint: str = "a" * 64,
    duration_frames: int = 240,
    width: int = 1920,
    height: int = 1080,
    has_audio: bool = True,
    sample_rate: int = 48000,
) -> ProbeResult:
    return ProbeResult(
        Path("candidate.mp4"),
        duration_frames,
        30 if media_type == "video" else 0,
        width,
        height,
        has_audio,
        fingerprint,
        media_type,
        8.0,
        1000,
        sample_rate,
    )


def test_exact_candidate_relinks_one_asset_and_one_undo_redo_transaction(tmp_path: Path) -> None:
    session = Session(_state())
    before_hash = session.state.semantic_hash()
    result = RelinkService(Probe(_probe())).relink(session, "A001", tmp_path / "renamed.mp4")

    assert (result.base_revision, result.applied_revision) == (14, 15)
    assert session.state.asset("A001").asset_id == "A001"
    assert session.state.asset("A001").path_ref == str((tmp_path / "renamed.mp4").resolve())
    assert session.state.asset("A001").source_name == "renamed.mp4"
    assert session.state.asset("A001").availability == "online"
    assert session.state.clip("C001").asset_id == "A001"
    applied_hash = session.state.semantic_hash()
    assert session.bus.undo().semantic_hash() == before_hash
    assert session.bus.state.asset("A001").path_ref == "old/location.mp4"
    assert session.bus.redo().semantic_hash() == applied_hash


@pytest.mark.parametrize(
    ("probe_result", "code"),
    [
        (_probe(media_type="image", has_audio=False), RelinkErrorCode.MEDIA_TYPE_MISMATCH),
        (_probe(fingerprint="b" * 64), RelinkErrorCode.FINGERPRINT_MISMATCH),
        (_probe(width=1280), RelinkErrorCode.METADATA_MISMATCH),
        (_probe(duration_frames=210), RelinkErrorCode.METADATA_MISMATCH),
        (_probe(sample_rate=44100), RelinkErrorCode.METADATA_MISMATCH),
    ],
)
def test_wrong_type_hash_or_metadata_fails_before_canonical_mutation(
    tmp_path: Path,
    probe_result: ProbeResult,
    code: RelinkErrorCode,
) -> None:
    session = Session(_state())
    before = session.state.semantic_json(include_revision=True)
    with pytest.raises(RelinkError) as caught:
        RelinkService(Probe(probe_result)).relink(session, "A001", tmp_path / "candidate")
    assert caught.value.code is code
    assert session.state.semantic_json(include_revision=True) == before
    assert session.bus.can_undo is False


def test_probe_failure_and_unknown_asset_are_typed_and_zero_mutation(tmp_path: Path) -> None:
    session = Session(_state())
    before = session.state.semantic_json(include_revision=True)
    with pytest.raises(RelinkError) as probe_error:
        RelinkService(Probe(RuntimeError("bad probe"))).relink(
            session, "A001", tmp_path / "bad.mp4"
        )
    assert probe_error.value.code is RelinkErrorCode.PROBE_FAILED
    with pytest.raises(RelinkError) as unknown_error:
        RelinkService(Probe(_probe())).relink(session, "A999", tmp_path / "candidate.mp4")
    assert unknown_error.value.code is RelinkErrorCode.UNKNOWN_ASSET
    assert session.state.semantic_json(include_revision=True) == before


def test_candidate_path_bound_to_other_asset_is_rejected(tmp_path: Path) -> None:
    shared = tmp_path / "shared.mp4"
    other = Asset(
        "A002",
        str(shared.resolve()),
        "video",
        FrameTime(240, 30),
        1920,
        1080,
        True,
        "c" * 64,
        source_name="shared.mp4",
        file_size=1000,
        sample_rate=48000,
    )
    session = Session(_state(extra_asset=other))
    before = session.state.semantic_json(include_revision=True)
    with pytest.raises(RelinkError) as caught:
        RelinkService(Probe(_probe())).relink(session, "A001", shared)
    assert caught.value.code is RelinkErrorCode.PATH_CONFLICT
    assert session.state.semantic_json(include_revision=True) == before


def test_relinked_project_save_reopen_is_semantically_exact(tmp_path: Path) -> None:
    session = Session(_state())
    RelinkService(Probe(_probe())).relink(session, "A001", tmp_path / "renamed.mp4")
    path = tmp_path / "relinked.angproj"
    repository = JsonProjectRepository()
    repository.save(session.state, path)
    loaded = repository.load(path)
    assert loaded.semantic_hash() == session.state.semantic_hash()
    assert loaded.asset("A001").path_ref == str((tmp_path / "renamed.mp4").resolve())
    assert loaded.asset("A001").fingerprint_sha256 == "a" * 64
    assert loaded.clip("C001").asset_id == "A001"
