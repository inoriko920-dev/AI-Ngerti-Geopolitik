"""W5-007 microphone recording orchestration with staging safety."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from ai_ngerti_geopolitik.application.narration import (
    CommandSession,
    NarrationImportService,
)
from ai_ngerti_geopolitik.application.ports import (
    CancellationToken,
    MediaProbePort,
    RecorderPort,
)


class MicrophoneRecordingError(RuntimeError):
    pass


class MicrophoneDeviceUnavailable(MicrophoneRecordingError):
    pass


class MicrophoneRecordingCancelled(MicrophoneRecordingError):
    pass


def _next_recording_path(directory: Path) -> Path:
    candidate = directory / "narration-recording.wav"
    if not candidate.exists():
        return candidate
    index = 2
    while True:
        candidate = directory / f"narration-recording-{index}.wav"
        if not candidate.exists():
            return candidate
        index += 1


def _reserve_and_replace(staging: Path, final_path: Path) -> None:
    descriptor: int | None = None
    reserved = False
    try:
        descriptor = os.open(
            final_path,
            os.O_CREAT | os.O_EXCL | os.O_WRONLY,
            0o600,
        )
        os.close(descriptor)
        descriptor = None
        reserved = True
        os.replace(staging, final_path)
        reserved = False
    finally:
        if descriptor is not None:
            os.close(descriptor)
        if reserved and final_path.exists():
            final_path.unlink()


@dataclass(slots=True)
class MicrophoneRecordingService:
    recorder: RecorderPort
    probe: MediaProbePort

    def record_and_bind(
        self,
        session: CommandSession,
        recordings_dir: Path,
        *,
        device_id: str,
        max_duration_seconds: float,
        timeline_start_frame: int = 0,
        gain_percent: int = 100,
        fade_in_frames: int = 0,
        fade_out_frames: int = 0,
        cancellation: CancellationToken | None = None,
    ) -> Path:
        if session.state.timeline_end_frame <= 0:
            raise MicrophoneRecordingError(
                "microphone recording requires an active project timeline"
            )
        if max_duration_seconds <= 0:
            raise MicrophoneRecordingError("recording duration must be positive")
        if max_duration_seconds > 3600:
            raise MicrophoneRecordingError("recording duration must not exceed 3600 seconds")
        if cancellation is not None and cancellation.cancelled:
            raise MicrophoneRecordingCancelled("microphone recording was cancelled")

        devices = self.recorder.devices()
        if not devices:
            raise MicrophoneDeviceUnavailable("no microphone input device is available")
        if all(device.device_id != device_id for device in devices):
            raise MicrophoneDeviceUnavailable(
                f"microphone input device is unavailable: {device_id}"
            )

        recordings_dir = recordings_dir.resolve()
        recordings_dir.mkdir(parents=True, exist_ok=True)
        staging_dir = recordings_dir / ".staging"
        staging_dir.mkdir(parents=True, exist_ok=True)
        staging = staging_dir / f".mic-{uuid4().hex}.staging.wav"
        final_path: Path | None = None

        try:
            try:
                result = self.recorder.capture(
                    device_id,
                    staging,
                    max_duration_seconds=max_duration_seconds,
                    cancellation=cancellation,
                )
            except MicrophoneRecordingCancelled:
                raise
            except Exception as exc:
                raise MicrophoneRecordingError(
                    f"microphone capture failed: {exc}"
                ) from exc

            if result.cancelled or (cancellation is not None and cancellation.cancelled):
                raise MicrophoneRecordingCancelled("microphone recording was cancelled")
            if result.path.resolve() != staging.resolve():
                raise MicrophoneRecordingError(
                    "recorder returned an unexpected staging path"
                )
            if not staging.is_file() or staging.stat().st_size <= 44:
                raise MicrophoneRecordingError("microphone recording is empty")

            try:
                probed = self.probe.probe(staging)
            except Exception as exc:
                raise MicrophoneRecordingError(
                    f"recorded staging audio could not be validated: {exc}"
                ) from exc
            if probed.media_type != "audio" or not probed.has_audio:
                raise MicrophoneRecordingError(
                    "recorded staging media is not valid audio"
                )
            if probed.duration_seconds <= 0.05:
                raise MicrophoneRecordingError(
                    "recorded staging audio is too short"
                )
            if probed.sample_rate <= 0:
                raise MicrophoneRecordingError(
                    "recorded staging audio has no valid sample rate"
                )

            final_path = _next_recording_path(recordings_dir)
            _reserve_and_replace(staging, final_path)

            try:
                NarrationImportService(self.probe).import_and_bind(
                    session,
                    final_path,
                    timeline_start_frame=timeline_start_frame,
                    gain_percent=gain_percent,
                    fade_in_frames=fade_in_frames,
                    fade_out_frames=fade_out_frames,
                )
            except Exception as exc:
                if final_path.exists():
                    final_path.unlink()
                raise MicrophoneRecordingError(
                    f"recording could not be bound as narration: {exc}"
                ) from exc
            return final_path
        finally:
            if staging.exists():
                staging.unlink()
