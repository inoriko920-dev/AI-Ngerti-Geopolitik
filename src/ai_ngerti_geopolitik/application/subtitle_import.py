"""S11 W5-002 canonical SRT import use-case.

This module maps validated parser DTOs into the W5-001 canonical subtitle model.
It never writes to the source SRT and does not own cue editing behavior.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from ai_ngerti_geopolitik.application.commands import (
    CommandBatch,
    SetSubtitleTrackCommand,
)
from ai_ngerti_geopolitik.application.ports import (
    ParsedSubtitleCue,
    SubtitleParseError,
    SubtitleParserPort,
)
from ai_ngerti_geopolitik.domain import (
    DomainValidationError,
    FrameTime,
    ProjectState,
    SubtitleTrack,
    SubtitleCue,
)


class SubtitleImportError(ValueError):
    """Actionable application-level failure while importing subtitle source."""


class CommandSession(Protocol):
    @property
    def state(self) -> ProjectState: ...

    def execute(self, batch: CommandBatch) -> ProjectState: ...


def milliseconds_to_frame(milliseconds: int, fps: int) -> int:
    if milliseconds < 0:
        raise SubtitleImportError("subtitle timestamp cannot be negative")
    if fps <= 0:
        raise SubtitleImportError("project FPS must be positive")
    return (milliseconds * fps + 500) // 1000


def build_subtitle_track(
    state: ProjectState,
    source_path: Path,
    parsed: tuple[ParsedSubtitleCue, ...],
) -> SubtitleTrack:
    if not parsed:
        raise SubtitleImportError("SRT does not contain any subtitle cues")
    if state.timeline_end_frame <= 0:
        raise SubtitleImportError("subtitle import requires a non-empty project timeline")

    canonical: list[SubtitleCue] = []
    previous_end = 0
    for position, item in enumerate(parsed, start=1):
        start_frame = milliseconds_to_frame(item.start_milliseconds, state.fps)
        end_frame = milliseconds_to_frame(item.end_milliseconds, state.fps)
        if end_frame <= start_frame:
            raise SubtitleImportError(
                f"SRT cue index {item.index} is shorter than one representable "
                f"frame at {state.fps} fps"
            )
        if start_frame < previous_end:
            raise SubtitleImportError(
                f"SRT cue index {item.index} overlaps after conversion to "
                f"{state.fps} fps"
            )
        if end_frame > state.timeline_end_frame:
            raise SubtitleImportError(
                f"SRT cue index {item.index} ends outside the project timeline"
            )
        try:
            canonical.append(
                SubtitleCue(
                    cue_id=f"SRT-{position:06d}",
                    index=item.index,
                    start=FrameTime(start_frame, state.fps),
                    end=FrameTime(end_frame, state.fps),
                    text=item.text,
                )
            )
        except DomainValidationError as exc:
            raise SubtitleImportError(
                f"SRT cue index {item.index} cannot enter canonical project state"
            ) from exc
        previous_end = end_frame

    try:
        return SubtitleTrack(
            source_ref=str(source_path.resolve()),
            cues=tuple(canonical),
        )
    except DomainValidationError as exc:
        raise SubtitleImportError("SRT cannot enter canonical subtitle state") from exc


@dataclass(slots=True)
class SubtitleImportService:
    parser: SubtitleParserPort

    def import_path(self, session: CommandSession, path: Path) -> SubtitleTrack:
        source = path.expanduser()
        try:
            parsed = self.parser.parse(source)
        except SubtitleParseError:
            raise
        track = build_subtitle_track(session.state, source, parsed)
        batch = CommandBatch(
            batch_id=f"W5-SRT-{session.state.revision + 1:06d}",
            label=f"Import SRT {source.name}",
            actor="manual",
            expected_revision=session.state.revision,
            commands=(SetSubtitleTrackCommand(track),),
        )
        session.execute(batch)
        return track
