"""Real FFmpeg/ffprobe STEP 10 qualification adapter.

This validates the frozen MediaEnginePort and end-to-end architecture. It is not
a replacement decision for D-020's libopenshot primary production candidate.
No FFmpeg binary is bundled by STEP 10.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import time
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from fractions import Fraction
from pathlib import Path

from ai_ngerti_geopolitik.application.ports import (
    CancellationToken,
    ExportResult,
    PreviewResult,
    ProbeResult,
)
from ai_ngerti_geopolitik.domain import Clip, ProjectState


class MediaToolError(RuntimeError):
    pass


class MediaOperationCancelled(MediaToolError):
    pass


def _tool(name: str) -> str:
    resolved = shutil.which(name)
    if resolved is None:
        raise MediaToolError(f"required media tool not found: {name}")
    return resolved


def _fraction(value: str) -> Fraction:
    if "/" in value:
        numerator, denominator = value.split("/", 1)
        if int(denominator) == 0:
            raise MediaToolError(f"invalid frame rate: {value}")
        return Fraction(int(numerator), int(denominator))
    return Fraction(value)


def _frames_from_seconds(seconds: str, fps: int) -> int:
    value = Decimal(seconds) * Decimal(fps)
    return int(value.to_integral_value(rounding=ROUND_HALF_UP))


def _seconds_string(frames: int, fps: int) -> str:
    return f"{frames / fps:.6f}"


@dataclass(frozen=True, slots=True)
class ProcessResult:
    stdout: str
    stderr: str


class FfmpegProcessRunner:
    def run(
        self,
        arguments: list[str],
        cancellation: CancellationToken | None = None,
    ) -> ProcessResult:
        process = subprocess.Popen(
            arguments,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=False,
        )
        while process.poll() is None:
            if cancellation is not None and cancellation.cancelled:
                process.terminate()
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=2)
                stdout, stderr = process.communicate()
                raise MediaOperationCancelled(
                    f"media process cancelled: {stderr[-500:] if stderr else stdout[-500:]}"
                )
            time.sleep(0.02)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            raise MediaToolError(f"media process failed ({process.returncode}): {stderr[-2000:]}")
        return ProcessResult(stdout=stdout, stderr=stderr)


class FfprobeMediaProbe:
    def __init__(self, ffprobe: str | None = None) -> None:
        self.ffprobe = ffprobe or _tool("ffprobe")

    def raw_probe(self, path: Path) -> dict[str, object]:
        path = path.resolve()
        if not path.is_file():
            raise MediaToolError(f"media file not found: {path}")
        command = [
            self.ffprobe,
            "-v",
            "error",
            "-print_format",
            "json",
            "-show_streams",
            "-show_format",
            str(path),
        ]
        result = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            shell=False,
        )
        if result.returncode != 0:
            raise MediaToolError(f"ffprobe failed: {result.stderr[-2000:]}")
        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise MediaToolError("ffprobe returned invalid JSON") from exc
        if not isinstance(data, dict):
            raise MediaToolError("ffprobe result must be an object")
        return data

    def probe(self, path: Path) -> ProbeResult:
        path = path.resolve()
        data = self.raw_probe(path)
        streams = data.get("streams")
        if not isinstance(streams, list):
            raise MediaToolError("ffprobe streams missing")
        video = next(
            (
                stream
                for stream in streams
                if isinstance(stream, dict) and stream.get("codec_type") == "video"
            ),
            None,
        )
        if video is None:
            raise MediaToolError("video stream missing")
        rate = str(video.get("avg_frame_rate") or video.get("r_frame_rate") or "0/1")
        fps_fraction = _fraction(rate)
        if fps_fraction.denominator != 1:
            raise MediaToolError(f"STEP 10 requires integer FPS, got {rate}")
        fps = fps_fraction.numerator
        format_data = data.get("format")
        duration = video.get("duration") if isinstance(video, dict) else None
        if duration is None and isinstance(format_data, dict):
            duration = format_data.get("duration")
        if duration is None:
            raise MediaToolError("media duration missing")
        fingerprint = hashlib.sha256(path.read_bytes()).hexdigest()
        return ProbeResult(
            path=path,
            duration_frames=_frames_from_seconds(str(duration), fps),
            fps=fps,
            width=int(video["width"]),
            height=int(video["height"]),
            has_audio=any(
                isinstance(stream, dict) and stream.get("codec_type") == "audio"
                for stream in streams
            ),
            fingerprint_sha256=fingerprint,
        )


class MutableCancellationToken:
    def __init__(self) -> None:
        import threading

        self._event = threading.Event()

    @property
    def cancelled(self) -> bool:
        return self._event.is_set()

    def cancel(self) -> None:
        self._event.set()


class FfmpegSliceMediaEngine:
    def __init__(
        self,
        probe: FfprobeMediaProbe,
        *,
        ffmpeg: str | None = None,
        runner: FfmpegProcessRunner | None = None,
    ) -> None:
        self.ffmpeg = ffmpeg or _tool("ffmpeg")
        self.probe = probe
        self.runner = runner or FfmpegProcessRunner()

    def _video_clips(self, state: ProjectState) -> list[Clip]:
        tracks = [track for track in state.tracks if track.kind == "video"]
        if not tracks:
            raise MediaToolError("project has no video track")
        clips = sorted(tracks[0].clips, key=lambda clip: clip.timeline_start.frames)
        if not clips:
            raise MediaToolError("project has no clips")
        expected = 0
        for clip in clips:
            if clip.timeline_start.frames != expected:
                raise MediaToolError("STEP 10 export requires a contiguous V1 timeline")
            expected = clip.timeline_end_frame
            asset = state.asset(clip.asset_id)
            if not asset.has_audio:
                raise MediaToolError("STEP 10 canonical fixture requires audio")
        return clips

    def preview_frame(
        self,
        state: ProjectState,
        timeline_frame: int,
        output_path: Path,
    ) -> PreviewResult:
        state.validate()
        selected: Clip | None = None
        for clip in self._video_clips(state):
            if clip.timeline_start.frames <= timeline_frame < clip.timeline_end_frame:
                selected = clip
                break
        if selected is None:
            raise MediaToolError(f"timeline frame outside clips: {timeline_frame}")
        source_frame = selected.source_in.frames + (timeline_frame - selected.timeline_start.frames)
        asset = state.asset(selected.asset_id)
        output_path = output_path.resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        command = [
            self.ffmpeg,
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-ss",
            _seconds_string(source_frame, state.fps),
            "-i",
            asset.path_ref,
            "-frames:v",
            "1",
            "-vf",
            "scale=960:-2",
            str(output_path),
        ]
        self.runner.run(command)
        if not output_path.is_file() or output_path.stat().st_size == 0:
            raise MediaToolError("preview frame was not created")
        return PreviewResult(
            project_revision=state.revision,
            timeline_frame=timeline_frame,
            output_path=output_path,
        )

    def export(
        self,
        state: ProjectState,
        output_path: Path,
        cancellation: CancellationToken | None = None,
    ) -> ExportResult:
        state.validate()
        clips = self._video_clips(state)
        if cancellation is not None and cancellation.cancelled:
            raise MediaOperationCancelled("export cancelled before start")
        output_path = output_path.resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        temp = output_path.with_name(f"{output_path.stem}.partial{output_path.suffix}")
        if temp.exists():
            temp.unlink()

        command = [self.ffmpeg, "-hide_banner", "-loglevel", "error", "-y"]
        filter_parts: list[str] = []
        concat_inputs: list[str] = []
        for index, clip in enumerate(clips):
            asset = state.asset(clip.asset_id)
            command.extend(["-i", asset.path_ref])
            start = _seconds_string(clip.source_in.frames, state.fps)
            end = _seconds_string(clip.source_out.frames, state.fps)
            filter_parts.append(
                f"[{index}:v]trim=start={start}:end={end},setpts=PTS-STARTPTS[v{index}]"
            )
            filter_parts.append(
                f"[{index}:a]atrim=start={start}:end={end},asetpts=PTS-STARTPTS[a{index}]"
            )
            concat_inputs.append(f"[v{index}][a{index}]")
        filter_parts.append("".join(concat_inputs) + f"concat=n={len(clips)}:v=1:a=1[outv][outa]")
        command.extend(
            [
                "-filter_complex",
                ";".join(filter_parts),
                "-map",
                "[outv]",
                "-map",
                "[outa]",
                "-c:v",
                "libx264",
                "-preset",
                "ultrafast",
                "-crf",
                "28",
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                "aac",
                "-b:a",
                "96k",
                "-movflags",
                "+faststart",
                str(temp),
            ]
        )
        try:
            self.runner.run(command, cancellation)
            result = self.probe.probe(temp)
            if result.width <= 0 or result.height <= 0 or result.duration_frames <= 0:
                raise MediaToolError("export verification failed")
            os.replace(temp, output_path)
            return ExportResult(
                project_revision=state.revision,
                output_path=output_path,
                duration_frames=result.duration_frames,
                width=result.width,
                height=result.height,
                fps=result.fps,
            )
        finally:
            if temp.exists():
                temp.unlink()
