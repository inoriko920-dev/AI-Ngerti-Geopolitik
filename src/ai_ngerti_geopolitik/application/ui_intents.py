"""Application-facing UI intents.

The presentation layer emits semantic intents only. Product mutation is owned by
application services and the canonical CommandBus.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol


class UiIntentType(StrEnum):
    NEW_PROJECT = "new_project"
    OPEN_PROJECT = "open_project"
    SAVE_PROJECT = "save_project"
    UNDO = "undo"
    REDO = "redo"
    IMPORT_MEDIA = "import_media"
    ADD_TEXT = "add_text"
    RECORD_NARRATION = "record_narration"
    AUTO_AI = "auto_ai"
    OPEN_EXPORT = "open_export"
    OPEN_VALIDATION = "open_validation"
    SELECT_SCENE = "select_scene"
    SELECT_ASSET = "select_asset"
    SELECT_CLIP = "select_clip"
    SET_LAYOUT = "set_layout"
    SPLIT_CUE = "split_cue"
    MERGE_CUE = "merge_cue"
    RELOAD_SRT = "reload_srt"
    PLAYBACK_PLAY = "playback_play"
    PLAYBACK_PAUSE = "playback_pause"
    PLAYBACK_SEEK = "playback_seek"
    TIMELINE_REORDER = "timeline_reorder"
    TIMELINE_SET_DURATION = "timeline_set_duration"
    TIMELINE_SPLIT = "timeline_split"
    TIMELINE_DELETE = "timeline_delete"
    TIMELINE_DUPLICATE = "timeline_duplicate"
    TIMELINE_MOVE = "timeline_move"
    TIMELINE_TRIM = "timeline_trim"
    TIMELINE_ADD_TRACK = "timeline_add_track"
    TIMELINE_DELETE_TRACK = "timeline_delete_track"
    TIMELINE_RENAME_TRACK = "timeline_rename_track"
    TIMELINE_REORDER_TRACK = "timeline_reorder_track"
    TIMELINE_SET_TRACK_STATE = "timeline_set_track_state"
    TIMELINE_SET_IN = "timeline_set_in"
    TIMELINE_SET_OUT = "timeline_set_out"
    TIMELINE_CLEAR_RANGE = "timeline_clear_range"
    TIMELINE_ADD_MARKER = "timeline_add_marker"
    TIMELINE_SET_SNAP = "timeline_set_snap"
    TIMELINE_SET_ZOOM = "timeline_set_zoom"
    TIMELINE_SET_FOLLOW = "timeline_set_follow"
    INSPECTOR_BIND = "inspector_bind"
    PROPERTY_SET_VIDEO = "property_set_video"
    PROPERTY_SET_AUDIO = "property_set_audio"
    PROPERTY_SET_COLOR = "property_set_color"
    PROPERTY_SET_SPEED = "property_set_speed"
    PROPERTY_SET_REVERSE = "property_set_reverse"


@dataclass(frozen=True, slots=True)
class UiIntent:
    kind: UiIntentType
    payload: tuple[tuple[str, str], ...] = ()


class UiIntentSink(Protocol):
    def __call__(self, intent: UiIntent) -> None: ...


class RecordingIntentSink:
    """Small deterministic sink used by the shell and Qt tests."""

    def __init__(self) -> None:
        self.intents: list[UiIntent] = []

    def __call__(self, intent: UiIntent) -> None:
        self.intents.append(intent)
