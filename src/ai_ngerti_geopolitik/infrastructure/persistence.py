"""Atomic .angproj JSON persistence for STEP 10."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from ai_ngerti_geopolitik.domain import Asset, Clip, FrameTime, ProjectState, Track


class ProjectFormatError(RuntimeError):
    pass


class JsonProjectRepository:
    def save(self, state: ProjectState, path: Path) -> None:
        state.validate()
        path = path.resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix.lower() != ".angproj":
            raise ProjectFormatError("project file must use .angproj")
        data = state.semantic_dict(include_revision=True)
        payload = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        temp = path.with_name(f"{path.name}.tmp")
        try:
            with temp.open("w", encoding="utf-8", newline="\n") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp, path)
        finally:
            if temp.exists():
                temp.unlink()

    def load(self, path: Path) -> ProjectState:
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            return self._decode(raw)
        except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            raise ProjectFormatError(f"invalid project file: {path}") from exc

    def _decode(self, raw: dict[str, Any]) -> ProjectState:
        fps = int(raw["fps"])
        assets = tuple(
            Asset(
                asset_id=str(item["asset_id"]),
                path_ref=str(item["path_ref"]),
                media_type=str(item["media_type"]),
                duration=FrameTime(
                    int(item["duration"]["frames"]),
                    int(item["duration"]["fps"]),
                ),
                width=int(item["width"]),
                height=int(item["height"]),
                has_audio=bool(item["has_audio"]),
                fingerprint_sha256=str(item["fingerprint_sha256"]),
            )
            for item in raw.get("assets", [])
        )
        tracks: list[Track] = []
        for item in raw.get("tracks", []):
            clips = tuple(
                Clip(
                    clip_id=str(clip["clip_id"]),
                    asset_id=str(clip["asset_id"]),
                    timeline_start=FrameTime(
                        int(clip["timeline_start"]["frames"]),
                        int(clip["timeline_start"]["fps"]),
                    ),
                    source_in=FrameTime(
                        int(clip["source_in"]["frames"]),
                        int(clip["source_in"]["fps"]),
                    ),
                    source_out=FrameTime(
                        int(clip["source_out"]["frames"]),
                        int(clip["source_out"]["fps"]),
                    ),
                    enabled=bool(clip.get("enabled", True)),
                )
                for clip in item.get("clips", [])
            )
            tracks.append(
                Track(
                    track_id=str(item["track_id"]),
                    kind=str(item["kind"]),
                    order=int(item["order"]),
                    clips=clips,
                )
            )
        state = ProjectState(
            project_id=str(raw["project_id"]),
            name=str(raw["name"]),
            schema_version=int(raw["schema_version"]),
            fps=fps,
            revision=int(raw["revision"]),
            assets=assets,
            tracks=tuple(tracks),
        )
        state.validate()
        return state
