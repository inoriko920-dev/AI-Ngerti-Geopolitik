from pathlib import Path

from ai_ngerti_geopolitik.application.commands import (
    CommandBatch,
    CommandBus,
    SetAssetAvailabilityCommand,
)
from ai_ngerti_geopolitik.domain import Asset, FrameTime, ProjectState
from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository


def test_w1_fields_roundtrip_and_second_save_keeps_previous_backup(tmp_path: Path) -> None:
    repository = JsonProjectRepository()
    asset = Asset(
        "A001",
        str(tmp_path / "audio.wav"),
        "audio",
        FrameTime(60, 30),
        0,
        0,
        True,
        "d" * 64,
        "audio.wav",
        1234,
        48000,
        "online",
    )
    bus = CommandBus(ProjectState.create("P1", "Roundtrip", 30, width=1280, height=720))
    from ai_ngerti_geopolitik.application.commands import ImportAssetCommand

    bus.execute(CommandBatch("B1", "import", "manual", 0, (ImportAssetCommand(asset),)))
    path = tmp_path / "project.angproj"
    repository.save(bus.state, path)

    before = bus.state.semantic_hash()
    bus.execute(
        CommandBatch(
            "B2",
            "offline",
            "manual",
            bus.state.revision,
            (SetAssetAvailabilityCommand("A001", "offline"),),
        )
    )
    repository.save(bus.state, path)

    backup = tmp_path / "project.angproj.bak"
    assert backup.is_file()
    assert repository.load(backup).semantic_hash() == before
    loaded = repository.load(path)
    assert loaded.settings.width == 1280
    assert loaded.settings.height == 720
    assert loaded.asset("A001").source_name == "audio.wav"
    assert loaded.asset("A001").sample_rate == 48000
    assert loaded.asset("A001").availability == "offline"
