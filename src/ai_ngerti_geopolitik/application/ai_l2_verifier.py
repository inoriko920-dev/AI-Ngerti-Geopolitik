"""W7-004 semantic verifier and sequential manual-command dry-run translator.

Provider JSON is parsed by the W7-003 parser first. This verifier then applies
state-dependent policy to an immutable candidate ProjectState and translates each
proposal to the exact existing manual command path. It never touches CommandBus
history or the live canonical ProjectState.

W7-006 qualifies this existing transform translation through the real-media
preview/export path; this module remains the canonical non-mutating verifier.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from ai_ngerti_geopolitik.application.ai_contracts import (
    EffectEditProposal,
    PlanContractError,
    PlanErrorCode,
    ProviderPlanResponse,
)
from ai_ngerti_geopolitik.application.ai_l2_contracts import (
    W7_POLICY_BOUNDS,
    AutoEditCommandProposal,
    AutoEditPlan,
    DurationEditProposal,
    SpeedEditProposal,
    TransformEditProposal,
    TransitionEditProposal,
    W7CommandFamily,
    capability_for,
)
from ai_ngerti_geopolitik.application.ai_l2_parser import AutoEditPlanParser
from ai_ngerti_geopolitik.application.ai_l2_scope import W7SelectedScope
from ai_ngerti_geopolitik.application.commands import (
    CommandError,
    SetClipDurationCommand,
    SetClipPropertiesCommand,
    SetClipSpeedCommand,
)
from ai_ngerti_geopolitik.domain import (
    Clip,
    DomainValidationError,
    EffectProperties,
    ProjectState,
    PropertyValidationError,
    Track,
    TransitionProperties,
    VideoProperties,
)

TranslatedAutoEditCommand = SetClipPropertiesCommand | SetClipDurationCommand | SetClipSpeedCommand


@dataclass(frozen=True, slots=True)
class VerifiedAutoEditPlan:
    """Proof plus canonical manual-command translation for a W7 plan."""

    plan: AutoEditPlan
    candidate_semantic_hash: str
    candidate_revision: int
    command_count: int
    target_count: int
    selected_scope_count: int
    translated_commands: tuple[TranslatedAutoEditCommand, ...]

    @property
    def translated_command_types(self) -> tuple[str, ...]:
        return tuple(type(command).__name__ for command in self.translated_commands)


class AutoEditPlanVerifier:
    """Provider-agnostic W7 L2 semantic verifier."""

    __slots__ = ("_parser",)

    def __init__(self, parser: AutoEditPlanParser | None = None) -> None:
        self._parser = parser or AutoEditPlanParser()

    @staticmethod
    def _semantic_error(message: str) -> PlanContractError:
        return PlanContractError(PlanErrorCode.SEMANTIC_INVALID, message)

    @staticmethod
    def _clip_location(state: ProjectState, clip_id: str) -> tuple[Track, Clip]:
        for track in state.tracks:
            for clip in track.clips:
                if clip.clip_id == clip_id:
                    return track, clip
        raise PlanContractError(
            PlanErrorCode.SEMANTIC_INVALID,
            f"AutoEditPlan references an unknown target clip: {clip_id}",
        )

    def _validate_scope(self, state: ProjectState, scope: W7SelectedScope) -> frozenset[str]:
        for clip_id in scope.clip_ids:
            try:
                self._clip_location(state, clip_id)
            except PlanContractError as exc:
                raise self._semantic_error("W7 selected scope contains an unknown clip") from exc
        return frozenset(scope.clip_ids)

    def _validate_family_constraints(self, plan: AutoEditPlan) -> None:
        seen: set[tuple[str, W7CommandFamily]] = set()
        pacing: dict[str, set[W7CommandFamily]] = {}
        for proposal in plan.commands:
            definition = capability_for(proposal.command_type)
            key = (proposal.target_clip_id, definition.family)
            if key in seen:
                raise self._semantic_error(
                    "AutoEditPlan contains a duplicate command family for one target"
                )
            seen.add(key)
            if definition.family in {W7CommandFamily.DURATION, W7CommandFamily.SPEED}:
                families = pacing.setdefault(proposal.target_clip_id, set())
                families.add(definition.family)
                if len(families) > 1:
                    raise self._semantic_error(
                        "AutoEditPlan duration and speed conflict for one target"
                    )

    @staticmethod
    def _assert_general_lock(track: Track) -> None:
        if track.locked:
            raise PlanContractError(
                PlanErrorCode.LOCK_CONFLICT,
                "AutoEditPlan target track is locked",
            )

    @staticmethod
    def _assert_effect_lock(track: Track, clip: Clip) -> None:
        if track.locked or clip.properties.effects.locked:
            raise PlanContractError(
                PlanErrorCode.LOCK_CONFLICT,
                "AutoEditPlan effect target is locked",
            )

    def _translate_effects(
        self,
        proposal: EffectEditProposal,
        clip: Clip,
    ) -> SetClipPropertiesCommand:
        effects = clip.properties.effects
        updated = EffectProperties(
            enter_effect=(
                effects.enter_effect if proposal.enter_effect is None else proposal.enter_effect
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
        return SetClipPropertiesCommand(
            proposal.target_clip_id,
            replace(clip.properties, effects=updated),
        )

    def _translate_duration(
        self,
        proposal: DurationEditProposal,
        state: ProjectState,
        clip: Clip,
    ) -> SetClipDurationCommand:
        minimum, maximum = W7_POLICY_BOUNDS.duration_bounds(
            state.fps,
            clip.duration_frames,
        )
        if not minimum <= proposal.duration_frames <= maximum:
            raise self._semantic_error(
                "W7 duration is outside the dynamic 50..200 percent/half-second policy"
            )
        return SetClipDurationCommand(
            proposal.target_clip_id,
            proposal.duration_frames,
            ripple=True,
        )

    def _translate_speed(
        self,
        proposal: SpeedEditProposal,
    ) -> SetClipSpeedCommand:
        if not (
            W7_POLICY_BOUNDS.speed_min_percent
            <= proposal.rate_percent
            <= W7_POLICY_BOUNDS.speed_max_percent
        ):
            raise self._semantic_error("W7 speed is outside the 50..200 percent policy")
        return SetClipSpeedCommand(
            proposal.target_clip_id,
            proposal.rate_percent,
            ripple=True,
        )

    def _translate_transform(
        self,
        proposal: TransformEditProposal,
        state: ProjectState,
        clip: Clip,
    ) -> SetClipPropertiesCommand:
        (x_min, x_max), (y_min, y_max) = W7_POLICY_BOUNDS.transform_position_bounds(
            state.settings.width,
            state.settings.height,
        )
        if proposal.position_x is not None and not x_min <= proposal.position_x <= x_max:
            raise self._semantic_error("W7 transform position_x exceeds half canvas width")
        if proposal.position_y is not None and not y_min <= proposal.position_y <= y_max:
            raise self._semantic_error("W7 transform position_y exceeds half canvas height")

        video = clip.properties.video
        scale_x = video.scale_x_percent
        scale_y = video.scale_y_percent
        if proposal.scale_percent is not None:
            scale_x = proposal.scale_percent
            scale_y = proposal.scale_percent
        updated = VideoProperties(
            position_x=video.position_x if proposal.position_x is None else proposal.position_x,
            position_y=video.position_y if proposal.position_y is None else proposal.position_y,
            scale_x_percent=scale_x,
            scale_y_percent=scale_y,
            rotation_tenths=(
                video.rotation_tenths
                if proposal.rotation_tenths is None
                else proposal.rotation_tenths
            ),
            opacity_percent=(
                video.opacity_percent
                if proposal.opacity_percent is None
                else proposal.opacity_percent
            ),
            crop_left_percent=video.crop_left_percent,
            crop_top_percent=video.crop_top_percent,
            crop_right_percent=video.crop_right_percent,
            crop_bottom_percent=video.crop_bottom_percent,
        )
        return SetClipPropertiesCommand(
            proposal.target_clip_id,
            replace(clip.properties, video=updated),
        )

    def _translate_transition(
        self,
        proposal: TransitionEditProposal,
        state: ProjectState,
        clip: Clip,
    ) -> SetClipPropertiesCommand:
        if proposal.preset == "fade_black":
            maximum = W7_POLICY_BOUNDS.transition_max_frames(
                state.fps,
                clip.duration_frames,
            )
            if proposal.duration_frames > maximum:
                raise self._semantic_error(
                    "W7 fade_black duration exceeds candidate clip transition maximum"
                )
        updated = TransitionProperties(
            preset=proposal.preset,
            duration_frames=proposal.duration_frames,
        )
        return SetClipPropertiesCommand(
            proposal.target_clip_id,
            replace(clip.properties, transition=updated),
        )

    def _translate(
        self,
        proposal: AutoEditCommandProposal,
        state: ProjectState,
        track: Track,
        clip: Clip,
    ) -> TranslatedAutoEditCommand:
        if isinstance(proposal, EffectEditProposal):
            self._assert_effect_lock(track, clip)
            return self._translate_effects(proposal, clip)

        self._assert_general_lock(track)
        if isinstance(proposal, DurationEditProposal):
            return self._translate_duration(proposal, state, clip)
        if isinstance(proposal, SpeedEditProposal):
            return self._translate_speed(proposal)
        if isinstance(proposal, TransformEditProposal):
            return self._translate_transform(proposal, state, clip)
        if isinstance(proposal, TransitionEditProposal):
            return self._translate_transition(proposal, state, clip)
        raise self._semantic_error("AutoEditPlan proposal type is unsupported")

    def _assert_candidate_transition_policy(
        self,
        state: ProjectState,
        target_clip_id: str,
    ) -> None:
        clip = state.clip(target_clip_id)
        transition = clip.properties.transition
        if transition.preset != "fade_black":
            return
        maximum = W7_POLICY_BOUNDS.transition_max_frames(
            state.fps,
            clip.duration_frames,
        )
        if transition.duration_frames > maximum:
            raise self._semantic_error(
                "candidate pacing makes the clip transition exceed the W7 maximum"
            )

    def verify(
        self,
        plan: AutoEditPlan,
        state: ProjectState,
        scope: W7SelectedScope,
    ) -> VerifiedAutoEditPlan:
        state.validate()
        if plan.base_project_revision != state.revision:
            raise PlanContractError(
                PlanErrorCode.STALE_PLAN,
                "AutoEditPlan base project revision is stale",
            )

        allowed_targets = self._validate_scope(state, scope)
        self._validate_family_constraints(plan)

        working = state
        translated: list[TranslatedAutoEditCommand] = []
        targets: set[str] = set()

        for proposal in plan.commands:
            if proposal.target_clip_id not in allowed_targets:
                raise self._semantic_error(
                    "AutoEditPlan target is outside the application-selected scope"
                )

            track, clip = self._clip_location(working, proposal.target_clip_id)
            try:
                command = self._translate(proposal, working, track, clip)
                candidate = command.apply(working)
                candidate.validate()
                if isinstance(
                    proposal,
                    (DurationEditProposal, SpeedEditProposal, TransitionEditProposal),
                ):
                    self._assert_candidate_transition_policy(
                        candidate,
                        proposal.target_clip_id,
                    )
            except PlanContractError:
                raise
            except (CommandError, DomainValidationError, PropertyValidationError) as exc:
                raise self._semantic_error(
                    "AutoEditPlan failed canonical manual-command dry-run validation"
                ) from exc

            translated.append(command)
            targets.add(proposal.target_clip_id)
            working = candidate

        working.validate()
        return VerifiedAutoEditPlan(
            plan=plan,
            candidate_semantic_hash=working.semantic_hash(),
            candidate_revision=working.revision,
            command_count=len(plan.commands),
            target_count=len(targets),
            selected_scope_count=scope.target_count,
            translated_commands=tuple(translated),
        )

    def verify_payload(
        self,
        payload_json: str,
        state: ProjectState,
        scope: W7SelectedScope,
    ) -> VerifiedAutoEditPlan:
        return self.verify(self._parser.parse(payload_json), state, scope)

    def verify_response(
        self,
        response: ProviderPlanResponse,
        state: ProjectState,
        scope: W7SelectedScope,
    ) -> VerifiedAutoEditPlan:
        plan = self._parser.parse(response.payload_json)
        if plan.request_id != response.request_id:
            raise PlanContractError(
                PlanErrorCode.SEMANTIC_INVALID,
                "provider response request ID does not match AutoEditPlan request ID",
            )
        return self.verify(plan, state, scope)
