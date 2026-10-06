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
    TIMELINE_SET_IN = "timeline_set_in"
    TIMELINE_SET_OUT = "timeline_set_out"
    TIMELINE_CLEAR_RANGE = "timeline_clear_range"
    TIMELINE_ADD_MARKER = "timeline_add_marker"


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
