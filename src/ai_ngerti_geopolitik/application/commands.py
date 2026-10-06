"""Semantic CommandBus and reversible canonical edit commands."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Protocol

from ai_ngerti_geopolitik.domain import (
    Asset,
    Clip,
    DomainValidationError,
    FrameTime,
    Marker,
    ProjectSettings,
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


def _sorted_clips(track: Track) -> list[Clip]:
    return sorted(track.clips, key=lambda item: item.timeline_start.frames)


def _repack_contiguous(clips: list[Clip], fps: int) -> tuple[Clip, ...]:
    cursor = 0
    packed: list[Clip] = []
    for clip in clips:
        packed.append(replace(clip, timeline_start=FrameTime(cursor, fps)))
        cursor += clip.duration_frames
    return tuple(packed)


@dataclass(frozen=True, slots=True)
class ImportAssetCommand:
    asset: Asset

    def apply(self, state: ProjectState) -> ProjectState:
        if any(item.asset_id == self.asset.asset_id for item in state.assets):
            raise CommandError(f"duplicate asset id: {self.asset.asset_id}")
        if any(item.path_ref == self.asset.path_ref for item in state.assets):
            raise CommandError("duplicate media path in canonical project")
        candidate = replace(state, assets=(*state.assets, self.asset))
        candidate.validate()
        return candidate


@dataclass(frozen=True, slots=True)
class SetAssetAvailabilityCommand:
    asset_id: str
    availability: str

    def apply(self, state: ProjectState) -> ProjectState:
        asset = state.asset(self.asset_id)
        updated = replace(asset, availability=self.availability)
        assets = tuple(updated if item.asset_id == self.asset_id else item for item in state.assets)
        candidate = replace(state, assets=assets)
        candidate.validate()
        return candidate


@dataclass(frozen=True, slots=True)
class UpdateProjectSettingsCommand:
    width: int
    height: int
    fps: int
    aspect_ratio: str

    def apply(self, state: ProjectState) -> ProjectState:
        if self.fps <= 0:
            raise CommandError("project FPS must be positive")
        if self.fps != state.fps and (state.assets or any(track.clips for track in state.tracks)):
            raise CommandError("cannot change FPS after media or timeline content exists")
        candidate = replace(
            state,
            fps=self.fps,
            settings=ProjectSettings(self.width, self.height, self.aspect_ratio),
        )
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
class ReorderClipCommand:
    clip_id: str
    target_index: int
    track_id: str = "V1"

    def apply(self, state: ProjectState) -> ProjectState:
        track = state.track(self.track_id)
        clips = _sorted_clips(track)
        if self.target_index < 0 or self.target_index >= len(clips):
            raise CommandError(f"target index outside track: {self.target_index}")
        source_index = next(
            (index for index, clip in enumerate(clips) if clip.clip_id == self.clip_id),
            None,
        )
        if source_index is None:
            raise CommandError(f"unknown clip: {self.clip_id}")
        clip = clips.pop(source_index)
        clips.insert(self.target_index, clip)
        packed = _repack_contiguous(clips, state.fps)
        return _replace_track(state, replace(track, clips=packed))


@dataclass(frozen=True, slots=True)
class SetClipDurationCommand:
    clip_id: str
    duration_frames: int
    ripple: bool = True

    def apply(self, state: ProjectState) -> ProjectState:
        if self.duration_frames <= 0:
            raise CommandError("clip duration must be positive")
        for track in state.tracks:
            ordered = _sorted_clips(track)
            for index, clip in enumerate(ordered):
                if clip.clip_id != self.clip_id:
                    continue
                asset = state.asset(clip.asset_id)
                new_source_out = clip.source_in.frames + self.duration_frames
                if new_source_out > asset.duration.frames:
                    raise CommandError("clip duration exceeds source media")
                delta = self.duration_frames - clip.duration_frames
                updated = replace(
                    clip,
                    source_out=FrameTime(new_source_out, state.fps),
                )
                ordered[index] = updated
                if self.ripple and delta:
                    for later_index in range(index + 1, len(ordered)):
                        later = ordered[later_index]
                        shifted = later.timeline_start.frames + delta
                        if shifted < 0:
                            raise CommandError("ripple edit would create negative timeline time")
                        ordered[later_index] = replace(
                            later,
                            timeline_start=FrameTime(shifted, state.fps),
                        )
                return _replace_track(state, replace(track, clips=tuple(ordered)))
        raise CommandError(f"unknown clip: {self.clip_id}")


@dataclass(frozen=True, slots=True)
class RemoveClipCommand:
    clip_id: str
    ripple: bool = True

    def apply(self, state: ProjectState) -> ProjectState:
        for track in state.tracks:
            ordered = _sorted_clips(track)
            index = next(
                (position for position, clip in enumerate(ordered) if clip.clip_id == self.clip_id),
                None,
            )
            if index is None:
                continue
            removed = ordered.pop(index)
            if self.ripple:
                for later_index in range(index, len(ordered)):
                    later = ordered[later_index]
                    ordered[later_index] = replace(
                        later,
                        timeline_start=FrameTime(
                            later.timeline_start.frames - removed.duration_frames,
                            state.fps,
                        ),
                    )
            candidate = _replace_track(state, replace(track, clips=tuple(ordered)))
            valid_markers = tuple(
                marker
                for marker in candidate.markers
                if marker.frame.frames < candidate.timeline_end_frame
            )
            if valid_markers != candidate.markers:
                candidate = replace(candidate, markers=valid_markers)
                candidate.validate()
            return candidate
        raise CommandError(f"unknown clip: {self.clip_id}")


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
                    enabled=clip.enabled,
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
            raise CommandError("canonical trim currently supports right edge only")
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
class AddMarkerCommand:
    marker: Marker

    def apply(self, state: ProjectState) -> ProjectState:
        if any(item.marker_id == self.marker.marker_id for item in state.markers):
            raise CommandError(f"duplicate marker id: {self.marker.marker_id}")
        candidate = replace(state, markers=(*state.markers, self.marker))
        candidate.validate()
        return candidate


@dataclass(frozen=True, slots=True)
class UpdateMarkerCommand:
    marker_id: str
    frame: FrameTime
    label: str
    marker_type: str = "marker"

    def apply(self, state: ProjectState) -> ProjectState:
        state.marker(self.marker_id)
        updated = Marker(self.marker_id, self.frame, self.label, self.marker_type)
        markers = tuple(
            updated if marker.marker_id == self.marker_id else marker for marker in state.markers
        )
        candidate = replace(state, markers=markers)
        candidate.validate()
        return candidate


@dataclass(frozen=True, slots=True)
class DeleteMarkerCommand:
    marker_id: str

    def apply(self, state: ProjectState) -> ProjectState:
        state.marker(self.marker_id)
        markers = tuple(marker for marker in state.markers if marker.marker_id != self.marker_id)
        candidate = replace(state, markers=markers)
        candidate.validate()
        return candidate


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

    @property
    def can_undo(self) -> bool:
        return bool(self._undo)

    @property
    def can_redo(self) -> bool:
        return bool(self._redo)

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
