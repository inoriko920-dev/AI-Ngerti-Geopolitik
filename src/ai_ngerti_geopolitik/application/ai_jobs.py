"""Provider-agnostic W6-007 background lifecycle for L1 plan generation."""

from __future__ import annotations

from concurrent.futures import CancelledError, Future, ThreadPoolExecutor
from dataclasses import dataclass
from threading import Event, Lock

from ai_ngerti_geopolitik.application.ai_contracts import (
    AIJobState,
    AIProviderRequest,
    AIRequestProfile,
    CredentialContractError,
    CredentialErrorCode,
    PlanContractError,
    PlanErrorCode,
    ProviderContractError,
    ProviderErrorCode,
)
from ai_ngerti_geopolitik.application.ai_context import ContextBuildError
from ai_ngerti_geopolitik.application.ai_l2_scope import W7SelectedScope
from ai_ngerti_geopolitik.application.ai_l2_verifier import (
    AutoEditPlanVerifier,
    VerifiedAutoEditPlan,
)
from ai_ngerti_geopolitik.application.ai_plan_verifier import PlanVerifier, VerifiedEditPlan
from ai_ngerti_geopolitik.application.credential_pool import CredentialPoolService
from ai_ngerti_geopolitik.application.ports import AIProviderPort
from ai_ngerti_geopolitik.domain import ProjectState


class AIPlanJobAccessError(RuntimeError):
    """Safe lifecycle access failure; contains no provider payload or credential."""

    def __init__(self, safe_message: str) -> None:
        self.safe_message = safe_message.strip() or "AI plan job access failed"
        super().__init__(self.safe_message)


class CancellationFlag:
    """Thread-safe best-effort cancellation token shared with provider adapters."""

    __slots__ = ("_event",)

    def __init__(self) -> None:
        self._event = Event()

    @property
    def cancelled(self) -> bool:
        return self._event.is_set()

    def cancel(self) -> None:
        self._event.set()


@dataclass(frozen=True, slots=True)
class AIPlanJobToken:
    project_id: str
    session_id: str
    base_project_revision: int

    def __post_init__(self) -> None:
        if not self.project_id.strip():
            raise ValueError("AI job project id is required")
        if not self.session_id.strip():
            raise ValueError("AI job session id is required")
        if self.base_project_revision < 0:
            raise ValueError("AI job base project revision must be non-negative")


@dataclass(frozen=True, slots=True)
class AIPlanJobSnapshot:
    job_id: str
    request_id: str
    state: AIJobState
    token: AIPlanJobToken
    provider_error: ProviderErrorCode | None = None
    plan_error: PlanErrorCode | None = None
    credential_error: CredentialErrorCode | None = None
    safe_message: str | None = None
    result_consumed: bool = False


VerifiedPlanResult = VerifiedEditPlan | VerifiedAutoEditPlan


@dataclass(slots=True)
class _JobRecord:
    job_id: str
    request: AIProviderRequest
    token: AIPlanJobToken
    cancellation: CancellationFlag
    state: AIJobState = AIJobState.QUEUED
    provider_error: ProviderErrorCode | None = None
    plan_error: PlanErrorCode | None = None
    credential_error: CredentialErrorCode | None = None
    safe_message: str | None = None
    verified: VerifiedPlanResult | None = None
    result_consumed: bool = False
    future: Future[None] | None = None


class AIPlanJobService:
    """Runs provider work off the caller thread and never applies canonical edits."""

    __slots__ = (
        "_executor",
        "_jobs",
        "_l2_verifier",
        "_lock",
        "_owns_executor",
        "_pool",
        "_provider",
        "_verifier",
    )

    def __init__(
        self,
        provider: AIProviderPort,
        pool: CredentialPoolService,
        verifier: PlanVerifier | None = None,
        l2_verifier: AutoEditPlanVerifier | None = None,
        *,
        executor: ThreadPoolExecutor | None = None,
        max_workers: int = 1,
    ) -> None:
        if max_workers != 1:
            raise ValueError("W6 AI provider lifecycle requires exactly one background worker")
        self._provider = provider
        self._pool = pool
        self._verifier = verifier or PlanVerifier()
        self._l2_verifier = l2_verifier or AutoEditPlanVerifier()
        self._executor = executor or ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="ang-ai-provider",
        )
        self._owns_executor = executor is None
        self._lock = Lock()
        self._jobs: dict[str, _JobRecord] = {}

    def __enter__(self) -> AIPlanJobService:
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        del exc_type, exc, traceback
        self.shutdown()

    @staticmethod
    def _snapshot(record: _JobRecord) -> AIPlanJobSnapshot:
        return AIPlanJobSnapshot(
            job_id=record.job_id,
            request_id=record.request.request_id,
            state=record.state,
            token=record.token,
            provider_error=record.provider_error,
            plan_error=record.plan_error,
            credential_error=record.credential_error,
            safe_message=record.safe_message,
            result_consumed=record.result_consumed,
        )

    def submit(
        self,
        request: AIProviderRequest,
        state: ProjectState,
        allowed_target_ids: tuple[str, ...],
        *,
        session_id: str,
    ) -> AIPlanJobSnapshot:
        state.validate()
        if request.base_project_revision != state.revision:
            raise PlanContractError(
                PlanErrorCode.STALE_PLAN,
                "provider request base revision does not match current project",
            )
        token = AIPlanJobToken(
            project_id=state.project_id,
            session_id=session_id,
            base_project_revision=state.revision,
        )
        job_id = request.request_id
        cancellation = CancellationFlag()
        record = _JobRecord(job_id, request, token, cancellation)

        with self._lock:
            if job_id in self._jobs:
                raise AIPlanJobAccessError("duplicate AI plan job id")
            self._jobs[job_id] = record

        try:
            future = self._executor.submit(
                self._run_job,
                job_id,
                state,
                allowed_target_ids,
            )
        except Exception:
            with self._lock:
                self._jobs.pop(job_id, None)
            raise
        with self._lock:
            record.future = future
            return self._snapshot(record)

    def _record(self, job_id: str) -> _JobRecord:
        try:
            return self._jobs[job_id]
        except KeyError as exc:
            raise AIPlanJobAccessError("unknown AI plan job id") from exc

    def snapshot(self, job_id: str) -> AIPlanJobSnapshot:
        with self._lock:
            return self._snapshot(self._record(job_id))

    def _mark_running(self, record: _JobRecord) -> bool:
        with self._lock:
            if record.cancellation.cancelled:
                record.state = AIJobState.CANCELLED
                record.safe_message = "AI plan job cancelled"
                return False
            record.state = AIJobState.RUNNING
            return True

    def _mark_cancelled(self, record: _JobRecord) -> None:
        with self._lock:
            record.state = AIJobState.CANCELLED
            record.safe_message = "AI plan job cancelled"
            record.verified = None

    def _mark_provider_failed(
        self,
        record: _JobRecord,
        error: ProviderContractError,
    ) -> None:
        with self._lock:
            record.state = AIJobState.FAILED
            record.provider_error = error.code
            record.safe_message = error.safe_message
            record.verified = None

    def _mark_plan_failed(
        self,
        record: _JobRecord,
        error: PlanContractError,
    ) -> None:
        with self._lock:
            record.state = AIJobState.FAILED
            record.plan_error = error.code
            record.safe_message = error.safe_message
            record.verified = None

    def _mark_credential_failed(
        self,
        record: _JobRecord,
        error: CredentialContractError,
    ) -> None:
        with self._lock:
            record.state = AIJobState.FAILED
            record.credential_error = error.code
            record.safe_message = error.safe_message
            record.verified = None

    def _mark_success(self, record: _JobRecord, verified: VerifiedPlanResult) -> None:
        with self._lock:
            if record.cancellation.cancelled:
                record.state = AIJobState.CANCELLED
                record.safe_message = "AI plan job cancelled"
                record.verified = None
                return
            record.state = AIJobState.SUCCESS
            record.safe_message = None
            record.verified = verified

    def _verify_response(
        self,
        record: _JobRecord,
        response: object,
        state: ProjectState,
        allowed_target_ids: tuple[str, ...],
    ) -> VerifiedPlanResult:
        from ai_ngerti_geopolitik.application.ai_contracts import ProviderPlanResponse

        if not isinstance(response, ProviderPlanResponse):
            raise PlanContractError(
                PlanErrorCode.SCHEMA_INVALID,
                "provider response type is invalid",
            )
        if record.request.profile is AIRequestProfile.L1_EFFECTS:
            return self._verifier.verify_response(
                response,
                state,
                allowed_target_ids,
            )
        if record.request.profile is AIRequestProfile.L2_AUTO_EDIT:
            try:
                scope = W7SelectedScope(allowed_target_ids)
            except ContextBuildError as exc:
                raise PlanContractError(
                    PlanErrorCode.SEMANTIC_INVALID,
                    exc.safe_message,
                ) from exc
            return self._l2_verifier.verify_response(
                response,
                state,
                scope,
            )
        raise PlanContractError(
            PlanErrorCode.SCHEMA_INVALID,
            "AI plan job request profile is unsupported",
        )

    def _run_job(
        self,
        job_id: str,
        state: ProjectState,
        allowed_target_ids: tuple[str, ...],
    ) -> None:
        with self._lock:
            record = self._record(job_id)
        if not self._mark_running(record):
            return

        session = self._pool.start_session()
        while True:
            if record.cancellation.cancelled:
                self._mark_cancelled(record)
                return

            try:
                lease = session.next_credential()
            except CredentialContractError as exc:
                self._mark_credential_failed(record, exc)
                return
            except ProviderContractError as exc:
                self._mark_provider_failed(record, exc)
                return

            try:
                response = self._provider.request_plan(
                    record.request,
                    lease.secret,
                    record.cancellation,
                )
            except CancelledError:
                self._mark_cancelled(record)
                return
            except ProviderContractError as exc:
                if record.cancellation.cancelled:
                    self._mark_cancelled(record)
                    return
                if exc.code in {
                    ProviderErrorCode.INVALID_AUTH,
                    ProviderErrorCode.NETWORK_TIMEOUT,
                }:
                    session.report_error(exc.code)
                    continue
                if exc.code is ProviderErrorCode.RATE_LIMIT_OR_QUOTA:
                    session.report_error(exc.code)
                self._mark_provider_failed(record, exc)
                return
            except Exception:
                self._mark_provider_failed(
                    record,
                    ProviderContractError(
                        ProviderErrorCode.MALFORMED_RESPONSE,
                        "provider job failed safely",
                    ),
                )
                return

            if record.cancellation.cancelled:
                self._mark_cancelled(record)
                return

            session.report_success()
            try:
                verified = self._verify_response(
                    record,
                    response,
                    state,
                    allowed_target_ids,
                )
            except PlanContractError as exc:
                self._mark_plan_failed(record, exc)
                return
            self._mark_success(record, verified)
            return

    def cancel(self, job_id: str) -> bool:
        with self._lock:
            record = self._record(job_id)
            if record.state in {
                AIJobState.SUCCESS,
                AIJobState.FAILED,
                AIJobState.CANCELLED,
            }:
                return False
            record.cancellation.cancel()
            future = record.future
            if future is not None and future.cancel():
                record.state = AIJobState.CANCELLED
                record.safe_message = "AI plan job cancelled"
            return True

    def take_verified(
        self,
        job_id: str,
        current_state: ProjectState,
        *,
        session_id: str,
    ) -> VerifiedEditPlan:
        current_state.validate()
        with self._lock:
            record = self._record(job_id)
            if record.state is not AIJobState.SUCCESS or record.verified is None:
                raise AIPlanJobAccessError("AI plan job has no successful verified result")
            if record.result_consumed:
                raise AIPlanJobAccessError("verified AI plan result was already consumed")
            token = record.token
            if (
                current_state.project_id != token.project_id
                or current_state.revision != token.base_project_revision
                or session_id != token.session_id
            ):
                raise PlanContractError(
                    PlanErrorCode.STALE_PLAN,
                    "AI plan result is stale for the current project session",
                )
            if (
                record.request.profile is not AIRequestProfile.L1_EFFECTS
                or not isinstance(record.verified, VerifiedEditPlan)
            ):
                raise AIPlanJobAccessError(
                    "AI plan job result is not an L1 verified plan"
                )
            record.result_consumed = True
            return record.verified

    def take_verified_l2(
        self,
        job_id: str,
        current_state: ProjectState,
        *,
        session_id: str,
    ) -> VerifiedAutoEditPlan:
        current_state.validate()
        with self._lock:
            record = self._record(job_id)
            if record.state is not AIJobState.SUCCESS or record.verified is None:
                raise AIPlanJobAccessError(
                    "AI plan job has no successful verified result"
                )
            if record.result_consumed:
                raise AIPlanJobAccessError(
                    "verified AI plan result was already consumed"
                )
            token = record.token
            if (
                current_state.project_id != token.project_id
                or current_state.revision != token.base_project_revision
                or session_id != token.session_id
            ):
                raise PlanContractError(
                    PlanErrorCode.STALE_PLAN,
                    "AI plan result is stale for the current project session",
                )
            if (
                record.request.profile is not AIRequestProfile.L2_AUTO_EDIT
                or not isinstance(record.verified, VerifiedAutoEditPlan)
            ):
                raise AIPlanJobAccessError(
                    "AI plan job result is not an L2 verified plan"
                )
            record.result_consumed = True
            return record.verified

    def shutdown(self, *, wait: bool = True) -> None:
        with self._lock:
            records = tuple(self._jobs.values())
        for record in records:
            if record.state in {AIJobState.QUEUED, AIJobState.RUNNING}:
                record.cancellation.cancel()
        if self._owns_executor:
            self._executor.shutdown(wait=wait, cancel_futures=True)
