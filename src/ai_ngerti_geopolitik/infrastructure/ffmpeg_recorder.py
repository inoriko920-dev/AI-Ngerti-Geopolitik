"""Windows FFmpeg/DirectShow microphone adapter for W5-007."""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

from ai_ngerti_geopolitik.application.ports import (
    CancellationToken,
    RecordingDevice,
    RecordingResult,
)


class RecorderToolError(RuntimeError):
    pass


class WindowsFfmpegRecorder:
    def __init__(self, ffmpeg: str | None = None) -> None:
        resolved = ffmpeg or shutil.which("ffmpeg")
        if resolved is None:
            raise RecorderToolError("required media tool not found: ffmpeg")
        self.ffmpeg = resolved

    def devices(self) -> tuple[RecordingDevice, ...]:
        if sys.platform != "win32":
            return ()
        result = subprocess.run(
            [
                self.ffmpeg,
                "-hide_banner",
                "-list_devices",
                "true",
                "-f",
                "dshow",
                "-i",
                "dummy",
            ],
            check=False,
            capture_output=True,
            text=True,
            shell=False,
            timeout=15,
        )
        names: list[str] = []
        for match in re.finditer(r'"([^"\r\n]+)"\s+\(audio\)', result.stderr):
            name = match.group(1).strip()
            if name and name not in names:
                names.append(name)
        return tuple(RecordingDevice(name, name) for name in names)

    def capture(
        self,
        device_id: str,
        staging_path: Path,
        *,
        max_duration_seconds: float,
        cancellation: CancellationToken | None = None,
    ) -> RecordingResult:
        if sys.platform != "win32":
            raise RecorderToolError("DirectShow microphone capture requires Windows")
        if max_duration_seconds <= 0:
            raise RecorderToolError("recording duration must be positive")
        if all(device.device_id != device_id for device in self.devices()):
            raise RecorderToolError(f"microphone input device is unavailable: {device_id}")
        if cancellation is not None and cancellation.cancelled:
            return RecordingResult(staging_path, cancelled=True)

        staging_path = staging_path.resolve()
        staging_path.parent.mkdir(parents=True, exist_ok=True)
        if staging_path.exists():
            staging_path.unlink()
        command = [
            self.ffmpeg,
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-f",
            "dshow",
            "-audio_buffer_size",
            "50",
            "-i",
            f"audio={device_id}",
            "-t",
            f"{max_duration_seconds:.3f}",
            "-ac",
            "1",
            "-ar",
            "48000",
            "-c:a",
            "pcm_s16le",
            str(staging_path),
        ]
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=False,
        )
        cancelled = False
        while process.poll() is None:
            if cancellation is not None and cancellation.cancelled:
                cancelled = True
                process.terminate()
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=2)
                break
            time.sleep(0.02)

        stdout, stderr = process.communicate()
        if cancelled:
            if staging_path.exists():
                staging_path.unlink()
            return RecordingResult(staging_path, cancelled=True)
        if process.returncode != 0:
            if staging_path.exists():
                staging_path.unlink()
            detail = stderr[-1200:] if stderr else stdout[-1200:]
            raise RecorderToolError(
                f"microphone capture failed ({process.returncode}): {detail}"
            )
        if not staging_path.is_file() or staging_path.stat().st_size <= 44:
            if staging_path.exists():
                staging_path.unlink()
            raise RecorderToolError("microphone capture produced empty audio")
        return RecordingResult(staging_path, cancelled=False)
