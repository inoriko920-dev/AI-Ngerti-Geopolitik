"""Canonical W7 Auto Edit L2 contracts and capability registry.

W7-001 deliberately defines DTOs, immutable capability metadata and typed policy
bounds only. It contains no provider calls, ContextBuilder, JSON parser/verifier,
Qt code or ProjectState mutation.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import Final

from ai_ngerti_geopolitik.application.ai_contracts import (
    EDIT_PLAN_SCHEMA_VERSION,
    L1_RENDER_QUALIFIED_EFFECTS,
    EffectEditProposal,
    PlanContractError,
    PlanErrorCode,
)

AUTO_EDIT_PLAN_SCHEMA_VERSION: Final = 2
MAX_W7_SELECTED_TARGETS: Final = 20
MAX_W7_COMMANDS: Final = 40

W7_ALLOWED_COMMAND_TYPES: Final = (
    "set_clip_effects",
    "set_clip_duration",
    "set_clip_speed",
    "set_clip_transform",
    "set_clip_transition",
)

W7_TRANSITION_PRESETS: Final = ("none", "fade_black")


class W7CommandFamily(StrEnum):
    EFFECTS = "effects"
    DURATION = "duration"
    SPEED = "speed"
    TRANSFORM = "transform"
    TRANSITION = "transition"


@dataclass(frozen=True, slots=True)
class W7CapabilityDefinition:
    command_type: str
    family: W7CommandFamily
    manual_command_owner: str
    property_owner: str | None
    application_owned_ripple: bool
    render_qualified: bool

    def __post_init__(self) -> None:
        if self.command_type not in W7_ALLOWED_COMMAND_TYPES:
            raise ValueError(f"unregistered W7 command type: {self.command_type}")
        if not self.manual_command_owner.strip():
            raise ValueError("manual command owner is required")
        if self.property_owner is not None and not self.property_owner.strip():
            raise ValueError("property owner cannot be blank")


W7_CAPABILITY_REGISTRY: Final[Mapping[str, W7CapabilityDefinition]] = MappingProxyType(
    {
        "set_clip_effects": W7CapabilityDefinition(
            command_type="set_clip_effects",
            family=W7CommandFamily.EFFECTS,
            manual_command_owner="SetClipPropertiesCommand",
            property_owner="EffectProperties",
            application_owned_ripple=False,
            render_qualified=True,
        ),
        "set_clip_duration": W7CapabilityDefinition(
            command_type="set_clip_duration",
            family=W7CommandFamily.DURATION,
            manual_command_owner="SetClipDurationCommand",
            property_owner=None,
            application_owned_ripple=True,
            render_qualified=True,
        ),
        "set_clip_speed": W7CapabilityDefinition(
            command_type="set_clip_speed",
            family=W7CommandFamily.SPEED,
            manual_command_owner="SetClipSpeedCommand",
            property_owner="SpeedProperties",
            application_owned_ripple=True,
            render_qualified=True,
        ),
        "set_clip_transform": W7CapabilityDefinition(
            command_type="set_clip_transform",
            family=W7CommandFamily.TRANSFORM,
            manual_command_owner="SetClipPropertiesCommand",
            property_owner="VideoProperties",
            application_owned_ripple=False,
            render_qualified=True,
        ),
        "set_clip_transition": W7CapabilityDefinition(
            command_type="set_clip_transition",
            family=W7CommandFamily.TRANSITION,
            manual_command_owner="SetClipPropertiesCommand",
            property_owner="TransitionProperties",
            application_owned_ripple=False,
            render_qualified=True,
        ),
    }
)


def capability_for(command_type: str) -> W7CapabilityDefinition:
    try:
        return W7_CAPABILITY_REGISTRY[command_type]
    except KeyError as exc:
        raise PlanContractError(
            PlanErrorCode.SCHEMA_INVALID,
            f"unsupported W7 command type: {command_type}",
        ) from exc


def _strict_int(name: str, value: object) -> int:
    if type(value) is not int:
        raise PlanContractError(
            PlanErrorCode.SCHEMA_INVALID,
            f"{name} must be an integer",
        )
    return value


def _stable_target(target_clip_id: str) -> str:
    target = target_clip_id.strip()
    if not target:
        raise PlanContractError(
            PlanErrorCode.SCHEMA_INVALID,
            "W7 proposal requires a stable target clip id",
        )
    return target


@dataclass(frozen=True, slots=True)
class W7PolicyBounds:
    duration_min_ratio_percent: int = 50
    duration_max_ratio_percent: int = 200
    speed_min_percent: int = 50
    speed_max_percent: int = 200
    scale_min_percent: int = 50
    scale_max_percent: int = 200
    rotation_min_tenths: int = -150
    rotation_max_tenths: int = 150
    opacity_min_percent: int = 60
    opacity_max_percent: int = 100
    effect_intensity_min_percent: int = 0
    effect_intensity_max_percent: int = 200
    transition_max_seconds: int = 2

    def duration_bounds(self, fps: int, current_duration_frames: int) -> tuple[int, int]:
        if fps <= 0 or current_duration_frames <= 0:
            raise ValueError("duration policy requires positive fps/current duration")
        minimum_half_second = (fps + 1) // 2
        minimum_ratio = (current_duration_frames * self.duration_min_ratio_percent + 99) // 100
        maximum_ratio = (current_duration_frames * self.duration_max_ratio_percent) // 100
        return max(minimum_half_second, minimum_ratio), maximum_ratio

    def transform_position_bounds(
        self,
        canvas_width: int,
        canvas_height: int,
    ) -> tuple[tuple[int, int], tuple[int, int]]:
        if canvas_width <= 0 or canvas_height <= 0:
            raise ValueError("transform policy requires positive canvas dimensions")
        half_width = canvas_width // 2
        half_height = canvas_height // 2
        return (-half_width, half_width), (-half_height, half_height)

    def transition_max_frames(self, fps: int, candidate_duration_frames: int) -> int:
        if fps <= 0 or candidate_duration_frames <= 0:
            raise ValueError("transition policy requires positive fps/candidate duration")
        return min(self.transition_max_seconds * fps, candidate_duration_frames // 2)


W7_POLICY_BOUNDS: Final = W7PolicyBounds()


@dataclass(frozen=True, slots=True)
class DurationEditProposal:
    target_clip_id: str
    duration_frames: int
    command_type: str = "set_clip_duration"

    def __post_init__(self) -> None:
        if self.command_type != "set_clip_duration":
            raise PlanContractError(
                PlanErrorCode.SCHEMA_INVALID,
                f"invalid duration command type: {self.command_type}",
            )
        object.__setattr__(self, "target_clip_id", _stable_target(self.target_clip_id))
        duration = _strict_int("duration_frames", self.duration_frames)
        if duration <= 0:
            raise PlanContractError(
                PlanErrorCode.SEMANTIC_INVALID,
                "duration_frames must be positive",
            )


@dataclass(frozen=True, slots=True)
class SpeedEditProposal:
    target_clip_id: str
    rate_percent: int
    command_type: str = "set_clip_speed"

    def __post_init__(self) -> None:
        if self.command_type != "set_clip_speed":
            raise PlanContractError(
                PlanErrorCode.SCHEMA_INVALID,
                f"invalid speed command type: {self.command_type}",
            )
        object.__setattr__(self, "target_clip_id", _stable_target(self.target_clip_id))
        rate = _strict_int("rate_percent", self.rate_percent)
        if not (W7_POLICY_BOUNDS.speed_min_percent <= rate <= W7_POLICY_BOUNDS.speed_max_percent):
            raise PlanContractError(
                PlanErrorCode.SEMANTIC_INVALID,
                "W7 AI speed must be between 50 and 200 percent",
            )


@dataclass(frozen=True, slots=True)
class TransformEditProposal:
    target_clip_id: str
    position_x: int | None = None
    position_y: int | None = None
    scale_percent: int | None = None
    rotation_tenths: int | None = None
    opacity_percent: int | None = None
    command_type: str = "set_clip_transform"

    def __post_init__(self) -> None:
        if self.command_type != "set_clip_transform":
            raise PlanContractError(
                PlanErrorCode.SCHEMA_INVALID,
                f"invalid transform command type: {self.command_type}",
            )
        object.__setattr__(self, "target_clip_id", _stable_target(self.target_clip_id))
        fields = {
            "position_x": self.position_x,
            "position_y": self.position_y,
            "scale_percent": self.scale_percent,
            "rotation_tenths": self.rotation_tenths,
            "opacity_percent": self.opacity_percent,
        }
        if all(value is None for value in fields.values()):
            raise PlanContractError(
                PlanErrorCode.SCHEMA_INVALID,
                "transform proposal must change at least one allowed field",
            )
        for name, value in fields.items():
            if value is not None:
                _strict_int(name, value)
        if self.scale_percent is not None and not (
            W7_POLICY_BOUNDS.scale_min_percent
            <= self.scale_percent
            <= W7_POLICY_BOUNDS.scale_max_percent
        ):
            raise PlanContractError(
                PlanErrorCode.SEMANTIC_INVALID,
                "W7 AI uniform scale must be between 50 and 200 percent",
            )
        if self.rotation_tenths is not None and not (
            W7_POLICY_BOUNDS.rotation_min_tenths
            <= self.rotation_tenths
            <= W7_POLICY_BOUNDS.rotation_max_tenths
        ):
            raise PlanContractError(
                PlanErrorCode.SEMANTIC_INVALID,
                "W7 AI rotation must stay within plus/minus 15 degrees",
            )
        if self.opacity_percent is not None and not (
            W7_POLICY_BOUNDS.opacity_min_percent
            <= self.opacity_percent
            <= W7_POLICY_BOUNDS.opacity_max_percent
        ):
            raise PlanContractError(
                PlanErrorCode.SEMANTIC_INVALID,
                "W7 AI opacity must be between 60 and 100 percent",
            )


@dataclass(frozen=True, slots=True)
class TransitionEditProposal:
    target_clip_id: str
    preset: str
    duration_frames: int
    command_type: str = "set_clip_transition"

    def __post_init__(self) -> None:
        if self.command_type != "set_clip_transition":
            raise PlanContractError(
                PlanErrorCode.SCHEMA_INVALID,
                f"invalid transition command type: {self.command_type}",
            )
        object.__setattr__(self, "target_clip_id", _stable_target(self.target_clip_id))
        if self.preset not in W7_TRANSITION_PRESETS:
            raise PlanContractError(
                PlanErrorCode.SEMANTIC_INVALID,
                f"unsupported W7 transition preset: {self.preset}",
            )
        duration = _strict_int("duration_frames", self.duration_frames)
        if self.preset == "none" and duration != 0:
            raise PlanContractError(
                PlanErrorCode.SEMANTIC_INVALID,
                "none transition requires zero duration",
            )
        if self.preset == "fade_black" and duration < 1:
            raise PlanContractError(
                PlanErrorCode.SEMANTIC_INVALID,
                "fade_black transition requires positive duration",
            )


AutoEditCommandProposal = (
    EffectEditProposal
    | DurationEditProposal
    | SpeedEditProposal
    | TransformEditProposal
    | TransitionEditProposal
)


@dataclass(frozen=True, slots=True)
class AutoEditPlan:
    schema_version: int
    base_project_revision: int
    request_id: str
    summary: str
    commands: tuple[AutoEditCommandProposal, ...]

    def __post_init__(self) -> None:
        schema_version = _strict_int("schema_version", self.schema_version)
        base_revision = _strict_int("base_project_revision", self.base_project_revision)
        if schema_version != AUTO_EDIT_PLAN_SCHEMA_VERSION:
            raise PlanContractError(
                PlanErrorCode.SCHEMA_INVALID,
                f"unsupported AutoEditPlan schema version: {schema_version}",
            )
        if base_revision < 0:
            raise PlanContractError(
                PlanErrorCode.SCHEMA_INVALID,
                "base project revision must be non-negative",
            )
        if not self.request_id.strip():
            raise PlanContractError(
                PlanErrorCode.SCHEMA_INVALID,
                "AutoEditPlan request id is required",
            )
        if not self.summary.strip():
            raise PlanContractError(
                PlanErrorCode.SCHEMA_INVALID,
                "AutoEditPlan summary is required",
            )
        if not 1 <= len(self.commands) <= MAX_W7_COMMANDS:
            raise PlanContractError(
                PlanErrorCode.SCHEMA_INVALID,
                f"AutoEditPlan requires 1..{MAX_W7_COMMANDS} commands",
            )

        seen: set[tuple[str, W7CommandFamily]] = set()
        pacing: dict[str, set[W7CommandFamily]] = {}
        targets: set[str] = set()
        supported_types = (
            EffectEditProposal,
            DurationEditProposal,
            SpeedEditProposal,
            TransformEditProposal,
            TransitionEditProposal,
        )

        for command in self.commands:
            if not isinstance(command, supported_types):
                raise PlanContractError(
                    PlanErrorCode.SCHEMA_INVALID,
                    "AutoEditPlan contains an unsupported proposal DTO",
                )
            capability = capability_for(command.command_type)
            target = command.target_clip_id
            targets.add(target)
            key = (target, capability.family)
            if key in seen:
                raise PlanContractError(
                    PlanErrorCode.SEMANTIC_INVALID,
                    f"duplicate W7 command family for target: {target}/{capability.family.value}",
                )
            seen.add(key)
            if capability.family in {W7CommandFamily.DURATION, W7CommandFamily.SPEED}:
                families = pacing.setdefault(target, set())
                families.add(capability.family)
                if len(families) > 1:
                    raise PlanContractError(
                        PlanErrorCode.SEMANTIC_INVALID,
                        f"duration and speed are mutually exclusive for target: {target}",
                    )

        if len(targets) > MAX_W7_SELECTED_TARGETS:
            raise PlanContractError(
                PlanErrorCode.SEMANTIC_INVALID,
                f"AutoEditPlan may target at most {MAX_W7_SELECTED_TARGETS} clips",
            )


def assert_w6_backward_compatibility_contract() -> None:
    """Fail fast if W7 accidentally changes the accepted W6 schema constants."""
    if EDIT_PLAN_SCHEMA_VERSION != 1:
        raise RuntimeError("W7 requires W6 EditPlan schema version 1 to remain unchanged")
    if tuple(L1_RENDER_QUALIFIED_EFFECTS) != (
        "None",
        "Fade",
        "Pop",
        "Breathe",
        "Stomp",
        "Tumble",
        "Tectonic",
        "Rise",
        "Pan",
        "Drift",
    ):
        raise RuntimeError("W7 requires the qualified W6 L1 effect allowlist unchanged")


assert_w6_backward_compatibility_contract()
