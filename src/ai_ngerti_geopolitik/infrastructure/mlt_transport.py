"""MLT subprocess transport for STEP 11 W2 runtime qualification."""

from __future__ import annotations

import os
import shutil
import subprocess
from collections.abc import Mapping

from ai_ngerti_geopolitik.domain import ProjectState
from ai_ngerti_geopolitik.infrastructure.mlt_projection import (
    MltProjectionError,
    MltTimelinePlan,
    build_mlt_timeline_plan,
)


class MltTransportError(RuntimeError):
    pass


class MltProcessPlaybackTransport:
    """Process-based MLT playback transport.

    This adapter keeps native playback out of the Qt UI thread. W2 qualifies the
    transport/projection contract; final embedded-display packaging remains a later
    hardening/release concern.
    """

    def __init__(
        self,
        melt_executable: str = "melt",
        *,
        consumer: str = "sdl2",
        environment: Mapping[str, str] | None = None,
    ) -> None:
        resolved = shutil.which(melt_executable)
        if resolved is None:
            raise MltTransportError(f"melt executable not found: {melt_executable}")
        self.melt_executable = resolved
        self.consumer = consumer
        self.environment = dict(environment or {})
        self._plan: MltTimelinePlan | None = None
        self._frame = 0
        self._process: subprocess.Popen[bytes] | None = None

    @property
    def is_playing(self) -> bool:
        return self._process is not None and self._process.poll() is None

    @property
    def frame(self) -> int:
        return self._frame

    def load(self, state: ProjectState) -> None:
        self.pause()
        self._plan = build_mlt_timeline_plan(state)
        self._frame = 0

    def seek(self, frame: int) -> None:
        if self._plan is None:
            raise MltTransportError("MLT transport has no loaded project")
        if frame < 0 or frame >= self._plan.timeline_end_frame:
            raise MltTransportError(f"seek frame outside timeline: {frame}")
        was_playing = self.is_playing
        self.pause()
        self._frame = frame
        if was_playing:
            self.play()

    def command(self) -> list[str]:
        if self._plan is None:
            raise MltTransportError("MLT transport has no loaded project")
        try:
            source_arguments = self._plan.melt_source_arguments(self._frame)
        except MltProjectionError as exc:
            raise MltTransportError(str(exc)) from exc
        return [
            self.melt_executable,
            *source_arguments,
            "-consumer",
            self.consumer,
            "terminate_on_pause=1",
            "real_time=-1",
        ]

    def play(self) -> None:
        if self.is_playing:
            return
        command = self.command()
        env = os.environ.copy()
        env.update(self.environment)
        self._process = subprocess.Popen(
            command,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            shell=False,
            env=env,
        )

    def pause(self) -> None:
        process = self._process
        self._process = None
        if process is None or process.poll() is not None:
            return
        process.terminate()
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=2)

    def stop(self) -> None:
        self.pause()
        self._frame = 0
