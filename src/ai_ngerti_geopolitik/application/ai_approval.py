"""W6-008 approval boundary and atomic CommandBatch application.

Only a W6-007 job result that has already passed W6-006 PlanVerifier may enter this
service. Staging and approval are non-mutating. Canonical mutation occurs only after
explicit approval and one final stale/semantic/lock revalidation.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import StrEnum

from ai_ngerti_geopolitik.application.ai_contracts import (
    EditPlan,
    PlanContractError,
    PlanErrorCode,
)
from ai_ngerti_geopolitik.application.ai_jobs import AIPlanJobService
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
from ai_ngerti_geopolitik.domain import EffectProperties, ProjectState


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


@dataclass(slots=True)
class _ApprovalRecord:
    approval_id: str
    job_id: str
    verified: VerifiedEditPlan
    project_id: str
    base_semantic_hash: str
    state: AIApprovalState = AIApprovalState.PENDING
    batch_id: str | None = None
    applied_revision: int | None = None


class AIPlanApprovalService:
    """Explicit W6 approval owner; no UI and no provider responsibilities."""

    __slots__ = ("_bus", "_job_to_approval", "_jobs", "_records", "_verifier")

    def __init__(
        self,
        jobs: AIPlanJobService,
        bus: CommandBus,
        verifier: PlanVerifier | None = None,
    ) -> None:
        self._jobs = jobs
        self._bus = bus
        self._verifier = verifier or PlanVerifier()
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

    def stage_from_job(self, job_id: str, *, session_id: str) -> AIApprovalSnapshot:
        if job_id in self._job_to_approval:
            raise AIApprovalError("AI plan job was already staged for approval")

        current = self._bus.state
        verified = self._jobs.take_verified(
            job_id,
            current,
            session_id=session_id,
        )
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
            project_id=current.project_id,
            base_semantic_hash=current.semantic_hash(),
        )
        self._records[approval_id] = record
        self._job_to_approval[job_id] = approval_id
        return self._snapshot(record)

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

    @staticmethod
    def _allowed_targets(plan: EditPlan) -> tuple[str, ...]:
        return tuple(dict.fromkeys(item.target_clip_id for item in plan.commands))

    @staticmethod
    def _translate_commands(
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

    def apply(self, approval_id: str) -> AIApprovalSnapshot:
        record = self._record(approval_id)
        if record.state is not AIApprovalState.APPROVED:
            raise AIApprovalError("AI plan requires explicit approval before apply")

        current = self._assert_current_base(record)
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

        commands, candidate = self._translate_commands(plan, current)
        if candidate.semantic_hash() != reverified.candidate_semantic_hash:
            raise AIApprovalError("AI plan command translation diverged from verified candidate")

        batch_id = f"AI-BATCH:{plan.request_id}"
        batch = CommandBatch(
            batch_id=batch_id,
            label=f"AI L1: {plan.summary}",
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
