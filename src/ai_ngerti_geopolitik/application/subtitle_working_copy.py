"""S11 W5-003 subtitle cue working-copy and safe save-copy flow."""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Protocol

from ai_ngerti_geopolitik.application.commands import (
    CommandBatch,
    SetSubtitleTrackCommand,
)
from ai_ngerti_geopolitik.application.ports import (
    ParsedSubtitleCue,
    SubtitleWriteError,
    SubtitleWriterPort,
)
from ai_ngerti_geopolitik.domain import (
    DomainValidationError,
    FrameTime,
    ProjectState,
    SubtitleCue,
    SubtitleTrack,
)


class SubtitleWorkingCopyError(ValueError):
    """Invalid edit, unsafe discard, or unsafe save-copy request."""


class DirtySubtitleWorkingCopyError(SubtitleWorkingCopyError):
    """Raised when dirty edits would be discarded without an explicit choice."""


class CommandSession(Protocol):
    @property
    def state(self) -> ProjectState: ...

    def execute(self, batch: CommandBatch) -> ProjectState: ...


def _cue_to_parsed(cue: SubtitleCue) -> ParsedSubtitleCue:
    return ParsedSubtitleCue(
        index=cue.index,
        start_milliseconds=(cue.start.frames * 1000 + cue.start.fps // 2) // cue.start.fps,
        end_milliseconds=(cue.end.frames * 1000 + cue.end.fps // 2) // cue.end.fps,
        text=cue.text,
    )


def _validate_editable_cues(cues: list[SubtitleCue]) -> None:
    if not cues:
        raise SubtitleWorkingCopyError("subtitle working copy requires at least one cue")

    cue_ids = [cue.cue_id for cue in cues]
    if len(cue_ids) != len(set(cue_ids)):
        raise SubtitleWorkingCopyError("subtitle working copy contains duplicate cue ids")

    indexes = [cue.index for cue in cues]
    if len(indexes) != len(set(indexes)):
        raise SubtitleWorkingCopyError("subtitle working copy contains duplicate cue indexes")

    chronological = sorted(cues, key=lambda cue: (cue.start.frames, cue.end.frames))
    previous_end = -1
    for cue in chronological:
        if cue.start.frames < previous_end:
            raise SubtitleWorkingCopyError("subtitle edit would create overlapping cues")
        previous_end = cue.end.frames


def _next_edit_id(cues: list[SubtitleCue]) -> str:
    used = {cue.cue_id for cue in cues}
    number = 1
    while True:
        candidate = f"EDIT-{number:06d}"
        if candidate not in used:
            return candidate
        number += 1


class SubtitleWorkingCopy:
    """Mutable local editor state that does not mutate ProjectState while typing."""

    def __init__(self, track: SubtitleTrack) -> None:
        self._baseline = track
        self._cues = list(track.cues)
        self._selected_cue_id: str | None = track.cues[0].cue_id
        _validate_editable_cues(self._cues)

    @property
    def source_ref(self) -> str:
        return self._baseline.source_ref

    @property
    def cues(self) -> tuple[SubtitleCue, ...]:
        return tuple(self._cues)

    @property
    def selected_cue_id(self) -> str | None:
        return self._selected_cue_id

    @property
    def selected(self) -> SubtitleCue | None:
        if self._selected_cue_id is None:
            return None
        return next(
            (cue for cue in self._cues if cue.cue_id == self._selected_cue_id),
            None,
        )

    @property
    def dirty(self) -> bool:
        return tuple(self._cues) != self._baseline.cues

    def select(self, cue_id: str) -> SubtitleCue:
        cue = next((item for item in self._cues if item.cue_id == cue_id), None)
        if cue is None:
            raise SubtitleWorkingCopyError(f"unknown subtitle cue: {cue_id}")
        self._selected_cue_id = cue_id
        return cue

    def edit_selected(
        self,
        *,
        text: str | None = None,
        start_frame: int | None = None,
        end_frame: int | None = None,
    ) -> SubtitleCue:
        cue = self.selected
        if cue is None:
            raise SubtitleWorkingCopyError("no subtitle cue is selected")
        candidate = replace(
            cue,
            text=cue.text if text is None else text,
            start=cue.start if start_frame is None else FrameTime(start_frame, cue.start.fps),
            end=cue.end if end_frame is None else FrameTime(end_frame, cue.end.fps),
        )
        try:
            candidate.__post_init__()
        except DomainValidationError as exc:
            raise SubtitleWorkingCopyError(str(exc)) from exc

        position = self._cues.index(cue)
        updated = list(self._cues)
        updated[position] = candidate
        _validate_editable_cues(updated)
        self._cues = updated
        return candidate

    def insert_after_selected(
        self,
        *,
        start_frame: int,
        end_frame: int,
        text: str,
        cue_id: str | None = None,
        index: int | None = None,
    ) -> SubtitleCue:
        selected = self.selected
        if selected is None:
            raise SubtitleWorkingCopyError("no subtitle cue is selected")
        new_id = cue_id or _next_edit_id(self._cues)
        new_index = index if index is not None else max(cue.index for cue in self._cues) + 1
        try:
            new_cue = SubtitleCue(
                cue_id=new_id,
                index=new_index,
                start=FrameTime(start_frame, selected.start.fps),
                end=FrameTime(end_frame, selected.end.fps),
                text=text,
            )
        except DomainValidationError as exc:
            raise SubtitleWorkingCopyError(str(exc)) from exc

        position = self._cues.index(selected) + 1
        updated = list(self._cues)
        updated.insert(position, new_cue)
        _validate_editable_cues(updated)
        self._cues = updated
        self._selected_cue_id = new_cue.cue_id
        return new_cue

    def delete_selected(self) -> SubtitleCue:
        selected = self.selected
        if selected is None:
            raise SubtitleWorkingCopyError("no subtitle cue is selected")
        if len(self._cues) == 1:
            raise SubtitleWorkingCopyError("cannot delete the last subtitle cue")

        position = self._cues.index(selected)
        removed = self._cues.pop(position)
        next_position = min(position, len(self._cues) - 1)
        self._selected_cue_id = self._cues[next_position].cue_id
        return removed

    def split_selected(
        self,
        *,
        split_frame: int,
        left_text: str,
        right_text: str,
        right_cue_id: str | None = None,
    ) -> tuple[SubtitleCue, SubtitleCue]:
        selected = self.selected
        if selected is None:
            raise SubtitleWorkingCopyError("no subtitle cue is selected")
        if not selected.start.frames < split_frame < selected.end.frames:
            raise SubtitleWorkingCopyError("subtitle split frame must be inside the selected cue")

        new_id = right_cue_id or _next_edit_id(self._cues)
        right_index = max(cue.index for cue in self._cues) + 1
        try:
            left = replace(
                selected,
                end=FrameTime(split_frame, selected.end.fps),
                text=left_text,
                word_timings=(),
            )
            right = SubtitleCue(
                cue_id=new_id,
                index=right_index,
                start=FrameTime(split_frame, selected.start.fps),
                end=selected.end,
                text=right_text,
            )
            left.__post_init__()
        except DomainValidationError as exc:
            raise SubtitleWorkingCopyError(str(exc)) from exc

        position = self._cues.index(selected)
        updated = list(self._cues)
        updated[position : position + 1] = [left, right]
        _validate_editable_cues(updated)
        self._cues = updated
        self._selected_cue_id = right.cue_id
        return left, right

    def merge_selected_with_next(self, *, merged_text: str) -> SubtitleCue:
        selected = self.selected
        if selected is None:
            raise SubtitleWorkingCopyError("no subtitle cue is selected")
        position = self._cues.index(selected)
        if position + 1 >= len(self._cues):
            raise SubtitleWorkingCopyError("selected subtitle cue has no next cue to merge")

        right = self._cues[position + 1]
        if right.start.frames < selected.end.frames:
            raise SubtitleWorkingCopyError("subtitle merge requires non-overlapping adjacent cues")
        try:
            merged = replace(
                selected,
                end=right.end,
                text=merged_text,
                word_timings=(),
            )
            merged.__post_init__()
        except DomainValidationError as exc:
            raise SubtitleWorkingCopyError(str(exc)) from exc

        updated = list(self._cues)
        updated[position : position + 2] = [merged]
        _validate_editable_cues(updated)
        self._cues = updated
        self._selected_cue_id = merged.cue_id
        return merged

    def sort_by_time(self) -> None:
        self._cues = sorted(
            self._cues,
            key=lambda cue: (cue.start.frames, cue.end.frames),
        )

    def normalize_indexes(self, *, start: int = 1) -> None:
        if start <= 0:
            raise SubtitleWorkingCopyError("subtitle index normalization must start above zero")
        self._cues = [
            replace(cue, index=start + position) for position, cue in enumerate(self._cues)
        ]

    def guard_discard(self) -> None:
        if self.dirty:
            raise DirtySubtitleWorkingCopyError(
                "subtitle working copy has unsaved changes; explicit discard is required"
            )

    def reload(self, track: SubtitleTrack, *, discard_dirty: bool = False) -> None:
        if self.dirty and not discard_dirty:
            self.guard_discard()
        self._baseline = track
        self._cues = list(track.cues)
        self._selected_cue_id = track.cues[0].cue_id
        _validate_editable_cues(self._cues)

    def build_track(self, *, source_ref: str | None = None) -> SubtitleTrack:
        try:
            return SubtitleTrack(
                source_ref=self.source_ref if source_ref is None else source_ref,
                cues=tuple(self._cues),
                style=self._baseline.style,
                animation=self._baseline.animation,
                enabled=self._baseline.enabled,
            )
        except DomainValidationError as exc:
            raise SubtitleWorkingCopyError(
                "subtitle working copy must be explicitly sorted/validated before save"
            ) from exc

    def accept_committed_track(self, track: SubtitleTrack) -> None:
        self._baseline = track
        self._cues = list(track.cues)
        self._selected_cue_id = track.cues[0].cue_id


@dataclass(slots=True)
class SubtitleWorkingCopyService:
    writer: SubtitleWriterPort

    @staticmethod
    def suggest_copy_path(working: SubtitleWorkingCopy) -> Path:
        source = Path(working.source_ref).expanduser()
        base = source.with_name(f"{source.stem}.edited.srt")
        if not base.exists():
            return base
        number = 2
        while True:
            candidate = source.with_name(f"{source.stem}.edited-{number}.srt")
            if not candidate.exists():
                return candidate
            number += 1

    def save_copy_and_commit(
        self,
        session: CommandSession,
        working: SubtitleWorkingCopy,
        destination: Path | None = None,
    ) -> Path:
        output = (
            self.suggest_copy_path(working) if destination is None else destination.expanduser()
        )
        source = Path(working.source_ref).expanduser()
        if output.suffix.lower() != ".srt":
            raise SubtitleWorkingCopyError("subtitle save-copy destination must use .srt")
        if output.resolve() == source.resolve():
            raise SubtitleWorkingCopyError(
                "source SRT cannot be overwritten by save-copy; choose a new destination"
            )
        if output.exists():
            raise SubtitleWorkingCopyError(
                "subtitle save-copy destination already exists; choose a new destination"
            )

        track = working.build_track(source_ref=str(output.resolve()))
        parsed = tuple(_cue_to_parsed(cue) for cue in track.cues)
        try:
            self.writer.write_copy(output, parsed)
        except SubtitleWriteError:
            raise

        batch = CommandBatch(
            batch_id=f"W5-EDIT-{session.state.revision + 1:06d}",
            label=f"Commit edited SRT {output.name}",
            actor="manual",
            expected_revision=session.state.revision,
            commands=(SetSubtitleTrackCommand(track),),
        )
        session.execute(batch)
        working.accept_committed_track(track)
        return output
