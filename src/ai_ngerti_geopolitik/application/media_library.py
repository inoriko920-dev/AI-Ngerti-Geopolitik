"""Queryable, stable-ID media-bin model for STEP 11 W1."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from ai_ngerti_geopolitik.domain import Asset, ProjectState


@dataclass(frozen=True, slots=True)
class MediaBinQuery:
    text: str = ""
    media_types: tuple[str, ...] = ()
    availability: tuple[str, ...] = ()
    sort_by: str = "id"
    descending: bool = False


@dataclass(frozen=True, slots=True)
class MediaBinItem:
    asset_id: str
    source_name: str
    path_ref: str
    media_type: str
    availability: str
    duration_frames: int
    width: int
    height: int
    selected: bool


class MediaBinController:
    def __init__(self, state_provider: Callable[[], ProjectState]) -> None:
        self._state_provider = state_provider
        self._selection: tuple[str, ...] = ()

    @property
    def selected_asset_ids(self) -> tuple[str, ...]:
        state_ids = {asset.asset_id for asset in self._state_provider().assets}
        self._selection = tuple(item for item in self._selection if item in state_ids)
        return self._selection

    def select(self, asset_id: str, *, additive: bool = False) -> tuple[str, ...]:
        self._state_provider().asset(asset_id)
        if additive:
            current = list(self.selected_asset_ids)
            if asset_id not in current:
                current.append(asset_id)
            self._selection = tuple(current)
        else:
            self._selection = (asset_id,)
        return self._selection

    def clear_selection(self) -> None:
        self._selection = ()

    def query(self, query: MediaBinQuery = MediaBinQuery()) -> tuple[MediaBinItem, ...]:
        if query.sort_by not in {"id", "name", "type", "availability"}:
            raise ValueError(f"unsupported media-bin sort: {query.sort_by}")
        needle = query.text.casefold().strip()
        selected = set(self.selected_asset_ids)
        assets = [
            asset
            for asset in self._state_provider().assets
            if self._matches(asset, query, needle)
        ]
        key_map = {
            "id": lambda asset: asset.asset_id.casefold(),
            "name": lambda asset: (asset.source_name or asset.path_ref).casefold(),
            "type": lambda asset: (asset.media_type, asset.asset_id),
            "availability": lambda asset: (asset.availability, asset.asset_id),
        }
        assets.sort(key=key_map[query.sort_by], reverse=query.descending)
        return tuple(
            MediaBinItem(
                asset_id=asset.asset_id,
                source_name=asset.source_name,
                path_ref=asset.path_ref,
                media_type=asset.media_type,
                availability=asset.availability,
                duration_frames=asset.duration.frames,
                width=asset.width,
                height=asset.height,
                selected=asset.asset_id in selected,
            )
            for asset in assets
        )

    @staticmethod
    def _matches(asset: Asset, query: MediaBinQuery, needle: str) -> bool:
        if query.media_types and asset.media_type not in query.media_types:
            return False
        if query.availability and asset.availability not in query.availability:
            return False
        if not needle:
            return True
        haystack = " ".join((asset.asset_id, asset.source_name, asset.path_ref)).casefold()
        return needle in haystack
