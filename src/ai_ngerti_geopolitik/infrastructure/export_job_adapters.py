"""T08 additive qualification dispatch plus no-clobber final publication."""

from __future__ import annotations

import os
from dataclasses import replace
from pathlib import Path

from ai_ngerti_geopolitik.application.export_capabilities import ExportToolchain
from ai_ngerti_geopolitik.application.export_preflight import ExportPreflightService
from ai_ngerti_geopolitik.application.export_profiles import candidate_for_request
from ai_ngerti_geopolitik.application.export_request import (
    ExportQuality,
    ExportRequest,
    ExportScope,
    ExportSharpen,
    ExportSubtitles,
)
from ai_ngerti_geopolitik.application.export_style_policy import style_for_request
from ai_ngerti_geopolitik.application.ports import CancellationToken, ExportResult
from ai_ngerti_geopolitik.application.validation import MediaIntegrityInspectorPort
from ai_ngerti_geopolitik.domain import ProjectState
from ai_ngerti_geopolitik.infrastructure.export_output_inspector import LocalExportOutputInspector
from ai_ngerti_geopolitik.infrastructure.ffmpeg_export_profiles import (
    FfmpegMatrixQualificationExporter,
)
from ai_ngerti_geopolitik.infrastructure.ffmpeg_export_style import (
    FfmpegStyleQualificationExporter,
)
from ai_ngerti_geopolitik.infrastructure.ffmpeg_slice import FfmpegSliceMediaEngine


class QualifiedStagedRender:
    """Routes only verified T04–T07 profiles; original destination preflight is worker-side."""

    def __init__(
        self,
        engine: FfmpegSliceMediaEngine,
        inspector: MediaIntegrityInspectorPort,
        toolchain: ExportToolchain,
        *,
        project_source_path: Path | None = None,
    ) -> None:
        self.engine = engine
        self.inspector = inspector
        self.toolchain = toolchain
        self.project_source_path = project_source_path
        self.targets = LocalExportOutputInspector()

    def render(
        self,
        state: ProjectState,
        request: ExportRequest,
        *,
        stage_path: Path,
        cancellation: CancellationToken,
    ) -> ExportResult:
        selection = request.scope is ExportScope.SELECTION
        matrix = candidate_for_request(request) if not selection else None
        style = style_for_request(request) if not selection else None
        # A default style is permitted via T04; nondefault is T07-only.
        plain = (
            request.scope is ExportScope.FULL
            and (request.width, request.height, request.fps) == (1920, 1080, 30)
            and request.quality is ExportQuality.HIGH
            and request.sharpen is ExportSharpen.NONE
            and request.subtitles is ExportSubtitles.BURN_IN
        )
        if not (selection or matrix is not None or style is not None):
            raise ValueError("UNSUPPORTED_EXPORT_PROFILE")
        if selection and not (
            request.codec.value == "h264"
            and request.quality is ExportQuality.HIGH
            and request.sharpen is ExportSharpen.NONE
            and request.subtitles is ExportSubtitles.BURN_IN
            and (request.width, request.height, request.fps) == (1920, 1080, 30)
        ):
            raise ValueError("UNSUPPORTED_SELECTION_PROFILE")

        preflight = ExportPreflightService(self.inspector, self.targets).check(
            state, request, request.session_id, self.toolchain,
            project_source_path=self.project_source_path,
            selection_qualified=selection,
            matrix_candidate=matrix,
            style_candidate=style,
        )
        if not preflight.precheck_pass:
            raise ValueError("EXPORT_PREFLIGHT_REJECTED")
        staged_request = replace(request, output_path=stage_path)
        opts = {
            "session_id": request.session_id,
            "media_inspector": self.inspector,
            "target_inspector": self.targets,
            "toolchain": self.toolchain,
            "project_source_path": self.project_source_path,
            "cancellation": cancellation,
        }
        if selection:
            return self.engine.export_h264_selection(state, staged_request, **opts)
        if not plain and matrix is not None and style is None:
            return FfmpegMatrixQualificationExporter(self.engine).export(
                state, staged_request, **opts
            )
        if not plain and style is not None:
            return FfmpegStyleQualificationExporter(self.engine).export(
                state, staged_request, **opts
            )
        if plain:
            return self.engine.export_h264_baseline(state, staged_request, **opts)
        raise ValueError("UNSUPPORTED_EXPORT_PROFILE")


class AtomicExportPublisher:
    """Fail closed on original media/project collisions; no file replacement."""

    def __init__(self, *, project_source_path: Path | None = None) -> None:
        self.project_source_path = project_source_path

    def publish(self, stage_path: Path, request: ExportRequest, state: ProjectState) -> None:
        target = request.output_path
        try:
            request.assert_current(state, request.session_id)
            if not stage_path.is_file() or stage_path.stat().st_size <= 0:
                raise ValueError("not staged")
            if not target.parent.is_dir() or target.exists() or target.is_symlink():
                raise ValueError("target invalid")
            protected = [Path(x.path_ref) for x in state.assets]
            if self.project_source_path is not None:
                protected.append(self.project_source_path)
            if target.resolve(strict=False) in {
                source.resolve(strict=False) for source in protected
            }:
                raise ValueError("source collision")
            os.link(stage_path, target)  # atomic create-if-absent on same volume
        except (OSError, ValueError):
            raise ValueError("EXPORT_PUBLISH_FAILED") from None
