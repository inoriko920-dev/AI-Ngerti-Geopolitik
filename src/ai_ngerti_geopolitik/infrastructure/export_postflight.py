"""SF12-T09 independent FFprobe + complete FFmpeg decode on the worker thread.

The T04–T07 encoding adapter cannot approve its own output. This verifier
enforces the immutable requested codec, size, FPS, selection frame count,
AAC and full decodability. All failures are redacted typed codes.
"""

from __future__ import annotations

import re
from fractions import Fraction
from pathlib import Path

from ai_ngerti_geopolitik.application.export_postflight import (
    ExportPostflightError,
    PostflightCode,
    PostflightReceipt,
)
from ai_ngerti_geopolitik.application.export_request import ExportCodec, ExportRequest
from ai_ngerti_geopolitik.application.ports import CancellationToken, ExportResult
from ai_ngerti_geopolitik.domain import ProjectState
from ai_ngerti_geopolitik.infrastructure.ffmpeg_slice import (
    FfmpegProcessRunner,
    FfprobeMediaProbe,
)


class IndependentMp4Postflight:
    """Inspect and decode the entire staged output before marking it READY."""

    def __init__(
        self,
        probe: FfprobeMediaProbe,
        *,
        ffmpeg: str,
        runner: FfmpegProcessRunner | None = None,
    ) -> None:
        self.probe = probe
        self.ffmpeg = ffmpeg
        self.runner = runner or FfmpegProcessRunner()

    def verify(
        self,
        stage_path: Path,
        request: ExportRequest,
        state: ProjectState,
        result: ExportResult,
        cancellation: CancellationToken,
    ) -> PostflightReceipt:
        expected = (
            request.selection.end - request.selection.start
            if request.selection is not None
            else state.timeline_end_frame
        )
        output_frames = expected * request.fps // state.fps
        # T05 selection and every matrix candidate keep integral frame mapping.
        if expected <= 0 or output_frames <= 0 or expected * request.fps % state.fps:
            raise ExportPostflightError(PostflightCode.RESULT_MISMATCH)
        if (
            result.output_path != stage_path
            or result.project_revision != request.project_revision
            or (result.width, result.height, result.fps)
            != (request.width, request.height, request.fps)
            or result.duration_frames != output_frames
        ):
            raise ExportPostflightError(PostflightCode.RESULT_MISMATCH)
        try:
            if (
                stage_path.is_symlink()
                or not stage_path.is_file()
                or stage_path.stat().st_size <= 0
            ):
                raise ExportPostflightError(PostflightCode.FILE_MISSING_OR_EMPTY)
            info = self.probe.raw_probe(stage_path)
        except ExportPostflightError:
            raise
        except Exception:
            raise ExportPostflightError(PostflightCode.INSPECTION_FAILED) from None

        try:
            raw_streams, fmt = info["streams"], info["format"]
            if not isinstance(raw_streams, list) or not isinstance(fmt, dict):
                raise ValueError("invalid metadata")
            if "mp4" not in str(fmt["format_name"]).split(","):
                raise ExportPostflightError(PostflightCode.INVALID_CONTAINER)
            if len(raw_streams) != 2 or not all(isinstance(x, dict) for x in raw_streams):
                raise ExportPostflightError(PostflightCode.STREAM_STRUCTURE)
            videos = [x for x in raw_streams if x["codec_type"] == "video"]
            audios = [x for x in raw_streams if x["codec_type"] == "audio"]
            if len(videos) != 1 or len(audios) != 1:
                raise ExportPostflightError(PostflightCode.STREAM_STRUCTURE)
            video = videos[0]
            expected_codec = "h264" if request.codec is ExportCodec.H264 else "hevc"
            if video["codec_name"] != expected_codec or audios[0]["codec_name"] != "aac":
                raise ExportPostflightError(PostflightCode.CODEC_MISMATCH)
            if (int(video["width"]), int(video["height"])) != (request.width, request.height):
                raise ExportPostflightError(PostflightCode.SIZE_MISMATCH)
            if Fraction(str(video["avg_frame_rate"])) != Fraction(request.fps, 1):
                raise ExportPostflightError(PostflightCode.FPS_MISMATCH)
            if int(video["nb_frames"]) != output_frames:
                raise ExportPostflightError(PostflightCode.FRAME_COUNT_MISMATCH)
            duration = float(fmt["duration"])
            if abs(duration - output_frames / request.fps) > max(0.06, 1 / request.fps):
                raise ExportPostflightError(PostflightCode.DURATION_MISMATCH)
        except ExportPostflightError:
            raise
        except (KeyError, TypeError, ValueError, ZeroDivisionError, OverflowError):
            raise ExportPostflightError(PostflightCode.INSPECTION_FAILED) from None

        if cancellation.cancelled:
            raise ExportPostflightError(PostflightCode.DECODE_FAILED)
        # Full decode, not a metadata-only probe. Frame count is independent of
        # reported nb_frames. AAC must be decodable as well as merely present.
        args = [
            self.ffmpeg,
            "-hide_banner",
            "-loglevel",
            "error",
            "-xerror",
            "-nostdin",
            "-progress",
            "pipe:1",
            "-nostats",
            "-i",
            str(stage_path),
            "-map",
            "0:v:0",
            "-map",
            "0:a:0",
            "-f",
            "null",
            "-",
        ]
        try:
            decoded = self.runner.run(args, cancellation)
            frames = [int(x) for x in re.findall(r"(?m)^frame=\s*([0-9]+)\s*$", decoded.stdout)]
            if (
                not frames
                or frames[-1] != output_frames
                or "progress=end" not in decoded.stdout
                or cancellation.cancelled
            ):
                raise ExportPostflightError(PostflightCode.DECODE_FAILED)
        except ExportPostflightError:
            raise
        except Exception:
            raise ExportPostflightError(PostflightCode.DECODE_FAILED) from None

        return PostflightReceipt.capture(stage_path, output_frames)
