"""Refresh explicit online/missing media state without deleting canonical clips."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ai_ngerti_geopolitik.application.commands import (
    CommandBatch,
    SetAssetAvailabilityCommand,
)
from ai_ngerti_geopolitik.application.media_import import CommandSession
from ai_ngerti_geopolitik.application.ports import MediaAvailabilityPort


@dataclass(slots=True)
class MediaStatusService:
    availability: MediaAvailabilityPort

    def refresh(self, session: CommandSession) -> tuple[str, ...]:
        changed: list[str] = []
        for asset in session.state.assets:
            status = self.availability.status(Path(asset.path_ref))
            if status == asset.availability:
                continue
            batch = CommandBatch(
                batch_id=f"W1-STATUS-{session.state.revision + 1:06d}",
                label=f"Media {status}: {asset.asset_id}",
                actor="system",
                expected_revision=session.state.revision,
                commands=(SetAssetAvailabilityCommand(asset.asset_id, status),),
            )
            session.execute(batch)
            changed.append(asset.asset_id)
        return tuple(changed)
