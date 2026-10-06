"""STEP 10 application use-cases and UI-intent routing with hardened E2E evidence."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ai_ngerti_geopolitik.application.commands import (
    AddClipCommand,
    Command,
    CommandBatch,
    CommandBus,
    ImportAssetCommand,
    SplitClipCommand,
    TrimClipCommand,
)
from ai_ngerti_geopolitik.application.media_import import (
    build_asset_from_probe,
    next_asset_id,
)
from ai_ngerti_geopolitik.application.ports import (
    CancellationToken,
    ExportResult,
    MediaEnginePort,
    MediaProbePort,
    PreviewResult,
    ProjectRepositoryPort,
)
from ai_ngerti_geopolitik.application.ui_intents import UiIntent, UiIntentType
from ai_ngerti_geopolitik.domain import Clip, FrameTime, ProjectState


class VerticalSliceError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class TimelineClipView:
    clip_id: str
    asset_id: str
    timeline_start_frame: int
    timeline_end_frame: int
    duration_frames: int


@dataclass(frozen=True, slots=True)
class TimelineProjection:
    project_revision: int
    track_id: str
    clips: tuple[TimelineClipView, ...]


def _payload(intent: UiIntent) -> dict[str, str]:
    return dict(intent.payload)


@dataclass(slots=True)
class VerticalSliceSession:
    probe: MediaProbePort
    repository: ProjectRepositoryPort
    media_engine: MediaEnginePort
    bus: CommandBus

    @classmethod
    def create(
        cls,
        probe: MediaProbePort,
        repository: ProjectRepositoryPort,
        media_engine: MediaEnginePort,
        *,
        project_id: str = "ANG-E2E-001",
        name: str = "ANG STEP10 E2E",
        fps: int = 30,
    ) -> VerticalSliceSession:
        return cls(
            probe=probe,
            repository=repository,
            media_engine=media_engine,
            bus=CommandBus(ProjectState.create(project_id, name, fps)),
        )

    @property
    def state(self) -> ProjectState:
        return self.bus.state

    def _next_clip_id(self) -> str:
        count = sum(len(track.clips) for track in self.state.tracks)
        return f"C{count + 1:03d}"

    def _execute(self, label: str, command: Command) -> ProjectState:
        batch = CommandBatch(
            batch_id=f"B{self.state.revision + 1:03d}",
            label=label,
            actor="manual",
            expected_revision=self.state.revision,
            commands=(command,),
        )
        return self.bus.execute(batch)

    def import_media(self, path: Path) -> str:
        result = self.probe.probe(path)
        asset_id = next_asset_id(self.state)
        try:
            asset = build_asset_from_probe(self.state, result, asset_id)
        except ValueError as exc:
            raise VerticalSliceError(str(exc)) from exc
        self._execute("Import media", ImportAssetCommand(asset))
        return asset_id

    def add_to_timeline(self, asset_id: str) -> str:
        asset = self.state.asset(asset_id)
        clip_id = self._next_clip_id()
        clip = Clip(
            clip_id=clip_id,
            asset_id=asset_id,
            timeline_start=FrameTime(0, self.state.fps),
            source_in=FrameTime(0, self.state.fps),
            source_out=asset.duration,
        )
        self._execute("Add clip to V1", AddClipCommand(clip))
        return clip_id

    def split_clip(self, clip_id: str, timeline_frame: int) -> str:
        right_clip_id = self._next_clip_id()
        command = SplitClipCommand(
            clip_id=clip_id,
            split_timeline_frame=timeline_frame,
            right_clip_id=right_clip_id,
        )
        self._execute("Split clip", command)
        return right_clip_id

    def trim_right(self, clip_id: str, trim_frames: int) -> None:
        self._execute(
            "Trim right edge",
            TrimClipCommand(clip_id=clip_id, trim_frames=trim_frames),
        )

    def undo(self) -> ProjectState:
        return self.bus.undo()

    def redo(self) -> ProjectState:
        return self.bus.redo()

    def save(self, path: Path) -> None:
        self.repository.save(self.state, path)

    def load(self, path: Path) -> ProjectState:
        return self.bus.replace_loaded_state(self.repository.load(path))

    def preview_frame(self, timeline_frame: int, output_path: Path) -> PreviewResult:
        return self.media_engine.preview_frame(self.state, timeline_frame, output_path)

    def timeline_projection(self) -> TimelineProjection:
        track = self.state.track("V1")
        clips = tuple(
            TimelineClipView(
                clip_id=clip.clip_id,
                asset_id=clip.asset_id,
                timeline_start_frame=clip.timeline_start.frames,
                timeline_end_frame=clip.timeline_end_frame,
                duration_frames=clip.duration_frames,
            )
            for clip in sorted(track.clips, key=lambda item: item.timeline_start.frames)
        )
        return TimelineProjection(
            project_revision=self.state.revision,
            track_id=track.track_id,
            clips=clips,
        )

    def export(
        self,
        output_path: Path,
        cancellation: CancellationToken | None = None,
    ) -> ExportResult:
        return self.media_engine.export(self.state, output_path, cancellation)


class VerticalSliceIntentRouter:
    """Application boundary used by STEP 10 to prove UI intent -> use-case."""

    def __init__(self, session: VerticalSliceSession) -> None:
        self.session = session
        self.last_result: str | None = None

    def __call__(self, intent: UiIntent) -> None:
        data = _payload(intent)
        if intent.kind is UiIntentType.IMPORT_MEDIA:
            path = data.get("path")
            if not path:
                raise VerticalSliceError("IMPORT_MEDIA intent requires path")
            self.last_result = self.session.import_media(Path(path))
            return
        if intent.kind is UiIntentType.UNDO:
            self.session.undo()
            self.last_result = "undo"
            return
        if intent.kind is UiIntentType.REDO:
            self.session.redo()
            self.last_result = "redo"
            return
        raise VerticalSliceError(f"unsupported STEP 10 intent: {intent.kind}")
