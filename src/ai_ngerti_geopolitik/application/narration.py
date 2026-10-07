"""W5-006 canonical narration import and binding use-cases."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from ai_ngerti_geopolitik.application.commands import (
    CommandBatch,
    ImportAssetCommand,
    SetNarrationTrackCommand,
)
from ai_ngerti_geopolitik.application.media_import import (
    build_asset_from_probe,
    next_asset_id,
)
from ai_ngerti_geopolitik.application.ports import MediaProbePort
from ai_ngerti_geopolitik.domain import FrameTime, NarrationTrack, ProjectState


class NarrationBindingError(ValueError):
    pass


class CommandSession(Protocol):
    @property
    def state(self) -> ProjectState: ...

    def execute(self, batch: CommandBatch) -> ProjectState: ...


def next_narration_id(state: ProjectState) -> str:
    current = state.narration
    if current is None:
        return "N001"
    if current.narration_id.startswith("N") and current.narration_id[1:].isdigit():
        return f"N{int(current.narration_id[1:]) + 1:03d}"
    return "N001"


def build_narration_track(
    state: ProjectState,
    *,
    narration_id: str,
    asset_id: str,
    timeline_start_frame: int = 0,
    gain_percent: int = 100,
    muted: bool = False,
    fade_in_frames: int = 0,
    fade_out_frames: int = 0,
) -> NarrationTrack:
    if timeline_start_frame < 0:
        raise NarrationBindingError("narration timeline start must be non-negative")
    try:
        asset = state.asset(asset_id)
    except ValueError as exc:
        raise NarrationBindingError(f"unknown narration asset: {asset_id}") from exc
    if asset.media_type != "audio":
        raise NarrationBindingError("narration binding requires an audio asset")

    track = NarrationTrack(
        narration_id=narration_id,
        asset_id=asset_id,
        timeline_start=FrameTime(timeline_start_frame, state.fps),
        gain_percent=gain_percent,
        muted=muted,
        fade_in_frames=fade_in_frames,
        fade_out_frames=fade_out_frames,
    )
    return track


@dataclass(slots=True)
class NarrationImportService:
    probe: MediaProbePort

    def import_and_bind(
        self,
        session: CommandSession,
        path: Path,
        *,
        timeline_start_frame: int = 0,
        gain_percent: int = 100,
        muted: bool = False,
        fade_in_frames: int = 0,
        fade_out_frames: int = 0,
    ) -> str:
        result = self.probe.probe(path)
        if result.media_type != "audio":
            raise NarrationBindingError("narration source must be an audio file")

        asset_id = next_asset_id(session.state)
        asset = build_asset_from_probe(session.state, result, asset_id)
        narration_id = next_narration_id(session.state)
        staged_state = ProjectState(
            project_id=session.state.project_id,
            name=session.state.name,
            schema_version=session.state.schema_version,
            fps=session.state.fps,
            revision=session.state.revision,
            assets=(*session.state.assets, asset),
            tracks=session.state.tracks,
            markers=session.state.markers,
            subtitle=session.state.subtitle,
            narration=session.state.narration,
            settings=session.state.settings,
        )
        track = build_narration_track(
            staged_state,
            narration_id=narration_id,
            asset_id=asset_id,
            timeline_start_frame=timeline_start_frame,
            gain_percent=gain_percent,
            muted=muted,
            fade_in_frames=fade_in_frames,
            fade_out_frames=fade_out_frames,
        )
        batch = CommandBatch(
            batch_id=f"W5-NARRATION-{session.state.revision + 1:06d}",
            label="Import and bind narration",
            actor="manual",
            expected_revision=session.state.revision,
            commands=(
                ImportAssetCommand(asset),
                SetNarrationTrackCommand(track),
            ),
        )
        try:
            session.execute(batch)
        except ValueError as exc:
            raise NarrationBindingError(str(exc)) from exc
        return asset_id

    def bind_existing(
        self,
        session: CommandSession,
        asset_id: str,
        *,
        timeline_start_frame: int = 0,
        gain_percent: int = 100,
        muted: bool = False,
        fade_in_frames: int = 0,
        fade_out_frames: int = 0,
    ) -> NarrationTrack:
        track = build_narration_track(
            session.state,
            narration_id=next_narration_id(session.state),
            asset_id=asset_id,
            timeline_start_frame=timeline_start_frame,
            gain_percent=gain_percent,
            muted=muted,
            fade_in_frames=fade_in_frames,
            fade_out_frames=fade_out_frames,
        )
        batch = CommandBatch(
            batch_id=f"W5-NARRATION-BIND-{session.state.revision + 1:06d}",
            label="Bind narration",
            actor="manual",
            expected_revision=session.state.revision,
            commands=(SetNarrationTrackCommand(track),),
        )
        try:
            session.execute(batch)
        except ValueError as exc:
            raise NarrationBindingError(str(exc)) from exc
        return track
