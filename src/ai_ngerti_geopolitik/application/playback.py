"""Provider-agnostic playback and playhead semantics for STEP 11 W2."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from ai_ngerti_geopolitik.application.ports import (
    MediaEnginePort,
    PreviewResult,
    RealtimePlaybackPort,
)
from ai_ngerti_geopolitik.domain import ProjectState


class PlaybackError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class PlaybackSnapshot:
    project_revision: int
    frame: int
    playing: bool


class PlaybackController:
    """Keeps playback cursor coherent with the canonical ProjectState.

    Native scheduling/audio belongs to a RealtimePlaybackPort implementation.
    The application controller owns play/pause/seek/edit-reconciliation semantics.
    """

    def __init__(
        self,
        state_provider: Callable[[], ProjectState],
        media_engine: MediaEnginePort,
        preview_dir: Path,
        realtime_transport: RealtimePlaybackPort | None = None,
    ) -> None:
        self._state_provider = state_provider
        self._media_engine = media_engine
        self._preview_dir = preview_dir
        self._realtime_transport = realtime_transport
        state = self._state_provider()
        self._frame = 0
        self._playing = False
        self._seen_revision = state.revision
        self._transport_revision: int | None = None

    @staticmethod
    def _timeline_end(state: ProjectState) -> int:
        return state.timeline_end_frame

    def _sync_transport(self, state: ProjectState) -> None:
        if self._realtime_transport is None:
            return
        if self._transport_revision == state.revision:
            return
        self._realtime_transport.pause()
        self._realtime_transport.load(state)
        self._transport_revision = state.revision
        if state.timeline_end_frame > 0:
            self._realtime_transport.seek(self._frame)

    def _reconcile(self) -> ProjectState:
        state = self._state_provider()
        end = self._timeline_end(state)
        if state.revision != self._seen_revision:
            self._seen_revision = state.revision
            self._playing = False
            if end == 0:
                self._frame = 0
            elif self._frame >= end:
                self._frame = end - 1
            self._sync_transport(state)
        return state

    @property
    def snapshot(self) -> PlaybackSnapshot:
        state = self._reconcile()
        return PlaybackSnapshot(state.revision, self._frame, self._playing)

    def seek(self, frame: int) -> PlaybackSnapshot:
        state = self._reconcile()
        end = self._timeline_end(state)
        if end <= 0:
            raise PlaybackError("timeline is empty")
        if frame < 0 or frame >= end:
            raise PlaybackError(f"seek frame outside timeline: {frame}")
        self._frame = frame
        self._sync_transport(state)
        if self._realtime_transport is not None:
            self._realtime_transport.seek(frame)
        return self.snapshot

    def scrub(self, frame: int) -> PlaybackSnapshot:
        self.pause()
        return self.seek(frame)

    def play(self) -> PlaybackSnapshot:
        state = self._reconcile()
        if self._timeline_end(state) <= 0:
            raise PlaybackError("cannot play an empty timeline")
        self._sync_transport(state)
        if self._realtime_transport is not None:
            self._realtime_transport.seek(self._frame)
            self._realtime_transport.play()
        self._playing = True
        return self.snapshot

    def pause(self) -> PlaybackSnapshot:
        self._reconcile()
        if self._realtime_transport is not None:
            self._realtime_transport.pause()
        self._playing = False
        return self.snapshot

    def prepare_edit(self) -> PlaybackSnapshot:
        """Explicit W2 policy: canonical edits auto-pause active playback."""

        return self.pause()

    def advance(self, frames: int = 1) -> PlaybackSnapshot:
        if frames <= 0:
            raise PlaybackError("advance frames must be positive")
        state = self._reconcile()
        if not self._playing:
            return self.snapshot
        end = self._timeline_end(state)
        self._frame = min(self._frame + frames, max(0, end - 1))
        if self._frame >= max(0, end - 1):
            if self._realtime_transport is not None:
                self._realtime_transport.pause()
            self._playing = False
        return self.snapshot

    def stop(self) -> PlaybackSnapshot:
        if self._realtime_transport is not None:
            self._realtime_transport.stop()
        self._playing = False
        self._frame = 0
        return self.snapshot

    def render_current(self) -> PreviewResult:
        state = self._reconcile()
        end = self._timeline_end(state)
        if end <= 0:
            raise PlaybackError("timeline is empty")
        self._preview_dir.mkdir(parents=True, exist_ok=True)
        output = self._preview_dir / (f"preview-r{state.revision:06d}-f{self._frame:09d}.png")
        result = self._media_engine.preview_frame(state, self._frame, output)
        if result.project_revision != state.revision:
            raise PlaybackError("stale preview revision returned by media engine")
        if result.timeline_frame != self._frame:
            raise PlaybackError("preview engine returned the wrong timeline frame")
        return result
