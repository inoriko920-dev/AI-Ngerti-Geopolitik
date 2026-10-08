"""SF12-T07 separate non-GUI qualification adapter.

Subtitle OFF uses an immutable derived render snapshot, not project mutation.
Narration stays mixed via W5 canonical FFmpeg render. User output is published
only after FFprobe checks with same-volume staging and atomic no-overwrite.
"""

from __future__ import annotations

import os
import tempfile
from dataclasses import replace
from fractions import Fraction
from pathlib import Path

from ai_ngerti_geopolitik.application.export_capabilities import ExportToolchain
from ai_ngerti_geopolitik.application.export_preflight import (
    ExportPreflightService,
    OutputTargetInspectorPort,
)
from ai_ngerti_geopolitik.application.export_request import ExportRequest, ExportSubtitles
from ai_ngerti_geopolitik.application.export_style_policy import style_for_request
from ai_ngerti_geopolitik.application.ports import CancellationToken, ExportResult
from ai_ngerti_geopolitik.application.validation import MediaIntegrityInspectorPort
from ai_ngerti_geopolitik.domain import ProjectState
from ai_ngerti_geopolitik.infrastructure.ffmpeg_slice import (
    FfmpegSliceMediaEngine,
    MediaOperationCancelled,
    MediaToolError,
)


class FfmpegStyleQualificationExporter:
    def __init__(self, engine: FfmpegSliceMediaEngine) -> None:
        self.engine = engine

    def export(
        self,
        state: ProjectState,
        request: ExportRequest,
        *,
        session_id: str | None,
        media_inspector: MediaIntegrityInspectorPort,
        target_inspector: OutputTargetInspectorPort,
        toolchain: ExportToolchain,
        project_source_path: Path | None = None,
        cancellation: CancellationToken | None = None,
    ) -> ExportResult:
        style = style_for_request(request)
        if style is None:
            raise MediaToolError("T07_STYLE_NOT_QUALIFIED")
        preflight = ExportPreflightService(media_inspector, target_inspector)

        def check(phase: str) -> None:
            result = preflight.check(
                state,
                request,
                session_id,
                toolchain,
                project_source_path=project_source_path,
                style_candidate=style,
            )
            if not result.precheck_pass:
                codes = ",".join(issue.value for issue in result.failure_codes)
                raise MediaToolError(f"{phase}:{codes}")

        check("T07_PREFLIGHT_REJECTED")
        if (
            state.fps != 30
            or (state.settings.width, state.settings.height) != (1920, 1080)
            or state.timeline_end_frame <= 0
        ):
            raise MediaToolError("T07_PROJECT_BASELINE_MISMATCH")
        if cancellation is not None and cancellation.cancelled:
            raise MediaOperationCancelled("T07_CANCELLED")

        derived = state
        if request.subtitles is ExportSubtitles.OFF and state.subtitle is not None:
            derived = replace(state, subtitle=replace(state.subtitle, enabled=False))

        with tempfile.TemporaryDirectory(
            prefix=".ang-t07-", dir=request.output_path.parent
        ) as work:
            folder = Path(work)
            composed = folder / "composed.mp4"
            styled = folder / "styled.mp4"
            self.engine.export(derived, composed, cancellation)
            self.engine._verify_h264_baseline(composed, derived)
            if cancellation is not None and cancellation.cancelled:
                raise MediaOperationCancelled("T07_CANCELLED")
            command = [
                self.engine.ffmpeg,
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-i",
                str(composed),
                "-vf",
                style.video_filter,
                "-c:v",
                "libx264",
                "-preset",
                style.preset,
                "-crf",
                str(style.crf),
                "-threads",
                "2",
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                "aac",
                "-b:a",
                "96k",
                "-movflags",
                "+faststart",
                str(styled),
            ]
            self.engine.runner.run(command, cancellation)
            self._verify(styled, state)
            if cancellation is not None and cancellation.cancelled:
                raise MediaOperationCancelled("T07_CANCELLED")
            check("T07_POST_RENDER_REJECTED")
            try:
                os.link(styled, request.output_path)
            except OSError:
                raise MediaToolError("T07_OUTPUT_PUBLISH_FAILED") from None

        return ExportResult(
            project_revision=state.revision,
            output_path=request.output_path,
            duration_frames=state.timeline_end_frame,
            width=1920,
            height=1080,
            fps=30,
        )

    def _verify(self, path: Path, state: ProjectState) -> None:
        try:
            if not path.is_file() or path.stat().st_size == 0:
                raise ValueError("empty file")
            info = self.engine.probe.raw_probe(path)
            streams = info["streams"]
            fmt = info["format"]
            if not isinstance(streams, list) or not isinstance(fmt, dict):
                raise ValueError("malformed metadata")
            videos = [
                s for s in streams if isinstance(s, dict) and s.get("codec_type") == "video"
            ]
            audios = [
                s for s in streams if isinstance(s, dict) and s.get("codec_type") == "audio"
            ]
            if len(videos) != 1 or len(audios) != 1:
                raise ValueError("invalid stream count")
            video = videos[0]
            if (
                video.get("codec_name") != "h264"
                or int(video.get("width", 0)) != 1920
                or int(video.get("height", 0)) != 1080
                or Fraction(str(video.get("avg_frame_rate", "0/1"))) != Fraction(30)
                or int(video["nb_frames"]) != state.timeline_end_frame
                or audios[0].get("codec_name") != "aac"
                or "mp4" not in str(fmt["format_name"]).split(",")
                or abs(float(fmt["duration"]) - (state.timeline_end_frame / 30)) > 0.07
            ):
                raise ValueError("mismatched output")
        except (OSError, TypeError, ValueError, KeyError, OverflowError, ZeroDivisionError):
            raise MediaToolError("T07_STREAM_VERIFICATION_FAILED") from None
