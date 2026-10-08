"""W8-009 opt-in bounded structured diagnostics without private content.

Only fixed enum labels and bounded numeric counters enter an exported record.
No free-text messages, paths, project IDs, media, exception args or credentials.
The optional support ZIP contains only aggregate event types and bounded counts.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from enum import StrEnum

from ai_ngerti_geopolitik.application.persistence_failure import PersistenceError, PersistenceStage
from ai_ngerti_geopolitik.application.validation import ValidationResult


class DiagnosticCode(StrEnum):
    PROJECT_OPEN = "PROJECT_OPEN"
    PROJECT_SAVE = "PROJECT_SAVE"
    PROJECT_SAVE_FAILED = "PROJECT_SAVE_FAILED"
    VALIDATION_RUN = "VALIDATION_RUN"
    RELINK_SCAN = "RELINK_SCAN"
    RECOVERY_DECISION = "RECOVERY_DECISION"
    EXPORT_JOB = "EXPORT_JOB"


class DiagnosticStatus(StrEnum):
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    STALE = "STALE"
    CANCELLED = "CANCELLED"


class DiagnosticErrorCode(StrEnum):
    INVALID_INPUT = "INVALID_INPUT"
    OUTPUT_EXISTS = "OUTPUT_EXISTS"
    OUTPUT_UNAVAILABLE = "OUTPUT_UNAVAILABLE"
    SIZE_LIMIT = "SIZE_LIMIT"
    CANCELLED = "CANCELLED"
    UNKNOWN_JOB = "UNKNOWN_JOB"


class DiagnosticError(RuntimeError):
    """Typed public error, never includes filesystem paths or raw exception text."""

    def __init__(self, code: DiagnosticErrorCode) -> None:
        self.code = code
        super().__init__(f"diagnostic bundle failed: {code.value}")


@dataclass(frozen=True, slots=True)
class DiagnosticEvent:
    sequence: int
    code: DiagnosticCode
    status: DiagnosticStatus
    count: int
    persistence_stage: PersistenceStage | None


@dataclass(frozen=True, slots=True)
class DiagnosticSnapshot:
    events: tuple[DiagnosticEvent, ...]
    dropped_count: int


class DiagnosticLedger:
    """Thread-safe snapshots are handled by the caller; this is an opt-in log."""

    def __init__(self, *, limit: int = 256) -> None:
        if not 1 <= limit <= 256:
            raise DiagnosticError(DiagnosticErrorCode.INVALID_INPUT)
        self._events: deque[DiagnosticEvent] = deque(maxlen=limit)
        self._sequence = 0
        self._dropped = 0

    def record(
        self,
        code: DiagnosticCode,
        status: DiagnosticStatus,
        *,
        count: int = 0,
        persistence_stage: PersistenceStage | None = None,
    ) -> DiagnosticEvent:
        if (
            not isinstance(code, DiagnosticCode)
            or not isinstance(status, DiagnosticStatus)
            or type(count) is not int
            or not 0 <= count <= 10_000
            or (
                persistence_stage is not None
                and not isinstance(persistence_stage, PersistenceStage)
            )
        ):
            raise DiagnosticError(DiagnosticErrorCode.INVALID_INPUT)
        self._sequence += 1
        if len(self._events) == self._events.maxlen:
            self._dropped += 1
        event = DiagnosticEvent(self._sequence, code, status, count, persistence_stage)
        self._events.append(event)
        return event

    def record_save_failure(self, error: PersistenceError) -> DiagnosticEvent:
        if not isinstance(error, PersistenceError):
            raise DiagnosticError(DiagnosticErrorCode.INVALID_INPUT)
        # Do not read or export exception args / cause, including raw OS paths.
        return self.record(
            DiagnosticCode.PROJECT_SAVE_FAILED,
            DiagnosticStatus.FAILED,
            persistence_stage=error.stage,
        )

    def record_validation(self, result: ValidationResult) -> DiagnosticEvent:
        if not isinstance(result, ValidationResult):
            raise DiagnosticError(DiagnosticErrorCode.INVALID_INPUT)
        # Only issue count; no target IDs, titles, messages or semantic hashes.
        return self.record(
            DiagnosticCode.VALIDATION_RUN,
            DiagnosticStatus.FAILED if result.has_blocker else DiagnosticStatus.SUCCESS,
            count=min(len(result.issues), 10_000),
        )

    def snapshot(self) -> DiagnosticSnapshot:
        return DiagnosticSnapshot(tuple(self._events), self._dropped)
