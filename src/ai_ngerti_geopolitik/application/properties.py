"""SF-STEP 11 W3 property editing owner.

All mutations flow through the existing canonical CommandBus. Presentation emits
semantic intents and never mutates ProjectState or engine objects directly.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import StrEnum

from ai_ngerti_geopolitik.application.commands import (
    CommandBatch,
    CommandBus,
    SetClipPropertiesCommand,
    SetClipSpeedCommand,
)
from ai_ngerti_geopolitik.application.playback import PlaybackController
from ai_ngerti_geopolitik.application.ui_intents import UiIntent, UiIntentType
from ai_ngerti_geopolitik.domain import (
    AudioProperties,
    ClipProperties,
    ColorProperties,
    ProjectState,
    VideoProperties,
)


class PropertyEditError(RuntimeError):
    pass


class InspectorTargetType(StrEnum):
    NONE = "none"
    PROJECT = "project"
    TRACK = "track"
    ASSET = "asset"
    CLIP = "clip"


@dataclass(frozen=True, slots=True)
class InspectorBinding:
    target_type: InspectorTargetType
    target_id: str | None
    editable: bool


@dataclass(frozen=True, slots=True)
class PropertyCapabilities:
    reverse_supported: bool = False
    reverse_reason: str = "Reverse belum lolos qualification backend W3 dan sengaja dinonaktifkan."


class PropertyController:
    def __init__(
        self,
        bus: CommandBus,
        playback: PlaybackController | None = None,
    ) -> None:
        self.bus = bus
        self.playback = playback
        self.binding = InspectorBinding(InspectorTargetType.NONE, None, False)
        self.capabilities = PropertyCapabilities()

    @property
    def state(self) -> ProjectState:
        return self.bus.state

    def bind_project(self) -> InspectorBinding:
        self.binding = InspectorBinding(InspectorTargetType.PROJECT, self.state.project_id, False)
        return self.binding

    def bind_track(self, track_id: str) -> InspectorBinding:
        self.state.track(track_id)
        self.binding = InspectorBinding(InspectorTargetType.TRACK, track_id, False)
        return self.binding

    def bind_asset(self, asset_id: str) -> InspectorBinding:
        self.state.asset(asset_id)
        self.binding = InspectorBinding(InspectorTargetType.ASSET, asset_id, False)
        return self.binding

    def bind_clip(self, clip_id: str) -> InspectorBinding:
        self.state.clip(clip_id)
        self.binding = InspectorBinding(InspectorTargetType.CLIP, clip_id, True)
        return self.binding

    def clear_binding(self) -> InspectorBinding:
        self.binding = InspectorBinding(InspectorTargetType.NONE, None, False)
        return self.binding

    def selected_properties(self) -> ClipProperties:
        return self.state.clip(self._selected_clip_id()).properties

    def _selected_clip_id(self) -> str:
        if self.binding.target_type is not InspectorTargetType.CLIP or not self.binding.target_id:
            raise PropertyEditError("clip property edit requires a selected clip")
        return self.binding.target_id

    def _prepare_edit(self) -> None:
        if self.playback is not None:
            self.playback.prepare_edit()

    def _execute(self, label: str, command: object) -> ProjectState:
        self._prepare_edit()
        state = self.bus.execute(
            CommandBatch(
                batch_id=f"W3-{self.state.revision + 1:06d}",
                label=label,
                actor="manual",
                expected_revision=self.state.revision,
                commands=(command,),
            )
        )
        return state

    def set_video(self, video: VideoProperties) -> ProjectState:
        clip_id = self._selected_clip_id()
        current = self.state.clip(clip_id).properties
        return self._execute(
            "Set video properties",
            SetClipPropertiesCommand(clip_id, replace(current, video=video)),
        )

    def set_audio(self, audio: AudioProperties) -> ProjectState:
        clip_id = self._selected_clip_id()
        current = self.state.clip(clip_id).properties
        return self._execute(
            "Set audio properties",
            SetClipPropertiesCommand(clip_id, replace(current, audio=audio)),
        )

    def set_color(self, color: ColorProperties) -> ProjectState:
        clip_id = self._selected_clip_id()
        current = self.state.clip(clip_id).properties
        return self._execute(
            "Set color properties",
            SetClipPropertiesCommand(clip_id, replace(current, color=color)),
        )

    def set_speed(self, rate_percent: int, *, ripple: bool = True) -> ProjectState:
        clip_id = self._selected_clip_id()
        return self._execute(
            "Set clip speed",
            SetClipSpeedCommand(clip_id, rate_percent, ripple),
        )

    def set_reverse(self, enabled: bool) -> ProjectState:
        if enabled and not self.capabilities.reverse_supported:
            raise PropertyEditError(self.capabilities.reverse_reason)
        return self.state

    def undo(self) -> ProjectState:
        self._prepare_edit()
        return self.bus.undo()

    def redo(self) -> ProjectState:
        self._prepare_edit()
        return self.bus.redo()


class PropertyIntentRouter:
    def __init__(self, controller: PropertyController) -> None:
        self.controller = controller
        self.last_result: object | None = None

    @staticmethod
    def _payload(intent: UiIntent) -> dict[str, str]:
        return dict(intent.payload)

    @staticmethod
    def _required(data: dict[str, str], key: str) -> str:
        value = data.get(key)
        if value is None or value == "":
            raise PropertyEditError(f"{key} is required")
        return value

    def _bind_clip_from_payload(self, data: dict[str, str]) -> None:
        clip_id = data.get("clip_id")
        if clip_id:
            self.controller.bind_clip(clip_id)

    def __call__(self, intent: UiIntent) -> None:
        data = self._payload(intent)
        if intent.kind is UiIntentType.INSPECTOR_BIND:
            target_type = InspectorTargetType(self._required(data, "target_type"))
            if target_type is InspectorTargetType.CLIP:
                self.last_result = self.controller.bind_clip(self._required(data, "target_id"))
            elif target_type is InspectorTargetType.TRACK:
                self.last_result = self.controller.bind_track(self._required(data, "target_id"))
            elif target_type is InspectorTargetType.ASSET:
                self.last_result = self.controller.bind_asset(self._required(data, "target_id"))
            elif target_type is InspectorTargetType.PROJECT:
                self.last_result = self.controller.bind_project()
            else:
                self.last_result = self.controller.clear_binding()
            return
        if intent.kind is UiIntentType.PROPERTY_SET_VIDEO:
            self._bind_clip_from_payload(data)
            self.last_result = self.controller.set_video(
                VideoProperties(
                    position_x=int(data.get("position_x", "0")),
                    position_y=int(data.get("position_y", "0")),
                    scale_x_percent=int(data.get("scale_x_percent", "100")),
                    scale_y_percent=int(data.get("scale_y_percent", "100")),
                    rotation_tenths=int(data.get("rotation_tenths", "0")),
                    opacity_percent=int(data.get("opacity_percent", "100")),
                    crop_left_percent=int(data.get("crop_left_percent", "0")),
                    crop_top_percent=int(data.get("crop_top_percent", "0")),
                    crop_right_percent=int(data.get("crop_right_percent", "0")),
                    crop_bottom_percent=int(data.get("crop_bottom_percent", "0")),
                )
            )
            return
        if intent.kind is UiIntentType.PROPERTY_SET_AUDIO:
            self._bind_clip_from_payload(data)
            self.last_result = self.controller.set_audio(
                AudioProperties(
                    volume_percent=int(data.get("volume_percent", "100")),
                    pan_percent=int(data.get("pan_percent", "0")),
                    fade_in_frames=int(data.get("fade_in_frames", "0")),
                    fade_out_frames=int(data.get("fade_out_frames", "0")),
                )
            )
            return
        if intent.kind is UiIntentType.PROPERTY_SET_COLOR:
            self._bind_clip_from_payload(data)
            self.last_result = self.controller.set_color(
                ColorProperties(
                    brightness_percent=int(data.get("brightness_percent", "0")),
                    exposure_tenths_ev=int(data.get("exposure_tenths_ev", "0")),
                    contrast_percent=int(data.get("contrast_percent", "0")),
                    saturation_percent=int(data.get("saturation_percent", "0")),
                    temperature_percent=int(data.get("temperature_percent", "0")),
                    tint_percent=int(data.get("tint_percent", "0")),
                )
            )
            return
        if intent.kind is UiIntentType.PROPERTY_SET_SPEED:
            self._bind_clip_from_payload(data)
            self.last_result = self.controller.set_speed(
                int(self._required(data, "rate_percent")),
                ripple=data.get("ripple", "true").lower() == "true",
            )
            return
        if intent.kind is UiIntentType.PROPERTY_SET_REVERSE:
            self._bind_clip_from_payload(data)
            self.last_result = self.controller.set_reverse(
                self._required(data, "enabled").lower() == "true"
            )
            return
        raise PropertyEditError(f"unsupported W3 property intent: {intent.kind}")
