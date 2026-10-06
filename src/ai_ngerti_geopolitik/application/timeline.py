"""Canonical timeline interaction owner for SF-STEP 11 W2."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from ai_ngerti_geopolitik.application.commands import (
    AddMarkerCommand,
    AddTrackCommand,
    Command,
    CommandBatch,
    CommandBus,
    DeleteMarkerCommand,
    DeleteTrackCommand,
    DuplicateClipCommand,
    MoveClipCommand,
    RemoveClipCommand,
    RenameTrackCommand,
    ReorderClipCommand,
    ReorderTrackCommand,
    SetClipDurationCommand,
    SetTrackStateCommand,
    SplitClipCommand,
    TrimClipCommand,
    UpdateMarkerCommand,
)
from ai_ngerti_geopolitik.application.playback import PlaybackController, PlaybackSnapshot
from ai_ngerti_geopolitik.application.ui_intents import UiIntent, UiIntentType
from ai_ngerti_geopolitik.domain import FrameTime, Marker, ProjectState


class TimelineError(RuntimeError):
    pass


class FollowMode(StrEnum):
    OFF = "off"
    ON = "on"
    SMOOTH = "smooth"


@dataclass(frozen=True, slots=True)
class TimelineRange:
    in_frame: int
    out_frame: int

    def __post_init__(self) -> None:
        if self.in_frame < 0:
            raise TimelineError("selection IN must be non-negative")
        if self.out_frame <= self.in_frame:
            raise TimelineError("selection OUT must be after IN")


@dataclass(frozen=True, slots=True)
class SnapResult:
    requested_frame: int
    resolved_frame: int
    snapped: bool
    target: str | None


@dataclass(frozen=True, slots=True)
class TimelineInteractionSnapshot:
    project_revision: int
    selected_clip_id: str | None
    playhead_frame: int
    selection: TimelineRange | None
    snap_enabled: bool
    snap_threshold_frames: int
    zoom: float
    follow_mode: FollowMode
    follow_suspended: bool


class TimelineController:
    def __init__(
        self,
        bus: CommandBus,
        playback: PlaybackController,
        *,
        snap_threshold_frames: int = 3,
    ) -> None:
        if snap_threshold_frames < 0:
            raise TimelineError("snap threshold must be non-negative")
        self.bus = bus
        self.playback = playback
        self.selected_clip_id: str | None = None
        self.selection: TimelineRange | None = None
        self.snap_enabled = True
        self.snap_threshold_frames = snap_threshold_frames
        self.zoom = 1.0
        self.follow_mode = FollowMode.ON
        self.follow_suspended = False

    @property
    def state(self) -> ProjectState:
        return self.bus.state

    @property
    def snapshot(self) -> TimelineInteractionSnapshot:
        playback = self.playback.snapshot
        return TimelineInteractionSnapshot(
            project_revision=self.state.revision,
            selected_clip_id=self.selected_clip_id,
            playhead_frame=playback.frame,
            selection=self.selection,
            snap_enabled=self.snap_enabled,
            snap_threshold_frames=self.snap_threshold_frames,
            zoom=self.zoom,
            follow_mode=self.follow_mode,
            follow_suspended=self.follow_suspended,
        )

    def _execute(self, label: str, command: Command) -> ProjectState:
        self.playback.prepare_edit()
        state = self.bus.execute(
            CommandBatch(
                batch_id=f"W2-{self.state.revision + 1:06d}",
                label=label,
                actor="manual",
                expected_revision=self.state.revision,
                commands=(command,),
            )
        )
        self._clamp_selection()
        return state

    def _clamp_selection(self) -> None:
        if self.selection is None:
            return
        end = self.state.timeline_end_frame
        if end <= 1:
            self.selection = None
            return
        if self.selection.in_frame >= end - 1:
            self.selection = None
            return
        if self.selection.out_frame > end:
            self.selection = TimelineRange(self.selection.in_frame, end)

    def select_clip(self, clip_id: str | None) -> TimelineInteractionSnapshot:
        if clip_id is not None:
            self.state.clip(clip_id)
        self.selected_clip_id = clip_id
        return self.snapshot

    def seek(self, frame: int) -> PlaybackSnapshot:
        self.follow_suspended = False
        return self.playback.seek(frame)

    def scrub(self, frame: int) -> PlaybackSnapshot:
        self.follow_suspended = True
        return self.playback.scrub(frame)

    def play(self) -> PlaybackSnapshot:
        self.follow_suspended = False
        return self.playback.play()

    def pause(self) -> PlaybackSnapshot:
        return self.playback.pause()

    def reorder_selected(self, target_index: int) -> ProjectState:
        if self.selected_clip_id is None:
            raise TimelineError("no clip selected")
        return self._execute(
            "Reorder clip",
            ReorderClipCommand(self.selected_clip_id, target_index),
        )

    def set_selected_duration(self, duration_frames: int) -> ProjectState:
        if self.selected_clip_id is None:
            raise TimelineError("no clip selected")
        return self._execute(
            "Set clip duration",
            SetClipDurationCommand(self.selected_clip_id, duration_frames, ripple=True),
        )

    def _next_clip_id(self) -> str:
        numbers: list[int] = []
        for track in self.state.tracks:
            for clip in track.clips:
                if clip.clip_id.startswith("C") and clip.clip_id[1:].isdigit():
                    numbers.append(int(clip.clip_id[1:]))
        return f"C{max(numbers, default=0) + 1:03d}"

    def split_selected(self, right_clip_id: str | None = None) -> ProjectState:
        if self.selected_clip_id is None:
            raise TimelineError("no clip selected")
        frame = self.playback.snapshot.frame
        new_clip_id = right_clip_id or self._next_clip_id()
        state = self._execute(
            "Split clip",
            SplitClipCommand(self.selected_clip_id, frame, new_clip_id),
        )
        self.selected_clip_id = new_clip_id
        return state

    def remove_selected(self) -> ProjectState:
        if self.selected_clip_id is None:
            raise TimelineError("no clip selected")
        clip_id = self.selected_clip_id
        state = self._execute("Remove clip", RemoveClipCommand(clip_id, ripple=True))
        self.selected_clip_id = None
        return state

    def duplicate_selected(
        self,
        new_clip_id: str | None = None,
        *,
        target_track_id: str | None = None,
        target_frame: int | None = None,
    ) -> ProjectState:
        if self.selected_clip_id is None:
            raise TimelineError("no clip selected")
        source_track = next(
            track
            for track in self.state.tracks
            if any(clip.clip_id == self.selected_clip_id for clip in track.clips)
        )
        target_id = target_track_id or source_track.track_id
        target_track = self.state.track(target_id)
        resolved_frame = (
            max((clip.timeline_end_frame for clip in target_track.clips), default=0)
            if target_frame is None
            else target_frame
        )
        resolved_id = new_clip_id or self._next_clip_id()
        state = self._execute(
            "Duplicate clip",
            DuplicateClipCommand(
                self.selected_clip_id,
                resolved_id,
                target_id,
                resolved_frame,
            ),
        )
        self.selected_clip_id = resolved_id
        return state

    def move_selected(self, target_track_id: str, target_frame: int) -> ProjectState:
        if self.selected_clip_id is None:
            raise TimelineError("no clip selected")
        return self._execute(
            "Move clip",
            MoveClipCommand(self.selected_clip_id, target_track_id, target_frame),
        )

    def trim_selected(
        self,
        trim_frames: int,
        *,
        edge: str = "right",
        ripple: bool = False,
    ) -> ProjectState:
        if self.selected_clip_id is None:
            raise TimelineError("no clip selected")
        return self._execute(
            "Trim clip",
            TrimClipCommand(self.selected_clip_id, trim_frames, edge, ripple),
        )

    def add_track(self, track_id: str, name: str = "", order: int | None = None) -> ProjectState:
        return self._execute("Add track", AddTrackCommand(track_id, name, order))

    def delete_track(self, track_id: str) -> ProjectState:
        return self._execute("Delete track", DeleteTrackCommand(track_id))

    def rename_track(self, track_id: str, name: str) -> ProjectState:
        return self._execute("Rename track", RenameTrackCommand(track_id, name))

    def reorder_track(self, track_id: str, target_index: int) -> ProjectState:
        return self._execute("Reorder track", ReorderTrackCommand(track_id, target_index))

    def set_track_state(
        self,
        track_id: str,
        *,
        locked: bool | None = None,
        muted: bool | None = None,
        visible: bool | None = None,
    ) -> ProjectState:
        return self._execute(
            "Set track state",
            SetTrackStateCommand(track_id, locked, muted, visible),
        )

    def set_in(self, frame: int | None = None) -> TimelineRange | None:
        end = self.state.timeline_end_frame
        if end <= 1:
            raise TimelineError("timeline too short for an IN/OUT range")
        value = self.playback.snapshot.frame if frame is None else frame
        if value < 0 or value >= end - 1:
            raise TimelineError("selection IN outside timeline")
        out_frame = self.selection.out_frame if self.selection is not None else end
        if out_frame <= value:
            out_frame = end
        self.selection = TimelineRange(value, out_frame)
        return self.selection

    def set_out(self, frame: int | None = None) -> TimelineRange:
        end = self.state.timeline_end_frame
        if end <= 1:
            raise TimelineError("timeline too short for an IN/OUT range")
        value = self.playback.snapshot.frame + 1 if frame is None else frame
        if value <= 0 or value > end:
            raise TimelineError("selection OUT outside timeline")
        in_frame = self.selection.in_frame if self.selection is not None else 0
        self.selection = TimelineRange(in_frame, value)
        return self.selection

    def clear_range(self) -> None:
        self.selection = None

    def _next_marker_id(self) -> str:
        numbers = [
            int(marker.marker_id[1:])
            for marker in self.state.markers
            if marker.marker_id.startswith("M") and marker.marker_id[1:].isdigit()
        ]
        return f"M{max(numbers, default=0) + 1:03d}"

    def add_marker(
        self,
        marker_id: str | None,
        label: str,
        *,
        frame: int | None = None,
        marker_type: str = "marker",
    ) -> ProjectState:
        value = self.playback.snapshot.frame if frame is None else frame
        resolved_id = marker_id or self._next_marker_id()
        marker = Marker(resolved_id, FrameTime(value, self.state.fps), label, marker_type)
        return self._execute("Add marker", AddMarkerCommand(marker))

    def update_marker(
        self,
        marker_id: str,
        label: str,
        *,
        frame: int | None = None,
        marker_type: str = "marker",
    ) -> ProjectState:
        current = self.state.marker(marker_id)
        value = current.frame.frames if frame is None else frame
        return self._execute(
            "Update marker",
            UpdateMarkerCommand(
                marker_id,
                FrameTime(value, self.state.fps),
                label,
                marker_type,
            ),
        )

    def delete_marker(self, marker_id: str) -> ProjectState:
        return self._execute("Delete marker", DeleteMarkerCommand(marker_id))

    def set_snap(self, enabled: bool, *, threshold_frames: int | None = None) -> None:
        if threshold_frames is not None:
            if threshold_frames < 0:
                raise TimelineError("snap threshold must be non-negative")
            self.snap_threshold_frames = threshold_frames
        self.snap_enabled = enabled

    def snap_frame(self, frame: int, *, bypass: bool = False) -> SnapResult:
        end = self.state.timeline_end_frame
        if frame < 0 or (end > 0 and frame > end):
            raise TimelineError("snap candidate outside timeline")
        if bypass or not self.snap_enabled:
            return SnapResult(frame, frame, False, None)

        targets: list[tuple[int, str]] = [(0, "timeline_start")]
        for track in self.state.tracks:
            for clip in track.clips:
                targets.append((clip.timeline_start.frames, f"{clip.clip_id}:start"))
                targets.append((clip.timeline_end_frame, f"{clip.clip_id}:end"))
        for marker in self.state.markers:
            targets.append((marker.frame.frames, f"{marker.marker_id}:marker"))

        resolved = min(
            targets,
            key=lambda item: (abs(item[0] - frame), item[0], item[1]),
        )
        if abs(resolved[0] - frame) <= self.snap_threshold_frames:
            return SnapResult(frame, resolved[0], True, resolved[1])
        return SnapResult(frame, frame, False, None)

    def set_zoom(self, zoom: float) -> float:
        if not 0.25 <= zoom <= 8.0:
            raise TimelineError("timeline zoom must be between 0.25 and 8.0")
        self.zoom = zoom
        return self.zoom

    def set_follow_mode(self, mode: FollowMode | str) -> FollowMode:
        self.follow_mode = FollowMode(mode)
        self.follow_suspended = False
        return self.follow_mode

    def manual_scroll(self) -> None:
        if self.follow_mode is not FollowMode.OFF:
            self.follow_suspended = True

    def resume_follow(self) -> None:
        self.follow_suspended = False


class TimelineIntentRouter:
    """Translate frozen-editor UI intents into canonical W2 operations."""

    def __init__(self, controller: TimelineController) -> None:
        self.controller = controller
        self.last_result: object | None = None

    @staticmethod
    def _payload(intent: UiIntent) -> dict[str, str]:
        return dict(intent.payload)

    @staticmethod
    def _required(data: dict[str, str], key: str) -> str:
        value = data.get(key)
        if value is None or value == "":
            raise TimelineError(f"{key} is required")
        return value

    def __call__(self, intent: UiIntent) -> None:
        data = self._payload(intent)
        if intent.kind is UiIntentType.PLAYBACK_PLAY:
            self.last_result = self.controller.play()
        elif intent.kind is UiIntentType.PLAYBACK_PAUSE:
            self.last_result = self.controller.pause()
        elif intent.kind is UiIntentType.PLAYBACK_SEEK:
            if "frame" in data:
                target = int(data["frame"])
            elif "delta" in data:
                end = self.controller.state.timeline_end_frame
                if end <= 0:
                    raise TimelineError("timeline is empty")
                current = self.controller.playback.snapshot.frame
                target = max(0, min(end - 1, current + int(data["delta"])))
            else:
                raise TimelineError("frame or delta is required")
            self.last_result = self.controller.scrub(target)
        elif intent.kind is UiIntentType.SELECT_CLIP:
            self.last_result = self.controller.select_clip(self._required(data, "clip_id"))
        elif intent.kind is UiIntentType.TIMELINE_REORDER:
            self.last_result = self.controller.reorder_selected(
                int(self._required(data, "target_index"))
            )
        elif intent.kind is UiIntentType.TIMELINE_SET_DURATION:
            self.last_result = self.controller.set_selected_duration(
                int(self._required(data, "duration_frames"))
            )
        elif intent.kind is UiIntentType.TIMELINE_SPLIT:
            self.last_result = self.controller.split_selected(data.get("right_clip_id"))
        elif intent.kind is UiIntentType.TIMELINE_DELETE:
            self.last_result = self.controller.remove_selected()
        elif intent.kind is UiIntentType.TIMELINE_DUPLICATE:
            self.last_result = self.controller.duplicate_selected(
                data.get("new_clip_id"),
                target_track_id=data.get("target_track_id"),
                target_frame=int(data["target_frame"]) if "target_frame" in data else None,
            )
        elif intent.kind is UiIntentType.TIMELINE_MOVE:
            self.last_result = self.controller.move_selected(
                self._required(data, "target_track_id"),
                int(self._required(data, "target_frame")),
            )
        elif intent.kind is UiIntentType.TIMELINE_TRIM:
            self.last_result = self.controller.trim_selected(
                int(self._required(data, "trim_frames")),
                edge=data.get("edge", "right"),
                ripple=data.get("ripple", "false").lower() == "true",
            )
        elif intent.kind is UiIntentType.TIMELINE_ADD_TRACK:
            self.last_result = self.controller.add_track(
                self._required(data, "track_id"),
                data.get("name", ""),
                int(data["order"]) if "order" in data else None,
            )
        elif intent.kind is UiIntentType.TIMELINE_DELETE_TRACK:
            self.last_result = self.controller.delete_track(self._required(data, "track_id"))
        elif intent.kind is UiIntentType.TIMELINE_RENAME_TRACK:
            self.last_result = self.controller.rename_track(
                self._required(data, "track_id"),
                self._required(data, "name"),
            )
        elif intent.kind is UiIntentType.TIMELINE_REORDER_TRACK:
            self.last_result = self.controller.reorder_track(
                self._required(data, "track_id"),
                int(self._required(data, "target_index")),
            )
        elif intent.kind is UiIntentType.TIMELINE_SET_TRACK_STATE:
            self.last_result = self.controller.set_track_state(
                self._required(data, "track_id"),
                locked=(
                    data["locked"].lower() == "true"
                    if "locked" in data
                    else None
                ),
                muted=(
                    data["muted"].lower() == "true"
                    if "muted" in data
                    else None
                ),
                visible=(
                    data["visible"].lower() == "true"
                    if "visible" in data
                    else None
                ),
            )
        elif intent.kind is UiIntentType.TIMELINE_SET_IN:
            self.last_result = self.controller.set_in(
                int(data["frame"]) if "frame" in data else None
            )
        elif intent.kind is UiIntentType.TIMELINE_SET_OUT:
            self.last_result = self.controller.set_out(
                int(data["frame"]) if "frame" in data else None
            )
        elif intent.kind is UiIntentType.TIMELINE_CLEAR_RANGE:
            self.controller.clear_range()
            self.last_result = None
        elif intent.kind is UiIntentType.TIMELINE_ADD_MARKER:
            self.last_result = self.controller.add_marker(
                data.get("marker_id"),
                data.get("label", "Marker"),
                frame=int(data["frame"]) if "frame" in data else None,
            )
        elif intent.kind is UiIntentType.TIMELINE_SET_SNAP:
            enabled = self._required(data, "enabled").lower() == "true"
            threshold = int(data["threshold"]) if "threshold" in data else None
            self.controller.set_snap(enabled, threshold_frames=threshold)
            self.last_result = self.controller.snapshot
        elif intent.kind is UiIntentType.TIMELINE_SET_ZOOM:
            self.last_result = self.controller.set_zoom(float(self._required(data, "zoom")))
        elif intent.kind is UiIntentType.TIMELINE_SET_FOLLOW:
            self.last_result = self.controller.set_follow_mode(self._required(data, "mode"))
        else:
            raise TimelineError(f"unsupported W2 timeline intent: {intent.kind}")
