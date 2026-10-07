from __future__ import annotations

from pathlib import Path

import pytest

from ai_ngerti_geopolitik.application.commands import CommandBus
from ai_ngerti_geopolitik.application.microphone import (
    MicrophoneDeviceUnavailable,
    MicrophoneRecordingCancelled,
    MicrophoneRecordingError,
    MicrophoneRecordingService,
)
from ai_ngerti_geopolitik.application.ports import (
    ProbeResult,
    RecordingDevice,
    RecordingResult,
)
from ai_ngerti_geopolitik.domain import (
    Asset,
    Clip,
    FrameTime,
    NarrationTrack,
    ProjectState,
    Track,
)


class Token:
    def __init__(self, cancelled: bool = False) -> None:
        self._cancelled = cancelled

    @property
    def cancelled(self) -> bool:
        return self._cancelled


class Probe:
    def __init__(
        self,
        *,
        media_type: str = "audio",
        duration_seconds: float = 1.0,
        sample_rate: int = 48000,
    ) -> None:
        self.media_type = media_type
        self.duration_seconds = duration_seconds
        self.sample_rate = sample_rate

    def probe(self, path: Path) -> ProbeResult:
        return ProbeResult(
            path=path.resolve(),
            duration_frames=0,
            fps=0,
            width=0,
            height=0,
            has_audio=self.media_type == "audio",
            fingerprint_sha256="b" * 64,
            media_type=self.media_type,
            duration_seconds=self.duration_seconds,
            file_size=path.stat().st_size if path.exists() else 0,
            sample_rate=self.sample_rate,
        )


class Recorder:
    def __init__(
        self,
        *,
        devices: tuple[RecordingDevice, ...] = (
            RecordingDevice("MIC1", "Test Microphone"),
        ),
        mode: str = "success",
    ) -> None:
        self._devices = devices
        self.mode = mode

    def devices(self) -> tuple[RecordingDevice, ...]:
        return self._devices

    def capture(
        self,
        device_id: str,
        staging_path: Path,
        *,
        max_duration_seconds: float,
        cancellation=None,
    ) -> RecordingResult:
        del device_id, max_duration_seconds
        if self.mode == "error":
            raise RuntimeError("simulated capture failure")
        if self.mode == "cancel":
            staging_path.write_bytes(b"partial" * 20)
            return RecordingResult(staging_path, cancelled=True)
        if self.mode == "empty":
            staging_path.write_bytes(b"")
            return RecordingResult(staging_path)
        if cancellation is not None and cancellation.cancelled:
            return RecordingResult(staging_path, cancelled=True)
        staging_path.write_bytes(b"RIFF" + b"0" * 256)
        return RecordingResult(staging_path)


def _state(*, existing_narration: bool = False) -> ProjectState:
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
    assets = [video]
    narration = None
    if existing_narration:
        assets.append(
            Asset(
                "A002",
                "old-narration.wav",
                "audio",
                FrameTime(90, 30),
                0,
                0,
                True,
                "c" * 64,
                sample_rate=48000,
            )
        )
        narration = NarrationTrack("N001", "A002", FrameTime(0, 30))
    clip = Clip(
        "C001",
        "A001",
        FrameTime(0, 30),
        FrameTime(0, 30),
        FrameTime(180, 30),
    )
    state = ProjectState(
        project_id="P-W5-007",
        name="Microphone",
        schema_version=1,
        fps=30,
        revision=0,
        assets=tuple(assets),
        tracks=(Track("V1", "video", 0, (clip,), "Video 1"),),
        narration=narration,
    )
    state.validate()
    return state


def test_success_stages_validates_finalizes_and_binds_atomically(tmp_path: Path) -> None:
    bus = CommandBus(_state())
    service = MicrophoneRecordingService(Recorder(), Probe())

    final_path = service.record_and_bind(
        bus,
        tmp_path,
        device_id="MIC1",
        max_duration_seconds=2.0,
        timeline_start_frame=30,
        gain_percent=90,
    )

    assert final_path == tmp_path / "narration-recording.wav"
    assert final_path.is_file()
    assert bus.state.revision == 1
    assert bus.state.narration is not None
    assert bus.state.narration.asset_id == "A002"
    assert bus.state.narration.timeline_start.frames == 30
    assert list((tmp_path / ".staging").glob("*")) == []

    bus.undo()
    assert bus.state.narration is None
    assert len(bus.state.assets) == 1
    bus.redo()
    assert bus.state.narration is not None


def test_cancel_failure_and_empty_capture_preserve_existing_narration(tmp_path: Path) -> None:
    for mode, error in (
        ("cancel", MicrophoneRecordingCancelled),
        ("error", MicrophoneRecordingError),
        ("empty", MicrophoneRecordingError),
    ):
        bus = CommandBus(_state(existing_narration=True))
        baseline = bus.state.semantic_hash()
        service = MicrophoneRecordingService(Recorder(mode=mode), Probe())
        with pytest.raises(error):
            service.record_and_bind(
                bus,
                tmp_path / mode,
                device_id="MIC1",
                max_duration_seconds=1.0,
            )
        assert bus.state.semantic_hash() == baseline
        assert bus.state.narration is not None
        assert bus.state.narration.asset_id == "A002"


def test_missing_or_unknown_device_never_mutates_project(tmp_path: Path) -> None:
    bus = CommandBus(_state(existing_narration=True))
    baseline = bus.state.semantic_hash()

    with pytest.raises(MicrophoneDeviceUnavailable, match="no microphone"):
        MicrophoneRecordingService(
            Recorder(devices=()),
            Probe(),
        ).record_and_bind(
            bus,
            tmp_path,
            device_id="MIC1",
            max_duration_seconds=1.0,
        )

    with pytest.raises(MicrophoneDeviceUnavailable, match="unavailable"):
        MicrophoneRecordingService(Recorder(), Probe()).record_and_bind(
            bus,
            tmp_path,
            device_id="MISSING",
            max_duration_seconds=1.0,
        )
    assert bus.state.semantic_hash() == baseline


def test_invalid_staged_audio_never_replaces_existing_narration(tmp_path: Path) -> None:
    bus = CommandBus(_state(existing_narration=True))
    baseline = bus.state.semantic_hash()

    with pytest.raises(MicrophoneRecordingError, match="not valid audio"):
        MicrophoneRecordingService(
            Recorder(),
            Probe(media_type="video"),
        ).record_and_bind(
            bus,
            tmp_path,
            device_id="MIC1",
            max_duration_seconds=1.0,
        )

    assert bus.state.semantic_hash() == baseline
    assert not (tmp_path / "narration-recording.wav").exists()
    assert list((tmp_path / ".staging").glob("*")) == []


def test_existing_final_file_is_never_overwritten(tmp_path: Path) -> None:
    sentinel = tmp_path / "narration-recording.wav"
    sentinel.write_bytes(b"DO-NOT-OVERWRITE")
    bus = CommandBus(_state())

    final_path = MicrophoneRecordingService(Recorder(), Probe()).record_and_bind(
        bus,
        tmp_path,
        device_id="MIC1",
        max_duration_seconds=1.0,
    )

    assert sentinel.read_bytes() == b"DO-NOT-OVERWRITE"
    assert final_path == tmp_path / "narration-recording-2.wav"
    assert final_path.is_file()


def test_active_timeline_and_pre_cancel_are_required(tmp_path: Path) -> None:
    empty = ProjectState.create("P-EMPTY", "Empty")
    empty_bus = CommandBus(empty)
    service = MicrophoneRecordingService(Recorder(), Probe())

    with pytest.raises(MicrophoneRecordingError, match="active project timeline"):
        service.record_and_bind(
            empty_bus,
            tmp_path,
            device_id="MIC1",
            max_duration_seconds=1.0,
        )

    bus = CommandBus(_state(existing_narration=True))
    baseline = bus.state.semantic_hash()
    with pytest.raises(MicrophoneRecordingCancelled):
        service.record_and_bind(
            bus,
            tmp_path,
            device_id="MIC1",
            max_duration_seconds=1.0,
            cancellation=Token(cancelled=True),
        )
    assert bus.state.semantic_hash() == baseline
