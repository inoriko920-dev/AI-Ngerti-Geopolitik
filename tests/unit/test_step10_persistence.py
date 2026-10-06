from pathlib import Path

import pytest

from ai_ngerti_geopolitik.application.commands import (
    AddClipCommand,
    CommandBatch,
    CommandBus,
    ImportAssetCommand,
)
from ai_ngerti_geopolitik.domain import Asset, Clip, FrameTime, ProjectState
from ai_ngerti_geopolitik.infrastructure.persistence import (
    JsonProjectRepository,
    ProjectFormatError,
)


def _state() -> ProjectState:
    bus = CommandBus(ProjectState.create("P1", "Roundtrip", 30))
    asset = Asset(
        "A001",
        str(Path("fixture.mp4")),
        "video",
        FrameTime(240, 30),
        1920,
        1080,
        True,
        "b" * 64,
    )
    bus.execute(CommandBatch("B1", "import", "manual", 0, (ImportAssetCommand(asset),)))
    clip = Clip(
        "C001",
        "A001",
        FrameTime(0, 30),
        FrameTime(0, 30),
        FrameTime(240, 30),
    )
    bus.execute(CommandBatch("B2", "add", "manual", 1, (AddClipCommand(clip),)))
    return bus.state


def test_angproj_roundtrip_is_semantically_identical(tmp_path: Path) -> None:
    repository = JsonProjectRepository()
    path = tmp_path / "sample.angproj"
    source = _state()
    repository.save(source, path)
    loaded = repository.load(path)
    assert loaded.semantic_hash() == source.semantic_hash()
    assert loaded.revision == source.revision
    assert not (tmp_path / "sample.angproj.tmp").exists()


def test_corrupt_project_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "broken.angproj"
    path.write_text("{nope", encoding="utf-8")
    with pytest.raises(ProjectFormatError):
        JsonProjectRepository().load(path)
