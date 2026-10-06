"""Provider-agnostic transport semantics for STEP 11 Wave 0."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from ai_ngerti_geopolitik.application.ports import MediaEnginePort, PreviewResult
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

    Real-time scheduling/audio is owned by the production engine adapter later.
    This controller owns only application-level play/pause/seek/edit semantics.
    """

    def __init__(
        self,
        state_provider: Callable[[], ProjectState],
        media_engine: MediaEnginePort,
        preview_dir: Path,
    ) -> None:
        self._state_provider = state_provider
        self._media_engine = media_engine
        self._preview_dir = preview_dir
        state = self._state_provider()
        self._frame = 0
        self._playing = False
        self._seen_revision = state.revision

    @staticmethod
    def _timeline_end(state: ProjectState) -> int:
        ends = [
            clip.timeline_end_frame
            for track in state.tracks
            for clip in track.clips
            if clip.enabled
        ]
        return max(ends, default=0)

    def _reconcile(self) -> ProjectState:
        state = self._state_provider()
        end = self._timeline_end(state)
        if state.revision != self._seen_revision:
            self._seen_revision = state.revision
            if end == 0:
                self._frame = 0
                self._playing = False
            elif self._frame >= end:
                self._frame = end - 1
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
        return self.snapshot

    def play(self) -> PlaybackSnapshot:
        state = self._reconcile()
        if self._timeline_end(state) <= 0:
            raise PlaybackError("cannot play an empty timeline")
        self._playing = True
        return self.snapshot

    def pause(self) -> PlaybackSnapshot:
        self._reconcile()
        self._playing = False
        return self.snapshot

    def advance(self, frames: int = 1) -> PlaybackSnapshot:
        if frames <= 0:
            raise PlaybackError("advance frames must be positive")
        state = self._reconcile()
        if not self._playing:
            return self.snapshot
        end = self._timeline_end(state)
        self._frame = min(self._frame + frames, max(0, end - 1))
        if self._frame >= max(0, end - 1):
            self._playing = False
        return self.snapshot

    def render_current(self) -> PreviewResult:
        state = self._reconcile()
        end = self._timeline_end(state)
        if end <= 0:
            raise PlaybackError("timeline is empty")
        self._preview_dir.mkdir(parents=True, exist_ok=True)
        output = self._preview_dir / (
            f"preview-r{state.revision:06d}-f{self._frame:09d}.png"
        )
        result = self._media_engine.preview_frame(state, self._frame, output)
        if result.project_revision != state.revision:
            raise PlaybackError("stale preview revision returned by media engine")
        if result.timeline_frame != self._frame:
            raise PlaybackError("preview engine returned the wrong timeline frame")
        return result
