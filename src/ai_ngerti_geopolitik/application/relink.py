"""W8-003 safe single-asset relink through canonical CommandBus history."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from ai_ngerti_geopolitik.application.commands import (
    CommandBatch,
    CommandError,
    RelinkAssetCommand,
)
from ai_ngerti_geopolitik.application.media_import import CommandSession, build_asset_from_probe
from ai_ngerti_geopolitik.application.ports import MediaProbePort
from ai_ngerti_geopolitik.domain import Asset, DomainValidationError, ProjectState


class RelinkErrorCode(StrEnum):
    UNKNOWN_ASSET = "UNKNOWN_ASSET"
    PROBE_FAILED = "PROBE_FAILED"
    PATH_CONFLICT = "PATH_CONFLICT"
    MEDIA_TYPE_MISMATCH = "MEDIA_TYPE_MISMATCH"
    FINGERPRINT_MISMATCH = "FINGERPRINT_MISMATCH"
    METADATA_MISMATCH = "METADATA_MISMATCH"
    COMMAND_REJECTED = "COMMAND_REJECTED"


class RelinkError(RuntimeError):
    def __init__(self, code: RelinkErrorCode, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True, slots=True)
class RelinkCandidate:
    asset_id: str
    original_path: str
    replacement: Asset


@dataclass(frozen=True, slots=True)
class RelinkResult:
    asset_id: str
    previous_path: str
    current_path: str
    base_revision: int
    applied_revision: int


def _metadata_compatible(current: Asset, replacement: Asset) -> bool:
    return (
        replacement.duration == current.duration
        and replacement.width == current.width
        and replacement.height == current.height
        and replacement.has_audio == current.has_audio
        and not (
            current.sample_rate > 0
            and replacement.sample_rate > 0
            and replacement.sample_rate != current.sample_rate
        )
    )


@dataclass(slots=True)
class RelinkService:
    probe: MediaProbePort

    def verify_candidate(
        self,
        state: ProjectState,
        asset_id: str,
        candidate_path: Path,
    ) -> RelinkCandidate:
        try:
            current = state.asset(asset_id)
        except DomainValidationError as exc:
            raise RelinkError(RelinkErrorCode.UNKNOWN_ASSET, f"unknown asset: {asset_id}") from exc

        try:
            result = self.probe.probe(candidate_path)
            replacement = build_asset_from_probe(state, result, current.asset_id)
        except (OSError, RuntimeError, ValueError) as exc:
            raise RelinkError(
                RelinkErrorCode.PROBE_FAILED,
                "candidate media could not be probed safely",
            ) from exc

        replacement_path = Path(replacement.path_ref).resolve()
        for asset in state.assets:
            if asset.asset_id == current.asset_id:
                continue
            if Path(asset.path_ref).resolve() == replacement_path:
                raise RelinkError(
                    RelinkErrorCode.PATH_CONFLICT,
                    "candidate path is already bound to another asset",
                )

        if replacement.media_type != current.media_type:
            raise RelinkError(
                RelinkErrorCode.MEDIA_TYPE_MISMATCH,
                "candidate media type does not match canonical asset",
            )
        if replacement.fingerprint_sha256 != current.fingerprint_sha256:
            raise RelinkError(
                RelinkErrorCode.FINGERPRINT_MISMATCH,
                "candidate fingerprint does not match canonical asset",
            )
        if not _metadata_compatible(current, replacement):
            raise RelinkError(
                RelinkErrorCode.METADATA_MISMATCH,
                "candidate media metadata is incompatible with canonical asset",
            )

        return RelinkCandidate(current.asset_id, current.path_ref, replacement)

    def relink(
        self,
        session: CommandSession,
        asset_id: str,
        candidate_path: Path,
    ) -> RelinkResult:
        candidate = self.verify_candidate(session.state, asset_id, candidate_path)
        base_revision = session.state.revision
        batch = CommandBatch(
            batch_id=f"W8-RELINK-{base_revision + 1:06d}",
            label=f"Relink {asset_id}",
            actor="manual",
            expected_revision=base_revision,
            commands=(RelinkAssetCommand(candidate.replacement),),
        )
        try:
            applied = session.execute(batch)
        except CommandError as exc:
            raise RelinkError(
                RelinkErrorCode.COMMAND_REJECTED,
                "verified relink candidate was rejected by canonical command",
            ) from exc
        return RelinkResult(
            asset_id=asset_id,
            previous_path=candidate.original_path,
            current_path=applied.asset(asset_id).path_ref,
            base_revision=base_revision,
            applied_revision=applied.revision,
        )
