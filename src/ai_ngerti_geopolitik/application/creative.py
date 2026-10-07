"""Canonical SF-STEP 11 W4 title, transition and effect editing owner."""

from __future__ import annotations

from dataclasses import dataclass, replace

from ai_ngerti_geopolitik.application.commands import (
    Command,
    CommandBatch,
    CommandBus,
    SetClipPropertiesCommand,
)
from ai_ngerti_geopolitik.application.playback import PlaybackController
from ai_ngerti_geopolitik.application.ui_intents import UiIntent, UiIntentType
from ai_ngerti_geopolitik.domain import (
    SUPPORTED_W4_EFFECTS,
    SUPPORTED_W4_TRANSITIONS,
    UNSUPPORTED_LEGACY_EFFECTS,
    EffectProperties,
    ProjectState,
    TitleProperties,
    TransitionProperties,
)


class CreativeEditError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class CreativeCapabilities:
    supported_effects: tuple[str, ...] = SUPPORTED_W4_EFFECTS
    unsupported_legacy_effects: tuple[str, ...] = UNSUPPORTED_LEGACY_EFFECTS
    supported_transitions: tuple[str, ...] = SUPPORTED_W4_TRANSITIONS
    crossfade_supported: bool = False
    crossfade_reason: str = (
        "Crossfade/dissolve belum didukung karena timeline canonical W4 tidak "
        "mengizinkan clip overlap."
    )


class CreativeController:
    def __init__(
        self,
        bus: CommandBus,
        playback: PlaybackController | None = None,
    ) -> None:
        self.bus = bus
        self.playback = playback
        self.clip_id: str | None = None
        self.capabilities = CreativeCapabilities()

    @property
    def state(self) -> ProjectState:
        return self.bus.state

    def bind_clip(self, clip_id: str) -> str:
        self.state.clip(clip_id)
        self.clip_id = clip_id
        return clip_id

    def _selected_clip_id(self) -> str:
        if not self.clip_id:
            raise CreativeEditError("creative edit requires a selected clip")
        return self.clip_id

    def _prepare_edit(self) -> None:
        if self.playback is not None:
            self.playback.prepare_edit()

    def _execute(self, label: str, command: Command) -> ProjectState:
        self._prepare_edit()
        return self.bus.execute(
            CommandBatch(
                batch_id=f"W4-{self.state.revision + 1:06d}",
                label=label,
                actor="manual",
                expected_revision=self.state.revision,
                commands=(command,),
            )
        )

    def set_title(self, title: TitleProperties) -> ProjectState:
        clip_id = self._selected_clip_id()
        current = self.state.clip(clip_id).properties
        return self._execute(
            "Set title overlay",
            SetClipPropertiesCommand(clip_id, replace(current, title=title)),
        )

    def set_transition(self, transition: TransitionProperties) -> ProjectState:
        clip_id = self._selected_clip_id()
        clip = self.state.clip(clip_id)
        if transition.preset != "none" and transition.duration_frames * 2 > clip.duration_frames:
            raise CreativeEditError("transition duration must not exceed half of the clip duration")
        return self._execute(
            "Set transition",
            SetClipPropertiesCommand(
                clip_id,
                replace(clip.properties, transition=transition),
            ),
        )

    def set_effects(self, effects: EffectProperties) -> ProjectState:
        clip_id = self._selected_clip_id()
        current = self.state.clip(clip_id).properties
        return self._execute(
            "Set render-backed effects",
            SetClipPropertiesCommand(
                clip_id,
                replace(current, effects=effects),
            ),
        )

    def undo(self) -> ProjectState:
        self._prepare_edit()
        return self.bus.undo()

    def redo(self) -> ProjectState:
        self._prepare_edit()
        return self.bus.redo()


class CreativeIntentRouter:
    def __init__(self, controller: CreativeController) -> None:
        self.controller = controller
        self.last_result: object | None = None

    @staticmethod
    def _payload(intent: UiIntent) -> dict[str, str]:
        return dict(intent.payload)

    @staticmethod
    def _required(data: dict[str, str], key: str) -> str:
        value = data.get(key)
        if value is None or value == "":
            raise CreativeEditError(f"{key} is required")
        return value

    def _bind(self, data: dict[str, str]) -> None:
        self.controller.bind_clip(self._required(data, "clip_id"))

    def __call__(self, intent: UiIntent) -> None:
        data = self._payload(intent)
        if intent.kind is UiIntentType.CREATIVE_SET_TITLE:
            self._bind(data)
            self.last_result = self.controller.set_title(
                TitleProperties(
                    enabled=data.get("enabled", "false").lower() == "true",
                    text=data.get("text", ""),
                    font_size=int(data.get("font_size", "54")),
                    position=data.get("position", "bottom"),
                    color_hex=data.get("color_hex", "FFFFFF"),
                    background_opacity_percent=int(data.get("background_opacity_percent", "55")),
                )
            )
            return
        if intent.kind is UiIntentType.CREATIVE_SET_TRANSITION:
            self._bind(data)
            self.last_result = self.controller.set_transition(
                TransitionProperties(
                    preset=data.get("preset", "none"),
                    duration_frames=int(data.get("duration_frames", "0")),
                )
            )
            return
        if intent.kind is UiIntentType.CREATIVE_SET_EFFECTS:
            self._bind(data)
            self.last_result = self.controller.set_effects(
                EffectProperties(
                    enter_effect=data.get("enter_effect", "None"),
                    exit_effect=data.get("exit_effect", "None"),
                    intensity_percent=int(data.get("intensity_percent", "100")),
                    locked=data.get("locked", "false").lower() == "true",
                )
            )
            return
        raise CreativeEditError(f"unsupported W4 creative intent: {intent.kind}")
