"""W6-006 strict EditPlan parser and non-mutating verifier.

Provider payloads are untrusted. This module accepts only the locked W6 L1 schema,
checks canonical revision/targets/locks/capabilities, then dry-runs the exact manual
W4 command path against an immutable candidate ProjectState.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from typing import Final

from ai_ngerti_geopolitik.application.ai_contracts import (
    EDIT_PLAN_SCHEMA_VERSION,
    EditPlan,
    EffectEditProposal,
    PlanContractError,
    PlanErrorCode,
    ProviderPlanResponse,
)
from ai_ngerti_geopolitik.application.commands import (
    CommandError,
    SetClipPropertiesCommand,
)
from ai_ngerti_geopolitik.domain import (
    Clip,
    DomainValidationError,
    EffectProperties,
    ProjectState,
    PropertyValidationError,
    Track,
)

MAX_L1_PLAN_COMMANDS: Final = 20

_ROOT_REQUIRED_FIELDS: Final = frozenset(
    {
        "schema_version",
        "base_project_revision",
        "request_id",
        "summary",
        "commands",
    }
)
_COMMAND_REQUIRED_FIELDS: Final = frozenset({"command_type", "target_clip_id"})
_COMMAND_OPTIONAL_FIELDS: Final = frozenset(
    {"enter_effect", "exit_effect", "intensity_percent"}
)
_COMMAND_ALLOWED_FIELDS: Final = _COMMAND_REQUIRED_FIELDS | _COMMAND_OPTIONAL_FIELDS


@dataclass(frozen=True, slots=True)
class VerifiedEditPlan:
    """Proof that an EditPlan passed W6-006 gates without canonical mutation."""

    plan: EditPlan
    candidate_semantic_hash: str
    candidate_revision: int
    command_count: int


class PlanVerifier:
    """Canonical W6 L1 parser/verifier.

    W6-006 deliberately does not create a CommandBatch and never executes against
    the live CommandBus. Approval/apply remains owned by W6-008.
    """

    __slots__ = ()

    @staticmethod
    def _schema_error(message: str) -> PlanContractError:
        return PlanContractError(PlanErrorCode.SCHEMA_INVALID, message)

    @staticmethod
    def _semantic_error(message: str) -> PlanContractError:
        return PlanContractError(PlanErrorCode.SEMANTIC_INVALID, message)

    @staticmethod
    def _is_strict_int(value: object) -> bool:
        return isinstance(value, int) and not isinstance(value, bool)

    @staticmethod
    def _clip_location(state: ProjectState, clip_id: str) -> tuple[Track, Clip]:
        for track in state.tracks:
            for clip in track.clips:
                if clip.clip_id == clip_id:
                    return track, clip
        raise PlanContractError(
            PlanErrorCode.SEMANTIC_INVALID,
            "EditPlan references an unknown target clip",
        )

    def parse(self, payload_json: str) -> EditPlan:
        if not isinstance(payload_json, str) or not payload_json.strip():
            raise self._schema_error("EditPlan payload must be a non-empty JSON string")
        try:
            raw = json.loads(payload_json)
        except json.JSONDecodeError as exc:
            raise self._schema_error("EditPlan payload is not valid JSON") from exc

        if not isinstance(raw, dict):
            raise self._schema_error("EditPlan root must be a JSON object")

        root_fields = set(raw)
        if root_fields != _ROOT_REQUIRED_FIELDS:
            if root_fields - _ROOT_REQUIRED_FIELDS:
                raise self._schema_error("EditPlan contains unknown root fields")
            raise self._schema_error("EditPlan is missing required root fields")

        schema_version = raw["schema_version"]
        base_revision = raw["base_project_revision"]
        request_id = raw["request_id"]
        summary = raw["summary"]
        commands_raw = raw["commands"]

        if not self._is_strict_int(schema_version):
            raise self._schema_error("EditPlan schema_version must be an integer")
        if schema_version != EDIT_PLAN_SCHEMA_VERSION:
            raise self._schema_error("EditPlan schema version is unsupported")
        if not self._is_strict_int(base_revision):
            raise self._schema_error("EditPlan base_project_revision must be an integer")
        if not isinstance(request_id, str):
            raise self._schema_error("EditPlan request_id must be a string")
        if not isinstance(summary, str):
            raise self._schema_error("EditPlan summary must be a string")
        if not isinstance(commands_raw, list):
            raise self._schema_error("EditPlan commands must be an array")
        if not commands_raw:
            raise self._schema_error("EditPlan must contain at least one L1 command")
        if len(commands_raw) > MAX_L1_PLAN_COMMANDS:
            raise self._schema_error(
                f"EditPlan supports at most {MAX_L1_PLAN_COMMANDS} L1 commands"
            )

        commands = tuple(self._parse_command(item) for item in commands_raw)
        return EditPlan(
            schema_version=schema_version,
            base_project_revision=base_revision,
            request_id=request_id,
            summary=summary,
            commands=commands,
        )

    def _parse_command(self, raw: object) -> EffectEditProposal:
        if not isinstance(raw, dict):
            raise self._schema_error("EditPlan command must be a JSON object")

        fields = set(raw)
        if fields - _COMMAND_ALLOWED_FIELDS:
            raise self._schema_error("EditPlan command contains unknown fields")
        if not _COMMAND_REQUIRED_FIELDS.issubset(fields):
            raise self._schema_error("EditPlan command is missing required fields")
        if not fields.intersection(_COMMAND_OPTIONAL_FIELDS):
            raise self._schema_error("L1 effect command must contain an effect change")

        command_type = raw["command_type"]
        target_clip_id = raw["target_clip_id"]
        if not isinstance(command_type, str):
            raise self._schema_error("EditPlan command_type must be a string")
        if command_type != "set_clip_effects":
            raise self._schema_error("EditPlan command_type is not allowed for W6 L1")
        if not isinstance(target_clip_id, str):
            raise self._schema_error("EditPlan target_clip_id must be a string")

        enter_effect: str | None = None
        exit_effect: str | None = None
        intensity_percent: int | None = None

        if "enter_effect" in raw:
            value = raw["enter_effect"]
            if not isinstance(value, str):
                raise self._schema_error("EditPlan enter_effect must be a string")
            enter_effect = value
        if "exit_effect" in raw:
            value = raw["exit_effect"]
            if not isinstance(value, str):
                raise self._schema_error("EditPlan exit_effect must be a string")
            exit_effect = value
        if "intensity_percent" in raw:
            intensity = raw["intensity_percent"]
            if not self._is_strict_int(intensity):
                raise self._schema_error("EditPlan intensity_percent must be an integer")
            intensity_percent = intensity

        return EffectEditProposal(
            target_clip_id=target_clip_id,
            enter_effect=enter_effect,
            exit_effect=exit_effect,
            intensity_percent=intensity_percent,
            command_type=command_type,
        )

    @staticmethod
    def _normalize_allowed_targets(allowed_target_ids: tuple[str, ...]) -> frozenset[str]:
        if not allowed_target_ids:
            raise PlanContractError(
                PlanErrorCode.SEMANTIC_INVALID,
                "PlanVerifier requires at least one allowed target",
            )
        if len(allowed_target_ids) > MAX_L1_PLAN_COMMANDS:
            raise PlanContractError(
                PlanErrorCode.SEMANTIC_INVALID,
                f"PlanVerifier supports at most {MAX_L1_PLAN_COMMANDS} allowed targets",
            )
        if len(set(allowed_target_ids)) != len(allowed_target_ids):
            raise PlanContractError(
                PlanErrorCode.SEMANTIC_INVALID,
                "PlanVerifier allowed target IDs must be unique",
            )
        if any(not isinstance(item, str) or not item.strip() for item in allowed_target_ids):
            raise PlanContractError(
                PlanErrorCode.SEMANTIC_INVALID,
                "PlanVerifier allowed target IDs must be non-empty strings",
            )
        return frozenset(allowed_target_ids)

    def verify(
        self,
        plan: EditPlan,
        state: ProjectState,
        allowed_target_ids: tuple[str, ...],
    ) -> VerifiedEditPlan:
        state.validate()
        if plan.base_project_revision != state.revision:
            raise PlanContractError(
                PlanErrorCode.STALE_PLAN,
                "EditPlan base project revision is stale",
            )

        allowed_targets = self._normalize_allowed_targets(allowed_target_ids)
        working = state
        for proposal in plan.commands:
            if proposal.target_clip_id not in allowed_targets:
                raise self._semantic_error("EditPlan target is outside the allowed selected scope")

            track, clip = self._clip_location(working, proposal.target_clip_id)
            effects = clip.properties.effects
            if track.locked or effects.locked:
                raise PlanContractError(
                    PlanErrorCode.LOCK_CONFLICT,
                    "EditPlan target is locked",
                )

            updated_effects = EffectProperties(
                enter_effect=(
                    effects.enter_effect
                    if proposal.enter_effect is None
                    else proposal.enter_effect
                ),
                exit_effect=(
                    effects.exit_effect if proposal.exit_effect is None else proposal.exit_effect
                ),
                intensity_percent=(
                    effects.intensity_percent
                    if proposal.intensity_percent is None
                    else proposal.intensity_percent
                ),
                locked=effects.locked,
            )
            command = SetClipPropertiesCommand(
                clip_id=proposal.target_clip_id,
                properties=replace(clip.properties, effects=updated_effects),
            )
            try:
                working = command.apply(working)
            except (CommandError, DomainValidationError, PropertyValidationError) as exc:
                raise self._semantic_error(
                    "EditPlan failed canonical W4 command dry-run validation"
                ) from exc

        working.validate()
        return VerifiedEditPlan(
            plan=plan,
            candidate_semantic_hash=working.semantic_hash(),
            candidate_revision=working.revision,
            command_count=len(plan.commands),
        )

    def verify_payload(
        self,
        payload_json: str,
        state: ProjectState,
        allowed_target_ids: tuple[str, ...],
    ) -> VerifiedEditPlan:
        return self.verify(self.parse(payload_json), state, allowed_target_ids)

    def verify_response(
        self,
        response: ProviderPlanResponse,
        state: ProjectState,
        allowed_target_ids: tuple[str, ...],
    ) -> VerifiedEditPlan:
        plan = self.parse(response.payload_json)
        if plan.request_id != response.request_id:
            raise PlanContractError(
                PlanErrorCode.SEMANTIC_INVALID,
                "provider response request ID does not match EditPlan request ID",
            )
        return self.verify(plan, state, allowed_target_ids)
