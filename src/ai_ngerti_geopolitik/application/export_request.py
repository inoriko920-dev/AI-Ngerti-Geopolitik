"""Typed, non-mutating export request contract for SF12-T02.

This is an application boundary only. It does not unlock UI rendering or change
the frozen MediaEnginePort. The future adapter must pass T03 preflight and T09
result-verification gates before publishing any file.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Protocol

from ai_ngerti_geopolitik.application.ports import CancellationToken, ExportResult
from ai_ngerti_geopolitik.domain import ProjectState


class ExportContractError(ValueError):
    """Safe typed failure: never includes user paths or content."""


class ExportScope(StrEnum):
    FULL = "full"
    SELECTION = "selection"


class ExportCodec(StrEnum):
    H264 = "h264"
    H265 = "h265"


class ExportQuality(StrEnum):
    HIGH = "high"
    YOUTUBE_CLEAN = "youtube_clean"
    DOCUMENTARY_CRISP = "documentary_crisp"


class ExportSharpen(StrEnum):
    NONE = "none"
    LIGHT = "light"
    CRISP = "crisp"


class ExportSubtitles(StrEnum):
    BURN_IN = "burn_in"
    OFF = "off"


class ExportAudio(StrEnum):
    AAC = "aac"
    OFF = "off"


@dataclass(frozen=True, slots=True)
class ExportFrameRange:
    """Half-open timeline frame interval [start, end)."""

    start: int
    end: int

    def __post_init__(self) -> None:
        if type(self.start) is not int or type(self.end) is not int:
            raise ExportContractError("INVALID_FRAME_RANGE")
        if self.start < 0 or self.end <= self.start:
            raise ExportContractError("INVALID_FRAME_RANGE")


@dataclass(frozen=True, slots=True)
class ExportRequest:
    """Immutable requested output; not a guarantee that a codec is available."""

    request_id: str
    project_id: str
    session_id: str
    project_revision: int
    project_semantic_hash: str
    output_path: Path = field(repr=False)
    scope: ExportScope = ExportScope.FULL
    selection: ExportFrameRange | None = None
    codec: ExportCodec = ExportCodec.H264
    width: int = 1920
    height: int = 1080
    fps: int = 30
    quality: ExportQuality = ExportQuality.HIGH
    sharpen: ExportSharpen = ExportSharpen.NONE
    subtitles: ExportSubtitles = ExportSubtitles.BURN_IN
    audio: ExportAudio = ExportAudio.AAC

    def __post_init__(self) -> None:
        for name in ("request_id", "project_id", "session_id"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip() or len(value) > 256:
                raise ExportContractError("INVALID_IDENTITY")
            if any(ord(char) < 32 for char in value):
                raise ExportContractError("INVALID_IDENTITY")
        if type(self.project_revision) is not int or self.project_revision < 0:
            raise ExportContractError("INVALID_REVISION")
        if not isinstance(self.project_semantic_hash, str) or not re.fullmatch(
            r"[0-9a-f]{64}", self.project_semantic_hash
        ):
            raise ExportContractError("INVALID_SEMANTIC_HASH")
        if not isinstance(self.output_path, Path):
            raise ExportContractError("INVALID_OUTPUT_PATH")
        if (
            not self.output_path.is_absolute()
            or self.output_path.suffix.lower() != ".mp4"
            or self.output_path.stem in {"", ".", ".."}
            or ".." in self.output_path.parts
            or "\x00" in str(self.output_path)
        ):
            raise ExportContractError("INVALID_OUTPUT_PATH")
        for name, enum_type in (
            ("scope", ExportScope),
            ("codec", ExportCodec),
            ("quality", ExportQuality),
            ("sharpen", ExportSharpen),
            ("subtitles", ExportSubtitles),
            ("audio", ExportAudio),
        ):
            if type(getattr(self, name)) is not enum_type:
                raise ExportContractError("INVALID_EXPORT_OPTION")
        if (
            type(self.width) is not int
            or type(self.height) is not int
            or (self.width, self.height) not in {(1920, 1080), (2560, 1440), (3840, 2160)}
        ):
            raise ExportContractError("INVALID_RESOLUTION")
        if type(self.fps) is not int or self.fps not in (30, 60):
            raise ExportContractError("INVALID_FPS")
        if self.scope is ExportScope.FULL and self.selection is not None:
            raise ExportContractError("SELECTION_NOT_ALLOWED")
        if self.scope is ExportScope.SELECTION and type(self.selection) is not ExportFrameRange:
            raise ExportContractError("SELECTION_REQUIRED")

    @classmethod
    def for_project(
        cls,
        state: ProjectState,
        *,
        session_id: str,
        request_id: str,
        output_path: Path,
        scope: ExportScope = ExportScope.FULL,
        selection: ExportFrameRange | None = None,
        codec: ExportCodec = ExportCodec.H264,
        width: int = 1920,
        height: int = 1080,
        fps: int = 30,
        quality: ExportQuality = ExportQuality.HIGH,
        sharpen: ExportSharpen = ExportSharpen.NONE,
        subtitles: ExportSubtitles = ExportSubtitles.BURN_IN,
        audio: ExportAudio = ExportAudio.AAC,
    ) -> ExportRequest:
        """Capture only identity and immutable options, not media or live state."""

        request = cls(
            request_id=request_id,
            project_id=state.project_id,
            session_id=session_id,
            project_revision=state.revision,
            project_semantic_hash=state.semantic_hash(),
            output_path=output_path,
            scope=scope,
            selection=selection,
            codec=codec,
            width=width,
            height=height,
            fps=fps,
            quality=quality,
            sharpen=sharpen,
            subtitles=subtitles,
            audio=audio,
        )
        request.assert_current(state, session_id)
        return request

    def assert_current(self, state: ProjectState, session_id: str | None) -> None:
        """Reject closed/replaced/edited projects, even at the same revision."""

        if (
            not session_id
            or self.session_id != session_id
            or self.project_id != state.project_id
            or self.project_revision != state.revision
            or self.project_semantic_hash != state.semantic_hash()
        ):
            raise ExportContractError("STALE_EXPORT_REQUEST")
        if self.selection is not None and self.selection.end > state.timeline_end_frame():
            raise ExportContractError("INVALID_SELECTION_BOUNDS")


class ExportRequestMediaPort(Protocol):
    """Prospective additive port; no adapter or production UI wiring in T02.

    Adoption by an engine is subject to the ASTRA/ADR gate. In particular the
    frozen MediaEnginePort.export signature is intentionally unchanged.
    """

    def export_request(
        self,
        state: ProjectState,
        request: ExportRequest,
        cancellation: CancellationToken | None = None,
    ) -> ExportResult: ...
