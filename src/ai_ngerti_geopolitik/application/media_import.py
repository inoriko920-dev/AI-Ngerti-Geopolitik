"""Canonical STEP 11 W1 media import construction and use-case."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from typing import Protocol

from ai_ngerti_geopolitik.application.commands import (
    CommandBatch,
    ImportAssetCommand,
)
from ai_ngerti_geopolitik.application.ports import MediaProbePort, ProbeResult
from ai_ngerti_geopolitik.domain import Asset, FrameTime, ProjectState


class CommandSession(Protocol):
    @property
    def state(self) -> ProjectState: ...

    def execute(self, batch: CommandBatch) -> ProjectState: ...


def next_asset_id(state: ProjectState) -> str:
    highest = 0
    for asset in state.assets:
        if asset.asset_id.startswith("A") and asset.asset_id[1:].isdigit():
            highest = max(highest, int(asset.asset_id[1:]))
    return f"A{highest + 1:03d}"


def _duration_frames(state: ProjectState, result: ProbeResult) -> int:
    if result.media_type == "video":
        if result.fps != state.fps:
            raise ValueError(f"media FPS {result.fps} does not match project FPS {state.fps}")
        return result.duration_frames
    if result.media_type == "image":
        return 1
    if result.media_type == "audio":
        seconds = Decimal(str(result.duration_seconds))
        frames = (seconds * Decimal(state.fps)).to_integral_value(rounding=ROUND_HALF_UP)
        return max(1, int(frames))
    raise ValueError(f"unsupported media type: {result.media_type}")


def build_asset_from_probe(
    state: ProjectState,
    result: ProbeResult,
    asset_id: str,
) -> Asset:
    return Asset(
        asset_id=asset_id,
        path_ref=str(result.path),
        media_type=result.media_type,
        duration=FrameTime(_duration_frames(state, result), state.fps),
        width=result.width,
        height=result.height,
        has_audio=result.has_audio,
        fingerprint_sha256=result.fingerprint_sha256,
        source_name=result.path.name,
        file_size=result.file_size,
        sample_rate=result.sample_rate,
        availability="online",
    )


@dataclass(slots=True)
class MediaImportService:
    probe: MediaProbePort

    def import_path(self, session: CommandSession, path: Path) -> str:
        result = self.probe.probe(path)
        asset_id = next_asset_id(session.state)
        asset = build_asset_from_probe(session.state, result, asset_id)
        batch = CommandBatch(
            batch_id=f"W1-IMPORT-{session.state.revision + 1:06d}",
            label=f"Import {asset.media_type}",
            actor="manual",
            expected_revision=session.state.revision,
            commands=(ImportAssetCommand(asset),),
        )
        session.execute(batch)
        return asset_id
