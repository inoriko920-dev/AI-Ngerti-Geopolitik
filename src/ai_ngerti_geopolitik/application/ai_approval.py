"""Shared W6/W7 explicit approval boundary and atomic CommandBatch application.

Provider results never mutate canonical ProjectState directly. W6 L1 and W7 L2
both stage verified results, require explicit approval, revalidate against the
current semantic base, then execute exactly one canonical CommandBatch. W7-010
closure regression reuses this owner unchanged.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import StrEnum

from ai_ngerti_geopolitik.application.ai_contracts import (
    AIRequestProfile,
    EditPlan,
    EffectEditProposal,
    PlanContractError,
    PlanErrorCode,
)
from ai_ngerti_geopolitik.application.ai_jobs import AIPlanJobService
from ai_ngerti_geopolitik.application.ai_l2_contracts import (
    AutoEditPlan,
    DurationEditProposal,
    SpeedEditProposal,
    TransformEditProposal,
    TransitionEditProposal,
)
from ai_ngerti_geopolitik.application.ai_l2_scope import W7SelectedScope
from ai_ngerti_geopolitik.application.ai_l2_verifier import (
    AutoEditPlanVerifier,
    VerifiedAutoEditPlan,
)
from ai_ngerti_geopolitik.application.ai_plan_verifier import (
    PlanVerifier,
    VerifiedEditPlan,
)
from ai_ngerti_geopolitik.application.commands import (
    Command,
    CommandBatch,
    CommandBus,
    SetClipPropertiesCommand,
    StaleRevisionError,
)
from ai_ngerti_geopolitik.domain import Clip, EffectProperties, ProjectState

_MAX_DIFF_TEXT = 180
_MAX_DIFF_DISPLAY = 280


class AIApprovalState(StrEnum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
    APPLIED = "APPLIED"


class AIApprovalError(RuntimeError):
    """Safe approval-lifecycle failure."""

    def __init__(self, safe_message: str) -> None:
        self.safe_message = safe_message.strip() or "AI plan approval failed"
        super().__init__(self.safe_message)


@dataclass(frozen=True, slots=True)
class AIApprovalSnapshot:
    approval_id: str
    job_id: str
    request_id: str
    state: AIApprovalState
    base_project_revision: int
    summary: str
    command_count: int
    batch_id: str | None = None
    applied_revision: int | None = None


@dataclass(frozen=True, slots=True)
class AIPlanDiffEntry:
    """Bounded W7 before/after text for one verified command."""

    target_clip_id: str
    command_type: str
    before_text: str
    after_text: str

    def __post_init__(self) -> None:
        for name, value in (
            ("target_clip_id", self.target_clip_id),
            ("command_type", self.command_type),
            ("before_text", self.before_text),
            ("after_text", self.after_text),
        ):
            if not value.strip():
                raise ValueError(f"AI plan diff {name} is required")
        if len(self.before_text) > _MAX_DIFF_TEXT or len(self.after_text) > _MAX_DIFF_TEXT:
            raise ValueError("AI plan diff text exceeds bounded UI size")

    @property
    def display_text(self) -> str:
        value = (
            f"{self.target_clip_id} · {self.command_type} · {self.before_text} → {self.after_text}"
        )
        if len(value) <= _MAX_DIFF_DISPLAY:
            return value
        return value[: _MAX_DIFF_DISPLAY - 1] + "…"


VerifiedApprovalPlan = VerifiedEditPlan | VerifiedAutoEditPlan
ApprovalPlan = EditPlan | AutoEditPlan


@dataclass(slots=True)
class _ApprovalRecord:
    approval_id: str
    job_id: str
    verified: VerifiedApprovalPlan
    profile: AIRequestProfile
    project_id: str
    base_semantic_hash: str
    diffs: tuple[AIPlanDiffEntry, ...] = ()
    state: AIApprovalState = AIApprovalState.PENDING
    batch_id: str | None = None
    applied_revision: int | None = None


def _effect_diff(
    proposal: EffectEditProposal,
    before: Clip,
    after: Clip,
) -> tuple[str, str]:
    before_values: list[str] = []
    after_values: list[str] = []
    old = before.properties.effects
    new = after.properties.effects
    if proposal.enter_effect is not None:
        before_values.append(f"enter={old.enter_effect}")
        after_values.append(f"enter={new.enter_effect}")
    if proposal.exit_effect is not None:
        before_values.append(f"exit={old.exit_effect}")
        after_values.append(f"exit={new.exit_effect}")
    if proposal.intensity_percent is not None:
        before_values.append(f"intensity={old.intensity_percent}%")
        after_values.append(f"intensity={new.intensity_percent}%")
    return f"effects[{', '.join(before_values)}]", f"effects[{', '.join(after_values)}]"


def _transform_diff(
    proposal: TransformEditProposal,
    before: Clip,
    after: Clip,
) -> tuple[str, str]:
    old = before.properties.video
    new = after.properties.video
    before_values: list[str] = []
    after_values: list[str] = []

    if proposal.position_x is not None:
        before_values.append(f"x={old.position_x}")
        after_values.append(f"x={new.position_x}")
    if proposal.position_y is not None:
        before_values.append(f"y={old.position_y}")
        after_values.append(f"y={new.position_y}")
    if proposal.scale_percent is not None:
        before_values.append(f"scale={old.scale_x_percent}%")
        after_values.append(f"scale={new.scale_x_percent}%")
    if proposal.rotation_tenths is not None:
        before_values.append(f"rotation={old.rotation_tenths / 10:.1f}°")
        after_values.append(f"rotation={new.rotation_tenths / 10:.1f}°")
    if proposal.opacity_percent is not None:
        before_values.append(f"opacity={old.opacity_percent}%")
        after_values.append(f"opacity={new.opacity_percent}%")
    return (
        f"transform[{', '.join(before_values)}]",
        f"transform[{', '.join(after_values)}]",
    )


def _l2_diff_text(
    proposal: object,
    before: Clip,
    after: Clip,
) -> tuple[str, str]:
    if isinstance(proposal, EffectEditProposal):
        return _effect_diff(proposal, before, after)
    if isinstance(proposal, DurationEditProposal):
        return (
            f"duration={before.duration_frames}f",
            f"duration={after.duration_frames}f",
        )
    if isinstance(proposal, SpeedEditProposal):
        return (
            f"speed={before.properties.speed.rate_percent}%, duration={before.duration_frames}f",
            f"speed={after.properties.speed.rate_percent}%, duration={after.duration_frames}f",
        )
    if isinstance(proposal, TransformEditProposal):
        return _transform_diff(proposal, before, after)
    if isinstance(proposal, TransitionEditProposal):
        old = before.properties.transition
        new = after.properties.transition
        return (
            f"transition={old.preset}/{old.duration_frames}f",
            f"transition={new.preset}/{new.duration_frames}f",
        )
    raise AIApprovalError("unsupported W7 proposal while building approval diff")


class AIPlanApprovalService:
    """Single explicit approval owner reused by W6 L1 and W7 L2."""

    __slots__ = (
        "_bus",
        "_job_to_approval",
        "_jobs",
        "_l2_verifier",
        "_records",
        "_verifier",
    )

    def __init__(
        self,
        jobs: AIPlanJobService,
        bus: CommandBus,
        verifier: PlanVerifier | None = None,
        l2_verifier: AutoEditPlanVerifier | None = None,
    ) -> None:
        self._jobs = jobs
        self._bus = bus
        self._verifier = verifier or PlanVerifier()
        self._l2_verifier = l2_verifier or AutoEditPlanVerifier()
        self._records: dict[str, _ApprovalRecord] = {}
        self._job_to_approval: dict[str, str] = {}

    @staticmethod
    def _snapshot(record: _ApprovalRecord) -> AIApprovalSnapshot:
        plan = record.verified.plan
        return AIApprovalSnapshot(
            approval_id=record.approval_id,
            job_id=record.job_id,
            request_id=plan.request_id,
            state=record.state,
            base_project_revision=plan.base_project_revision,
            summary=plan.summary,
            command_count=len(plan.commands),
            batch_id=record.batch_id,
            applied_revision=record.applied_revision,
        )

    def _record(self, approval_id: str) -> _ApprovalRecord:
        try:
            return self._records[approval_id]
        except KeyError as exc:
            raise AIApprovalError("unknown AI approval id") from exc

    def snapshot(self, approval_id: str) -> AIApprovalSnapshot:
        return self._snapshot(self._record(approval_id))

    def diff_entries(self, approval_id: str) -> tuple[AIPlanDiffEntry, ...]:
        return self._record(approval_id).diffs

    def diff_texts(self, approval_id: str) -> tuple[str, ...]:
        return tuple(item.display_text for item in self.diff_entries(approval_id))

    @staticmethod
    def _allowed_targets(plan: ApprovalPlan) -> tuple[str, ...]:
        return tuple(dict.fromkeys(item.target_clip_id for item in plan.commands))

    @staticmethod
    def _apply_commands(
        state: ProjectState,
        commands: tuple[Command, ...],
    ) -> ProjectState:
        working = state
        for command in commands:
            working = command.apply(working)
            working.validate()
        return working

    @staticmethod
    def _translate_l1_commands(
        plan: EditPlan,
        state: ProjectState,
    ) -> tuple[tuple[Command, ...], ProjectState]:
        commands: list[Command] = []
        working = state

        for proposal in plan.commands:
            clip = working.clip(proposal.target_clip_id)
            effects = clip.properties.effects
            updated_effects = EffectProperties(
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
            command = SetClipPropertiesCommand(
                clip_id=proposal.target_clip_id,
                properties=replace(clip.properties, effects=updated_effects),
            )
            working = command.apply(working)
            commands.append(command)

        return tuple(commands), working

    @staticmethod
    def _build_l2_diffs(
        verified: VerifiedAutoEditPlan,
        state: ProjectState,
    ) -> tuple[AIPlanDiffEntry, ...]:
        if len(verified.plan.commands) != len(verified.translated_commands):
            raise AIApprovalError("W7 verified plan translation cardinality changed")

        working = state
        diffs: list[AIPlanDiffEntry] = []
        for proposal, command in zip(
            verified.plan.commands,
            verified.translated_commands,
            strict=True,
        ):
            before = working.clip(proposal.target_clip_id)
            candidate = command.apply(working)
            candidate.validate()
            after = candidate.clip(proposal.target_clip_id)
            before_text, after_text = _l2_diff_text(proposal, before, after)
            diffs.append(
                AIPlanDiffEntry(
                    target_clip_id=proposal.target_clip_id,
                    command_type=proposal.command_type,
                    before_text=before_text,
                    after_text=after_text,
                )
            )
            working = candidate

        if working.semantic_hash() != verified.candidate_semantic_hash:
            raise AIApprovalError("W7 approval diff diverged from verified candidate")
        return tuple(diffs)

    def _stage_verified(
        self,
        job_id: str,
        verified: VerifiedApprovalPlan,
        current: ProjectState,
        profile: AIRequestProfile,
        diffs: tuple[AIPlanDiffEntry, ...] = (),
    ) -> AIApprovalSnapshot:
        plan = verified.plan
        if plan.base_project_revision != current.revision:
            raise PlanContractError(
                PlanErrorCode.STALE_PLAN,
                "verified AI plan is stale before approval staging",
            )

        approval_id = f"AI-APPROVAL:{plan.request_id}"
        if approval_id in self._records:
            raise AIApprovalError("AI approval id already exists")

        record = _ApprovalRecord(
            approval_id=approval_id,
            job_id=job_id,
            verified=verified,
            profile=profile,
            project_id=current.project_id,
            base_semantic_hash=current.semantic_hash(),
            diffs=diffs,
        )
        self._records[approval_id] = record
        self._job_to_approval[job_id] = approval_id
        return self._snapshot(record)

    def stage_from_job(self, job_id: str, *, session_id: str) -> AIApprovalSnapshot:
        if job_id in self._job_to_approval:
            raise AIApprovalError("AI plan job was already staged for approval")

        current = self._bus.state
        verified = self._jobs.take_verified(
            job_id,
            current,
            session_id=session_id,
        )
        return self._stage_verified(
            job_id,
            verified,
            current,
            AIRequestProfile.L1_EFFECTS,
        )

    def stage_from_job_l2(self, job_id: str, *, session_id: str) -> AIApprovalSnapshot:
        if job_id in self._job_to_approval:
            raise AIApprovalError("AI plan job was already staged for approval")

        current = self._bus.state
        verified = self._jobs.take_verified_l2(
            job_id,
            current,
            session_id=session_id,
        )
        diffs = self._build_l2_diffs(verified, current)
        return self._stage_verified(
            job_id,
            verified,
            current,
            AIRequestProfile.L2_AUTO_EDIT,
            diffs,
        )

    def approve(self, approval_id: str) -> AIApprovalSnapshot:
        record = self._record(approval_id)
        if record.state is not AIApprovalState.PENDING:
            raise AIApprovalError("only a pending AI plan may be approved")
        record.state = AIApprovalState.APPROVED
        return self._snapshot(record)

    def reject(self, approval_id: str) -> AIApprovalSnapshot:
        record = self._record(approval_id)
        if record.state is not AIApprovalState.PENDING:
            raise AIApprovalError("only a pending AI plan may be rejected")
        record.state = AIApprovalState.REJECTED
        return self._snapshot(record)

    def cancel(self, approval_id: str) -> AIApprovalSnapshot:
        record = self._record(approval_id)
        if record.state not in {AIApprovalState.PENDING, AIApprovalState.APPROVED}:
            raise AIApprovalError("AI plan cannot be cancelled from its current state")
        record.state = AIApprovalState.CANCELLED
        return self._snapshot(record)

    def _assert_current_base(self, record: _ApprovalRecord) -> ProjectState:
        current = self._bus.state
        plan = record.verified.plan
        if (
            current.project_id != record.project_id
            or current.revision != plan.base_project_revision
            or current.semantic_hash() != record.base_semantic_hash
        ):
            raise PlanContractError(
                PlanErrorCode.STALE_PLAN,
                "AI plan became stale before approval apply",
            )
        return current

    def _reverify_l1(
        self,
        record: _ApprovalRecord,
        current: ProjectState,
    ) -> tuple[tuple[Command, ...], str]:
        if not isinstance(record.verified, VerifiedEditPlan):
            raise AIApprovalError("L1 approval record has the wrong verified plan type")
        plan = record.verified.plan
        reverified = self._verifier.verify(
            plan,
            current,
            self._allowed_targets(plan),
        )
        if reverified.candidate_semantic_hash != record.verified.candidate_semantic_hash:
            raise PlanContractError(
                PlanErrorCode.STALE_PLAN,
                "AI plan candidate changed before apply",
            )

        commands, candidate = self._translate_l1_commands(plan, current)
        if candidate.semantic_hash() != reverified.candidate_semantic_hash:
            raise AIApprovalError("AI plan command translation diverged from verified candidate")
        return commands, "AI L1"

    def _reverify_l2(
        self,
        record: _ApprovalRecord,
        current: ProjectState,
    ) -> tuple[tuple[Command, ...], str]:
        if not isinstance(record.verified, VerifiedAutoEditPlan):
            raise AIApprovalError("L2 approval record has the wrong verified plan type")
        plan = record.verified.plan
        scope = W7SelectedScope(self._allowed_targets(plan))
        reverified = self._l2_verifier.verify(plan, current, scope)
        if reverified.candidate_semantic_hash != record.verified.candidate_semantic_hash:
            raise PlanContractError(
                PlanErrorCode.STALE_PLAN,
                "AI L2 candidate changed before apply",
            )

        commands: tuple[Command, ...] = tuple(reverified.translated_commands)
        candidate = self._apply_commands(current, commands)
        if candidate.semantic_hash() != reverified.candidate_semantic_hash:
            raise AIApprovalError("AI L2 command translation diverged from verified candidate")
        return commands, "AI L2"

    def apply(self, approval_id: str) -> AIApprovalSnapshot:
        record = self._record(approval_id)
        if record.state is not AIApprovalState.APPROVED:
            raise AIApprovalError("AI plan requires explicit approval before apply")

        current = self._assert_current_base(record)
        if record.profile is AIRequestProfile.L1_EFFECTS:
            commands, label_prefix = self._reverify_l1(record, current)
        elif record.profile is AIRequestProfile.L2_AUTO_EDIT:
            commands, label_prefix = self._reverify_l2(record, current)
        else:
            raise AIApprovalError("AI approval profile is unsupported")

        plan = record.verified.plan
        batch_id = f"AI-BATCH:{plan.request_id}"
        batch = CommandBatch(
            batch_id=batch_id,
            label=f"{label_prefix}: {plan.summary}",
            actor="ai",
            expected_revision=current.revision,
            commands=commands,
        )
        try:
            applied = self._bus.execute(batch)
        except StaleRevisionError as exc:
            raise PlanContractError(
                PlanErrorCode.STALE_PLAN,
                "AI plan became stale during atomic apply",
            ) from exc

        record.state = AIApprovalState.APPLIED
        record.batch_id = batch_id
        record.applied_revision = applied.revision
        return self._snapshot(record)
