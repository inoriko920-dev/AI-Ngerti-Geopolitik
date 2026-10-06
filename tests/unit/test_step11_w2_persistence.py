from pathlib import Path

from ai_ngerti_geopolitik.application.commands import (
    AddClipCommand,
    AddMarkerCommand,
    CommandBatch,
    CommandBus,
    ImportAssetCommand,
)
from ai_ngerti_geopolitik.domain import Asset, Clip, FrameTime, Marker, ProjectState
from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository


def test_w2_marker_round_trip_is_backward_compatible_schema_v1(tmp_path: Path) -> None:
    bus = CommandBus(ProjectState.create("W2-PERSIST", "Markers", 30))
    asset = Asset(
        "A001",
        "fixture.mp4",
        "video",
        FrameTime(120, 30),
        1920,
        1080,
        True,
        "d" * 64,
    )
    bus.execute(CommandBatch("B1", "import", "manual", 0, (ImportAssetCommand(asset),)))
    bus.execute(
        CommandBatch(
            "B2",
            "clip",
            "manual",
            1,
            (
                AddClipCommand(
                    Clip(
                        "C001",
                        "A001",
                        FrameTime(0, 30),
                        FrameTime(0, 30),
                        FrameTime(120, 30),
                    )
                ),
            ),
        )
    )
    bus.execute(
        CommandBatch(
            "B3",
            "marker",
            "manual",
            2,
            (AddMarkerCommand(Marker("M001", FrameTime(45, 30), "Chapter 1", "chapter")),),
        )
    )

    path = tmp_path / "markers.angproj"
    repository = JsonProjectRepository()
    repository.save(bus.state, path)
    loaded = repository.load(path)

    assert loaded.schema_version == 1
    assert loaded.marker("M001").frame.frames == 45
    assert loaded.marker("M001").marker_type == "chapter"
    assert loaded.semantic_hash() == bus.state.semantic_hash()
