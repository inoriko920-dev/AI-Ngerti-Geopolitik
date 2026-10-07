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
from ai_ngerti_geopolitik.infrastructure.ffmpeg_properties import build_w3_filter_plan


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


def _number_seconds(seconds: float) -> str:
    return f"{seconds:.6f}"


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


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
        audio = next(
            (
                stream
                for stream in streams
                if isinstance(stream, dict) and stream.get("codec_type") == "audio"
            ),
            None,
        )
        format_data = data.get("format")
        format_duration = format_data.get("duration") if isinstance(format_data, dict) else None
        fingerprint = _sha256_file(path)
        file_size = path.stat().st_size
        image_suffixes = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}

        if video is not None and path.suffix.lower() in image_suffixes:
            return ProbeResult(
                path=path,
                duration_frames=1,
                fps=0,
                width=int(video["width"]),
                height=int(video["height"]),
                has_audio=False,
                fingerprint_sha256=fingerprint,
                media_type="image",
                duration_seconds=0.0,
                file_size=file_size,
            )

        if video is not None:
            rate = str(video.get("avg_frame_rate") or video.get("r_frame_rate") or "0/1")
            fps_fraction = _fraction(rate)
            if fps_fraction.denominator != 1:
                raise MediaToolError(f"current project model requires integer FPS, got {rate}")
            fps = fps_fraction.numerator
            duration = video.get("duration")
            if duration is None:
                duration = format_duration
            if duration is None:
                raise MediaToolError("media duration missing")
            duration_seconds = float(duration)
            return ProbeResult(
                path=path,
                duration_frames=_frames_from_seconds(str(duration), fps),
                fps=fps,
                width=int(video["width"]),
                height=int(video["height"]),
                has_audio=audio is not None,
                fingerprint_sha256=fingerprint,
                media_type="video",
                duration_seconds=duration_seconds,
                file_size=file_size,
                sample_rate=int(audio.get("sample_rate", 0)) if isinstance(audio, dict) else 0,
            )

        if audio is not None:
            duration = audio.get("duration")
            if duration is None:
                duration = format_duration
            if duration is None:
                raise MediaToolError("audio duration missing")
            return ProbeResult(
                path=path,
                duration_frames=0,
                fps=0,
                width=0,
                height=0,
                has_audio=True,
                fingerprint_sha256=fingerprint,
                media_type="audio",
                duration_seconds=float(duration),
                file_size=file_size,
                sample_rate=int(audio.get("sample_rate", 0)),
            )

        raise MediaToolError("supported video/audio/image stream missing")


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
        timeline_offset = timeline_frame - selected.timeline_start.frames
        source_frame = selected.source_frame_at_timeline_offset(timeline_offset)
        asset = state.asset(selected.asset_id)
        output_path = output_path.resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)

        plan = build_w3_filter_plan(selected, state.fps)
        creative = build_w4_creative_plan(
            selected,
            state.fps,
            base_x=plan.overlay_x,
            base_y=plan.overlay_y,
        )
        source_filters = (*plan.video_filters, *creative.source_filters)
        overlay_chain = (
            "[w4bg][w4src]overlay="
            f"x='{creative.overlay_x}':"
            f"y='{creative.overlay_y}':shortest=1"
        )
        if creative.post_filters:
            overlay_chain += "," + ",".join(
                creative.post_filters
            )
        overlay_chain += ",format=yuv420p[outv]"
        filter_parts = [
            f"[0:v]{','.join(source_filters)}[w4src]",
            (
                f"color=c=black:s={state.settings.width}x{state.settings.height}:"
                f"r={state.fps}:d={_seconds_string(1, state.fps)}[w4bg]"
            ),
            overlay_chain,
        ]
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
            "-filter_complex",
            ";".join(filter_parts),
            "-map",
            "[outv]",
            "-frames:v",
            "1",
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
            rate = clip.properties.speed.rate_percent / 100.0
            plan = build_w3_filter_plan(clip, state.fps)
            creative = build_w4_creative_plan(
                clip,
                state.fps,
                base_x=plan.overlay_x,
                base_y=plan.overlay_y,
            )
            source_filters = (
                *plan.video_filters,
                *creative.source_filters,
            )
            filter_parts.append(
                f"[{index}:v]trim=start={start}:end={end},"
                f"setpts=(PTS-STARTPTS)/{rate:.8f},"
                f"{','.join(source_filters)}[vsrc{index}]"
            )
            filter_parts.append(
                f"color=c=black:s={state.settings.width}x{state.settings.height}:"
                f"r={state.fps}:d={_number_seconds(plan.duration_seconds)}[bg{index}]"
            )
            overlay_chain = (
                f"[bg{index}][vsrc{index}]overlay="
                f"x='{creative.overlay_x}':"
                f"y='{creative.overlay_y}':shortest=1"
            )
            if creative.post_filters:
                overlay_chain += "," + ",".join(
                    creative.post_filters
                )
            overlay_chain += f",format=yuv420p[v{index}]"
            filter_parts.append(overlay_chain)
            audio_chain = [
                f"atrim=start={start}:end={end}",
                "asetpts=PTS-STARTPTS",
                *plan.audio_filters,
            ]
            filter_parts.append(f"[{index}:a]{','.join(audio_chain)}[a{index}]")
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
