"""Application-facing UI intents for SF-STEP 09.

STEP 09 only routes presentation intent. It deliberately does not perform project
mutation, media work, persistence, Gemini calls, or rendering.
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
    SET_LAYOUT = "set_layout"
    SPLIT_CUE = "split_cue"
    MERGE_CUE = "merge_cue"
    RELOAD_SRT = "reload_srt"


@dataclass(frozen=True, slots=True)
class UiIntent:
    kind: UiIntentType
    payload: tuple[tuple[str, str], ...] = ()


class UiIntentSink(Protocol):
    def __call__(self, intent: UiIntent) -> None: ...


class RecordingIntentSink:
    """Small deterministic sink used by the STEP 09 shell and Qt tests."""

    def __init__(self) -> None:
        self.intents: list[UiIntent] = []

    def __call__(self, intent: UiIntent) -> None:
        self.intents.append(intent)
