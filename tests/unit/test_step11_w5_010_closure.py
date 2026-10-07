# W5-010 final regression lock: tests/** intentionally retriggers prior accepted waves.
from __future__ import annotations

from pathlib import Path

import pytest

from ai_ngerti_geopolitik.application.commands import (
    CommandBatch,
    CommandBus,
    ImportAssetCommand,
    SetNarrationTrackCommand,
    SetSubtitleTrackCommand,
)
from ai_ngerti_geopolitik.application.microphone import (
    MicrophoneRecordingError,
    MicrophoneRecordingService,
)
from ai_ngerti_geopolitik.application.narration import NarrationImportService
from ai_ngerti_geopolitik.application.ports import (
    ProbeResult,
    RecordingDevice,
    RecordingResult,
    SubtitleParseError,
)
from ai_ngerti_geopolitik.application.subtitle_import import SubtitleImportService
from ai_ngerti_geopolitik.application.subtitle_working_copy import (
    DirtySubtitleWorkingCopyError,
    SubtitleWorkingCopy,
)
from ai_ngerti_geopolitik.domain import (
    Asset,
    Clip,
    FrameTime,
    NarrationTrack,
    ProjectState,
    SubtitleCue,
    SubtitleTrack,
    Track,
)
from ai_ngerti_geopolitik.infrastructure.persistence import JsonProjectRepository
from ai_ngerti_geopolitik.infrastructure.srt import Utf8SrtParser


def _video_state() -> ProjectState:
    video = Asset(
        "A001",
        "video.mp4",
        "video",
        FrameTime(180, 30),
        1920,
        1080,
        True,
        "a" * 64,
    )
    clip = Clip(
        "C001",
        "A001",
        FrameTime(0, 30),
        FrameTime(0, 30),
        FrameTime(180, 30),
    )
    state = ProjectState(
        project_id="P-W5-010",
        name="W5 closure",
        schema_version=1,
        fps=30,
        revision=0,
        assets=(video,),
        tracks=(Track("V1", "video", 0, (clip,), "Video 1"),),
    )
    state.validate()
    return state


def _subtitle() -> SubtitleTrack:
    return SubtitleTrack(
        "source.srt",
        (
            SubtitleCue(
                "S001",
                1,
                FrameTime(30, 30),
                FrameTime(90, 30),
                "W5 closure subtitle",
            ),
        ),
    )


def _audio_asset() -> Asset:
    return Asset(
        "A002",
        "narration.wav",
        "audio",
        FrameTime(120, 30),
        0,
        0,
        True,
        "b" * 64,
        sample_rate=48000,
    )


def test_pre_w5_w4_fixture_loads_with_safe_w5_defaults() -> None:
    state = JsonProjectRepository().load(Path("tests/fixtures/step11_w4_pre_w5.angproj"))
    assert state.subtitle is None
    assert state.narration is None
    clip = state.clip("C001")
    assert clip.properties.title.text == "GEOPOLITIK"
    assert clip.properties.transition.preset == "fade_black"
    assert clip.properties.effects.enter_effect == "Rise"
    assert clip.properties.effects.locked is True


def test_subtitle_narration_history_walk_is_reversible() -> None:
    bus = CommandBus(_video_state())
    video_hash = bus.state.semantic_hash()

    bus.execute(
        CommandBatch(
            "W5-010-SUBTITLE",
            "Bind subtitle",
            "manual",
            bus.state.revision,
            (SetSubtitleTrackCommand(_subtitle()),),
        )
    )
    subtitle_hash = bus.state.semantic_hash()

    narration = NarrationTrack(
        "N001",
        "A002",
        FrameTime(60, 30),
        gain_percent=80,
        fade_in_frames=15,
        fade_out_frames=15,
    )
    bus.execute(
        CommandBatch(
            "W5-010-NARRATION",
            "Bind narration",
            "manual",
            bus.state.revision,
            (
                ImportAssetCommand(_audio_asset()),
                SetNarrationTrackCommand(narration),
            ),
        )
    )
    combined_hash = bus.state.semantic_hash()

    bus.undo()
    assert bus.state.semantic_hash() == subtitle_hash
    assert bus.state.narration is None
    bus.undo()
    assert bus.state.semantic_hash() == video_hash
    assert bus.state.subtitle is None

    bus.redo()
    assert bus.state.semantic_hash() == subtitle_hash
    bus.redo()
    assert bus.state.semantic_hash() == combined_hash
    assert bus.state.subtitle is not None
    assert bus.state.narration == narration


def test_malformed_srt_failure_does_not_mutate_project(tmp_path: Path) -> None:
    source = tmp_path / "malformed.srt"
    source.write_text(
        "1\n00:00:01.000 --> 00:00:02,000\nMalformed\n",
        encoding="utf-8",
    )
    bus = CommandBus(_video_state())
    baseline = bus.state.semantic_hash()

    with pytest.raises(SubtitleParseError, match="invalid timestamp"):
        SubtitleImportService(Utf8SrtParser()).import_path(bus, source)

    assert bus.state.semantic_hash() == baseline
    assert bus.state.subtitle is None


def test_dirty_working_copy_reload_guard_preserves_unsaved_edit() -> None:
    baseline = _subtitle()
    working = SubtitleWorkingCopy(baseline)
    working.edit_selected(text="UNSAVED EDIT")

    with pytest.raises(DirtySubtitleWorkingCopyError, match="explicit discard"):
        working.reload(baseline)

    assert working.dirty is True
    assert working.selected is not None
    assert working.selected.text == "UNSAVED EDIT"


class FailingProbe:
    def probe(self, path: Path) -> ProbeResult:
        raise RuntimeError(f"cannot probe narration: {path.name}")


def test_missing_or_corrupt_narration_probe_cannot_fake_success(tmp_path: Path) -> None:
    bus = CommandBus(_video_state())
    baseline = bus.state.semantic_hash()
    service = NarrationImportService(FailingProbe())

    for name in ("missing.wav", "corrupt.wav"):
        with pytest.raises(RuntimeError, match="cannot probe narration"):
            service.import_and_bind(bus, tmp_path / name)
        assert bus.state.semantic_hash() == baseline
        assert bus.state.narration is None
        assert len(bus.state.assets) == 1


class FailingRecorder:
    def devices(self) -> tuple[RecordingDevice, ...]:
        return (RecordingDevice("MIC1", "Test Microphone"),)

    def capture(
        self,
        device_id: str,
        staging_path: Path,
        *,
        max_duration_seconds: float,
        cancellation=None,
    ) -> RecordingResult:
        del device_id, staging_path, max_duration_seconds, cancellation
        raise RuntimeError("simulated hardware capture failure")


def test_failed_recording_preserves_existing_narration(tmp_path: Path) -> None:
    state = _video_state()
    audio = _audio_asset()
    narration = NarrationTrack("N001", "A002", FrameTime(0, 30))
    state = ProjectState(
        project_id=state.project_id,
        name=state.name,
        schema_version=state.schema_version,
        fps=state.fps,
        revision=state.revision,
        assets=(*state.assets, audio),
        tracks=state.tracks,
        narration=narration,
        settings=state.settings,
    )
    state.validate()
    bus = CommandBus(state)
    baseline = bus.state.semantic_hash()

    with pytest.raises(MicrophoneRecordingError, match="capture failed"):
        MicrophoneRecordingService(FailingRecorder(), FailingProbe()).record_and_bind(
            bus,
            tmp_path,
            device_id="MIC1",
            max_duration_seconds=1.0,
        )

    assert bus.state.semantic_hash() == baseline
    assert bus.state.narration == narration
    assert not list(tmp_path.rglob("*.wav"))
