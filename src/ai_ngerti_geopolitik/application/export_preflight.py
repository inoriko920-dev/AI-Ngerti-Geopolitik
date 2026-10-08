"""SF12-T03 read-only export preflight and conservative capability negotiation.

A passing preflight is NOT permission to render: T04/T08/T09 are responsible
for actual encoding, jobs and postflight before the UI can be enabled.
Run this service outside the GUI thread; media inspection may be expensive.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Protocol

from ai_ngerti_geopolitik.application.export_capabilities import ExportToolchain
from ai_ngerti_geopolitik.application.export_profiles import (
    MatrixProfile,
    T06_CANDIDATE_PROFILES,
    candidate_for_request,
)
from ai_ngerti_geopolitik.application.export_request import (
    ExportAudio,
    ExportCodec,
    ExportContractError,
    ExportQuality,
    ExportRequest,
    ExportScope,
    ExportSharpen,
    ExportSubtitles,
)
from ai_ngerti_geopolitik.application.validation import (
    MediaIntegrityInspectorPort,
    RealMediaIntegrityRule,
    ValidationService,
    ValidationSeverity,
)
from ai_ngerti_geopolitik.domain import ProjectState


class ExportPreflightCode(StrEnum):
    STALE_REQUEST = "STALE_REQUEST"
    INVALID_REQUEST = "INVALID_REQUEST"
    INVALID_PROJECT = "INVALID_PROJECT"
    EMPTY_TIMELINE = "EMPTY_TIMELINE"
    INVALID_MEDIA = "INVALID_MEDIA"
    VALIDATION_UNAVAILABLE = "VALIDATION_UNAVAILABLE"
    ENCODER_UNAVAILABLE = "ENCODER_UNAVAILABLE"
    UNSUPPORTED_PROFILE = "UNSUPPORTED_PROFILE"
    SELECTION_NOT_QUALIFIED = "SELECTION_NOT_QUALIFIED"
    OUTPUT_COLLISION = "OUTPUT_COLLISION"
    OUTPUT_EXISTS = "OUTPUT_EXISTS"
    OUTPUT_PARENT_INVALID = "OUTPUT_PARENT_INVALID"
    OUTPUT_NOT_WRITABLE = "OUTPUT_NOT_WRITABLE"
    INSUFFICIENT_DISK = "INSUFFICIENT_DISK"
    OUTPUT_INSPECTION_FAILED = "OUTPUT_INSPECTION_FAILED"


@dataclass(frozen=True, slots=True)
class OutputTargetInspection:
    """Safe observation without logging private names/paths."""

    issue: ExportPreflightCode | None = None

    def __post_init__(self) -> None:
        if self.issue is not None and type(self.issue) is not ExportPreflightCode:
            raise ValueError("invalid output inspection code")


class OutputTargetInspectorPort(Protocol):
    def inspect(
        self,
        output_path: Path,
        protected_paths: tuple[Path, ...],
        min_free_bytes: int,
    ) -> OutputTargetInspection: ...


@dataclass(frozen=True, slots=True)
class ExportPreflightResult:
    request_id: str
    project_revision: int
    failure_codes: tuple[ExportPreflightCode, ...]

    @property
    def precheck_pass(self) -> bool:
        return not self.failure_codes

    @property
    def can_start_render(self) -> bool:
        """Always false: T03 can preflight, but cannot enable unfinished render."""

        return False


@dataclass(slots=True)
class ExportPreflightService:
    media_inspector: MediaIntegrityInspectorPort
    target_inspector: OutputTargetInspectorPort

    def check(
        self,
        state: ProjectState,
        request: ExportRequest,
        session_id: str | None,
        toolchain: ExportToolchain,
        *,
        project_source_path: Path | None = None,
        selection_qualified: bool = False,
        matrix_candidate: MatrixProfile | None = None,
    ) -> ExportPreflightResult:
        """Read-only, deterministic reasons; output checks stay behind a port."""

        failures: list[ExportPreflightCode] = []

        def add(issue: ExportPreflightCode) -> None:
            if issue not in failures:
                failures.append(issue)

        try:
            request.assert_current(state, session_id)
        except ExportContractError as exc:
            add(
                ExportPreflightCode.STALE_REQUEST
                if str(exc) == "STALE_EXPORT_REQUEST"
                else ExportPreflightCode.INVALID_REQUEST
            )
            return ExportPreflightResult(request.request_id, state.revision, tuple(failures))

        if state.timeline_end_frame <= 0:
            add(ExportPreflightCode.EMPTY_TIMELINE)

        # W8 real-media validation. Both BLOCKER and ERROR prohibit export;
        # unrelated WARNING/INFO on unused assets are non-blocking.
        try:
            validation = ValidationService(
                (RealMediaIntegrityRule(self.media_inspector),)
            ).validate(state)
            if validation.is_stale(state):
                add(ExportPreflightCode.STALE_REQUEST)
            if any(
                issue.severity in (ValidationSeverity.BLOCKER, ValidationSeverity.ERROR)
                for issue in validation.issues
            ):
                add(ExportPreflightCode.INVALID_MEDIA)
        except Exception:
            # Never emit exception text; the inspector may have private paths.
            add(ExportPreflightCode.VALIDATION_UNAVAILABLE)

        if not toolchain.baseline_detected:
            add(ExportPreflightCode.ENCODER_UNAVAILABLE)
        if request.codec is ExportCodec.H265 and not toolchain.h265_encoder_found:
            add(ExportPreflightCode.ENCODER_UNAVAILABLE)

        # T03 deliberately negotiates only the original H.264/1080p/30
        # qualification profile. A declared encoder does not prove HEVC,
        # 4K, FPS conversions, sharpen or selection rendering.
        if request.scope is ExportScope.SELECTION and not selection_qualified:
            add(ExportPreflightCode.SELECTION_NOT_QUALIFIED)
        baseline = (
            request.codec is ExportCodec.H264
            and (request.width, request.height, request.fps) == (1920, 1080, 30)
        )
        qualified_matrix_candidate = (
            matrix_candidate is not None
            and type(matrix_candidate) is MatrixProfile
            and matrix_candidate in T06_CANDIDATE_PROFILES
            and matrix_candidate == candidate_for_request(request)
        )
        if (
            not (baseline or qualified_matrix_candidate)
            or request.quality is not ExportQuality.HIGH
            or request.sharpen is not ExportSharpen.NONE
            or request.subtitles is not ExportSubtitles.BURN_IN
            or request.audio is not ExportAudio.AAC
        ):
            add(ExportPreflightCode.UNSUPPORTED_PROFILE)

        duration_frames = (
            request.selection.end if request.selection is not None else state.timeline_end_frame
        )
        if request.selection is not None:
            duration_frames -= request.selection.start

        # Conservative reserve is a floor, not a promised size prediction.
        min_bytes = max(
            256 * 1024 * 1024,
            128 * 1024 * 1024 + (duration_frames * 2_000_000 // max(1, state.fps)),
        )
        protected = tuple(Path(asset.path_ref) for asset in state.assets)
        if project_source_path is not None:
            protected += (project_source_path,)
        try:
            inspection = self.target_inspector.inspect(request.output_path, protected, min_bytes)
            if inspection.issue is not None:
                add(inspection.issue)
        except Exception:
            add(ExportPreflightCode.OUTPUT_INSPECTION_FAILED)

        return ExportPreflightResult(request.request_id, state.revision, tuple(failures))
