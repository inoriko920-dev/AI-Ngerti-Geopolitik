"""Semantic CommandBus and reversible canonical edit commands."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Protocol

from ai_ngerti_geopolitik.domain import (
    Asset,
    Clip,
    ClipProperties,
    DomainValidationError,
    FrameTime,
    Marker,
    ProjectSettings,
    ProjectState,
    SpeedProperties,
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


def _sorted_tracks(state: ProjectState) -> list[Track]:
    return sorted(state.tracks, key=lambda item: item.order)


def _normalize_track_orders(tracks: list[Track]) -> tuple[Track, ...]:
    return tuple(replace(track, order=index) for index, track in enumerate(tracks))


def _replace_tracks(state: ProjectState, tracks: tuple[Track, ...]) -> ProjectState:
    candidate = replace(state, tracks=tracks)
    candidate.validate()
    return candidate


def _require_track_editable(track: Track) -> None:
    if track.locked:
        raise CommandError(f"track is locked: {track.track_id}")


def _find_clip_location(state: ProjectState, clip_id: str) -> tuple[Track, Clip]:
    for track in state.tracks:
        for clip in track.clips:
            if clip.clip_id == clip_id:
                return track, clip
    raise CommandError(f"unknown clip: {clip_id}")


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
class AddTrackCommand:
    track_id: str
    name: str = ""
    order: int | None = None

    def apply(self, state: ProjectState) -> ProjectState:
        if any(track.track_id == self.track_id for track in state.tracks):
            raise CommandError(f"duplicate track id: {self.track_id}")
        tracks = _sorted_tracks(state)
        target = len(tracks) if self.order is None else self.order
        if target < 0 or target > len(tracks):
            raise CommandError(f"track order outside range: {target}")
        tracks.insert(
            target,
            Track(
                track_id=self.track_id,
                kind="video",
                order=target,
                name=self.name.strip(),
            ),
        )
        return _replace_tracks(state, _normalize_track_orders(tracks))


@dataclass(frozen=True, slots=True)
class DeleteTrackCommand:
    track_id: str

    def apply(self, state: ProjectState) -> ProjectState:
        track = state.track(self.track_id)
        _require_track_editable(track)
        if track.clips:
            raise CommandError("delete track requires an empty track")
        tracks = [item for item in _sorted_tracks(state) if item.track_id != self.track_id]
        return _replace_tracks(state, _normalize_track_orders(tracks))


@dataclass(frozen=True, slots=True)
class RenameTrackCommand:
    track_id: str
    name: str

    def apply(self, state: ProjectState) -> ProjectState:
        track = state.track(self.track_id)
        _require_track_editable(track)
        name = self.name.strip()
        if not name:
            raise CommandError("track name is required")
        return _replace_track(state, replace(track, name=name))


@dataclass(frozen=True, slots=True)
class ReorderTrackCommand:
    track_id: str
    target_index: int

    def apply(self, state: ProjectState) -> ProjectState:
        tracks = _sorted_tracks(state)
        if self.target_index < 0 or self.target_index >= len(tracks):
            raise CommandError(f"target track index outside range: {self.target_index}")
        source_index = next(
            (index for index, track in enumerate(tracks) if track.track_id == self.track_id),
            None,
        )
        if source_index is None:
            raise CommandError(f"unknown track: {self.track_id}")
        track = tracks[source_index]
        _require_track_editable(track)
        tracks.pop(source_index)
        tracks.insert(self.target_index, track)
        return _replace_tracks(state, _normalize_track_orders(tracks))


@dataclass(frozen=True, slots=True)
class SetTrackStateCommand:
    track_id: str
    locked: bool | None = None
    muted: bool | None = None
    visible: bool | None = None

    def apply(self, state: ProjectState) -> ProjectState:
        track = state.track(self.track_id)
        updated = replace(
            track,
            locked=track.locked if self.locked is None else self.locked,
            muted=track.muted if self.muted is None else self.muted,
            visible=track.visible if self.visible is None else self.visible,
        )
        return _replace_track(state, updated)


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
            order = max((item.order for item in state.tracks), default=-1) + 1
            track = Track(track_id=self.track_id, kind="video", order=order)
        _require_track_editable(track)
        track = replace(track, clips=(*track.clips, self.clip))
        return _replace_track(state, track)


@dataclass(frozen=True, slots=True)
class MoveClipCommand:
    clip_id: str
    target_track_id: str
    target_frame: int

    def apply(self, state: ProjectState) -> ProjectState:
        if self.target_frame < 0:
            raise CommandError("target frame must be non-negative")
        source_track, clip = _find_clip_location(state, self.clip_id)
        target_track = state.track(self.target_track_id)
        _require_track_editable(source_track)
        _require_track_editable(target_track)
        moved = replace(clip, timeline_start=FrameTime(self.target_frame, state.fps))
        tracks: list[Track] = []
        for track in state.tracks:
            if source_track.track_id == target_track.track_id == track.track_id:
                clips = tuple(item for item in track.clips if item.clip_id != self.clip_id)
                tracks.append(replace(track, clips=(*clips, moved)))
            elif track.track_id == source_track.track_id:
                tracks.append(
                    replace(
                        track,
                        clips=tuple(item for item in track.clips if item.clip_id != self.clip_id),
                    )
                )
            elif track.track_id == target_track.track_id:
                tracks.append(replace(track, clips=(*track.clips, moved)))
            else:
                tracks.append(track)
        try:
            return _replace_tracks(state, tuple(tracks))
        except DomainValidationError as exc:
            raise CommandError("clip move would create an invalid overlap") from exc


@dataclass(frozen=True, slots=True)
class DuplicateClipCommand:
    clip_id: str
    new_clip_id: str
    target_track_id: str
    target_frame: int

    def apply(self, state: ProjectState) -> ProjectState:
        if self.target_frame < 0:
            raise CommandError("target frame must be non-negative")
        if any(
            existing.clip_id == self.new_clip_id
            for track in state.tracks
            for existing in track.clips
        ):
            raise CommandError(f"duplicate clip id: {self.new_clip_id}")
        _source_track, clip = _find_clip_location(state, self.clip_id)
        target_track = state.track(self.target_track_id)
        _require_track_editable(target_track)
        duplicate = replace(
            clip,
            clip_id=self.new_clip_id,
            timeline_start=FrameTime(self.target_frame, state.fps),
        )
        try:
            return _replace_track(
                state,
                replace(target_track, clips=(*target_track.clips, duplicate)),
            )
        except DomainValidationError as exc:
            raise CommandError("clip duplicate would create an invalid overlap") from exc


@dataclass(frozen=True, slots=True)
class ReorderClipCommand:
    clip_id: str
    target_index: int
    track_id: str = "V1"

    def apply(self, state: ProjectState) -> ProjectState:
        track = state.track(self.track_id)
        _require_track_editable(track)
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
                _require_track_editable(track)
                asset = state.asset(clip.asset_id)
                source_duration = clip.timeline_frames_to_source_frames(self.duration_frames)
                new_source_out = clip.source_in.frames + source_duration
                if new_source_out > asset.duration.frames:
                    raise CommandError("clip duration exceeds source media")
                updated = replace(
                    clip,
                    source_out=FrameTime(new_source_out, state.fps),
                )
                if updated.duration_frames != self.duration_frames:
                    raise CommandError(
                        "requested duration is not exactly representable at current speed"
                    )
                delta = updated.duration_frames - clip.duration_frames
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
            _require_track_editable(track)
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
                _require_track_editable(track)
                start = clip.timeline_start.frames
                end = clip.timeline_end_frame
                if not start < self.split_timeline_frame < end:
                    raise CommandError("split point must be inside clip")
                offset = self.split_timeline_frame - start
                source_offset = clip.timeline_frames_to_source_frames(offset)
                split_source_frame = clip.source_in.frames + source_offset
                if split_source_frame >= clip.source_out.frames:
                    raise CommandError("split point exceeds source media at current speed")
                left = replace(
                    clip,
                    source_out=FrameTime(split_source_frame, state.fps),
                )
                if left.duration_frames != offset:
                    raise CommandError("split point is not exactly representable at current speed")
                right = Clip(
                    clip_id=self.right_clip_id,
                    asset_id=clip.asset_id,
                    timeline_start=FrameTime(self.split_timeline_frame, state.fps),
                    source_in=FrameTime(split_source_frame, state.fps),
                    source_out=clip.source_out,
                    enabled=clip.enabled,
                    properties=clip.properties,
                )
                clips = (*track.clips[:index], left, right, *track.clips[index + 1 :])
                return _replace_track(state, replace(track, clips=clips))
        raise CommandError(f"unknown clip: {self.clip_id}")


@dataclass(frozen=True, slots=True)
class TrimClipCommand:
    clip_id: str
    trim_frames: int
    edge: str = "right"
    ripple: bool = False

    def apply(self, state: ProjectState) -> ProjectState:
        if self.edge not in {"left", "right"}:
            raise CommandError("trim edge must be left or right")
        if self.trim_frames <= 0:
            raise CommandError("trim_frames must be positive")
        for track in state.tracks:
            ordered = _sorted_clips(track)
            for index, clip in enumerate(ordered):
                if clip.clip_id != self.clip_id:
                    continue
                _require_track_editable(track)
                if self.trim_frames >= clip.duration_frames:
                    raise CommandError("trim would remove entire clip")
                source_trim = clip.timeline_frames_to_source_frames(self.trim_frames)
                if source_trim >= clip.source_duration_frames:
                    raise CommandError("trim would remove entire source clip")
                if self.edge == "left":
                    trimmed_source = replace(
                        clip,
                        source_in=FrameTime(
                            clip.source_in.frames + source_trim,
                            state.fps,
                        ),
                    )
                    actual_trim = clip.duration_frames - trimmed_source.duration_frames
                    trimmed = replace(
                        trimmed_source,
                        timeline_start=FrameTime(
                            clip.timeline_start.frames + actual_trim,
                            state.fps,
                        ),
                    )
                else:
                    trimmed = replace(
                        clip,
                        source_out=FrameTime(
                            clip.source_out.frames - source_trim,
                            state.fps,
                        ),
                    )
                    actual_trim = clip.duration_frames - trimmed.duration_frames
                if actual_trim <= 0:
                    raise CommandError("trim is below the current speed frame granularity")
                ordered[index] = trimmed
                if self.ripple and self.edge == "right":
                    for later_index in range(index + 1, len(ordered)):
                        later = ordered[later_index]
                        ordered[later_index] = replace(
                            later,
                            timeline_start=FrameTime(
                                later.timeline_start.frames - actual_trim,
                                state.fps,
                            ),
                        )
                return _replace_track(state, replace(track, clips=tuple(ordered)))
        raise CommandError(f"unknown clip: {self.clip_id}")


@dataclass(frozen=True, slots=True)
class SetClipPropertiesCommand:
    clip_id: str
    properties: ClipProperties

    def apply(self, state: ProjectState) -> ProjectState:
        track, clip = _find_clip_location(state, self.clip_id)
        _require_track_editable(track)
        if self.properties.speed != clip.properties.speed:
            raise CommandError("speed changes must use SetClipSpeedCommand")
        updated = replace(clip, properties=self.properties)
        return _replace_track(
            state,
            replace(
                track,
                clips=tuple(
                    updated if item.clip_id == self.clip_id else item for item in track.clips
                ),
            ),
        )


@dataclass(frozen=True, slots=True)
class SetClipSpeedCommand:
    clip_id: str
    rate_percent: int
    ripple: bool = True

    def apply(self, state: ProjectState) -> ProjectState:
        track, clip = _find_clip_location(state, self.clip_id)
        _require_track_editable(track)
        speed = SpeedProperties(self.rate_percent)
        properties = replace(clip.properties, speed=speed)
        updated = replace(clip, properties=properties)
        delta = updated.duration_frames - clip.duration_frames
        ordered = _sorted_clips(track)
        index = next(
            position for position, item in enumerate(ordered) if item.clip_id == self.clip_id
        )
        ordered[index] = updated
        if self.ripple and delta:
            for later_index in range(index + 1, len(ordered)):
                later = ordered[later_index]
                ordered[later_index] = replace(
                    later,
                    timeline_start=FrameTime(
                        later.timeline_start.frames + delta,
                        state.fps,
                    ),
                )
        try:
            return _replace_track(state, replace(track, clips=tuple(ordered)))
        except DomainValidationError as exc:
            raise CommandError("speed change would create an invalid timeline") from exc


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
