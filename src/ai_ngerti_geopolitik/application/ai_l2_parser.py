"""W7-003 strict AutoEditPlan v2 JSON parser and canonical JSON schema.

Provider JSON is untrusted. This module owns structural decoding only. It does not
read ProjectState, selected scope, locks, session/revision freshness, run manual
commands, call Gemini, or create canonical history. Those semantic gates begin in
W7-004 and later tasks.
"""

from __future__ import annotations

import json
from typing import Any, Final

from ai_ngerti_geopolitik.application.ai_contracts import (
    L1_RENDER_QUALIFIED_EFFECTS,
    EffectEditProposal,
    PlanContractError,
    PlanErrorCode,
)
from ai_ngerti_geopolitik.application.ai_l2_contracts import (
    AUTO_EDIT_PLAN_SCHEMA_VERSION,
    MAX_W7_COMMANDS,
    AutoEditCommandProposal,
    AutoEditPlan,
    DurationEditProposal,
    SpeedEditProposal,
    TransformEditProposal,
    TransitionEditProposal,
    W7_TRANSITION_PRESETS,
)

_ROOT_FIELDS: Final = frozenset(
    {
        "schema_version",
        "base_project_revision",
        "request_id",
        "summary",
        "commands",
    }
)

_COMMON_FIELDS: Final = frozenset({"command_type", "target_clip_id"})
_EFFECT_FIELDS: Final = _COMMON_FIELDS | frozenset(
    {"enter_effect", "exit_effect", "intensity_percent"}
)
_DURATION_FIELDS: Final = _COMMON_FIELDS | frozenset({"duration_frames"})
_SPEED_FIELDS: Final = _COMMON_FIELDS | frozenset({"rate_percent"})
_TRANSFORM_OPTIONAL_FIELDS: Final = frozenset(
    {
        "position_x",
        "position_y",
        "scale_percent",
        "rotation_tenths",
        "opacity_percent",
    }
)
_TRANSFORM_FIELDS: Final = _COMMON_FIELDS | _TRANSFORM_OPTIONAL_FIELDS
_TRANSITION_FIELDS: Final = _COMMON_FIELDS | frozenset({"preset", "duration_frames"})


def _effect_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["command_type", "target_clip_id"],
        "anyOf": [
            {"required": ["enter_effect"]},
            {"required": ["exit_effect"]},
            {"required": ["intensity_percent"]},
        ],
        "properties": {
            "command_type": {"const": "set_clip_effects"},
            "target_clip_id": {"type": "string", "minLength": 1},
            "enter_effect": {
                "type": "string",
                "enum": list(L1_RENDER_QUALIFIED_EFFECTS),
            },
            "exit_effect": {
                "type": "string",
                "enum": list(L1_RENDER_QUALIFIED_EFFECTS),
            },
            "intensity_percent": {
                "type": "integer",
                "minimum": 0,
                "maximum": 200,
            },
        },
    }


def _duration_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["command_type", "target_clip_id", "duration_frames"],
        "properties": {
            "command_type": {"const": "set_clip_duration"},
            "target_clip_id": {"type": "string", "minLength": 1},
            "duration_frames": {"type": "integer", "minimum": 1},
        },
    }


def _speed_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["command_type", "target_clip_id", "rate_percent"],
        "properties": {
            "command_type": {"const": "set_clip_speed"},
            "target_clip_id": {"type": "string", "minLength": 1},
            "rate_percent": {
                "type": "integer",
                "minimum": 50,
                "maximum": 200,
            },
        },
    }


def _transform_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["command_type", "target_clip_id"],
        "anyOf": [
            {"required": ["position_x"]},
            {"required": ["position_y"]},
            {"required": ["scale_percent"]},
            {"required": ["rotation_tenths"]},
            {"required": ["opacity_percent"]},
        ],
        "properties": {
            "command_type": {"const": "set_clip_transform"},
            "target_clip_id": {"type": "string", "minLength": 1},
            "position_x": {"type": "integer"},
            "position_y": {"type": "integer"},
            "scale_percent": {
                "type": "integer",
                "minimum": 50,
                "maximum": 200,
            },
            "rotation_tenths": {
                "type": "integer",
                "minimum": -150,
                "maximum": 150,
            },
            "opacity_percent": {
                "type": "integer",
                "minimum": 60,
                "maximum": 100,
            },
        },
    }


def _transition_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "command_type",
            "target_clip_id",
            "preset",
            "duration_frames",
        ],
        "properties": {
            "command_type": {"const": "set_clip_transition"},
            "target_clip_id": {"type": "string", "minLength": 1},
            "preset": {"type": "string", "enum": list(W7_TRANSITION_PRESETS)},
            "duration_frames": {"type": "integer", "minimum": 0},
        },
        "allOf": [
            {
                "if": {"properties": {"preset": {"const": "none"}}},
                "then": {"properties": {"duration_frames": {"const": 0}}},
            },
            {
                "if": {"properties": {"preset": {"const": "fade_black"}}},
                "then": {"properties": {"duration_frames": {"minimum": 1}}},
            },
        ],
    }


AUTO_EDIT_PLAN_V2_JSON_SCHEMA: Final[dict[str, Any]] = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "schema_version",
        "base_project_revision",
        "request_id",
        "summary",
        "commands",
    ],
    "properties": {
        "schema_version": {
            "type": "integer",
            "const": AUTO_EDIT_PLAN_SCHEMA_VERSION,
        },
        "base_project_revision": {"type": "integer", "minimum": 0},
        "request_id": {"type": "string", "minLength": 1},
        "summary": {"type": "string", "minLength": 1},
        "commands": {
            "type": "array",
            "minItems": 1,
            "maxItems": MAX_W7_COMMANDS,
            "items": {
                "oneOf": [
                    _effect_schema(),
                    _duration_schema(),
                    _speed_schema(),
                    _transform_schema(),
                    _transition_schema(),
                ]
            },
        },
    },
}


class AutoEditPlanParser:
    """Strict JSON-to-AutoEditPlan decoder for W7 schema v2."""

    __slots__ = ()

    @staticmethod
    def _schema_error(message: str) -> PlanContractError:
        return PlanContractError(PlanErrorCode.SCHEMA_INVALID, message)

    @staticmethod
    def _strict_int(name: str, value: object) -> int:
        if type(value) is not int:
            raise AutoEditPlanParser._schema_error(f"{name} must be an integer")
        return value

    @staticmethod
    def _strict_string(name: str, value: object) -> str:
        if not isinstance(value, str):
            raise AutoEditPlanParser._schema_error(f"{name} must be a string")
        if not value.strip():
            raise AutoEditPlanParser._schema_error(f"{name} must not be blank")
        return value

    @classmethod
    def _target_id(cls, raw: dict[str, object]) -> str:
        target = cls._strict_string("target_clip_id", raw["target_clip_id"])
        if target != target.strip():
            raise cls._schema_error("target_clip_id must not contain outer whitespace")
        return target

    @classmethod
    def _exact_fields(
        cls,
        raw: dict[str, object],
        *,
        allowed: frozenset[str],
        required: frozenset[str],
        label: str,
    ) -> None:
        fields = set(raw)
        if fields - allowed:
            raise cls._schema_error(f"{label} contains unknown fields")
        if not required.issubset(fields):
            raise cls._schema_error(f"{label} is missing required fields")

    def parse(self, payload_json: str) -> AutoEditPlan:
        if not isinstance(payload_json, str) or not payload_json.strip():
            raise self._schema_error(
                "AutoEditPlan payload must be a non-empty JSON string"
            )
        try:
            raw = json.loads(payload_json)
        except json.JSONDecodeError as exc:
            raise self._schema_error("AutoEditPlan payload is not valid JSON") from exc

        if not isinstance(raw, dict):
            raise self._schema_error("AutoEditPlan root must be a JSON object")

        fields = set(raw)
        if fields != _ROOT_FIELDS:
            if fields - _ROOT_FIELDS:
                raise self._schema_error("AutoEditPlan contains unknown root fields")
            raise self._schema_error("AutoEditPlan is missing required root fields")

        schema_version = self._strict_int("schema_version", raw["schema_version"])
        if schema_version != AUTO_EDIT_PLAN_SCHEMA_VERSION:
            raise self._schema_error("AutoEditPlan schema version is unsupported")

        base_revision = self._strict_int(
            "base_project_revision",
            raw["base_project_revision"],
        )
        if base_revision < 0:
            raise self._schema_error(
                "AutoEditPlan base_project_revision must be non-negative"
            )

        request_id = self._strict_string("request_id", raw["request_id"])
        summary = self._strict_string("summary", raw["summary"])
        commands_raw = raw["commands"]
        if not isinstance(commands_raw, list):
            raise self._schema_error("AutoEditPlan commands must be an array")
        if not commands_raw:
            raise self._schema_error("AutoEditPlan must contain at least one command")
        if len(commands_raw) > MAX_W7_COMMANDS:
            raise self._schema_error(
                f"AutoEditPlan supports at most {MAX_W7_COMMANDS} commands"
            )

        commands = tuple(self._parse_command(item) for item in commands_raw)
        return AutoEditPlan(
            schema_version=schema_version,
            base_project_revision=base_revision,
            request_id=request_id,
            summary=summary,
            commands=commands,
        )

    def _parse_command(self, raw: object) -> AutoEditCommandProposal:
        if not isinstance(raw, dict):
            raise self._schema_error("AutoEditPlan command must be a JSON object")
        if "command_type" not in raw or "target_clip_id" not in raw:
            raise self._schema_error(
                "AutoEditPlan command requires command_type and target_clip_id"
            )

        command_type = self._strict_string("command_type", raw["command_type"])
        target = self._target_id(raw)

        if command_type == "set_clip_effects":
            return self._parse_effects(raw, target)
        if command_type == "set_clip_duration":
            return self._parse_duration(raw, target)
        if command_type == "set_clip_speed":
            return self._parse_speed(raw, target)
        if command_type == "set_clip_transform":
            return self._parse_transform(raw, target)
        if command_type == "set_clip_transition":
            return self._parse_transition(raw, target)
        raise self._schema_error(
            f"unsupported AutoEditPlan command_type: {command_type}"
        )

    def _parse_effects(
        self,
        raw: dict[str, object],
        target: str,
    ) -> EffectEditProposal:
        self._exact_fields(
            raw,
            allowed=_EFFECT_FIELDS,
            required=_COMMON_FIELDS,
            label="set_clip_effects",
        )
        effect_fields = {"enter_effect", "exit_effect", "intensity_percent"}
        if not set(raw).intersection(effect_fields):
            raise self._schema_error(
                "set_clip_effects requires at least one effect change"
            )

        enter_effect: str | None = None
        exit_effect: str | None = None
        intensity_percent: int | None = None
        if "enter_effect" in raw:
            enter_effect = self._strict_string("enter_effect", raw["enter_effect"])
        if "exit_effect" in raw:
            exit_effect = self._strict_string("exit_effect", raw["exit_effect"])
        if "intensity_percent" in raw:
            intensity_percent = self._strict_int(
                "intensity_percent",
                raw["intensity_percent"],
            )
        return EffectEditProposal(
            target_clip_id=target,
            enter_effect=enter_effect,
            exit_effect=exit_effect,
            intensity_percent=intensity_percent,
            command_type="set_clip_effects",
        )

    def _parse_duration(
        self,
        raw: dict[str, object],
        target: str,
    ) -> DurationEditProposal:
        self._exact_fields(
            raw,
            allowed=_DURATION_FIELDS,
            required=_DURATION_FIELDS,
            label="set_clip_duration",
        )
        duration = self._strict_int("duration_frames", raw["duration_frames"])
        return DurationEditProposal(target, duration)

    def _parse_speed(
        self,
        raw: dict[str, object],
        target: str,
    ) -> SpeedEditProposal:
        self._exact_fields(
            raw,
            allowed=_SPEED_FIELDS,
            required=_SPEED_FIELDS,
            label="set_clip_speed",
        )
        rate = self._strict_int("rate_percent", raw["rate_percent"])
        return SpeedEditProposal(target, rate)

    def _parse_transform(
        self,
        raw: dict[str, object],
        target: str,
    ) -> TransformEditProposal:
        self._exact_fields(
            raw,
            allowed=_TRANSFORM_FIELDS,
            required=_COMMON_FIELDS,
            label="set_clip_transform",
        )
        if not set(raw).intersection(_TRANSFORM_OPTIONAL_FIELDS):
            raise self._schema_error(
                "set_clip_transform requires at least one transform change"
            )

        values: dict[str, int | None] = {}
        for name in _TRANSFORM_OPTIONAL_FIELDS:
            values[name] = (
                self._strict_int(name, raw[name]) if name in raw else None
            )
        return TransformEditProposal(
            target_clip_id=target,
            position_x=values["position_x"],
            position_y=values["position_y"],
            scale_percent=values["scale_percent"],
            rotation_tenths=values["rotation_tenths"],
            opacity_percent=values["opacity_percent"],
        )

    def _parse_transition(
        self,
        raw: dict[str, object],
        target: str,
    ) -> TransitionEditProposal:
        self._exact_fields(
            raw,
            allowed=_TRANSITION_FIELDS,
            required=_TRANSITION_FIELDS,
            label="set_clip_transition",
        )
        preset = self._strict_string("preset", raw["preset"])
        duration = self._strict_int("duration_frames", raw["duration_frames"])
        return TransitionEditProposal(target, preset, duration)
