from pathlib import Path

import pytest

from ai_ngerti_geopolitik.application.commands import (
    AddClipCommand,
    CommandBatch,
    CommandBus,
    ImportAssetCommand,
    TrimClipCommand,
)
from ai_ngerti_geopolitik.application.playback import PlaybackController, PlaybackError
from ai_ngerti_geopolitik.application.ports import PreviewResult
from ai_ngerti_geopolitik.domain import Asset, Clip, FrameTime, ProjectState


class RecordingPreviewEngine:
    def __init__(self) -> None:
        self.calls: list[tuple[int, int, Path]] = []

    def preview_frame(
        self,
        state: ProjectState,
        timeline_frame: int,
        output_path: Path,
    ) -> PreviewResult:
        self.calls.append((state.revision, timeline_frame, output_path))
        return PreviewResult(state.revision, timeline_frame, output_path)

    def export(self, state, output_path, cancellation=None):  # type: ignore[no-untyped-def]
        raise AssertionError("export is outside playback-controller scope")


def _bus() -> CommandBus:
    bus = CommandBus(ProjectState.create("P-S11", "Playback", 30))
    asset = Asset(
        "A001",
        "fixture.mp4",
        "video",
        FrameTime(120, 30),
        1920,
        1080,
        True,
        "a" * 64,
    )
    bus.execute(CommandBatch("B1", "import", "manual", 0, (ImportAssetCommand(asset),)))
    clip = Clip(
        "C001",
        "A001",
        FrameTime(0, 30),
        FrameTime(0, 30),
        FrameTime(120, 30),
    )
    bus.execute(CommandBatch("B2", "add", "manual", 1, (AddClipCommand(clip),)))
    return bus


def test_play_seek_pause_and_edit_revision_stay_coherent(tmp_path: Path) -> None:
    bus = _bus()
    engine = RecordingPreviewEngine()
    playback = PlaybackController(lambda: bus.state, engine, tmp_path)

    assert playback.seek(60).frame == 60
    assert playback.play().playing
    assert playback.advance(10).frame == 70
    result = playback.render_current()
    assert result.project_revision == bus.state.revision
    assert engine.calls[-1][:2] == (bus.state.revision, 70)

    bus.execute(
        CommandBatch(
            "B3",
            "trim",
            "manual",
            bus.state.revision,
            (TrimClipCommand("C001", 60),),
        )
    )
    snapshot = playback.snapshot
    assert snapshot.project_revision == bus.state.revision
    assert snapshot.frame == 59
    assert playback.pause().playing is False


def test_invalid_seek_and_empty_timeline_are_rejected(tmp_path: Path) -> None:
    empty = ProjectState.create("EMPTY", "Empty", 30)
    engine = RecordingPreviewEngine()
    playback = PlaybackController(lambda: empty, engine, tmp_path)

    with pytest.raises(PlaybackError, match="empty timeline"):
        playback.play()
    with pytest.raises(PlaybackError, match="empty"):
        playback.seek(0)

    bus = _bus()
    playback = PlaybackController(lambda: bus.state, engine, tmp_path)
    with pytest.raises(PlaybackError, match="outside timeline"):
        playback.seek(120)
