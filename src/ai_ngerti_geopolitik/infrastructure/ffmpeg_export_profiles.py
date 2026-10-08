"""T06 matrix qualification FFmpeg adapter (read-only ProjectState).

The native project renderer remains the unchanged 1080p30 composer from T04.
This adapter deliberately transcodes it to one of four tightly-scoped
qualification candidates and independently verifies resulting MP4 streams.
It is synchronous, has no GUI wiring, and does not qualify the final engine.
"""

from __future__ import annotations

import os
import tempfile
from fractions import Fraction
from pathlib import Path

from ai_ngerti_geopolitik.application.export_capabilities import ExportToolchain
from ai_ngerti_geopolitik.application.export_preflight import (
    ExportPreflightService,
    OutputTargetInspectorPort,
)
from ai_ngerti_geopolitik.application.export_profiles import candidate_for_request
from ai_ngerti_geopolitik.application.export_request import ExportRequest, ExportScope
from ai_ngerti_geopolitik.application.ports import CancellationToken, ExportResult
from ai_ngerti_geopolitik.application.validation import MediaIntegrityInspectorPort
from ai_ngerti_geopolitik.domain import ProjectState
from ai_ngerti_geopolitik.infrastructure.ffmpeg_slice import (
    FfmpegSliceMediaEngine,
    MediaOperationCancelled,
    MediaToolError,
)


class FfmpegMatrixQualificationExporter:
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
        profile = candidate_for_request(request)
        if profile is None or request.scope is not ExportScope.FULL:
            raise MediaToolError("T06_PROFILE_NOT_QUALIFIED")
        check = ExportPreflightService(media_inspector, target_inspector)

        def assert_safe(phase: str) -> None:
            result = check.check(
                state,
                request,
                session_id,
                toolchain,
                project_source_path=project_source_path,
                matrix_candidate=profile,
            )
            if not result.precheck_pass:
                reasons = ",".join(issue.value for issue in result.failure_codes)
                raise MediaToolError(f"{phase}:{reasons}")

        assert_safe("T06_PREFLIGHT_REJECTED")
        if (
            state.fps != 30
            or (state.settings.width, state.settings.height) != (1920, 1080)
            or state.timeline_end_frame <= 0
        ):
            raise MediaToolError("T06_PROJECT_BASELINE_MISMATCH")
        if cancellation is not None and cancellation.cancelled:
            raise MediaOperationCancelled("T06_CANCELLED")
        with tempfile.TemporaryDirectory(
            prefix=".ang-t06-", dir=request.output_path.parent
        ) as work:
            folder = Path(work)
            composed = folder / "composed.mp4"
            selected = folder / "qualified.mp4"
            self.engine.export(state, composed, cancellation)
            self.engine._verify_h264_baseline(composed, state)
            if cancellation is not None and cancellation.cancelled:
                raise MediaOperationCancelled("T06_CANCELLED")
            command = [
                self.engine.ffmpeg,
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-i",
                str(composed),
                "-vf",
                f"scale={profile.width}:{profile.height}:flags=bicubic,"
                f"fps={profile.fps},format=yuv420p",
                "-frames:v",
                str(state.timeline_end_frame * profile.fps // state.fps),
                "-c:v",
                profile.encoder,
                "-preset",
                "ultrafast" if profile.encoder == "libx264" else "fast",
                "-crf",
                "28",
                "-threads",
                "2",
                "-c:a",
                "aac",
                "-b:a",
                "96k",
                "-movflags",
                "+faststart",
            ]
            if profile.encoder == "libx265":
                command.extend(["-x265-params", "pools=2:frame-threads=1:log-level=error"])
            command.append(str(selected))
            self.engine.runner.run(command, cancellation)
            self._verify(selected, request, state.timeline_end_frame)
            if cancellation is not None and cancellation.cancelled:
                raise MediaOperationCancelled("T06_CANCELLED")
            assert_safe("T06_POST_RENDER_REJECTED")
            try:
                os.link(selected, request.output_path)
            except OSError:
                raise MediaToolError("T06_OUTPUT_PUBLISH_FAILED") from None
        return ExportResult(
            project_revision=state.revision,
            output_path=request.output_path,
            duration_frames=state.timeline_end_frame * profile.fps // state.fps,
            width=profile.width,
            height=profile.height,
            fps=profile.fps,
        )

    def _verify(self, path: Path, request: ExportRequest, input_frames: int) -> None:
        profile = candidate_for_request(request)
        if profile is None:
            raise MediaToolError("T06_PROFILE_NOT_QUALIFIED")
        try:
            if not path.is_file() or path.stat().st_size == 0:
                raise ValueError("empty")
            info = self.engine.probe.raw_probe(path)
            streams = info["streams"]
            video = [
                s for s in streams
                if isinstance(s, dict) and s.get("codec_type") == "video"
            ]
            audio = [
                s for s in streams
                if isinstance(s, dict) and s.get("codec_type") == "audio"
            ]
            if len(video) != 1 or len(audio) != 1:
                raise ValueError("stream count")
            stream = video[0]
            if (
                stream.get("codec_name") != profile.expected_decoder
                or int(stream.get("width", 0)) != profile.width
                or int(stream.get("height", 0)) != profile.height
                or Fraction(str(stream.get("avg_frame_rate", "0/1"))) != Fraction(profile.fps)
                or audio[0].get("codec_name") != "aac"
                or "mp4" not in str(info["format"]["format_name"]).split(",")
            ):
                raise ValueError("stream mismatch")
            count = input_frames * profile.fps // 30
            if int(stream["nb_frames"]) != count:
                raise ValueError("frame count mismatch")
            duration = float(info["format"]["duration"])
            if abs(duration - (count / profile.fps)) > (1 / profile.fps + 0.04):
                raise ValueError("duration mismatch")
        except (OSError, TypeError, ValueError, KeyError, ZeroDivisionError, OverflowError):
            raise MediaToolError("T06_PROFILE_STREAM_VERIFICATION_FAILED") from None
