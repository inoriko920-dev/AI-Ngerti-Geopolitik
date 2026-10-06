"""Semantic CommandBus and reversible STEP 10 edit commands."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Protocol

from ai_ngerti_geopolitik.domain import (
    Asset,
    Clip,
    DomainValidationError,
    FrameTime,
    ProjectState,
    Track,
)


class CommandError(RuntimeError):
    pass


class StaleRevisionError(CommandError):
    pass


class Command(Protocol):
    def apply(self, state: ProjectState) -> ProjectState: ...


def _replace_track(state: ProjectState, new_track: Track) -> ProjectState:
    tracks = tuple(
        new_track if track.track_id == new_track.track_id else track for track in state.tracks
    )
    if all(track.track_id != new_track.track_id for track in state.tracks):
        tracks = (*state.tracks, new_track)
    candidate = replace(state, tracks=tracks)
    candidate.validate()
    return candidate


@dataclass(frozen=True, slots=True)
class ImportAssetCommand:
    asset: Asset

    def apply(self, state: ProjectState) -> ProjectState:
        if any(item.asset_id == self.asset.asset_id for item in state.assets):
            raise CommandError(f"duplicate asset id: {self.asset.asset_id}")
        if any(item.path_ref == self.asset.path_ref for item in state.assets):
            raise CommandError("duplicate media path in STEP 10 slice")
        candidate = replace(state, assets=(*state.assets, self.asset))
        candidate.validate()
        return candidate


@dataclass(frozen=True, slots=True)
class AddClipCommand:
    clip: Clip
    track_id: str = "V1"

    def apply(self, state: ProjectState) -> ProjectState:
        state.asset(self.clip.asset_id)
        if any(
            self.clip.clip_id == existing.clip_id
            for track in state.tracks
            for existing in track.clips
        ):
            raise CommandError(f"duplicate clip id: {self.clip.clip_id}")
        try:
            track = state.track(self.track_id)
        except DomainValidationError:
            track = Track(track_id=self.track_id, kind="video", order=0)
        track = replace(track, clips=(*track.clips, self.clip))
        return _replace_track(state, track)


@dataclass(frozen=True, slots=True)
class SplitClipCommand:
    clip_id: str
    split_timeline_frame: int
    right_clip_id: str

    def apply(self, state: ProjectState) -> ProjectState:
        if any(
            self.right_clip_id == existing.clip_id
            for track in state.tracks
            for existing in track.clips
        ):
            raise CommandError(f"duplicate right clip id: {self.right_clip_id}")
        for track in state.tracks:
            for index, clip in enumerate(track.clips):
                if clip.clip_id != self.clip_id:
                    continue
                start = clip.timeline_start.frames
                end = clip.timeline_end_frame
                if not start < self.split_timeline_frame < end:
                    raise CommandError("split point must be inside clip")
                offset = self.split_timeline_frame - start
                split_source_frame = clip.source_in.frames + offset
                left = replace(
                    clip,
                    source_out=FrameTime(split_source_frame, state.fps),
                )
                right = Clip(
                    clip_id=self.right_clip_id,
                    asset_id=clip.asset_id,
                    timeline_start=FrameTime(self.split_timeline_frame, state.fps),
                    source_in=FrameTime(split_source_frame, state.fps),
                    source_out=clip.source_out,
                )
                clips = (*track.clips[:index], left, right, *track.clips[index + 1 :])
                return _replace_track(state, replace(track, clips=clips))
        raise CommandError(f"unknown clip: {self.clip_id}")


@dataclass(frozen=True, slots=True)
class TrimClipCommand:
    clip_id: str
    trim_frames: int
    edge: str = "right"

    def apply(self, state: ProjectState) -> ProjectState:
        if self.edge != "right":
            raise CommandError("STEP 10 canonical trim supports right edge only")
        if self.trim_frames <= 0:
            raise CommandError("trim_frames must be positive")
        for track in state.tracks:
            for index, clip in enumerate(track.clips):
                if clip.clip_id != self.clip_id:
                    continue
                if self.trim_frames >= clip.duration_frames:
                    raise CommandError("trim would remove entire clip")
                trimmed = replace(
                    clip,
                    source_out=FrameTime(
                        clip.source_out.frames - self.trim_frames,
                        state.fps,
                    ),
                )
                clips = (*track.clips[:index], trimmed, *track.clips[index + 1 :])
                return _replace_track(state, replace(track, clips=clips))
        raise CommandError(f"unknown clip: {self.clip_id}")


@dataclass(frozen=True, slots=True)
class CommandBatch:
    batch_id: str
    label: str
    actor: str
    expected_revision: int
    commands: tuple[Command, ...]


@dataclass(frozen=True, slots=True)
class HistoryEntry:
    batch: CommandBatch
    before: ProjectState
    after: ProjectState


class CommandBus:
    def __init__(self, state: ProjectState) -> None:
        state.validate()
        self._state = state
        self._undo: list[HistoryEntry] = []
        self._redo: list[HistoryEntry] = []

    @property
    def state(self) -> ProjectState:
        return self._state

    def execute(self, batch: CommandBatch) -> ProjectState:
        if batch.expected_revision != self._state.revision:
            raise StaleRevisionError(
                f"expected revision {batch.expected_revision}, current {self._state.revision}"
            )
        before = self._state
        working = before
        for command in batch.commands:
            working = command.apply(working)
        working.validate()
        committed = working.with_revision(before.revision + 1)
        self._state = committed
        self._undo.append(HistoryEntry(batch=batch, before=before, after=committed))
        self._redo.clear()
        return committed

    def undo(self) -> ProjectState:
        if not self._undo:
            raise CommandError("nothing to undo")
        entry = self._undo.pop()
        self._redo.append(entry)
        self._state = entry.before.with_revision(self._state.revision + 1)
        return self._state

    def redo(self) -> ProjectState:
        if not self._redo:
            raise CommandError("nothing to redo")
        entry = self._redo.pop()
        self._undo.append(entry)
        self._state = entry.after.with_revision(self._state.revision + 1)
        return self._state

    def replace_loaded_state(self, state: ProjectState) -> ProjectState:
        state.validate()
        self._state = state
        self._undo.clear()
        self._redo.clear()
        return state
