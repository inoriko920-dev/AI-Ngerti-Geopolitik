"""Application ports for persistence, probing, media execution and playback."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from ai_ngerti_geopolitik.domain import ProjectState


@dataclass(frozen=True, slots=True)
class ProbeResult:
    path: Path
    duration_frames: int
    fps: int
    width: int
    height: int
    has_audio: bool
    fingerprint_sha256: str
    media_type: str = "video"
    duration_seconds: float = 0.0
    file_size: int = 0
    sample_rate: int = 0


@dataclass(frozen=True, slots=True)
class PreviewResult:
    project_revision: int
    timeline_frame: int
    output_path: Path


@dataclass(frozen=True, slots=True)
class ExportResult:
    project_revision: int
    output_path: Path
    duration_frames: int
    width: int
    height: int
    fps: int


@dataclass(frozen=True, slots=True)
class ParsedSubtitleCue:
    index: int
    start_milliseconds: int
    end_milliseconds: int
    text: str


class SubtitleParseError(ValueError):
    """Typed failure for untrusted subtitle source parsing."""


class SubtitleParserPort(Protocol):
    def parse(self, path: Path) -> tuple[ParsedSubtitleCue, ...]: ...


class SubtitleWriteError(RuntimeError):
    """Typed failure for safe subtitle-copy writing."""


class SubtitleWriterPort(Protocol):
    def write_copy(
        self,
        path: Path,
        cues: tuple[ParsedSubtitleCue, ...],
    ) -> None: ...


class CancellationToken(Protocol):
    @property
    def cancelled(self) -> bool: ...


@dataclass(frozen=True, slots=True)
class RecordingDevice:
    device_id: str
    name: str


@dataclass(frozen=True, slots=True)
class RecordingResult:
    path: Path
    cancelled: bool = False


class RecorderPort(Protocol):
    def devices(self) -> tuple[RecordingDevice, ...]: ...

    def capture(
        self,
        device_id: str,
        staging_path: Path,
        *,
        max_duration_seconds: float,
        cancellation: CancellationToken | None = None,
    ) -> RecordingResult: ...


class MediaProbePort(Protocol):
    def probe(self, path: Path) -> ProbeResult: ...


class MediaAvailabilityPort(Protocol):
    def status(self, path: Path) -> str: ...


class ProjectRepositoryPort(Protocol):
    def save(self, state: ProjectState, path: Path) -> None: ...

    def save_snapshot(self, state: ProjectState, path: Path) -> None: ...

    def load(self, path: Path) -> ProjectState: ...


class MediaEnginePort(Protocol):
    def preview_frame(
        self,
        state: ProjectState,
        timeline_frame: int,
        output_path: Path,
    ) -> PreviewResult: ...

    def export(
        self,
        state: ProjectState,
        output_path: Path,
        cancellation: CancellationToken | None = None,
    ) -> ExportResult: ...


class RealtimePlaybackPort(Protocol):
    """Non-blocking native playback transport behind the application boundary."""

    def load(self, state: ProjectState) -> None: ...

    def seek(self, frame: int) -> None: ...

    def play(self) -> None: ...

    def pause(self) -> None: ...

    def stop(self) -> None: ...
